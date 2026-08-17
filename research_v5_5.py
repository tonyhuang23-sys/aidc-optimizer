#!/usr/bin/env python3
"""
HISTORICAL SCRIPT — period artifact, not engine 1.2.1.
0.375 is the v5.1 compensation for the old 1-phys double-count engine.
Live research_l4.py bills residual unsold only; live S default is 0.75.

v5.5 — Transfer pricing, matched counterparty, CE bootstrap CI,
IRASR_econ primary, GPU-only CE parity, access p* with L3 fallback.

Does not expand the framework. Addresses remaining P0/P1 from the v5.4 review.
"""
from __future__ import annotations
import csv, json, math
from pathlib import Path
import numpy as np

from aidc_optimizer.cli import load_config, apply_overrides
from aidc_optimizer.risk import run_full_pipeline
from research_l4 import L4Params, run_l4, GPU_PER_IT_KW
from research_v5_4 import (
    summarize, wilson, econ_cap, B200, CFG, SEED,
    allrisk_L3, allrisk_L4M, allrisk_L4C, allrisk_L4S,
    ILLUSTRATIVE_BULK, PUBLIC_NONSPOT_MEDIAN, M3_SHORT_DED,
    write_csv,
)

OUT = Path("research_outputs/v5_5")
OUT.mkdir(parents=True, exist_ok=True)

# L3 market rent: $185/kW-mo × 12 = $2,220/kW-yr
L3_RENT_KW_MO = CFG["dc"]["ready_rent_kw_mo"]  # 185
TRANSFER_OPEX_KW_YR = L3_RENT_KW_MO * 12       # 2220
N_HEAD = 800   # screening; paper notes formal freeze target 10000
N_GRID = 300    # CE parity grid


def cfg_gpu_only(charge_l3_rent: bool):
    ov = ["power.capex_per_kw=0", "power.dev_capex_musd=0",
          "dc.ready_capex_per_kw=0", "dc.hosting_capex_increment_per_kw=4000"]
    if charge_l3_rent:
        base = CFG["gpu"].get("extra_opex_kw_yr", 15)
        ov.append(f"gpu.extra_opex_kw_yr={base + TRANSFER_OPEX_KW_YR}")
    return apply_overrides(CFG, ov)


def allrisk_gpuonly(rate, charge_l3_rent, n=N_HEAD, seed=SEED, label="go"):
    """GPU-only with optional L3 transfer rent in opex."""
    print(f"=== GPU-only {label} rent={rate} transfer={charge_l3_rent} N={n} ===")
    rng = np.random.default_rng(seed)
    cfg0 = cfg_gpu_only(charge_l3_rent)
    npvs = []
    for _ in range(n):
        rm = math.exp(rng.normal(-0.5 * 0.25 ** 2, 0.25))
        um = max(0.35, min(0.98, 1 + rng.normal(0, 0.12)))
        dec = max(-0.45, min(0.05, -0.22 + float(rng.normal(0, 0.04))))
        if rng.random() < 0.12:
            lev, kd = 0.25, 0.12
        else:
            lev, kd = 0.35, 0.095
        if rm < 0.75 and rng.random() < 0.3:
            dec = min(dec, -0.30)
        try:
            r = run_l4(cfg0, L4Params("m", rate * rm, dec, min(0.95, 0.75 * um),
                                      min(0.95, 0.75 * um), lev, kd, 48, 0, 0.0, B200, "m", 0))
            npvs.append(r["npv_musd"])
        except Exception:
            continue
    s = summarize(npvs, label, n)
    s["npv_samples"] = npvs
    print(f"  CE={s.get('ce05')} E={s.get('e_npv')} loss={s.get('loss_rate')}")
    return s


def bootstrap_ci(npvs, n_boot=2000, seed=99):
    """Bootstrap 95% CI for E, ES5, CE(λ=0.5)."""
    a = np.asarray(npvs, dtype=float)
    rng = np.random.default_rng(seed)
    n = len(a)
    e_s, es_s, ce_s = [], [], []
    for _ in range(n_boot):
        b = rng.choice(a, size=n, replace=True)
        e = float(b.mean())
        p5 = float(np.quantile(b, 0.05))
        tail = b[b <= p5]
        es = float(tail.mean()) if len(tail) else p5
        e_s.append(e); es_s.append(es); ce_s.append(0.5 * e + 0.5 * es)
    def ci(x):
        return round(float(np.quantile(x, 0.025)), 1), round(float(np.quantile(x, 0.975)), 1)
    return dict(E_lo=ci(e_s)[0], E_hi=ci(e_s)[1],
                ES_lo=ci(es_s)[0], ES_hi=ci(es_s)[1],
                CE_lo=ci(ce_s)[0], CE_hi=ci(ce_s)[1])


