#!/usr/bin/env python3
"""
v6.1 — review must-dos on the frozen v6.0 structure.

  1. All-risk Headline N=10,000 (fixed seed / param version / commit)
  2. EconCap Low / Base / High (risk-equivalent guarantee; no LC+reserve double-count in Base)
  3. Matched Counterparty: same shock stream as Headline; only PD changes
  4. C4 tech-refresh formal rerun on the frequency-fixed path
  5. Cheap extras: transfer-rent CE-parity curve; access p* with delay/option cost

Does not expand the framework. Does not invent a realized bulk rate.

    python research_v6_1.py
"""
from __future__ import annotations

import csv
import json
import math
import subprocess
import time
from pathlib import Path

import numpy as np

from aidc_optimizer.cli import load_config, apply_overrides
from aidc_optimizer.risk import run_full_pipeline
from research_l4 import L4Params, run_l4, GPU_PER_IT_KW
from research_v5_4 import summarize, wilson, write_csv
from research_v5_5 import (
    cfg_gpu_only, TRANSFER_OPEX_KW_YR, L3_RENT_KW_MO,
    bootstrap_ci, ce_from_samples,
)
from research_v5 import CONTRACTS, run_contract

OUT = Path("research_outputs/v6_1")
OUT.mkdir(parents=True, exist_ok=True)
CFG = load_config("configs/alberta.yaml")
B200 = 60000 * GPU_PER_IT_KW
SEED = 42
N_HEAD = 10_000
N_GRID = 300
PARAM_VERSION = "v6.1-2026-08-15"
ILLUSTRATIVE_BULK = 7.02
PUBLIC_NONSPOT_MEDIAN = 7.80
LIST_DEDICATED = 9.36


def _commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True
        ).strip()
    except Exception:
        return "unknown"


COMMIT = _commit()


def meta():
    return dict(
        parameter_version=PARAM_VERSION,
        commit=COMMIT,
        seed=SEED,
        n_headline=N_HEAD,
        decay_convention="(1+g)**(k/12)",
        ci_name="Simulation Bootstrap Interval, conditional on model assumptions",
    )


# ---------------------------------------------------------------------------
# Shock factories — generate once; apply PD / mode afterwards (Matched)
# ---------------------------------------------------------------------------
def shocks_L3(n, seed):
    rng = np.random.default_rng(seed)
    return dict(
        u_default=rng.random(n),
        u_vacancy=rng.random(n),
        rent_z=rng.normal(-0.5 * 0.12 ** 2, 0.12, n),
        vac_u=rng.uniform(0.85, 0.95, n),
        capex_z=rng.normal(-0.5 * 0.10 ** 2, 0.10, n),
        u_refi=rng.random(n),
    )


def npvs_L3(shocks, pd):
    n = len(shocks["u_default"])
    npvs = []
    for i in range(n):
        default = shocks["u_default"][i] < pd
        rent_m = 0.0 if default else math.exp(shocks["rent_z"][i])
        if shocks["u_vacancy"][i] < pd * 2:
            rent_m *= float(shocks["vac_u"][i])
        capex_m = math.exp(shocks["capex_z"][i])
        if shocks["u_refi"][i] < 0.08:
            rent_m *= 0.92
        try:
            cfg = apply_overrides(CFG, [
                f"dc.ready_rent_kw_mo={CFG['dc']['ready_rent_kw_mo'] * rent_m}",
                f"dc.ready_capex_per_kw={CFG['dc']['ready_capex_per_kw'] * capex_m}",
            ])
            npvs.append(run_full_pipeline(cfg, "critical_it").project_npv / 1e6)
        except Exception:
            continue
        if (i + 1) % 2500 == 0:
            print(f"    L3 pd={pd} {i+1}/{n}")
    return npvs


def shocks_M(n, seed):
    rng = np.random.default_rng(seed)
    return dict(
        rm=np.exp(rng.normal(-0.5 * 0.25 ** 2, 0.25, n)),
        um=np.clip(1 + rng.normal(0, 0.12, n), 0.35, 0.98),
        dec_z=rng.normal(0, 0.04, n),
        u_refi=rng.random(n),
        u_collapse=rng.random(n),
    )


def npvs_M(shocks, rate, cfg0, capex_it, decay=-0.22):
    n = len(shocks["rm"])
    npvs = []
    for i in range(n):
        rm = float(shocks["rm"][i])
        um = float(shocks["um"][i])
        dec = max(-0.45, min(0.05, decay + float(shocks["dec_z"][i])))
        lev, kd = (0.25, 0.12) if shocks["u_refi"][i] < 0.12 else (0.35, 0.095)
        if rm < 0.75 and shocks["u_collapse"][i] < 0.3:
            dec = min(dec, -0.30)
        try:
            r = run_l4(cfg0, L4Params(
                "m", rate * rm, dec, min(0.95, 0.75 * um), min(0.95, 0.75 * um),
                lev, kd, 48, 0, 0.0, capex_it, "m", 0,
            ))
            npvs.append(r["npv_musd"])
        except Exception:
            continue
        if (i + 1) % 2500 == 0:
            print(f"    M rate={rate} {i+1}/{n}")
    return npvs


