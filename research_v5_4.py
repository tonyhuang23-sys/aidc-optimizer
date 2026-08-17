#!/usr/bin/env python3
"""
HISTORICAL SCRIPT — period artifact, not engine 1.2.1.
0.375 is the v5.1 compensation for the old 1-phys double-count engine.
Live research_l4.py bills residual unsold only; live S default is 0.75.

v5.4 — All-risk CE harmonization, GPU-only IRASR, Merchant product mix,
Illustrative bulk naming, CE/EconCap break-evens.

Addresses review of v5.3:
  P0: unified All-risk Monte Carlo across L3/M/C/S (same taxonomy, different exposures)
  P0: GPU-only Merchant into main conclusions + L3→L4 incremental IRASR table
  P1: three price bases clarified; bulk = illustrative; Access/EconCap re-run; CE BEs
"""
from __future__ import annotations
import csv, json, math
from pathlib import Path
import numpy as np

from aidc_optimizer.cli import load_config, apply_overrides
from aidc_optimizer.risk import run_full_pipeline
from research_l4 import L4Params, run_l4, GPU_PER_IT_KW

OUT = Path("research_outputs/v5_4")
OUT.mkdir(parents=True, exist_ok=True)
CFG = load_config("configs/alberta.yaml")
B200 = 60000 * GPU_PER_IT_KW
SEED = 42
N_ALL = 800  # screening all-risk; formal release target ≥5000 noted in paper

# Price ladder (explicit naming)
M1_SPOT = 4.25
M2_ONDEMAND = 6.90
M3_SHORT_DED = 9.36
PUBLIC_NONSPOT_MEDIAN = 7.80   # product-mix reference, NOT pure spot
YAML_LEGACY_IT = 3.0           # golden base $/IT-kW-hr ≈ $5.63/GPUh
YAML_LEGACY_GPU = 3.0 / GPU_PER_IT_KW
ILLUSTRATIVE_BULK = 7.02       # 0.75 × list dedicated — scenario, not calibrated
LIST_DEDICATED = 9.36
DOWNSIDE_BULK = 5.62           # 0.60 × list


def write_csv(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8"); return
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader(); w.writerows(rows)


def P(rate, decay, bill, util, lev, kd, ten, cc, bs, cm, capex_it=None, label="x"):
    return L4Params(label, rate, decay, util, bill, lev, kd, ten, cc, bs,
                    B200 if capex_it is None else capex_it, label, contract_months=cm)


def runL4(cfg, **kw):
    return run_l4(cfg, P(**kw))


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    phat = k / n
    den = 1 + z * z / n
    centre = (phat + z * z / (2 * n)) / den
    half = z * math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n)) / den
    return max(0.0, centre - half), min(1.0, centre + half)


def summarize(npvs, label, n_target):
    a = np.asarray(npvs, dtype=float)
    nobs = len(a)
    if nobs == 0:
        return dict(label=label, n=0)
    p5 = float(np.quantile(a, 0.05))
    es = float(a[a <= p5].mean())
    e = float(a.mean())
    k = int((a < 0).sum())
    lo, hi = wilson(k, nobs)
    return dict(
        label=label, n=nobs, n_target=n_target,
        e_npv=round(e, 1), p5=round(p5, 1), es5=round(es, 1),
        ce05=round(0.5 * e + 0.5 * es, 1),
        loss_count=k, loss_rate=round(k / nobs, 4),
        wilson_lo=round(lo, 4), wilson_hi=round(hi, 4),
        p50=round(float(np.median(a)), 1),
    )