def matched_counterparty():
    """Same customer-credit intensity for L3 and L4-C (layer effect vs credit effect)."""
    print("=== Matched Counterparty Test ===")
    # Weak tenant (generic): higher PD
    # Strong tenant (IG): lower PD
    # We approximate by scaling default-like rent/rate haircut frequency
    # Reuse allrisk with seed variants documented as credit tiers
    # L3 weak already ~2% default in allrisk_L3
    l3_weak = allrisk_L3(n=N_HEAD, seed=SEED)
    l3_weak["label"] = "L3_generic_tenant"
    # L3 strong: lower default — rerun with patched function via rent volatility only
    l3_strong = allrisk_L3_credit(n=N_HEAD, pd=0.008, seed=SEED + 1)
    c_weak = allrisk_L4C_credit(ILLUSTRATIVE_BULK, pd=0.04, n=N_HEAD, seed=SEED + 2, label="C_generic")
    c_strong = allrisk_L4C_credit(ILLUSTRATIVE_BULK, pd=0.008, n=N_HEAD, seed=SEED + 3, label="C_IG")
    rows = [l3_weak, l3_strong, c_weak, c_strong]
    # strip samples for csv
    slim = []
    for r in rows:
        d = {k: v for k, v in r.items() if k != "npv_samples"}
        slim.append(d)
        print(f"  {d['label']:22s} CE={d.get('ce05')} loss={d.get('loss_rate')}")
    write_csv(OUT / "matched_counterparty.csv", slim)
    layer = c_strong["ce05"] - l3_strong["ce05"]   # same IG credit
    credit = (c_strong["ce05"] - c_weak["ce05"]) - (l3_strong["ce05"] - l3_weak["ce05"])
    decomp = dict(
        CE_L3_generic=l3_weak["ce05"], CE_L3_IG=l3_strong["ce05"],
        CE_C_generic=c_weak["ce05"], CE_C_IG=c_strong["ce05"],
        layer_effect_IG=round(layer, 1),
        note="layer_effect = CE_C_IG - CE_L3_IG (same credit); remaining gap may be tenor/structure",
    )
    write_csv(OUT / "layer_vs_counterparty.csv", [decomp])
    print("  Layer effect (IG matched):", decomp["layer_effect_IG"])
    return {r["label"]: r for r in rows}, decomp


def allrisk_L3_credit(n, pd, seed):
    rng = np.random.default_rng(seed)
    npvs = []
    for _ in range(n):
        default = rng.random() < pd
        rent_m = 0.0 if default else math.exp(rng.normal(-0.5 * 0.12 ** 2, 0.12))
        if rng.random() < pd * 2:
            rent_m *= float(rng.uniform(0.85, 0.95))
        capex_m = math.exp(rng.normal(-0.5 * 0.10 ** 2, 0.10))
        if rng.random() < 0.08:
            rent_m *= 0.92
        try:
            cfg = apply_overrides(CFG, [
                f"dc.ready_rent_kw_mo={CFG['dc']['ready_rent_kw_mo'] * rent_m}",
                f"dc.ready_capex_per_kw={CFG['dc']['ready_capex_per_kw'] * capex_m}",
            ])
            r = run_full_pipeline(cfg, "critical_it")
            npvs.append(r.project_npv / 1e6)
        except Exception:
            continue
    s = summarize(npvs, "L3_IG_tenant", n)
    s["npv_samples"] = npvs
    s["pd"] = pd
    return s


def allrisk_L4C_credit(rate, pd, n, seed, label):
    rng = np.random.default_rng(seed)
    npvs = []
    for _ in range(n):
        default = rng.random() < pd
        term_y = int(rng.integers(2, 5)) if default else None
        haircut = 0.0
        if rng.random() < pd * 4:
            haircut = float(rng.uniform(0.05, 0.30))
        if rng.random() < 0.12:
            haircut = max(haircut, float(rng.uniform(0.10, 0.30)))
        res_shock = max(0.5, 1 + rng.normal(0, 0.15))
        lev, kd = (0.45, 0.085) if rng.random() < 0.12 else (0.55, 0.070)
        cm = 60 if term_y is None else term_y * 12
        try:
            r = run_l4(CFG, L4Params("c", rate * (1 - haircut), 0.0, 0.90, 0.95,
                                     lev, kd, min(60, cm), 150, 0.0, B200, "c", cm))
            npvs.append(r["npv_musd"] * (0.85 + 0.15 * res_shock))
        except Exception:
            continue
    s = summarize(npvs, label, n)
    s["npv_samples"] = npvs
    s["pd"] = pd
    return s