def shocks_C(n, seed):
    rng = np.random.default_rng(seed)
    return dict(
        u_default=rng.random(n),
        term_y=rng.integers(2, 5, n),
        u_hair=rng.random(n),
        hair1=rng.uniform(0.05, 0.30, n),
        u_reset=rng.random(n),
        hair2=rng.uniform(0.10, 0.30, n),
        res_shock=np.maximum(0.5, 1 + rng.normal(0, 0.15, n)),
        u_refi=rng.random(n),
    )


def npvs_C(shocks, rate, pd, decay=0.0, cm_base=60, cc=150, lev_hi=(0.55, 0.070)):
    n = len(shocks["u_default"])
    npvs = []
    for i in range(n):
        default = shocks["u_default"][i] < pd
        term_y = int(shocks["term_y"][i]) if default else None
        haircut = 0.0
        if shocks["u_hair"][i] < max(0.12, pd * 4):
            haircut = float(shocks["hair1"][i])
        if shocks["u_reset"][i] < 0.12:
            haircut = max(haircut, float(shocks["hair2"][i]))
        lev, kd = (0.45, 0.085) if shocks["u_refi"][i] < 0.12 else lev_hi
        cm = cm_base if term_y is None else min(cm_base, term_y * 12)
        try:
            r = run_l4(CFG, L4Params(
                "c", rate * (1 - haircut), decay, 0.90, 0.95,
                lev, kd, min(cm_base, cm), cc, 0.0, B200, "c", cm,
            ))
            npvs.append(r["npv_musd"] * (0.85 + 0.15 * float(shocks["res_shock"][i])))
        except Exception:
            continue
        if (i + 1) % 2500 == 0:
            print(f"    C rate={rate} pd={pd} cm={cm_base} {i+1}/{n}")
    return npvs


def shocks_S(n, seed):
    rng = np.random.default_rng(seed)
    return dict(
        u_default=rng.random(n),
        term_y=rng.integers(2, 5, n),
        u_hair=rng.random(n),
        hair1=rng.uniform(0.05, 0.25, n),
        u_reset=rng.random(n),
        hair2=rng.uniform(0.10, 0.30, n),
        u_bs=rng.random(n),
        u_refi=rng.random(n),
        res_shock=np.maximum(0.5, 1 + rng.normal(0, 0.12, n)),
    )


def npvs_S(shocks, rate):
    n = len(shocks["u_default"])
    npvs = []
    for i in range(n):
        default = shocks["u_default"][i] < 0.03
        term_y = int(shocks["term_y"][i]) if default else None
        haircut = 0.0 if shocks["u_hair"][i] > 0.15 else float(shocks["hair1"][i])
        if shocks["u_reset"][i] < 0.10:
            haircut = max(haircut, float(shocks["hair2"][i]))
        bs = 0.375 if shocks["u_bs"][i] > 0.08 else 0.0
        lev, kd = (0.55, 0.095) if shocks["u_refi"][i] < 0.10 else (0.70, 0.059)
        cm = 60 if term_y is None else term_y * 12
        try:
            r = run_l4(CFG, L4Params(
                "s", rate * (1 - haircut), 0.0, 0.90, 0.95,
                lev, kd, min(60, cm), 500, bs, B200, "s", cm,
            ))
            npvs.append(r["npv_musd"] * (0.9 + 0.1 * float(shocks["res_shock"][i])))
        except Exception:
            continue
        if (i + 1) % 2500 == 0:
            print(f"    S rate={rate} {i+1}/{n}")
    return npvs


def pack(label, npvs, n_target=N_HEAD):
    s = summarize(npvs, label, n_target)
    ci = bootstrap_ci(npvs)
    rec = {**s, **ci, **meta()}
    print(f"  {label:28s} CE={s.get('ce05')}  "
          f"SBI[{ci['CE_lo']},{ci['CE_hi']}]  "
          f"E={s.get('e_npv')}  loss={s.get('loss_rate')}")
    return rec, npvs


# ---------------------------------------------------------------------------
# EconCap Low / Base / High
# ---------------------------------------------------------------------------
# Base add-ons remain screening prototypes (gtee, LC, reserve as fractions).
# Guarantee is converted to a risk-equivalent (EL haircut), not face value.
# Liquidity: Low = reserve only; Base = max(LC, reserve); High = LC + reserve.
ECON_ADD = {
    "L3": (0.10, 0.05, 0.03),
    "M": (0.05, 0.02, 0.03),
    "C": (0.15, 0.08, 0.05),
    "S": (0.25, 0.10, 0.08),
    "gpu": (0.05, 0.02, 0.03),
}
EL_HAIRCUT = {"low": 0.15, "base": 0.30, "high": 0.50}