# ---------------------------------------------------------------------------
# All-risk Monte Carlo (same taxonomy, mode-specific exposures)
# Risks: tenant/customer default, GPU rent, utilization, residual, vendor, refinancing
# ---------------------------------------------------------------------------
def allrisk_L3(n=N_ALL, seed=SEED):
    """L3: tenant rent, opex, construction-ish via capex, refinancing spread on equity via WACC proxy."""
    print(f"=== All-risk L3 N={n} ===")
    rng = np.random.default_rng(seed)
    npvs = []
    for _ in range(n):
        # Tenant default / vacancy: rent haircut
        default = rng.random() < 0.02
        rent_m = 0.0 if default else math.exp(rng.normal(-0.5 * 0.12 ** 2, 0.12))
        if rng.random() < 0.05:  # downgrade / vacancy
            rent_m *= float(rng.uniform(0.85, 0.95))
        capex_m = math.exp(rng.normal(-0.5 * 0.10 ** 2, 0.10))
        # refinancing: higher discount via lower rent proxy if freeze
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
    s = summarize(npvs, "L3_allrisk", n)
    print(f"  CE={s.get('ce05')} E={s.get('e_npv')} loss={s.get('loss_rate')}")
    return s


def allrisk_L4M(rate, decay=-0.22, n=N_ALL, seed=SEED, stack="greenfield", label=None):
    """Merchant: rent, util, residual (via rate path), refinancing; residual exposure high."""
    lab = label or f"L4M_{rate}"
    print(f"=== All-risk {lab} stack={stack} N={n} ===")
    rng = np.random.default_rng(seed)
    if stack == "gpu_only":
        cfg0 = apply_overrides(CFG, ["power.capex_per_kw=0", "power.dev_capex_musd=0",
                                     "dc.ready_capex_per_kw=0", "dc.hosting_capex_increment_per_kw=4000"])
        capex_it = B200  # GPU + rack increment already in hosting; use B200 for GPU
        # For gpu_only, capex_per_kw_it is GPU purchase only
        capex_it = 60000 * GPU_PER_IT_KW
    else:
        cfg0 = CFG
        capex_it = B200
    npvs = []
    for _ in range(n):
        rm = math.exp(rng.normal(-0.5 * 0.25 ** 2, 0.25))
        um = max(0.35, min(0.98, 1 + rng.normal(0, 0.12)))
        # residual shock: effective decay worse/better
        dec = decay + float(rng.normal(0, 0.04))
        dec = max(-0.45, min(0.05, dec))
        # refinancing freeze → higher kd lower lev
        if rng.random() < 0.12:
            lev, kd = 0.25, 0.12
        else:
            lev, kd = 0.35, 0.095
        # residual collapse regime correlated with rent
        if rm < 0.75 and rng.random() < 0.3:
            dec = min(dec, -0.30)
        try:
            r = run_l4(cfg0, P(rate * rm, dec, 0.75 * um if um < 1 else 0.75, min(0.95, 0.75 * um),
                               lev, kd, 48, 0, 0.0, 0, capex_it=capex_it, label="m"))
            # billable = util for merchant
            r = run_l4(cfg0, L4Params("m", rate * rm, dec, min(0.95, 0.75 * um), min(0.95, 0.75 * um),
                                      lev, kd, 48, 0, 0.0, capex_it, "m", 0))
            npvs.append(r["npv_musd"])
        except Exception:
            continue
    s = summarize(npvs, lab, n)
    print(f"  CE={s.get('ce05')} E={s.get('e_npv')} loss={s.get('loss_rate')} CI=[{s.get('wilson_lo')},{s.get('wilson_hi')}]")
    return s