def ce_from_samples(npvs, lam):
    a = np.asarray(npvs, dtype=float)
    e = float(a.mean())
    p5 = float(np.quantile(a, 0.05))
    tail = a[a <= p5]
    es = float(tail.mean()) if len(tail) else p5
    return (1 - lam) * e + lam * es


def lambda_table(sample_map):
    print("=== λ sensitivity (All-risk samples) ===")
    rows = []
    for name, npvs in sample_map.items():
        rec = {"mode": name}
        ces = []
        for lam in (0.0, 0.25, 0.5, 0.75, 1.0):
            v = ce_from_samples(npvs, lam)
            rec[f"CE_l{str(lam).replace('.','')}"] = round(v, 1)
            ces.append(v)
        rec["rank_note"] = "see paper"
        rows.append(rec)
        print(f"  {name:28s} λ0={ces[0]:.0f} λ.5={ces[2]:.0f} λ1={ces[4]:.0f}")
    write_csv(OUT / "lambda_sensitivity_allrisk.csv", rows)
    return rows


def gpuonly_ce_parity(l3_ce):
    print("=== GPU-only CE parity vs L3 ===")
    # accounting (no transfer) and economic (transfer rent)
    rows = []
    for charge, tag in [(False, "accounting_sunk"), (True, "economic_transfer")]:
        grid = []
        for rt in [7.0, 8.0, 9.0, 10.0, 11.0, 12.0]:
            s = allrisk_gpuonly(rt, charge, n=N_GRID, seed=11, label=f"{tag}_{rt}")
            grid.append((rt, s["ce05"]))
            print(f"  {tag} r={rt} CE={s['ce05']}")
        rate_ce = None
        for (r0, c0), (r1, c1) in zip(grid, grid[1:]):
            if (c0 - l3_ce) * (c1 - l3_ce) <= 0:
                rate_ce = r0 + (l3_ce - c0) * (r1 - r0) / (c1 - c0 + 1e-9)
                break
        if rate_ce is None:
            r0, c0 = grid[0]; r1, c1 = grid[-1]
            rate_ce = r0 + (l3_ce - c0) * (r1 - r0) / (c1 - c0 + 1e-9)
        rows.append(dict(view=tag, CE_parity_vs_L3=round(rate_ce, 2),
                         grid=";".join(f"{r}:{c}" for r, c in grid)))
        print(f"  {tag} CE=L3 at ~${rate_ce:.2f}/GPUh")
    write_csv(OUT / "gpuonly_ce_parity.csv", rows)
    return rows


def access_pstar(ce_l3, ce_c, ce_s):
    print("=== Access p* with L3 fallback ===")
    rows = []
    for pursuit in [5, 10, 20, 50, 100]:
        # EV_C = p*CE_C + (1-p)*CE_L3 - pursuit
        # beats L3 iff p*(CE_C-CE_L3) > pursuit
        p_c = pursuit / max(1e-6, ce_c - ce_l3)
        p_s = pursuit / max(1e-6, ce_s - ce_l3)
        rows.append(dict(
            pursuit_cost_musd=pursuit,
            pC_star=round(min(1.0, max(0.0, p_c)), 4),
            pS_star=round(min(1.0, max(0.0, p_s)), 4),
            CE_C=ce_c, CE_S=ce_s, CE_L3=ce_l3,
            formula="p* = Pursuit / (CE_contract - CE_L3)  [fallback = stay L3]",
        ))
        print(f"  pursuit ${pursuit}M → pC*={p_c:.3f} pS*={p_s:.3f}")
    write_csv(OUT / "access_pstar_l3_fallback.csv", rows)
    return rows