def econ_cap_band(peak, capex, mode, band="base"):
    gtee, lc, resv = ECON_ADD[mode]
    gtee_eq = gtee * capex * EL_HAIRCUT[band]
    lc_amt = lc * capex
    resv_amt = resv * peak
    if band == "low":
        liq = resv_amt
    elif band == "base":
        liq = max(lc_amt, resv_amt)
    else:
        liq = lc_amt + resv_amt
    return peak + gtee_eq + liq


def irasr_table(ce_l3, peak_l3, specs):
    """specs: list of (name, mode, ce, det_result)."""
    rows = []
    l3_capex = run_full_pipeline(CFG, "critical_it").capex_total / 1e6
    for band in ("low", "base", "high"):
        l3_e = econ_cap_band(peak_l3, l3_capex, "L3", band)
        for name, mode, ce, r in specs:
            peak = r["peak_equity_musd"]
            econ = econ_cap_band(peak, r["capex_musd"], mode, band)
            d_ce = round(ce - ce_l3, 1)
            d_econ = round(econ - l3_e, 1)
            d_peak = round(peak - peak_l3, 1)
            ir_e = None if abs(d_econ) < 1e-6 else round(d_ce / d_econ, 3)
            ir_p = None if abs(d_peak) < 1e-6 else round(d_ce / d_peak, 3)
            rows.append(dict(
                band=band, case=name, mode=mode, ce=ce, peak=round(peak, 1),
                econ_cap=round(econ, 1), delta_ce=d_ce, delta_econ=d_econ,
                delta_peak=d_peak, IRASR_econ=ir_e, IRASR_peak=ir_p,
                note="screening EconCap; IRASR_econ theoretically preferred",
            ))
            if band == "base":
                print(f"  [{band}] {name:42s} ΔCE={d_ce:8.1f}  "
                      f"IRASR_econ={ir_e}  IRASR_peak={ir_p}")
    write_csv(OUT / "irasr_econ_bands.csv", rows)
    return rows


# ---------------------------------------------------------------------------
# C4 formal
# ---------------------------------------------------------------------------
def c4_block():
    print("=== C4 tech-refresh formal (freq-fixed) ===")
    c4 = next(c for c in CONTRACTS if c["id"].startswith("C4"))
    rows = []
    samples = {}
    for rate, cc_mode, cc_fixed in (
        (LIST_DEDICATED, "tcv15", None),
        (ILLUSTRATIVE_BULK, "tcv15", None),
        (LIST_DEDICATED, "cc150", 150.0),
        (ILLUSTRATIVE_BULK, "cc150", 150.0),
    ):
        det = run_contract(CFG, c4, rate_gpuh=rate, capex_it=B200)
        if cc_fixed is not None:
            from research_l4 import L4Params as _P
            det = run_l4(CFG, _P(
                "c", rate, c4["decay"], c4["util"], c4["billable"],
                0.55, 0.070, c4["tenor"], cc_fixed, 0.0, B200, "C4", c4["tenor"],
            ))
            det["customer_capital_musd"] = cc_fixed
        cc = det["customer_capital_musd"]
        print(f"  DET C4 r={rate} {cc_mode} NPV={det['npv_musd']} "
              f"Peak={det['peak_equity_musd']} cc={cc}")
        sh = shocks_C(N_HEAD, SEED)
        npvs = npvs_C(
            sh, rate, pd=0.04, decay=c4["decay"],
            cm_base=c4["tenor"], cc=cc,
        )
        rec, _ = pack(f"C4_{cc_mode}_r{rate}", npvs)
        rec.update(dict(
            rate=rate, cc_mode=cc_mode, det_npv=det["npv_musd"],
            det_peak=det["peak_equity_musd"], det_irr=det.get("project_irr"),
            customer_capital=cc, tenor=c4["tenor"], decay=c4["decay"],
        ))
        rows.append(rec)
        samples[f"{cc_mode}_{rate}"] = npvs
        np.save(OUT / f"samples_C4_{cc_mode}_{rate}.npy", np.asarray(npvs))
    write_csv(OUT / "c4_formal.csv", [{k: v for k, v in r.items()} for r in rows])
    return rows, samples