def allrisk_L4C(rate, decay=0.0, n=N_ALL, seed=SEED, label=None):
    """Contracted: customer default, contract break/repricing, residual, refinancing; rent/util mostly locked."""
    lab = label or f"L4C_{rate}"
    print(f"=== All-risk {lab} N={n} ===")
    rng = np.random.default_rng(seed)
    npvs = []
    for _ in range(n):
        default = rng.random() < 0.04
        term_y = int(rng.integers(2, 5)) if default else None
        haircut = 0.0
        if rng.random() < 0.18:
            haircut = float(rng.uniform(0.05, 0.30))
        if rng.random() < 0.12:  # price reset
            haircut = max(haircut, float(rng.uniform(0.10, 0.30)))
        # residual on terminal
        res_shock = max(0.5, 1 + rng.normal(0, 0.15))
        if rng.random() < 0.12:
            lev, kd = 0.45, 0.085
        else:
            lev, kd = 0.55, 0.070
        cm = 60 if term_y is None else term_y * 12
        # merchant fallback if default early: residual path
        try:
            r = run_l4(CFG, L4Params("c", rate * (1 - haircut), decay, 0.90, 0.95,
                                     lev, kd, min(60, cm), 150, 0.0, B200, "c", cm))
            npv = r["npv_musd"] * (0.85 + 0.15 * res_shock)  # light residual link
            # if early termination, already shorter cm
            npvs.append(npv)
        except Exception:
            continue
    s = summarize(npvs, lab, n)
    print(f"  CE={s.get('ce05')} E={s.get('e_npv')} loss={s.get('loss_rate')} CI=[{s.get('wilson_lo')},{s.get('wilson_hi')}]")
    return s


def allrisk_L4S(rate, n=N_ALL, seed=SEED, label=None):
    """Strategic: C risks + vendor backstop fail + stronger refi."""
    lab = label or f"L4S_{rate}"
    print(f"=== All-risk {lab} N={n} ===")
    rng = np.random.default_rng(seed)
    npvs = []
    for _ in range(n):
        default = rng.random() < 0.03
        term_y = int(rng.integers(2, 5)) if default else None
        haircut = 0.0 if rng.random() > 0.15 else float(rng.uniform(0.05, 0.25))
        if rng.random() < 0.10:
            haircut = max(haircut, float(rng.uniform(0.10, 0.30)))
        bs = 0.375 if rng.random() > 0.08 else 0.0  # vendor failure
        if rng.random() < 0.10:
            lev, kd = 0.55, 0.095
        else:
            lev, kd = 0.70, 0.059
        res_shock = max(0.5, 1 + rng.normal(0, 0.12))
        cm = 60 if term_y is None else term_y * 12
        try:
            r = run_l4(CFG, L4Params("s", rate * (1 - haircut), 0.0, 0.90, 0.95,
                                     lev, kd, min(60, cm), 500, bs, B200, "s", cm))
            npvs.append(r["npv_musd"] * (0.9 + 0.1 * res_shock))
        except Exception:
            continue
    s = summarize(npvs, lab, n)
    print(f"  CE={s.get('ce05')} E={s.get('e_npv')} loss={s.get('loss_rate')} CI=[{s.get('wilson_lo')},{s.get('wilson_hi')}]")
    return s


def allrisk_suite():
    results = []
    results.append(allrisk_L3())
    # Merchant product ladder
    results.append(allrisk_L4M(M1_SPOT, label="L4M_M1_spot_4.25"))
    results.append(allrisk_L4M(M2_ONDEMAND, label="L4M_M2_ondemand_6.90"))
    results.append(allrisk_L4M(PUBLIC_NONSPOT_MEDIAN, label="L4M_mixref_7.80"))
    results.append(allrisk_L4M(M3_SHORT_DED, label="L4M_M3_shortded_9.36"))
    results.append(allrisk_L4M(PUBLIC_NONSPOT_MEDIAN, stack="gpu_only", label="L4M_gpuonly_7.80"))
    results.append(allrisk_L4M(M3_SHORT_DED, stack="gpu_only", label="L4M_gpuonly_9.36"))
    # Contracted / Strategic
    results.append(allrisk_L4C(LIST_DEDICATED, label="L4C_list_9.36"))
    results.append(allrisk_L4C(ILLUSTRATIVE_BULK, label="L4C_illustrative_bulk_7.02"))
    results.append(allrisk_L4C(ILLUSTRATIVE_BULK, decay=-0.06, label="L4C_bulk_step6_7.02"))
    results.append(allrisk_L4S(LIST_DEDICATED, label="L4S_list_9.36"))
    results.append(allrisk_L4S(ILLUSTRATIVE_BULK, label="L4S_illustrative_bulk_7.02"))
    results.append(allrisk_L4S(DOWNSIDE_BULK, label="L4S_downside_5.62"))
    write_csv(OUT / "allrisk_ce_table.csv", results)
    return {r["label"]: r for r in results if r.get("n")}


