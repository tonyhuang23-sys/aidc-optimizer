#!/usr/bin/env python3
"""
v6.1 — Frequency-corrected 2×2×2 (Asset × Contract × Vintage).

Replaces the pre-P0-0 Table 5 effects. Decay path is (1+g)^(k/12) in models.py.
Reports deterministic NPV / IRR / Peak plus All-risk-lite CE per cell, then
main effects and two-way interactions.

    python research_v6_factorial_fixed.py
"""
from __future__ import annotations

import csv
import json
import math
import subprocess
from pathlib import Path

import numpy as np

from aidc_optimizer.cli import load_config, apply_overrides
from aidc_optimizer.risk import run_full_pipeline
from reproduce import FACTOR_LEVELS, RATE_BY_CELL, gpu_correlated_mc, run_scenario

OUT = Path("research_outputs/v6_1")
OUT.mkdir(parents=True, exist_ok=True)
CFG = load_config("configs/alberta.yaml")
SEED = 42
N_CE = 800  # per-cell CE; not Headline N=10,000


def _commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True
        ).strip()
    except Exception:
        return "unknown"


def write_csv(path: Path, rows):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def ce_from_npvs(npvs_usd):
    a = np.asarray(npvs_usd, dtype=float) / 1e6
    e = float(a.mean())
    p5 = float(np.quantile(a, 0.05))
    tail = a[a <= p5]
    es = float(tail.mean()) if len(tail) else p5
    k = int((a < 0).sum())
    return dict(
        e_npv=round(e, 1),
        es5=round(es, 1),
        ce05=round(0.5 * e + 0.5 * es, 1),
        loss_rate=round(k / len(a), 4),
        n_ce=len(a),
    )


def cells():
    rows = []
    for asset, ov_a in FACTOR_LEVELS["asset"].items():
        for contract, ov_c in FACTOR_LEVELS["contract"].items():
            for vintage, ov_v in FACTOR_LEVELS["vintage"].items():
                rate = RATE_BY_CELL[(vintage, contract)]
                overrides = ov_a + ov_c + ov_v + [f"gpu.rate_per_kw_hr={rate}"]
                key = f"{asset} x {contract} x {vintage}"
                det = run_scenario(CFG, "compute", overrides)
                print(f"  DET {key:40s} NPV={det['npv_musd']:8.1f}  "
                      f"IRR={det['project_irr']}  Peak={det['peak_equity_musd']}")
                npvs = gpu_correlated_mc(CFG, overrides, N_CE, SEED)
                risk = ce_from_npvs(npvs)
                print(f"      CE={risk['ce05']}  E={risk['e_npv']}  "
                      f"loss={risk['loss_rate']}")
                rows.append(dict(
                    cell=key,
                    asset=asset,
                    contract=contract,
                    vintage=vintage,
                    rate_per_kw_hr=rate,
                    **det,
                    **risk,
                ))
    write_csv(OUT / "factorial_2x2x2_fixed.csv", rows)
    return rows


def contrast(rows, key, hi, lo, metric):
    a = np.mean([r[metric] for r in rows if r[key] == hi])
    b = np.mean([r[metric] for r in rows if r[key] == lo])
    return round(float(a - b), 1)


def two_way(rows, k1, v1a, v1b, k2, v2a, v2b, metric):
    """(A1B1 − A1B0) − (A0B1 − A0B0), averaged over the third factor."""
    def m(c1, c2):
        vals = [r[metric] for r in rows if r[k1] == c1 and r[k2] == c2]
        return float(np.mean(vals))
    return round((m(v1a, v2a) - m(v1a, v2b)) - (m(v1b, v2a) - m(v1b, v2b)), 1)


def effects(rows):
    metrics = ["npv_musd", "ce05", "peak_equity_musd", "e_npv"]
    out = []
    for metric in metrics:
        rec = dict(metric=metric)
        rec["vintage_New_minus_Used"] = contrast(rows, "vintage", "New", "Used", metric)
        rec["contract_C_minus_M"] = contrast(rows, "contract", "Contracted", "Merchant", metric)
        rec["asset_BF_minus_GF"] = contrast(rows, "asset", "Brownfield", "Greenfield", metric)
        rec["int_Vintage_x_Contract"] = two_way(
            rows, "vintage", "New", "Used", "contract", "Contracted", "Merchant", metric
        )
        rec["int_Vintage_x_Asset"] = two_way(
            rows, "vintage", "New", "Used", "asset", "Brownfield", "Greenfield", metric
        )
        rec["int_Contract_x_Asset"] = two_way(
            rows, "contract", "Contracted", "Merchant", "asset", "Brownfield", "Greenfield", metric
        )
        out.append(rec)
        print(f"  {metric:20s}  Vint={rec['vintage_New_minus_Used']}  "
              f"Ctr={rec['contract_C_minus_M']}  "
              f"Ast={rec['asset_BF_minus_GF']}  "
              f"VxC={rec['int_Vintage_x_Contract']}")
    write_csv(OUT / "factorial_effects_fixed.csv", out)
    return out


def main():
    print("=== Frequency-fixed 2×2×2  N_CE=%d  seed=%d ===" % (N_CE, SEED))
    rows = cells()
    fx = effects(rows)
    summary = dict(
        parameter_version="v6.1-factorial",
        commit=_commit(),
        seed=SEED,
        n_ce_per_cell=N_CE,
        decay_convention="(1+g)**(k/12) annual-to-month",
        note="Economic scenario package, not single-variable causal attribution",
        effects=fx,
        cells=[{k: r[k] for k in (
            "cell", "npv_musd", "project_irr", "peak_equity_musd", "ce05", "e_npv", "loss_rate"
        )} for r in rows],
    )
    (OUT / "factorial_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