# ---------------------------------------------------------------------------
# Transfer-rent CE parity curve
# ---------------------------------------------------------------------------
def transfer_curve(l3_ce):
    print("=== Transfer-rent CE-parity curve ===")
    rents = [125, 150, 185, 225, 250]
    rate_grid = [7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0]
    rows = []
    for rent in rents:
        opex = rent * 12
        cfg_e = apply_overrides(CFG, [
            "power.capex_per_kw=0", "power.dev_capex_musd=0",
            "dc.ready_capex_per_kw=0", "dc.hosting_capex_increment_per_kw=4000",
            f"gpu.extra_opex_kw_yr={CFG['gpu'].get('extra_opex_kw_yr', 15) + opex}",
        ])
        grid = []
        for rt in rate_grid:
            sh = shocks_M(N_GRID, 11)
            npvs = npvs_M(sh, rt, cfg_e, B200)
            ce = summarize(npvs, f"go_{rent}_{rt}", N_GRID)["ce05"]
            grid.append((rt, ce))
            print(f"  rent={rent} r={rt} CE={ce}")
        rate_ce = None
        for (r0, c0), (r1, c1) in zip(grid, grid[1:]):
            if (c0 - l3_ce) * (c1 - l3_ce) <= 0:
                rate_ce = r0 + (l3_ce - c0) * (r1 - r0) / (c1 - c0 + 1e-9)
                break
        if rate_ce is None:
            r0, c0 = grid[0]
            r1, c1 = grid[-1]
            rate_ce = r0 + (l3_ce - c0) * (r1 - r0) / (c1 - c0 + 1e-9)
        rows.append(dict(
            l3_transfer_rent_kw_mo=rent,
            CE_parity_gpuh=round(rate_ce, 2),
            grid=";".join(f"{r}:{c}" for r, c in grid),
            l3_ce=l3_ce,
        ))
        print(f"  rent ${rent}/kW-mo → economic CE-parity ~${rate_ce:.2f}/GPU-h")
    write_csv(OUT / "transfer_rent_parity_curve.csv", rows)
    return rows


def access_extended(ce_l3, ce_c, ce_s):
    """p* with cash + delay/option cost bands."""
    print("=== Access p* with delay / option cost ===")
    # cash, months, delay+option add-on ($M)
    cases = [
        (20, 6, 15),
        (50, 12, 40),
        (100, 18, 80),
        (200, 24, 160),
    ]
    rows = []
    for cash, months, extra in cases:
        total = cash + extra
        p_c = total / max(1e-6, ce_c - ce_l3)
        p_s = total / max(1e-6, ce_s - ce_l3)
        rows.append(dict(
            cash_musd=cash, delay_months=months, delay_option_musd=extra,
            pursuit_total_musd=total,
            pC_star=round(min(1.0, max(0.0, p_c)), 4),
            pS_star=round(min(1.0, max(0.0, p_s)), 4),
            CE_C=ce_c, CE_S=ce_s, CE_L3=ce_l3,
            formula="p* = (Cash+Delay+OptionLost) / (CE_contract - CE_L3)",
        ))
        print(f"  ${cash}M + {months}mo/${extra}M → pC*={p_c:.3f} pS*={p_s:.3f}")
    write_csv(OUT / "access_pstar_delay.csv", rows)
    return rows


def lambda_table(sample_map):
    rows = []
    for name, npvs in sample_map.items():
        rec = {"mode": name}
        for lam in (0.0, 0.25, 0.5, 0.75, 1.0):
            rec[f"CE_l{str(lam).replace('.','')}"] = round(ce_from_samples(npvs, lam), 1)
        rows.append(rec)
    write_csv(OUT / "lambda_sensitivity_n10000.csv", rows)
    return rows