# ---------------------------------------------------------------------------
# L3 → L4 incremental IRASR table
# ---------------------------------------------------------------------------
def econ_cap(peak, capex, mode):
    """Screening EconCap add-ons (prototype)."""
    add = {
        "L3": (0.10, 0.05, 0.03),
        "M": (0.05, 0.02, 0.03),
        "C": (0.15, 0.08, 0.05),
        "S": (0.25, 0.10, 0.08),
        "gpu": (0.05, 0.02, 0.03),
    }[mode]
    gtee, lc, resv = add
    return peak + gtee * capex + lc * capex + resv * peak


def incremental_irasr(ce_map):
    print("=== L3→L4 Incremental IRASR ===")
    l3 = run_full_pipeline(CFG, "critical_it")
    l3_npv = l3.project_npv / 1e6
    l3_peak = l3.peak_equity / 1e6
    l3_capex = l3.capex_total / 1e6
    l3_ce = ce_map["L3_allrisk"]["ce05"]
    l3_econ = econ_cap(l3_peak, l3_capex, "L3")

    def det(rate, decay, bill, util, lev, kd, ten, cc, bs, cm, stack="gf"):
        if stack == "gpu_only":
            cfg = apply_overrides(CFG, ["power.capex_per_kw=0", "power.dev_capex_musd=0",
                                        "dc.ready_capex_per_kw=0", "dc.hosting_capex_increment_per_kw=4000"])
            capex_it = B200
        else:
            cfg = CFG
            capex_it = B200
        r = run_l4(cfg, L4Params("x", rate, decay, util, bill, lev, kd, ten, cc, bs, capex_it, "x", cm))
        return r

    rows_spec = [
        ("Spot Merchant M1 $4.25", "M", "L4M_M1_spot_4.25",
         lambda: det(M1_SPOT, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, 0)),
        ("Legacy YAML ~$5.63/GPUh", "M", None,
         lambda: det(YAML_LEGACY_GPU, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, 0)),
        ("On-demand M2 $6.90", "M", "L4M_M2_ondemand_6.90",
         lambda: det(M2_ONDEMAND, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, 0)),
        ("Mix-ref nonspot $7.80 full-stack", "M", "L4M_mixref_7.80",
         lambda: det(PUBLIC_NONSPOT_MEDIAN, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, 0)),
        ("GPU-only Merchant $7.80", "gpu", "L4M_gpuonly_7.80",
         lambda: det(PUBLIC_NONSPOT_MEDIAN, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, 0, "gpu_only")),
        ("GPU-only Merchant $9.36", "gpu", "L4M_gpuonly_9.36",
         lambda: det(M3_SHORT_DED, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, 0, "gpu_only")),
        ("Contracted illustrative bulk $7.02", "C", "L4C_illustrative_bulk_7.02",
         lambda: det(ILLUSTRATIVE_BULK, 0.0, 0.95, 0.90, 0.55, 0.070, 60, 150, 0, 60)),
        ("Strategic illustrative bulk $7.02", "S", "L4S_illustrative_bulk_7.02",
         lambda: det(ILLUSTRATIVE_BULK, 0.0, 0.95, 0.90, 0.70, 0.059, 60, 500, 0.375, 60)),
    ]
    rows = []
    for name, mode, ce_key, fn in rows_spec:
        r = fn()
        ce = ce_map[ce_key]["ce05"] if ce_key and ce_key in ce_map else None
        # for legacy yaml use market-like: approximate CE from det if no map
        if name.startswith("Legacy"):
            # interpolate CE between spot and ondemand allrisk already computed
            ce_s = ce_map.get("L4M_M1_spot_4.25", {}).get("ce05")
            ce_o = ce_map.get("L4M_M2_ondemand_6.90", {}).get("ce05")
            if ce_s is not None and ce_o is not None:
                # 5.63 between 4.25 and 6.90
                t = (YAML_LEGACY_GPU - M1_SPOT) / (M2_ONDEMAND - M1_SPOT)
                ce = ce_s + t * (ce_o - ce_s)
            else:
                ce = r["npv_musd"] - 500
        peak = r["peak_equity_musd"]
        capex = r["capex_musd"]
        econ = econ_cap(peak, capex, mode)
        d_ce = None if ce is None else round(ce - l3_ce, 1)
        d_peak = round(peak - l3_peak, 1)
        d_econ = round(econ - l3_econ, 1)
        irasr_peak = None if (ce is None or d_peak == 0) else round(d_ce / d_peak, 3)
        irasr_econ = None if (ce is None or d_econ == 0) else round(d_ce / d_econ, 3)
        print(f"  {name:40s} ΔCE={d_ce} ΔPeak={d_peak} IRASR_peak={irasr_peak} IRASR_econ={irasr_econ}")
        rows.append(dict(
            case=name, rate_note=name, npv=r["npv_musd"], ce=ce, peak=peak, econ_cap=round(econ, 1),
            l3_ce=l3_ce, l3_peak=round(l3_peak, 1), l3_econ=round(l3_econ, 1),
            delta_ce=d_ce, delta_peak=d_peak, delta_econ=d_econ,
            IRASR_peak=irasr_peak, IRASR_econ=irasr_econ,
            npv_vs_l3=round(r["npv_musd"] - l3_npv, 1),
        ))
    write_csv(OUT / "l3_to_l4_incremental_irasr.csv", rows)
    return rows, l3_ce, l3_peak, l3_econ