def irasr_econ_primary(ce_l3, peak_l3, samples):
    """Primary IRASR_econ using All-risk CE."""
    print("=== IRASR_econ primary ===")
    l3 = run_full_pipeline(CFG, "critical_it")
    l3_capex = l3.capex_total / 1e6
    l3_econ = econ_cap(peak_l3, l3_capex, "L3")

    def det_gpuonly(rate, transfer):
        cfg = cfg_gpu_only(transfer)
        return run_l4(cfg, L4Params("m", rate, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, B200, "m", 0))

    specs = [
        ("Full-stack mix-ref $7.80", "M", samples["m_mix"]["ce05"],
         run_l4(CFG, L4Params("m", 7.8, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, B200, "m", 0))),
        ("GPU-only accounting $7.80", "gpu", samples["go_acc"]["ce05"], det_gpuonly(7.8, False)),
        ("GPU-only economic (pay L3 rent) $7.80", "gpu", samples["go_econ"]["ce05"], det_gpuonly(7.8, True)),
        ("Contracted illustrative bulk $7.02", "C", samples["c"]["ce05"],
         run_l4(CFG, L4Params("c", ILLUSTRATIVE_BULK, 0, 0.90, 0.95, 0.55, 0.07, 60, 150, 0, B200, "c", 60))),
        ("Strategic illustrative bulk $7.02", "S", samples["s"]["ce05"],
         run_l4(CFG, L4Params("s", ILLUSTRATIVE_BULK, 0, 0.90, 0.95, 0.70, 0.059, 60, 500, 0.375, B200, "s", 60))),
    ]
    rows = []
    for name, mode, ce, r in specs:
        peak = r["peak_equity_musd"]
        econ = econ_cap(peak, r["capex_musd"], mode)
        d_ce = round(ce - ce_l3, 1)
        d_econ = round(econ - l3_econ, 1)
        d_peak = round(peak - peak_l3, 1)
        ir_e = None if d_econ == 0 else round(d_ce / d_econ, 3)
        ir_p = None if d_peak == 0 else round(d_ce / d_peak, 3)
        print(f"  {name:42s} ΔCE={d_ce:8.1f} IRASR_econ={ir_e} IRASR_peak={ir_p}")
        rows.append(dict(case=name, ce=ce, peak=peak, econ_cap=round(econ, 1),
                         delta_ce=d_ce, delta_econ=d_econ, delta_peak=d_peak,
                         IRASR_econ_PRIMARY=ir_e, IRASR_peak_secondary=ir_p))
    write_csv(OUT / "irasr_econ_primary.csv", rows)
    return rows


def main():
    # Headline All-risk N=2000 + keep samples for bootstrap / lambda
    print("=== Headline All-risk N=%d ===" % N_HEAD)
    l3 = allrisk_L3(n=N_HEAD, seed=SEED)
    # monkeypatch: allrisk_L3 does not return samples — re-run wrapper
    # We need samples. Patch by re-calling credit L3
    l3s = allrisk_L3_credit(N_HEAD, pd=0.02, seed=SEED)
    l3s["label"] = "L3_allrisk"
    m_mix = allrisk_L4M(PUBLIC_NONSPOT_MEDIAN, n=N_HEAD, seed=SEED, label="L4M_mixref_7.80")
    # allrisk_L4M doesn't store samples either. Re-run gpuonly helpers for samples.
    go_acc = allrisk_gpuonly(7.80, False, n=N_HEAD, seed=SEED, label="GO_accounting_7.80")
    go_econ = allrisk_gpuonly(7.80, True, n=N_HEAD, seed=SEED + 5, label="GO_economic_7.80")
    go_econ936 = allrisk_gpuonly(9.36, True, n=N_HEAD, seed=SEED + 6, label="GO_economic_9.36")
    c = allrisk_L4C_credit(ILLUSTRATIVE_BULK, pd=0.04, n=N_HEAD, seed=SEED + 2, label="C_bulk")
    s = allrisk_L4S(ILLUSTRATIVE_BULK, n=N_HEAD, seed=SEED, label="S_bulk")

    # For L3/M/C/S bootstrap we need samples. L3s, go_*, c have samples.
    # Re-collect M and S with wrappers that save samples
    m_samples = go_acc["npv_samples"]  # not mix full-stack
    # full-stack mix via allrisk_L4M — patch: run a sample-saving copy
    m_full = allrisk_gpuonly_fullstack(7.80, n=N_HEAD, seed=SEED)
    s_samp = collect_S_samples(ILLUSTRATIVE_BULK, n=N_HEAD, seed=SEED)

    sample_map = {
        "L3": l3s["npv_samples"],
        "M_fullstack_7.80": m_full["npv_samples"],
        "GO_accounting": go_acc["npv_samples"],
        "GO_economic": go_econ["npv_samples"],
        "C_bulk": c["npv_samples"],
        "S_bulk": s_samp,
    }

    ci_rows = []
    for name, samp in sample_map.items():
        sm = summarize(samp, name, N_HEAD)
        ci = bootstrap_ci(samp)
        rec = {**{k: v for k, v in sm.items() if k != "npv_samples"}, **ci}
        ci_rows.append(rec)
        print(f"  CI {name:22s} CE={sm['ce05']} [{ci['CE_lo']},{ci['CE_hi']}]")
    write_csv(OUT / "allrisk_ce_bootstrap_ci.csv", ci_rows)

    ce_l3 = summarize(sample_map["L3"], "L3", N_HEAD)["ce05"]
    peak_l3 = run_full_pipeline(CFG, "critical_it").peak_equity / 1e6
    samples = dict(
        m_mix=summarize(sample_map["M_fullstack_7.80"], "m", N_HEAD),
        go_acc=go_acc, go_econ=go_econ, c=c,
        s=summarize(s_samp, "s", N_HEAD),
    )
    irasr_econ_primary(ce_l3, peak_l3, samples)
    lambda_table(sample_map)
    gpuonly_ce_parity(ce_l3)
    ce_c = summarize(sample_map["C_bulk"], "c", N_HEAD)["ce05"]
    ce_s = summarize(s_samp, "s", N_HEAD)["ce05"]
    access_pstar(ce_l3, ce_c, ce_s)

    # Transfer pricing headline
    acc = go_acc["ce05"]; eon = go_econ["ce05"]
    print(f"\nTransfer pricing: accounting CE={acc} vs economic (pay L3 rent) CE={eon}")

    matched, decomp = matched_counterparty()

    summary = dict(
        n_headline=N_HEAD,
        n_note="screening 2000; formal freeze target 10000",
        CE_L3=ce_l3,
        CE_M_fullstack=summarize(sample_map["M_fullstack_7.80"], "m", N_HEAD)["ce05"],
        CE_GO_accounting=acc,
        CE_GO_economic=eon,
        CE_C_bulk=ce_c,
        CE_S_bulk=ce_s,
        layer_effect_IG=decomp["layer_effect_IG"],
        transfer_rent_kw_mo=L3_RENT_KW_MO,
        transfer_opex_kw_yr=TRANSFER_OPEX_KW_YR,
    )
    with open(OUT / "v5_5_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nSUMMARY", json.dumps(summary, indent=2))
    print("Outputs →", OUT)