def main():
    t0 = time.time()
    print(f"=== v6.1 Headline All-risk N={N_HEAD} seed={SEED} commit={COMMIT} ===")

    # --- Headline samples (one shock stream per family) ---
    sh_l3 = shocks_L3(N_HEAD, SEED)
    l3_npvs = npvs_L3(sh_l3, pd=0.02)
    l3_rec, _ = pack("L3_headline", l3_npvs)
    np.save(OUT / "samples_L3.npy", np.asarray(l3_npvs))

    sh_m = shocks_M(N_HEAD, SEED)
    m_npvs = npvs_M(sh_m, PUBLIC_NONSPOT_MEDIAN, CFG, B200)
    m_rec, _ = pack("M_fullstack_7.80", m_npvs)
    np.save(OUT / "samples_M.npy", np.asarray(m_npvs))

    cfg_acc = cfg_gpu_only(False)
    cfg_eon = cfg_gpu_only(True)
    go_acc = npvs_M(sh_m, PUBLIC_NONSPOT_MEDIAN, cfg_acc, B200)  # same market shocks
    go_eon = npvs_M(sh_m, PUBLIC_NONSPOT_MEDIAN, cfg_eon, B200)
    goa_rec, _ = pack("GO_accounting_7.80", go_acc)
    goe_rec, _ = pack("GO_economic_7.80", go_eon)
    np.save(OUT / "samples_GO_acc.npy", np.asarray(go_acc))
    np.save(OUT / "samples_GO_econ.npy", np.asarray(go_eon))

    sh_c = shocks_C(N_HEAD, SEED)
    c_npvs = npvs_C(sh_c, ILLUSTRATIVE_BULK, pd=0.04)
    c_rec, _ = pack("C_bulk_7.02", c_npvs)
    np.save(OUT / "samples_C.npy", np.asarray(c_npvs))

    sh_s = shocks_S(N_HEAD, SEED)
    s_npvs = npvs_S(sh_s, ILLUSTRATIVE_BULK)
    s_rec, _ = pack("S_bulk_7.02", s_npvs)
    np.save(OUT / "samples_S.npy", np.asarray(s_npvs))

    headline = [l3_rec, m_rec, goa_rec, goe_rec, c_rec, s_rec]
    write_csv(OUT / "allrisk_n10000.csv", headline)

    # --- Matched: same L3 / C shocks, only PD ---
    print("=== Matched Counterparty (same shocks, PD only) ===")
    l3_ig = npvs_L3(sh_l3, pd=0.008)
    c_ig = npvs_C(sh_c, ILLUSTRATIVE_BULK, pd=0.008)
    l3g_rec, _ = pack("L3_generic_pd0.02", l3_npvs)  # identical to headline
    l3i_rec, _ = pack("L3_IG_pd0.008", l3_ig)
    cg_rec, _ = pack("C_generic_pd0.04", c_npvs)
    ci_rec, _ = pack("C_IG_pd0.008", c_ig)
    layer = ci_rec["ce05"] - l3i_rec["ce05"]
    credit_c = ci_rec["ce05"] - cg_rec["ce05"]
    credit_l3 = l3i_rec["ce05"] - l3g_rec["ce05"]
    decomp = dict(
        CE_L3_generic=l3g_rec["ce05"],
        CE_L3_IG=l3i_rec["ce05"],
        CE_C_generic=cg_rec["ce05"],
        CE_C_IG=ci_rec["ce05"],
        layer_effect_IG=round(layer, 1),
        credit_effect_C=round(credit_c, 1),
        credit_effect_L3=round(credit_l3, 1),
        headline_L3_equals_generic=abs(l3_rec["ce05"] - l3g_rec["ce05"]) < 0.05,
        note="same seed/shocks as Headline; only PD changes",
    )
    write_csv(OUT / "matched_counterparty.csv", [l3g_rec, l3i_rec, cg_rec, ci_rec])
    write_csv(OUT / "layer_vs_counterparty.csv", [decomp])
    print("  Layer effect (IG matched):", decomp["layer_effect_IG"])

    # --- IRASR three-band ---
    print("=== IRASR_econ Low/Base/High ===")
    peak_l3 = run_full_pipeline(CFG, "critical_it").peak_equity / 1e6
    det_m = run_l4(CFG, L4Params("m", 7.8, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, B200, "m", 0))
    det_goa = run_l4(cfg_acc, L4Params("m", 7.8, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, B200, "m", 0))
    det_goe = run_l4(cfg_eon, L4Params("m", 7.8, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, B200, "m", 0))
    det_c = run_l4(CFG, L4Params("c", ILLUSTRATIVE_BULK, 0, 0.90, 0.95, 0.55, 0.07, 60, 150, 0, B200, "c", 60))
    det_s = run_l4(CFG, L4Params("s", ILLUSTRATIVE_BULK, 0, 0.90, 0.95, 0.70, 0.059, 60, 500, 0.375, B200, "s", 60))
    irasr_table(l3_rec["ce05"], peak_l3, [
        ("Full-stack mix-ref $7.80", "M", m_rec["ce05"], det_m),
        ("GPU-only accounting $7.80", "gpu", goa_rec["ce05"], det_goa),
        ("GPU-only economic $7.80", "gpu", goe_rec["ce05"], det_goe),
        ("Contracted illustrative bulk $7.02", "C", c_rec["ce05"], det_c),
        ("Strategic illustrative bulk $7.02", "S", s_rec["ce05"], det_s),
    ])

    sample_map = {
        "L3": l3_npvs,
        "M_fullstack_7.80": m_npvs,
        "GO_accounting": go_acc,
        "GO_economic": go_eon,
        "C_bulk": c_npvs,
        "S_bulk": s_npvs,
    }
    lambda_table(sample_map)

    c4_rows, _ = c4_block()
    transfer_curve(l3_rec["ce05"])
    access_extended(l3_rec["ce05"], c_rec["ce05"], s_rec["ce05"])

    summary = {
        **meta(),
        "runtime_sec": round(time.time() - t0, 1),
        "CE_L3": l3_rec["ce05"],
        "CE_L3_SBI": [l3_rec["CE_lo"], l3_rec["CE_hi"]],
        "CE_M": m_rec["ce05"],
        "CE_M_SBI": [m_rec["CE_lo"], m_rec["CE_hi"]],
        "CE_GO_acc": goa_rec["ce05"],
        "CE_GO_econ": goe_rec["ce05"],
        "CE_C": c_rec["ce05"],
        "CE_C_SBI": [c_rec["CE_lo"], c_rec["CE_hi"]],
        "CE_S": s_rec["ce05"],
        "CE_S_SBI": [s_rec["CE_lo"], s_rec["CE_hi"]],
        "matched": decomp,
        "C4": [
            {k: r.get(k) for k in (
                "label", "rate", "cc_mode", "det_npv", "ce05", "det_peak", "customer_capital"
            )}
            for r in c4_rows
        ],
        "realized_rate_status": "NOT CALIBRATED — $7.02 remains illustrative (9.36x0.75)",
    }
    (OUT / "v6_1_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\nSUMMARY", json.dumps(summary, indent=2))
    print(f"Done in {summary['runtime_sec']}s → {OUT}")



