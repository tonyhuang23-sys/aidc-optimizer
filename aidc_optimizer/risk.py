"""
蒙特卡洛 + 敏感性分析（第二十三~二十五节）
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np
from .core import LayerResult
from .models import BUILDERS, run_asset, DEFAULT_WACC
from .financing import DebtInputs, apply_financing
from .core import TaxEngine


def _set_path(d: dict, path: str, value):
    keys = path.split(".")
    cur = d
    for k in keys[:-1]:
        cur = cur[k]
    cur[keys[-1]] = value


def _get_path(d: dict, path: str):
    cur = d
    for k in path.split("."):
        cur = cur[k]
    return cur


def run_full_pipeline(cfg: dict, case_key: str, financing_cfg: Optional[dict] = None,
                      wacc: Optional[float] = None) -> LayerResult:
    import copy
    c = copy.deepcopy(cfg)
    if wacc is not None:
        c.setdefault("wacc", {})
        c["wacc"][BUILDERS[case_key](cfg).layer] = wacc
    case = BUILDERS[case_key](c)
    res = run_asset(case, c)
    fcfg = (financing_cfg or c.get("finance", {})).get(res.layer, {})
    if fcfg.get("enabled", True) and res.layer != "L0_Dev":
        debt_in = DebtInputs(**{k: v for k, v in fcfg.items() if k in DebtInputs.__dataclass_fields__})
        tax_cfg = c.get("tax", {})
        tax = TaxEngine(rate=tax_cfg.get("rate", 0.23),
                        dep_life_months=tax_cfg.get("dep_life_months", 240),
                        method=tax_cfg.get("method", "straight_line"))
        fr = apply_financing(case, debt_in, tax,
                             customer_capital=fcfg.get("customer_capital_musd", 0) * 1e6,
                             wacc_for_llcr=c.get("wacc", DEFAULT_WACC).get(res.layer, 0.09))
        res.debt_amount = fr.debt_amount
        res.idc = fr.idc
        res.sponsor_equity = fr.sponsor_equity
        res.peak_equity = fr.peak_equity
        res.customer_capital = fr.customer_capital
        res.equity_irr = fr.equity_irr
        res.moic = fr.moic
        res.min_dscr = fr.min_dscr
        res.avg_dscr = fr.avg_dscr
        res.llcr = fr.llcr
        res.levered_fcf_equity = fr.equity_cf
    else:
        res.sponsor_equity = res.capex_total
        res.peak_equity = res.capex_total
    return res


@dataclass
class MCResult:
    n_sims: int
    npv_p10: float
    npv_p50: float
    npv_p90: float
    irr_p50: float
    eqirr_p50: float
    prob_npv_negative: float
    prob_irr_below_hurdle: float
    hurdle: float
    npv_samples: Optional[np.ndarray] = None


def monte_carlo(cfg: dict, case_key: str, n_sims: int = 500, seed: int = 42,
                mc_section: Optional[dict] = None) -> MCResult:
    import copy
    rng = np.random.default_rng(seed)
    layer = BUILDERS[case_key](cfg).layer if case_key in BUILDERS else case_key
    mc_cfg = (mc_section or cfg.get("mc", {})).get(layer, {})
    hurdle = mc_cfg.get("hurdle", DEFAULT_WACC.get(layer, 0.12))
    npvs, irrs, eqirrs = [], [], []
    for i in range(n_sims):
        c = copy.deepcopy(cfg)
        for spec in mc_cfg.get("params", []):
            base = _get_path(c, spec["path"])
            if spec.get("dist") == "lognormal":
                sigma = spec.get("sigma", 0.15)
                mult = float(rng.lognormal(-sigma ** 2 / 2, sigma))
                _set_path(c, spec["path"], base * mult)
            elif spec.get("dist") == "normal":
                mu, sigma = spec.get("mu", 0.0), spec.get("sigma", 0.1)
                mult = float(max(0.2, rng.normal(1 + mu, sigma)))
                _set_path(c, spec["path"], base * mult)
        try:
            r = run_full_pipeline(c, case_key)
            npvs.append(r.project_npv)
            irrs.append(r.project_irr if r.project_irr is not None else np.nan)
            eqirrs.append(r.equity_irr if r.equity_irr is not None else np.nan)
        except Exception:
            continue
    npvs = np.array(npvs)
    if len(npvs) == 0:
        nan = float("nan")
        return MCResult(n_sims=0, npv_p10=nan, npv_p50=nan, npv_p90=nan,
                        irr_p50=nan, eqirr_p50=nan, prob_npv_negative=nan,
                        prob_irr_below_hurdle=nan, hurdle=hurdle)
    irrs = np.array([x for x in irrs if x == x])
    eqirrs = np.array([x for x in eqirrs if x == x])
    return MCResult(
        n_sims=len(npvs),
        npv_p10=float(np.percentile(npvs, 10)),
        npv_p50=float(np.percentile(npvs, 50)),
        npv_p90=float(np.percentile(npvs, 90)),
        irr_p50=float(np.median(irrs)) if len(irrs) else float("nan"),
        eqirr_p50=float(np.median(eqirrs)) if len(eqirrs) else float("nan"),
        prob_npv_negative=float((npvs < 0).mean()),
        prob_irr_below_hurdle=float((irrs < hurdle).mean()) if len(irrs) else float("nan"),
        hurdle=hurdle,
        npv_samples=npvs,
    )


def tornado(cfg: dict, case_key: str, delta: float = 0.15,
            variables: Optional[List[dict]] = None) -> List[dict]:
    import copy
    layer = BUILDERS[case_key](cfg).layer
    mc_cfg = cfg.get("mc", {}).get(layer, {})
    variables = variables or mc_cfg.get("params", [])
    out = []
    for spec in variables:
        row = {"path": spec["path"], "base": _get_path(cfg, spec["path"])}
        for tag, mult in [("low", 1 - delta), ("high", 1 + delta)]:
            c = copy.deepcopy(cfg)
            _set_path(c, spec["path"], row["base"] * mult)
            try:
                r = run_full_pipeline(c, case_key)
                row[f"npv_{tag}"] = r.project_npv / 1e6
                row[f"eqirr_{tag}"] = r.equity_irr
            except Exception:
                row[f"npv_{tag}"] = float("nan")
                row[f"eqirr_{tag}"] = float("nan")
        row["npv_swing"] = abs(row.get("npv_high", 0) - row.get("npv_low", 0))
        out.append(row)
    out.sort(key=lambda x: -(x["npv_swing"] if x["npv_swing"] == x["npv_swing"] else 0))
    return out