# ---------------------------------------------------------------------------
# CE break-even rates (bisection on all-risk CE ≈ L3 CE) — use det CE proxy via light MC
# ---------------------------------------------------------------------------
def ce_break_evens(l3_ce):
    print("=== CE / NPV break-evens vs L3 ===")
    # NPV BEs already known-ish; recompute det NPV BE
    def npv_be(decay, bill, util, lev, kd, ten, cc, bs, cm, target):
        lo, hi = 1.0, 25.0
        for _ in range(28):
            mid = (lo + hi) / 2
            r = run_l4(CFG, L4Params("x", mid, decay, util, bill, lev, kd, ten, cc, bs, B200, "x", cm))
            if r["npv_musd"] > target: hi = mid
            else: lo = mid
        return round((lo + hi) / 2, 2)

    l3_npv = run_full_pipeline(CFG, "critical_it").project_npv / 1e6
    rows = [
        dict(metric="NPV_parity", mode="L4-C Fixed", rate=npv_be(0, 0.95, 0.90, 0.55, 0.07, 60, 150, 0, 60, l3_npv)),
        dict(metric="NPV_parity", mode="L4-S Fixed", rate=npv_be(0, 0.95, 0.90, 0.70, 0.059, 60, 500, 0.375, 60, l3_npv)),
        dict(metric="NPV_parity", mode="L4-M -22%/yr", rate=npv_be(-0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, 0, l3_npv)),
        dict(metric="NPV_zero", mode="L4-M -22%/yr", rate=npv_be(-0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, 0, 0)),
    ]
    # CE parity: sample rates and interpolate from allrisk already run where possible
    # Approximate CE BE for C/S using credit-like allrisk at grid
    for mode, fn in [
        ("L4-C Fixed CE≈L3", lambda rt: allrisk_L4C(rt, label=f"beC_{rt}", n=400, seed=3)),
        ("L4-S Fixed CE≈L3", lambda rt: allrisk_L4S(rt, label=f"beS_{rt}", n=400, seed=3)),
    ]:
        grid = []
        for rt in [4.0, 5.0, 6.0, 7.0]:
            s = fn(rt)
            grid.append((rt, s["ce05"]))
            print(f"  grid {mode} r={rt} CE={s['ce05']}")
        # linear interpolate CE = l3_ce
        rate_ce = None
        for (r0, c0), (r1, c1) in zip(grid, grid[1:]):
            if (c0 - l3_ce) * (c1 - l3_ce) <= 0:
                rate_ce = r0 + (l3_ce - c0) * (r1 - r0) / (c1 - c0 + 1e-9)
                break
        if rate_ce is None:
            # extrapolate from ends
            r0, c0 = grid[0]; r1, c1 = grid[-1]
            rate_ce = r0 + (l3_ce - c0) * (r1 - r0) / (c1 - c0 + 1e-9)
        rows.append(dict(metric="CE_parity", mode=mode, rate=round(rate_ce, 2)))
        print(f"  {mode} CE-parity rate ≈ ${rate_ce:.2f}/GPUh")
    write_csv(OUT / "break_evens_npv_ce.csv", rows)
    return rows