def _slice_shocks(sh, a, b):
    return {k: np.asarray(v)[a:b] for k, v in sh.items()}


def _append_samples(path: Path, new_vals):
    arr = np.asarray(new_vals, dtype=float)
    if path.exists() and path.stat().st_size > 0:
        old = np.load(path)
        arr = np.concatenate([old, arr])
    np.save(path, arr)
    return arr


def _resume_apply(sample_path: Path, shocks, apply_fn, max_n, budget):
    """Apply apply_fn to remaining shocks, at most `budget` paths this call."""
    done = 0
    if sample_path.exists() and sample_path.stat().st_size > 0:
        done = int(np.load(sample_path).shape[0])
    if done >= max_n:
        return np.load(sample_path), True
    end = min(max_n, done + budget)
    sl = _slice_shocks(shocks, done, end)
    chunk = apply_fn(sl)
    arr = _append_samples(sample_path, chunk)
    complete = len(arr) >= max_n
    print(f"    progress {sample_path.name}: {len(arr)}/{max_n} complete={complete}")
    return arr, complete


# ~28s L3 / ~17s M at measured 3.1 / 1.7 ms
BUDGET = {"l3": 8500, "m": 10000, "go": 5000, "c": 10000, "s": 10000,
          "matched": 4000, "c4": 10000}


def run_stage(stage: str):
    """Incremental runner so each bash call finishes inside the 45s tool window."""
    t0 = time.time()
    print(f"=== stage={stage} N={N_HEAD} seed={SEED} commit={COMMIT} ===")
    complete = True
    if stage == "l3":
        sh_path = OUT / "shocks_L3.npz"
        if sh_path.exists():
            sh = dict(np.load(sh_path))
        else:
            sh = shocks_L3(N_HEAD, SEED)
            np.savez(sh_path, **sh)
        arr, complete = _resume_apply(
            OUT / "samples_L3.npy", sh,
            lambda sl: npvs_L3(sl, pd=0.02), N_HEAD, BUDGET["l3"])
        if complete:
            rec, _ = pack("L3_headline", arr.tolist())
            (OUT / "rec_L3.json").write_text(json.dumps(rec), encoding="utf-8")
    elif stage == "m":
        sh_path = OUT / "shocks_M.npz"
        if sh_path.exists():
            sh = dict(np.load(sh_path))
        else:
            sh = shocks_M(N_HEAD, SEED)
            np.savez(sh_path, **sh)
        arr, complete = _resume_apply(
            OUT / "samples_M.npy", sh,
            lambda sl: npvs_M(sl, PUBLIC_NONSPOT_MEDIAN, CFG, B200),
            N_HEAD, BUDGET["m"])
        if complete:
            rec, _ = pack("M_fullstack_7.80", arr.tolist())
            (OUT / "rec_M.json").write_text(json.dumps(rec), encoding="utf-8")
    elif stage == "go":
        sh = dict(np.load(OUT / "shocks_M.npz"))
        cfg_acc = cfg_gpu_only(False)
        cfg_eon = cfg_gpu_only(True)
        a_arr, c1 = _resume_apply(
            OUT / "samples_GO_acc.npy", sh,
            lambda sl: npvs_M(sl, PUBLIC_NONSPOT_MEDIAN, cfg_acc, B200),
            N_HEAD, BUDGET["go"])
        e_arr, c2 = _resume_apply(
            OUT / "samples_GO_econ.npy", sh,
            lambda sl: npvs_M(sl, PUBLIC_NONSPOT_MEDIAN, cfg_eon, B200),
            N_HEAD, BUDGET["go"])
        complete = c1 and c2
        if complete:
            a, _ = pack("GO_accounting_7.80", a_arr.tolist())
            e, _ = pack("GO_economic_7.80", e_arr.tolist())
            (OUT / "rec_GO_acc.json").write_text(json.dumps(a), encoding="utf-8")
            (OUT / "rec_GO_econ.json").write_text(json.dumps(e), encoding="utf-8")
    elif stage == "c":
        sh_path = OUT / "shocks_C.npz"
        if sh_path.exists():
            sh = dict(np.load(sh_path))
        else:
            sh = shocks_C(N_HEAD, SEED)
            np.savez(sh_path, **sh)
        arr, complete = _resume_apply(
            OUT / "samples_C.npy", sh,
            lambda sl: npvs_C(sl, ILLUSTRATIVE_BULK, pd=0.04),
            N_HEAD, BUDGET["c"])
        if complete:
            rec, _ = pack("C_bulk_7.02", arr.tolist())
            (OUT / "rec_C.json").write_text(json.dumps(rec), encoding="utf-8")
    elif stage == "s":
        sh_path = OUT / "shocks_S.npz"
        if sh_path.exists():
            sh = dict(np.load(sh_path))
        else:
            sh = shocks_S(N_HEAD, SEED)
            np.savez(sh_path, **sh)
        arr, complete = _resume_apply(
            OUT / "samples_S.npy", sh,
            lambda sl: npvs_S(sl, ILLUSTRATIVE_BULK),
            N_HEAD, BUDGET["s"])
        if complete:
            rec, _ = pack("S_bulk_7.02", arr.tolist())
            (OUT / "rec_S.json").write_text(json.dumps(rec), encoding="utf-8")
    elif stage == "matched":
        sh_l3 = dict(np.load(OUT / "shocks_L3.npz"))
        sh_c = dict(np.load(OUT / "shocks_C.npz"))
        a, c1 = _resume_apply(
            OUT / "samples_L3_IG.npy", sh_l3,
            lambda sl: npvs_L3(sl, pd=0.008), N_HEAD, BUDGET["matched"])
        b, c2 = _resume_apply(
            OUT / "samples_C_IG.npy", sh_c,
            lambda sl: npvs_C(sl, ILLUSTRATIVE_BULK, pd=0.008),
            N_HEAD, BUDGET["matched"])
        complete = c1 and c2
        if complete:
            li, _ = pack("L3_IG_pd0.008", a.tolist())
            ci, _ = pack("C_IG_pd0.008", b.tolist())
            (OUT / "rec_L3_IG.json").write_text(json.dumps(li), encoding="utf-8")
            (OUT / "rec_C_IG.json").write_text(json.dumps(ci), encoding="utf-8")
    elif stage == "c4a":
        complete = c4_one("tcv15", LIST_DEDICATED, None)
    elif stage == "c4b":
        complete = c4_one("tcv15", ILLUSTRATIVE_BULK, None)
    elif stage == "c4c":
        complete = c4_one("cc150", LIST_DEDICATED, 150.0)
    elif stage == "c4d":
        complete = c4_one("cc150", ILLUSTRATIVE_BULK, 150.0)
    elif stage == "post":
        pack_post()
    else:
        raise SystemExit(f"unknown stage {stage}")
    flag = "COMPLETE" if complete else "PARTIAL — re-run same --stage"
    print(f"stage {stage} {flag} in {time.time()-t0:.1f}s")
    if not complete:
        raise SystemExit(2)


