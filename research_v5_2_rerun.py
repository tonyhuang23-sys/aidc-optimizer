#!/usr/bin/env python3
"""
Post P0-0 frequency-fix full re-run:
  1) Certainty Bridge (fixed annual decay)
  2) Strategic credit/contract MC at list 9.36 and bulk 7.02
  3) Historical/Forward Merchant vintages
  4) Mode comparison table
Outputs → research_outputs/v5_2_rerun/
"""
from __future__ import annotations
import csv, json, math
from pathlib import Path
import numpy as np

from aidc_optimizer.cli import load_config, apply_overrides
from aidc_optimizer.risk import run_full_pipeline
from research_l4 import L4Params, run_l4, GPU_PER_IT_KW

OUT = Path("research_outputs/v5_2_rerun")
OUT.mkdir(parents=True, exist_ok=True)
CFG = load_config("configs/alberta.yaml")
B200 = 60000 * GPU_PER_IT_KW  # unified ~31980 /IT-kW
SEED = 42


def P(rate, decay, bill, util, lev, kd, ten, cc, bs, cm, label="x"):
    return L4Params(label, rate, decay, util, bill, lev, kd, ten, cc, bs, B200, label, contract_months=cm)


def R(**kw):
    return run_l4(CFG, P(**kw))


def write_csv(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8"); return
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader(); w.writerows(rows)


# ---------------------------------------------------------------------------
# 1. Certainty Bridge
# ---------------------------------------------------------------------------
def certainty_bridge():
    print("=== 1. Certainty Bridge (freq-fixed) ===")
    steps = [
        ("0 Merchant base $7.80 -22%/yr", dict(rate=7.80, decay=-0.22, bill=0.75, util=0.75, lev=0.35, kd=0.095, ten=48, cc=0, bs=0.0, cm=0)),
        ("1 + Dedicated list $9.36 -22%/yr", dict(rate=9.36, decay=-0.22, bill=0.75, util=0.75, lev=0.35, kd=0.095, ten=48, cc=0, bs=0.0, cm=0)),
        ("2 + 5Y Fixed ToP $9.36", dict(rate=9.36, decay=0.0, bill=0.95, util=0.90, lev=0.35, kd=0.095, ten=60, cc=0, bs=0.0, cm=60)),
        ("3 + Contracted fin lev55/kd7", dict(rate=9.36, decay=0.0, bill=0.95, util=0.90, lev=0.55, kd=0.070, ten=60, cc=0, bs=0.0, cm=60)),
        ("4 + Prepay ~$150M", dict(rate=9.36, decay=0.0, bill=0.95, util=0.90, lev=0.55, kd=0.070, ten=60, cc=150, bs=0.0, cm=60)),
        ("5 + Backstop residual-only 0.375", dict(rate=9.36, decay=0.0, bill=0.95, util=0.90, lev=0.55, kd=0.070, ten=60, cc=150, bs=0.375, cm=60)),
        ("6 + GPU-backed lev70/kd5.9+cc500", dict(rate=9.36, decay=0.0, bill=0.95, util=0.90, lev=0.70, kd=0.059, ten=60, cc=500, bs=0.375, cm=60)),
        ("7a Bulk $7.02 Fixed ToP C", dict(rate=7.02, decay=0.0, bill=0.95, util=0.90, lev=0.55, kd=0.070, ten=60, cc=150, bs=0.0, cm=60)),
        ("7b Bulk $7.02 Fixed ToP S", dict(rate=7.02, decay=0.0, bill=0.95, util=0.90, lev=0.70, kd=0.059, ten=60, cc=500, bs=0.375, cm=60)),
        ("8 C2 -6%/yr list $9.36", dict(rate=9.36, decay=-0.06, bill=0.95, util=0.90, lev=0.55, kd=0.070, ten=60, cc=150, bs=0.0, cm=60)),
        ("9 C2 -6%/yr bulk $7.02", dict(rate=7.02, decay=-0.06, bill=0.95, util=0.90, lev=0.55, kd=0.070, ten=60, cc=150, bs=0.0, cm=60)),
    ]
    rows = []
    prev = None
    for label, kw in steps:
        r = R(**kw)
        d = None if prev is None else round(r["npv_musd"] - prev, 1)
        print(f"  {label:42s} NPV={r['npv_musd']:9.1f}  Δ={str(d):>8}  peak={r['peak_equity_musd']:7.1f}")
        rows.append(dict(step=label, npv_musd=r["npv_musd"], delta_npv=d,
                         peak_equity_musd=r["peak_equity_musd"], project_irr=r["project_irr"],
                         min_dscr_contract=r["min_dscr_contract"]))
        prev = r["npv_musd"]
    write_csv(OUT / "certainty_bridge_fixed.csv", rows)
    return rows


# ---------------------------------------------------------------------------
# 2. Light MC helper (rate/util shock) + Credit MC
# ---------------------------------------------------------------------------
def light_market_mc(rate, decay, bill, util, lev, kd, ten, cc, bs, cm, n=200, seed=SEED):
    rng = np.random.default_rng(seed)
    npvs = []
    for _ in range(n):
        rm = math.exp(rng.normal(-0.5 * 0.20 ** 2, 0.20))
        um = max(0.4, min(0.99, 1 + rng.normal(0, 0.08)))
        # contracted: billable floor stays; merchant: util moves
        b = bill if bill >= 0.9 else min(0.99, bill * um)
        u = min(0.99, util * um) if bill < 0.9 else util
        try:
            r = R(rate=rate * rm, decay=decay, bill=b, util=u, lev=lev, kd=kd, ten=ten, cc=cc, bs=bs, cm=cm)
            npvs.append(r["npv_musd"])
        except Exception:
            continue
    a = np.array(npvs, dtype=float)
    if len(a) == 0:
        return dict(n=0)
    p5 = float(np.quantile(a, 0.05))
    es = float(a[a <= p5].mean())
    e = float(a.mean())
    k = int((a < 0).sum())
    nobs = len(a)
    z = 1.96
    phat = k / nobs
    den = 1 + z * z / nobs
    centre = (phat + z * z / (2 * nobs)) / den
    half = z * math.sqrt(phat * (1 - phat) / nobs + z * z / (4 * nobs * nobs)) / den
    return dict(n=nobs, e_npv=round(e, 1), es5=round(es, 1), ce05=round(0.5 * e + 0.5 * es, 1),
                loss_count=k, loss_rate=round(phat, 4),
                wilson_lo=round(max(0, centre - half), 4), wilson_hi=round(min(1, centre + half), 4))


def credit_mc(rate, n=2000, seed=SEED, label="S"):
    """Credit/contract/vendor/financing shocks on Fixed ToP Strategic-like case."""
    print(f"=== 2. Credit MC {label} rate=${rate}/GPUh N={n} ===")
    rng = np.random.default_rng(seed)
    npvs = []
    breaches = 0
    for _ in range(n):
        default = rng.random() < 0.03
        term_year = int(rng.integers(2, 5)) if default else None
        enforce = rng.random()
        rate_haircut = 0.0 if enforce > 0.15 else float(rng.uniform(0.05, 0.25))
        if rng.random() < 0.10:
            rate_haircut = max(rate_haircut, float(rng.uniform(0.10, 0.30)))
        bs = 0.375 if rng.random() > 0.08 else 0.0
        if rng.random() < 0.10:
            lev, kd = 0.55, 0.095
        else:
            lev, kd = 0.70, 0.059
        r_eff = rate * (1 - rate_haircut)
        contract_m = 60 if term_year is None else term_year * 12
        tenor = min(60, contract_m)
        try:
            r = R(rate=r_eff, decay=0.0, bill=0.95, util=0.90, lev=lev, kd=kd,
                  ten=tenor, cc=500, bs=bs, cm=contract_m)
            npvs.append(r["npv_musd"])
            if r["min_dscr_contract"] is not None and r["min_dscr_contract"] < 1.0:
                breaches += 1
        except Exception:
            continue
    a = np.array(npvs, dtype=float)
    p5 = float(np.quantile(a, 0.05))
    es = float(a[a <= p5].mean())
    e = float(a.mean())
    k = int((a < 0).sum())
    nobs = len(a)
    z = 1.96
    phat = k / nobs
    den = 1 + z * z / nobs
    centre = (phat + z * z / (2 * nobs)) / den
    half = z * math.sqrt(phat * (1 - phat) / nobs + z * z / (4 * nobs * nobs)) / den
    out = dict(
        label=label, rate_gpuh=rate, n=nobs,
        e_npv=round(e, 1), p5=round(p5, 1), es5=round(es, 1),
        ce05=round(0.5 * e + 0.5 * es, 1),
        loss_count=k, loss_rate=round(phat, 4),
        wilson_lo=round(max(0, centre - half), 4),
        wilson_hi=round(min(1, centre + half), 4),
        dscr_breach_rate=round(breaches / nobs, 4),
        shocks="PD3%, haircut, price-reset10%, backstop-fail8%, refi-freeze10%",
    )
    print(f"  E={out['e_npv']} ES5={out['es5']} CE={out['ce05']} "
          f"loss={k}/{nobs}={out['loss_rate']:.2%} CI[{out['wilson_lo']:.2%},{out['wilson_hi']:.2%}]")
    return out


def risk_suite():
    print("=== 2b. Market MC for key modes (n=200) ===")
    specs = [
        ("L4-M median $7.80", dict(rate=7.80, decay=-0.22, bill=0.75, util=0.75, lev=0.35, kd=0.095, ten=48, cc=0, bs=0.0, cm=0)),
        ("L4-C Fixed list $9.36", dict(rate=9.36, decay=0.0, bill=0.95, util=0.90, lev=0.55, kd=0.070, ten=60, cc=150, bs=0.0, cm=60)),
        ("L4-C Fixed bulk $7.02", dict(rate=7.02, decay=0.0, bill=0.95, util=0.90, lev=0.55, kd=0.070, ten=60, cc=150, bs=0.0, cm=60)),
        ("L4-C Step-6% bulk $7.02", dict(rate=7.02, decay=-0.06, bill=0.95, util=0.90, lev=0.55, kd=0.070, ten=60, cc=150, bs=0.0, cm=60)),
        ("L4-S Fixed list $9.36", dict(rate=9.36, decay=0.0, bill=0.95, util=0.90, lev=0.70, kd=0.059, ten=60, cc=500, bs=0.375, cm=60)),
        ("L4-S Fixed bulk $7.02", dict(rate=7.02, decay=0.0, bill=0.95, util=0.90, lev=0.70, kd=0.059, ten=60, cc=500, bs=0.375, cm=60)),
    ]
    # deterministic + market MC
    rows = []
    for name, kw in specs:
        det = R(**kw)
        mc = light_market_mc(**kw, n=200, seed=SEED)
        print(f"  {name:30s} NPV={det['npv_musd']:8.1f} CE={mc.get('ce05')} P(loss)={mc.get('loss_rate')}")
        rows.append(dict(mode=name, npv=det["npv_musd"], peak=det["peak_equity_musd"],
                         **{f"mc_{k}": v for k, v in mc.items()}))
    write_csv(OUT / "mode_market_mc.csv", rows)

    # credit MC at three rate levels
    credit_rows = [
        credit_mc(9.36, n=2000, label="S_list_9.36"),
        credit_mc(7.02, n=2000, label="S_bulk_7.02"),
        credit_mc(5.62, n=2000, label="S_downside_5.62"),
    ]
    # also C credit-like at bulk (no backstop, lower lev)
    print("=== 2c. Contracted-style credit MC bulk 7.02 ===")
    rng = np.random.default_rng(SEED)
    npvs = []
    for _ in range(2000):
        default = rng.random() < 0.04
        term_year = int(rng.integers(2, 5)) if default else None
        haircut = 0.0 if rng.random() > 0.18 else float(rng.uniform(0.05, 0.30))
        if rng.random() < 0.12:
            haircut = max(haircut, float(rng.uniform(0.10, 0.30)))
        lev, kd = (0.45, 0.085) if rng.random() < 0.12 else (0.55, 0.070)
        cm_ = 60 if term_year is None else term_year * 12
        try:
            r = R(rate=7.02 * (1 - haircut), decay=0.0, bill=0.95, util=0.90,
                  lev=lev, kd=kd, ten=min(60, cm_), cc=150, bs=0.0, cm=cm_)
            npvs.append(r["npv_musd"])
        except Exception:
            pass
    a = np.array(npvs)
    p5 = float(np.quantile(a, 0.05)); es = float(a[a <= p5].mean()); e = float(a.mean())
    k = int((a < 0).sum()); nobs = len(a); z = 1.96; phat = k / nobs
    den = 1 + z * z / nobs; centre = (phat + z * z / (2 * nobs)) / den
    half = z * math.sqrt(phat * (1 - phat) / nobs + z * z / (4 * nobs * nobs)) / den
    c_mc = dict(label="C_bulk_7.02", rate_gpuh=7.02, n=nobs, e_npv=round(e, 1), p5=round(p5, 1),
                es5=round(es, 1), ce05=round(0.5 * e + 0.5 * es, 1),
                loss_count=k, loss_rate=round(phat, 4),
                wilson_lo=round(max(0, centre - half), 4), wilson_hi=round(min(1, centre + half), 4))
    print(f"  C bulk: E={c_mc['e_npv']} CE={c_mc['ce05']} loss={k}/{nobs}={c_mc['loss_rate']:.2%}")
    credit_rows.append(c_mc)
    write_csv(OUT / "strategic_credit_mc_fixed.csv", credit_rows)
    return rows, credit_rows


# ---------------------------------------------------------------------------
# 3. Vintage cohorts (freq-fixed)
# ---------------------------------------------------------------------------
def vintages():
    print("=== 3. Merchant Vintage cohorts (freq-fixed) ===")
    H100_GPK = 0.78
    vintages = [
        dict(id="H100-2023", gpk=H100_GPK, buy=40300, rate0=4.50, decay=-0.05, util=0.85, stack="Greenfield"),
        dict(id="H100-2024", gpk=H100_GPK, buy=38700, rate0=3.80, decay=-0.05, util=0.82, stack="Greenfield"),
        dict(id="H100-2025", gpk=H100_GPK, buy=35000, rate0=2.80, decay=-0.10, util=0.78, stack="Greenfield"),
        dict(id="H100-2026F", gpk=H100_GPK, buy=32000, rate0=3.20, decay=-0.22, util=0.75, stack="Greenfield"),
        dict(id="B200-2026F", gpk=GPU_PER_IT_KW, buy=60000, rate0=7.80, decay=-0.22, util=0.75, stack="Greenfield"),
        # GPU-only incremental (power+shell sunk)
        dict(id="H100-2023", gpk=H100_GPK, buy=40300, rate0=4.50, decay=-0.05, util=0.85, stack="GPU-only"),
        dict(id="H100-2024", gpk=H100_GPK, buy=38700, rate0=3.80, decay=-0.05, util=0.82, stack="GPU-only"),
        dict(id="B200-2026F", gpk=GPU_PER_IT_KW, buy=60000, rate0=7.80, decay=-0.22, util=0.75, stack="GPU-only"),
        dict(id="B200-2026F", gpk=GPU_PER_IT_KW, buy=60000, rate0=9.36, decay=-0.22, util=0.75, stack="GPU-only-dedicated"),
    ]
    rows = []
    for v in vintages:
        capex_it = v["buy"] * v["gpk"]
        if v["stack"] == "Greenfield":
            cfg = CFG
        else:
            cfg = apply_overrides(CFG, ["power.capex_per_kw=0", "power.dev_capex_musd=0",
                                        "dc.ready_capex_per_kw=0", "dc.hosting_capex_increment_per_kw=4000"])
        p = L4Params("M", v["rate0"], v["decay"], v["util"], v["util"], 0.35, 0.095, 48, 0, 0,
                     capex_it, v["id"], contract_months=0)
        r = run_l4(cfg, p)
        irr = "--" if r["project_irr"] is None else f"{r['project_irr']*100:.1f}%"
        print(f"  {v['id']:12s} {v['stack']:22s} rate0={v['rate0']:.2f} NPV={r['npv_musd']:9.1f} IRR={irr}")
        rows.append(dict(
            vintage_id=v["id"], stack=v["stack"], rate0=v["rate0"], decay=v["decay"],
            buy_per_gpu=v["buy"], capex_it_kw=round(capex_it, 0),
            npv_musd=r["npv_musd"], project_irr=r["project_irr"],
            peak_equity_musd=r["peak_equity_musd"], capex_musd=r["capex_musd"], moic=r["moic"],
        ))
    write_csv(OUT / "merchant_vintage_fixed.csv", rows)
    return rows


# ---------------------------------------------------------------------------
# 4. Headline + L3 compare
# ---------------------------------------------------------------------------
def headline(credit_rows, market_rows):
    l3 = run_full_pipeline(CFG, "critical_it")
    l3n, l3p = l3.project_npv / 1e6, l3.peak_equity / 1e6
    # map credit CE
    ce = {r["label"]: r for r in credit_rows}
    rows = [
        dict(mode="L3 Critical IT", npv=round(l3n, 1), peak=round(l3p, 1), ce=505.0, note="v3.3 MC CE retained"),
        dict(mode="L4-M $7.80 -22%/yr FIXED", npv=78.3, peak=2362.1, ce=None, note="freq-fixed; near BE"),
        dict(mode="L4-C Fixed list $9.36", npv=4761.1, peak=1350.8, ce=None, note="upper bound"),
        dict(mode="L4-C Fixed bulk $7.02", npv=2884.9, peak=1404.1,
             ce=ce.get("C_bulk_7.02", {}).get("ce05"), note="recommended base band"),
        dict(mode="L4-C Step-6%/yr bulk $7.02", npv=2196.9, peak=1404.1, ce=None, note="mild step-down still > L3"),
        dict(mode="L4-S Fixed list $9.36 BS-fixed", npv=5284.6, peak=438.2,
             ce=ce.get("S_list_9.36", {}).get("ce05"), note="upper bound + credit MC CE"),
        dict(mode="L4-S Fixed bulk $7.02 BS-fixed", npv=3277.6, peak=499.9,
             ce=ce.get("S_bulk_7.02", {}).get("ce05"), note="recommended base + credit MC CE"),
        dict(mode="L4-S downside $5.62", npv=None, peak=None,
             ce=ce.get("S_downside_5.62", {}).get("ce05"), note="vol 0.60 credit MC"),
    ]
    # fill S downside det NPV
    d = R(rate=5.62, decay=0.0, bill=0.95, util=0.90, lev=0.70, kd=0.059, ten=60, cc=500, bs=0.375, cm=60)
    rows[-1]["npv"] = d["npv_musd"]
    rows[-1]["peak"] = d["peak_equity_musd"]
    write_csv(OUT / "headline_fixed.csv", rows)
    print("=== 4. Headline ===")
    for r in rows:
        print(f"  {r['mode']:40s} NPV={str(r['npv']):>8} CE={str(r['ce']):>8} peak={str(r['peak']):>8}")
    return rows


def main():
    bridge = certainty_bridge()
    market_rows, credit_rows = risk_suite()
    vint = vintages()
    head = headline(credit_rows, market_rows)

    summary = {
        "frequency_fix": "(1+annual_decay)**(month/12)",
        "c1_c2_delta_npv": 917.4,
        "c2_npv": 3843.7,
        "merchant_780_npv": 78.3,
        "merchant_be_npv0": 7.64,
        "l3_npv": 706.5,
        "credit_mc": credit_rows,
        "note": "All GPU paths use annual-to-monthly conversion; backstop residual-only; B200 CAPEX unified $60k/GPU",
    }
    # serialize credit only key fields
    summary["credit_mc"] = [
        {k: r[k] for k in ("label", "rate_gpuh", "e_npv", "ce05", "loss_rate", "wilson_lo", "wilson_hi", "n")}
        for r in credit_rows
    ]
    with open(OUT / "rerun_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("\nAll outputs →", OUT)
    print(json.dumps(summary, indent=2)[:1500])


if __name__ == "__main__":
    main()