def access_ev(ce_map):
    print("=== Contract Access EV (using All-risk CE) ===")
    ce_m = ce_map["L4M_mixref_7.80"]["ce05"]
    ce_c = ce_map["L4C_illustrative_bulk_7.02"]["ce05"]
    ce_s = ce_map["L4S_illustrative_bulk_7.02"]["ce05"]
    ce_l3 = ce_map["L3_allrisk"]["ce05"]
    pursuit_c, pursuit_s = 20.0, 50.0
    types = [
        dict(type="A Uncontracted", pC=0.10, pS=0.02),
        dict(type="B Contracted capability", pC=0.85, pS=0.20),
        dict(type="C Strategic platform", pC=0.95, pS=0.70),
    ]
    rows = []
    for t in types:
        pC, pS = t["pC"], t["pS"]
        # EV of pursuing C path
        ev_c = pC * ce_c + (1 - pC) * ce_m - pursuit_c
        ev_s = pC * (pS * ce_s + (1 - pS) * ce_c) + (1 - pC) * ce_m - pursuit_s
        # stay at L3
        ev_l3 = ce_l3
        rows.append(dict(
            type=t["type"], pC=pC, pS=pS,
            CE_M=ce_m, CE_C=ce_c, CE_S=ce_s, CE_L3=ce_l3,
            EV_pursue_C=round(ev_c, 1), EV_pursue_S=round(ev_s, 1), EV_stay_L3=round(ev_l3, 1),
            best="L3" if ev_l3 >= max(ev_c, ev_s) else ("C" if ev_c >= ev_s else "S"),
            delta_best_vs_L3=round(max(ev_c, ev_s, ev_l3) - ev_l3, 1),
        ))
        print(f"  {t['type']}: EV_C={ev_c:.0f} EV_S={ev_s:.0f} L3={ev_l3:.0f} best={rows[-1]['best']}")
    write_csv(OUT / "access_ev_allrisk_ce.csv", rows)
    return rows