def c4_one(cc_mode, rate, cc_fixed):
    c4 = next(c for c in CONTRACTS if c["id"].startswith("C4"))
    det = run_contract(CFG, c4, rate_gpuh=rate, capex_it=B200)
    if cc_fixed is not None:
        det = run_l4(CFG, L4Params(
            "c", rate, c4["decay"], c4["util"], c4["billable"],
            0.55, 0.070, c4["tenor"], cc_fixed, 0.0, B200, "C4", c4["tenor"],
        ))
        det["customer_capital_musd"] = cc_fixed
    cc = det["customer_capital_musd"]
    print(f"  DET C4 r={rate} {cc_mode} NPV={det['npv_musd']} Peak={det['peak_equity_musd']} cc={cc}")
    sh_path = OUT / "shocks_C.npz"
    if sh_path.exists():
        sh = dict(np.load(sh_path))
    else:
        sh = shocks_C(N_HEAD, SEED)
        np.savez(sh_path, **sh)
    sample_path = OUT / f"samples_C4_{cc_mode}_{rate}.npy"
    arr, complete = _resume_apply(
        sample_path, sh,
        lambda sl: npvs_C(sl, rate, pd=0.04, decay=c4["decay"],
                          cm_base=c4["tenor"], cc=cc),
        N_HEAD, BUDGET["c4"])
    if complete:
        rec, _ = pack(f"C4_{cc_mode}_r{rate}", arr.tolist())
        rec.update(dict(
            rate=rate, cc_mode=cc_mode, det_npv=float(det["npv_musd"]),
            det_peak=float(det["peak_equity_musd"]),
            det_irr=None if det.get("project_irr") is None else float(det["project_irr"]),
            customer_capital=float(cc), tenor=c4["tenor"], decay=c4["decay"],
        ))
        (OUT / f"rec_C4_{cc_mode}_{rate}.json").write_text(json.dumps(rec), encoding="utf-8")
    return complete


def _load_rec(name):
    return json.loads((OUT / f"rec_{name}.json").read_text(encoding="utf-8"))