def allrisk_gpuonly_fullstack(rate, n, seed):
    """Full-stack merchant with saved samples (same shocks as allrisk_L4M)."""
    rng = np.random.default_rng(seed)
    npvs = []
    for _ in range(n):
        rm = math.exp(rng.normal(-0.5 * 0.25 ** 2, 0.25))
        um = max(0.35, min(0.98, 1 + rng.normal(0, 0.12)))
        dec = max(-0.45, min(0.05, -0.22 + float(rng.normal(0, 0.04))))
        lev, kd = (0.25, 0.12) if rng.random() < 0.12 else (0.35, 0.095)
        if rm < 0.75 and rng.random() < 0.3:
            dec = min(dec, -0.30)
        try:
            r = run_l4(CFG, L4Params("m", rate * rm, dec, min(0.95, 0.75 * um),
                                      min(0.95, 0.75 * um), lev, kd, 48, 0, 0.0, B200, "m", 0))
            npvs.append(r["npv_musd"])
        except Exception:
            continue
    s = summarize(npvs, "M_fullstack", n)
    s["npv_samples"] = npvs
    print(f"  fullstack mix CE={s['ce05']} loss={s['loss_rate']}")
    return s


def collect_S_samples(rate, n, seed):
    rng = np.random.default_rng(seed)
    npvs = []
    for _ in range(n):
        default = rng.random() < 0.03
        term_y = int(rng.integers(2, 5)) if default else None
        haircut = 0.0 if rng.random() > 0.15 else float(rng.uniform(0.05, 0.25))
        if rng.random() < 0.10:
            haircut = max(haircut, float(rng.uniform(0.10, 0.30)))
        bs = 0.375 if rng.random() > 0.08 else 0.0
        lev, kd = (0.55, 0.095) if rng.random() < 0.10 else (0.70, 0.059)
        res_shock = max(0.5, 1 + rng.normal(0, 0.12))
        cm = 60 if term_y is None else term_y * 12
        try:
            r = run_l4(CFG, L4Params("s", rate * (1 - haircut), 0.0, 0.90, 0.95,
                                     lev, kd, min(60, cm), 500, bs, B200, "s", cm))
            npvs.append(r["npv_musd"] * (0.9 + 0.1 * res_shock))
        except Exception:
            continue
    print(f"  S samples n={len(npvs)} CE={summarize(npvs,'s',n)['ce05']}")
    return npvs


if __name__ == "__main__":
    main()