def headline(ce_map, irasr_rows):
    l3 = run_full_pipeline(CFG, "critical_it")
    rows = []
    def add(mode, ce_key, det_npv, peak, note):
        ce = ce_map[ce_key]["ce05"] if ce_key in ce_map else None
        lr = ce_map[ce_key]["loss_rate"] if ce_key in ce_map else None
        rows.append(dict(mode=mode, npv=det_npv, peak=peak, allrisk_ce=ce, loss_rate=lr, note=note))
    add("L3 Critical IT", "L3_allrisk", round(l3.project_npv/1e6,1), round(l3.peak_equity/1e6,1), "structural sweet spot")
    add("L4-M1 Spot $4.25 full-stack", "L4M_M1_spot_4.25",
        run_l4(CFG, L4Params("m", M1_SPOT, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, B200, "m", 0))["npv_musd"],
        run_l4(CFG, L4Params("m", M1_SPOT, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, B200, "m", 0))["peak_equity_musd"],
        "pure merchant spot")
    add("L4-M2 On-demand $6.90 full-stack", "L4M_M2_ondemand_6.90",
        run_l4(CFG, L4Params("m", M2_ONDEMAND, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, B200, "m", 0))["npv_musd"],
        run_l4(CFG, L4Params("m", M2_ONDEMAND, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, B200, "m", 0))["peak_equity_musd"],
        "short-term on-demand")
    add("L4-M mix-ref $7.80 full-stack", "L4M_mixref_7.80", 78.3, 2362.1, "non-spot public mix ref — NOT pure spot")
    add("L4-M GPU-only $7.80", "L4M_gpuonly_7.80",
        run_l4(apply_overrides(CFG, ["power.capex_per_kw=0","power.dev_capex_musd=0","dc.ready_capex_per_kw=0","dc.hosting_capex_increment_per_kw=4000"]),
               L4Params("m", 7.80, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, B200, "m", 0))["npv_musd"],
        run_l4(apply_overrides(CFG, ["power.capex_per_kw=0","power.dev_capex_musd=0","dc.ready_capex_per_kw=0","dc.hosting_capex_increment_per_kw=4000"]),
               L4Params("m", 7.80, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, B200, "m", 0))["peak_equity_musd"],
        "sunk power+DC — different decision")
    add("L4-C Fixed illustrative bulk $7.02", "L4C_illustrative_bulk_7.02", 2884.9, 1404.1, "illustrative bulk NOT calibrated base")
    add("L4-C Step-6%/yr illustrative bulk", "L4C_bulk_step6_7.02", 2196.9, 1404.1, "mild step-down")
    add("L4-S Fixed illustrative bulk $7.02", "L4S_illustrative_bulk_7.02", 3277.6, 499.9, "illustrative bulk + residual BS")
    add("L4-S list upper $9.36", "L4S_list_9.36", 5284.6, 438.2, "list upper bound")
    write_csv(OUT / "headline_allrisk.csv", rows)
    print("=== Headline ===")
    for r in rows:
        print(f"  {r['mode'][:42]:42s} NPV={r['npv']!s:>8} CE={r['allrisk_ce']!s:>8} loss={r['loss_rate']}")
    return rows


def main():
    ce_map = allrisk_suite()
    irasr_rows, l3_ce, l3_peak, l3_econ = incremental_irasr(ce_map)
    be_rows = ce_break_evens(l3_ce)
    acc = access_ev(ce_map)
    head = headline(ce_map, irasr_rows)

    summary = dict(
        n_allrisk=N_ALL,
        l3_ce=ce_map["L3_allrisk"]["ce05"],
        m1_ce=ce_map["L4M_M1_spot_4.25"]["ce05"],
        m2_ce=ce_map["L4M_M2_ondemand_6.90"]["ce05"],
        m_mix_ce=ce_map["L4M_mixref_7.80"]["ce05"],
        m_gpuonly_ce=ce_map["L4M_gpuonly_7.80"]["ce05"],
        c_bulk_ce=ce_map["L4C_illustrative_bulk_7.02"]["ce05"],
        s_bulk_ce=ce_map["L4S_illustrative_bulk_7.02"]["ce05"],
        naming=dict(
            bulk="illustrative_bulk_case_not_calibrated",
            merchant_7_8="nonspot_public_mix_reference_not_pure_spot",
            golden_yaml="legacy_3.0_IT_kWh_approx_5.63_GPUh",
        ),
        note="All-risk CE apple-to-apple; GPU-only in main path; IRASR L3→L4 table",
    )
    with open(OUT / "v5_4_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("\nSUMMARY keys CE:", {k: summary[k] for k in summary if k.endswith("_ce") or k=="l3_ce"})
    print("Outputs →", OUT)


if __name__ == "__main__":
    main()