def pack_post():
    l3 = _load_rec("L3"); m = _load_rec("M")
    goa = _load_rec("GO_acc"); goe = _load_rec("GO_econ")
    c = _load_rec("C"); s = _load_rec("S")
    l3i = _load_rec("L3_IG"); ci = _load_rec("C_IG")
    l3_npvs = np.load(OUT / "samples_L3.npy")
    m_npvs = np.load(OUT / "samples_M.npy")
    go_acc = np.load(OUT / "samples_GO_acc.npy")
    go_eon = np.load(OUT / "samples_GO_econ.npy")
    c_npvs = np.load(OUT / "samples_C.npy")
    s_npvs = np.load(OUT / "samples_S.npy")
    write_csv(OUT / "allrisk_n10000.csv", [l3, m, goa, goe, c, s])
    layer = ci["ce05"] - l3i["ce05"]
    decomp = dict(
        CE_L3_generic=l3["ce05"], CE_L3_IG=l3i["ce05"],
        CE_C_generic=c["ce05"], CE_C_IG=ci["ce05"],
        layer_effect_IG=round(layer, 1),
        credit_effect_C=round(ci["ce05"] - c["ce05"], 1),
        credit_effect_L3=round(l3i["ce05"] - l3["ce05"], 1),
        headline_L3_equals_generic=True,
        note="same seed/shocks as Headline; only PD changes",
    )
    write_csv(OUT / "matched_counterparty.csv", [l3, l3i, c, ci])
    write_csv(OUT / "layer_vs_counterparty.csv", [decomp])
    print("Layer effect (IG matched):", decomp["layer_effect_IG"])
    peak_l3 = run_full_pipeline(CFG, "critical_it").peak_equity / 1e6
    cfg_acc = cfg_gpu_only(False); cfg_eon = cfg_gpu_only(True)
    det_m = run_l4(CFG, L4Params("m", 7.8, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, B200, "m", 0))
    det_goa = run_l4(cfg_acc, L4Params("m", 7.8, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, B200, "m", 0))
    det_goe = run_l4(cfg_eon, L4Params("m", 7.8, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, B200, "m", 0))
    det_c = run_l4(CFG, L4Params("c", ILLUSTRATIVE_BULK, 0, 0.90, 0.95, 0.55, 0.07, 60, 150, 0, B200, "c", 60))
    det_s = run_l4(CFG, L4Params("s", ILLUSTRATIVE_BULK, 0, 0.90, 0.95, 0.70, 0.059, 60, 500, 0.375, B200, "s", 60))
    irasr_table(l3["ce05"], peak_l3, [
        ("Full-stack mix-ref $7.80", "M", m["ce05"], det_m),
        ("GPU-only accounting $7.80", "gpu", goa["ce05"], det_goa),
        ("GPU-only economic $7.80", "gpu", goe["ce05"], det_goe),
        ("Contracted illustrative bulk $7.02", "C", c["ce05"], det_c),
        ("Strategic illustrative bulk $7.02", "S", s["ce05"], det_s),
    ])
    lambda_table({
        "L3": l3_npvs, "M_fullstack_7.80": m_npvs,
        "GO_accounting": go_acc, "GO_economic": go_eon,
        "C_bulk": c_npvs, "S_bulk": s_npvs,
    })
    access_extended(l3["ce05"], c["ce05"], s["ce05"])
    # transfer curve is expensive; skip if file exists
    if not (OUT / "transfer_rent_parity_curve.csv").exists():
        transfer_curve(l3["ce05"])
    c4_rows = []
    for fn in sorted(OUT.glob("rec_C4_*.json")):
        c4_rows.append(json.loads(fn.read_text(encoding="utf-8")))
    summary = {
        **meta(),
        "CE_L3": l3["ce05"], "CE_L3_SBI": [l3["CE_lo"], l3["CE_hi"]],
        "CE_M": m["ce05"], "CE_M_SBI": [m["CE_lo"], m["CE_hi"]],
        "CE_GO_acc": goa["ce05"], "CE_GO_econ": goe["ce05"],
        "CE_C": c["ce05"], "CE_C_SBI": [c["CE_lo"], c["CE_hi"]],
        "CE_S": s["ce05"], "CE_S_SBI": [s["CE_lo"], s["CE_hi"]],
        "matched": decomp,
        "C4": [{k: r.get(k) for k in (
            "label", "rate", "cc_mode", "det_npv", "ce05", "det_peak", "customer_capital"
        )} for r in c4_rows],
        "realized_rate_status": "NOT CALIBRATED — $7.02 remains illustrative (9.36x0.75)",
    }
    (OUT / "v6_1_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("SUMMARY", json.dumps(summary, indent=2))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all",
                    help="all|l3|m|go|c|s|matched|post|c4|transfer|access|pack")
    args = ap.parse_args()
    if args.stage == "all":
        main()
    else:
        run_stage(args.stage)
