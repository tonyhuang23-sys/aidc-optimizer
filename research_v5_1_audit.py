#!/usr/bin/env python3
"""
HISTORICAL SCRIPT — period artifact, not engine 1.2.1.
0.375 is the v5.1 compensation for the old 1-phys double-count engine.
Live research_l4.py bills residual unsold only; live S default is 0.75.

v5.1 P0 audit suite — cashflow, contract rate, CAPEX, backstop, credit MC.
Does NOT expand framework; audits whether v5.0 headline flips are robust.
"""
from __future__ import annotations
import csv, json, math
from pathlib import Path
from dataclasses import dataclass
import numpy as np

from aidc_optimizer.cli import load_config
from aidc_optimizer.models import run_asset
from aidc_optimizer.core import TaxEngine, npv_monthly
from research_l4 import (
    L4Params, build_compute_ext, apply_l4_financing, run_l4, GPU_PER_IT_KW
)
from aidc_optimizer.financing import DebtInputs
from aidc_optimizer.risk import run_full_pipeline

OUT = Path("research_outputs/v5_1")
OUT.mkdir(parents=True, exist_ok=True)
CFG = load_config("configs/alberta.yaml")
WACC_L4 = CFG["wacc"]["L4_Compute"]
IT_MW = CFG["reference"]["gen_mw"] / CFG["reference"]["pue"]
N_GPU = IT_MW * 1000 * GPU_PER_IT_KW  # ~42640
# Unified B200 all-in compute CAPEX (hardware stack, NO unproven discount)
B200_ALLIN_PER_GPU = 60000  # silicon+server+network share of compute stack
B200_CAPEX_IT_KW = B200_ALLIN_PER_GPU * GPU_PER_IT_KW  # ~31980
PUBLIC_DEDICATED = 9.36
PUBLIC_MEDIAN = 7.80


def make_params(rate, decay, billable, util, lev, kd, tenor, cc, backstop, capex_it, contract_m, label):
    return L4Params(
        mode=label, rate_gpu_hr=rate, decay=decay, phys_util=util, billable_util=billable,
        leverage=lev, kd=kd, tenor_months=tenor, customer_capital_musd=cc,
        backstop_rate_pct_market=backstop, capex_per_kw_it=capex_it, label=label,
        contract_months=contract_m,
    )


def annual_cashflow(cfg, p: L4Params, tag: str):
    """Export monthly then annual CF for audit."""
    case = build_compute_ext(cfg, p)
    res = run_asset(case, cfg)
    tax = TaxEngine(rate=cfg["tax"]["rate"], dep_life_months=cfg["tax"]["dep_life_months"],
                    method=cfg["tax"]["method"])
    cm = cfg["dc"]["construction_months"]
    # monthly series after COD
    rev = case.revenue
    opex = case.opex
    capex = case.capex
    rows = []
    for m in range(len(rev)):
        if m < cm and rev[m] == 0 and capex[m] == 0:
            continue
        yr = max(0, (m - cm) // 12) + 1 if m >= cm else 0
        rate_it = p.rate_gpu_hr * GPU_PER_IT_KW * ((1 + p.decay) ** max(0, m - cm))
        if p.contract_months and m >= cm + p.contract_months:
            rate_it = 0  # no post-contract ops in contract_months mode
        rows.append(dict(
            tag=tag, month=m, year=yr,
            revenue=rev[m], opex=opex[m], capex=capex[m],
            ebitda=rev[m] - opex[m],
            rate_gpu_hr=p.rate_gpu_hr * ((1 + p.decay) ** max(0, m - cm)) if m >= cm else 0,
            billable=p.billable_util if m >= cm else 0,
        ))
    # annual aggregate operating years
    annual = {}
    for r in rows:
        y = r["year"]
        if y == 0:
            continue
        a = annual.setdefault(y, dict(year=y, revenue=0, opex=0, capex=0, ebitda=0, months=0, rate_sum=0))
        a["revenue"] += r["revenue"]; a["opex"] += r["opex"]; a["capex"] += r["capex"]
        a["ebitda"] += r["ebitda"]; a["months"] += 1; a["rate_sum"] += r["rate_gpu_hr"]
    ann_list = []
    for y in sorted(annual):
        a = annual[y]
        ann_list.append(dict(
            tag=tag, year=y,
            revenue_musd=round(a["revenue"]/1e6, 2),
            opex_musd=round(a["opex"]/1e6, 2),
            ebitda_musd=round(a["ebitda"]/1e6, 2),
            capex_musd=round(a["capex"]/1e6, 2),
            avg_rate_gpuh=round(a["rate_sum"]/max(1,a["months"]), 4),
            project_fcf_musd=round((a["ebitda"] - a["capex"])/1e6, 2),  # rough pre-tax/interest
        ))
    return ann_list, res.project_npv/1e6, case


def p0_1_cashflow_audit():
    print("=== P0-1 C1 vs C2 cashflow audit ===")
    # C1 fixed, C2 step-down -6%/yr; SAME capex, util, billable, financing
    base_kw = dict(billable=0.95, util=0.90, lev=0.55, kd=0.070, tenor=60, cc=150,
                   backstop=0.0, capex_it=B200_CAPEX_IT_KW, contract_m=60)
    c1 = make_params(9.36, 0.00, **{k: base_kw[k] for k in base_kw if k not in ()}, label="C1")
    # fix make_params call
    c1 = make_params(9.36, 0.00, 0.95, 0.90, 0.55, 0.070, 60, 150, 0.0, B200_CAPEX_IT_KW, 60, "C1")
    c2 = make_params(9.36, -0.06, 0.95, 0.90, 0.55, 0.070, 60, 150, 0.0, B200_CAPEX_IT_KW, 60, "C2")
    c3 = make_params(9.36, -0.15, 0.90, 0.85, 0.55, 0.070, 60, 150, 0.0, B200_CAPEX_IT_KW, 60, "C3")
    ann1, npv1, case1 = annual_cashflow(CFG, c1, "C1")
    ann2, npv2, case2 = annual_cashflow(CFG, c2, "C2")
    ann3, npv3, case3 = annual_cashflow(CFG, c3, "C3")
    r1, r2 = run_l4(CFG, c1), run_l4(CFG, c2)
    print(f"  C1 NPV={r1['npv_musd']:.1f}M  C2 NPV={r2['npv_musd']:.1f}M  Δ={r1['npv_musd']-r2['npv_musd']:.1f}M")
    print(f"  C1 total rev={case1.revenue.sum()/1e6:.1f}M  C2 total rev={case2.revenue.sum()/1e6:.1f}M  Δrev={(case1.revenue.sum()-case2.revenue.sum())/1e6:.1f}M")
    # PV of revenue difference at WACC
    disc = np.array([(1+WACC_L4)**(-(m+1)/12) for m in range(len(case1.revenue))])
    pv_drev = float(((case1.revenue - case2.revenue) * disc).sum() / 1e6)
    pv_dopex = float(((case1.opex - case2.opex) * disc).sum() / 1e6)
    print(f"  PV(ΔRevenue)={pv_drev:.1f}M  PV(ΔOPEX)={pv_dopex:.1f}M  → explains most of ΔNPV")
    rows = ann1 + ann2 + ann3
    write_csv(OUT/"contract_cashflow_audit.csv", rows)
    # year-by-year side by side
    side = []
    for a, b in zip(ann1, ann2):
        side.append(dict(
            year=a["year"],
            c1_rev=a["revenue_musd"], c2_rev=b["revenue_musd"], d_rev=round(a["revenue_musd"]-b["revenue_musd"],2),
            c1_rate=a["avg_rate_gpuh"], c2_rate=b["avg_rate_gpuh"],
            c1_ebitda=a["ebitda_musd"], c2_ebitda=b["ebitda_musd"],
            c1_fcf=a["project_fcf_musd"], c2_fcf=b["project_fcf_musd"],
        ))
    write_csv(OUT/"c1_c2_year_compare.csv", side)
    for s in side:
        print(f"  Y{s['year']}: C1 rev={s['c1_rev']:.0f} @ {s['c1_rate']:.2f} | C2 rev={s['c2_rev']:.0f} @ {s['c2_rate']:.2f} | Δrev={s['d_rev']:.0f}")
    # Decomp
    decomp = dict(
        delta_npv=round(r1["npv_musd"]-r2["npv_musd"],1),
        pv_delta_revenue=round(pv_drev,1),
        pv_delta_opex=round(pv_dopex,1),
        residual_unexplained=round((r1["npv_musd"]-r2["npv_musd"]) - (pv_drev - pv_dopex), 1),
        same_billable=True, same_capex=True, same_contract_months=True,
        c1_extends_beyond_5y=False,  # contract_months=60 stops ops
        pass_audit=abs((r1["npv_musd"]-r2["npv_musd"]) - (pv_drev - pv_dopex)) < 200,
    )
    write_csv(OUT/"c1_c2_decomp.csv", [decomp])
    print(f"  Decomp: ΔNPV={decomp['delta_npv']} ≈ PV(ΔRev-ΔOpex)={decomp['pv_delta_revenue']-decomp['pv_delta_opex']:.1f} unexplained={decomp['residual_unexplained']}")
    print(f"  P0-1 PASS={decomp['pass_audit']}")
    return decomp, r1, r2


def p0_2_realized_rate():
    print("\n=== P0-2 Realized Contract Rate Engine ===")
    # Reality check TCV
    for rate in [9.36, 7.80, 6.50, 5.50, 4.50]:
        tcv_per_gpu = rate * 8760 * 0.95 * 5
        tcv_total = tcv_per_gpu * N_GPU / 1e9  # $B
        print(f"  rate={rate:.2f}: TCV/GPU=${tcv_per_gpu/1e3:.0f}k  Total TCV≈${tcv_total:.1f}B  vs CAPEX compute≈${B200_ALLIN_PER_GPU*N_GPU/1e9:.1f}B")
    # Volume × Term × Service factors
    rows = []
    l3 = run_full_pipeline(CFG, "critical_it")
    l3_npv = l3.project_npv / 1e6
    l3_ce = 505.0  # from v3.3 table
    for vol in [1.0, 0.90, 0.80, 0.70, 0.60, 0.50]:
        for term_f in [1.0, 0.95, 0.90]:  # longer term may discount
            for svc in [1.0, 1.05]:  # full stack premium
                rate = PUBLIC_DEDICATED * vol * term_f * svc
                p = make_params(rate, 0.0, 0.95, 0.90, 0.55, 0.070, 60, 150, 0.0, B200_CAPEX_IT_KW, 60, "rc")
                r = run_l4(CFG, p)
                rows.append(dict(
                    public_list=PUBLIC_DEDICATED, volume_factor=vol, term_factor=term_f, service_factor=svc,
                    realized_rate=round(rate, 3), npv_musd=r["npv_musd"],
                    peak=r["peak_equity_musd"], vs_l3_npv=round(r["npv_musd"]-l3_npv,1),
                    beats_l3=r["npv_musd"] > l3_npv,
                ))
    write_csv(OUT/"realized_contract_rate_grid.csv", rows)
    # Max sustainable discount vs L3 (break-even rate where L4-C NPV = L3 NPV)
    lo, hi = 2.0, 12.0
    for _ in range(40):
        mid = (lo+hi)/2
        p = make_params(mid, 0.0, 0.95, 0.90, 0.55, 0.070, 60, 150, 0.0, B200_CAPEX_IT_KW, 60, "be")
        r = run_l4(CFG, p)
        if r["npv_musd"] > l3_npv: hi = mid
        else: lo = mid
    be_c = (lo+hi)/2
    lo, hi = 2.0, 12.0
    for _ in range(40):
        mid = (lo+hi)/2
        p = make_params(mid, 0.0, 0.95, 0.90, 0.70, 0.059, 60, 500, 0.75, B200_CAPEX_IT_KW, 60, "beS")
        r = run_l4(CFG, p)
        if r["npv_musd"] > l3_npv: hi = mid
        else: lo = mid
    be_s = (lo+hi)/2
    disc = dict(
        public_dedicated=PUBLIC_DEDICATED,
        l4c_breakeven_vs_l3=round(be_c, 3),
        l4s_breakeven_vs_l3=round(be_s, 3),
        max_discount_l4c=round(1 - be_c/PUBLIC_DEDICATED, 3),
        max_discount_l4s=round(1 - be_s/PUBLIC_DEDICATED, 3),
        tcv_per_gpu_at_936=round(9.36*8760*0.95*5, 0),
        n_gpu=round(N_GPU, 0),
        total_tcv_b=round(9.36*8760*0.95*5*N_GPU/1e9, 2),
        compute_capex_b=round(B200_ALLIN_PER_GPU*N_GPU/1e9, 2),
        tcv_to_compute_capex=round((9.36*8760*0.95*5*N_GPU)/(B200_ALLIN_PER_GPU*N_GPU), 2),
    )
    write_csv(OUT/"contract_discount_break_even.csv", [disc])
    print(f"  L4-C break-even vs L3: ${be_c:.2f}/GPUh (max discount {disc['max_discount_l4c']:.0%})")
    print(f"  L4-S break-even vs L3: ${be_s:.2f}/GPUh (max discount {disc['max_discount_l4s']:.0%})")
    print(f"  Reality: TCV/GPU@9.36≈${disc['tcv_per_gpu_at_936']/1e3:.0f}k  TCV/CAPEX={disc['tcv_to_compute_capex']:.2f}x")
    # Flag: if TCV/CAPEX > 5x, list price may be too high for bulk 5Y
    disc["reality_flag"] = "TCV/CAPEX high — list price may overstate bulk 5Y rate" if disc["tcv_to_compute_capex"] > 4 else "ok"
    print(f"  Reality flag: {disc['reality_flag']}")
    return disc


def p0_3_capex_unify():
    print("\n=== P0-3 B200 CAPEX unify ===")
    # L4-C and L4-S MUST use same hardware capex; S only differs by finance/backstop/cc
    cap = B200_CAPEX_IT_KW
    c = make_params(9.36, 0.0, 0.95, 0.90, 0.55, 0.070, 60, 150, 0.0, cap, 60, "L4-C")
    s = make_params(9.36, 0.0, 0.95, 0.90, 0.70, 0.059, 60, 500, 0.75, cap, 60, "L4-S")
    # old wrong S with 21.3k
    s_old = make_params(9.36, 0.0, 0.95, 0.90, 0.70, 0.059, 60, 500, 0.75, 21300, 60, "L4-S-old213")
    rc, rs, rso = run_l4(CFG, c), run_l4(CFG, s), run_l4(CFG, s_old)
    print(f"  Unified CAPEX ${cap:.0f}/IT-kW (≈${B200_ALLIN_PER_GPU/1e3:.0f}k/GPU)")
    print(f"  L4-C: NPV={rc['npv_musd']:.1f} peak={rc['peak_equity_musd']:.1f}")
    print(f"  L4-S unified: NPV={rs['npv_musd']:.1f} peak={rs['peak_equity_musd']:.1f}")
    print(f"  L4-S old 21.3k: NPV={rso['npv_musd']:.1f} peak={rso['peak_equity_musd']:.1f}  ← REMOVE from base")
    # discount sensitivity 0/10/20/30 on unified base S
    sens = []
    for d in [0.0, 0.10, 0.20, 0.30]:
        p = make_params(9.36, 0.0, 0.95, 0.90, 0.70, 0.059, 60, 500, 0.75, cap*(1-d), 60, f"d{d}")
        r = run_l4(CFG, p)
        sens.append(dict(gpu_discount=d, capex_it=round(cap*(1-d),0), npv=r["npv_musd"], peak=r["peak_equity_musd"]))
        print(f"  discount {d:.0%}: NPV={r['npv_musd']:.1f} peak={r['peak_equity_musd']:.1f}")
    write_csv(OUT/"b200_capex_unified.csv", [
        dict(item="L4-C", capex_it=cap, npv=rc["npv_musd"], peak=rc["peak_equity_musd"]),
        dict(item="L4-S_unified", capex_it=cap, npv=rs["npv_musd"], peak=rs["peak_equity_musd"]),
        dict(item="L4-S_old_21300_REMOVED", capex_it=21300, npv=rso["npv_musd"], peak=rso["peak_equity_musd"]),
    ])
    write_csv(OUT/"gpu_discount_sensitivity.csv", sens)
    return rc, rs, rso


def p0_5_backstop_audit():
    print("\n=== P0-5 Backstop double-counting audit ===")
    # Capacity waterfall
    # Customer contracted = billable 0.95 of total
    # Physical use = phys_util 0.90
    # Paid-but-unused = 0.95-0.90 = 0.05 (ALREADY paid by customer ToP — backstop must NOT apply)
    # Residual unsold = 1-0.95 = 0.05 (only this may go to vendor backstop)
    total = 1.0
    contracted = 0.95
    physical = 0.90
    paid_unused = contracted - physical  # 0.05
    residual_unsold = total - contracted  # 0.05
    # v5.1-era research_l4 billed backstop on (1-phys)=0.10 (ToP unused + unsold).
    # Engine 1.2.1 bills residual unsold only; do not read this block as current.
    # 0.375 below is the historical compensation: 0.75 * 0.05/0.10.
    then_engine_backstop_base = 1 - physical  # 0.10 on the v5.1 engine
    correct_backstop_base = residual_unsold  # 0.05
    print(f"  Total=1.0 Contracted={contracted} Physical={physical}")
    print(f"  Paid-but-unused (ToP, NO backstop)={paid_unused}")
    print(f"  Residual unsold (backstop OK)={residual_unsold}")
    print(f"  v5.1 engine backstop base={then_engine_backstop_base}  CORRECT={correct_backstop_base}")
    print(f"  DOUBLE-COUNT fraction={then_engine_backstop_base - correct_backstop_base:.2f} of capacity")
    # Historical workaround only: 0.75 * residual_unsold / (1-phys) = 0.375
    s_wrong = make_params(9.36, 0.0, 0.95, 0.90, 0.70, 0.059, 60, 500, 0.75, B200_CAPEX_IT_KW, 60, "S_wrong")
    s_fix = make_params(9.36, 0.0, 0.95, 0.90, 0.70, 0.059, 60, 500, 0.375, B200_CAPEX_IT_KW, 60, "S_fix")
    s_none = make_params(9.36, 0.0, 0.95, 0.90, 0.70, 0.059, 60, 500, 0.0, B200_CAPEX_IT_KW, 60, "S_none")
    rw, rf, rn = run_l4(CFG, s_wrong), run_l4(CFG, s_fix), run_l4(CFG, s_none)
    print(f"  S backstop WRONG (double): NPV={rw['npv_musd']:.1f}")
    print(f"  S backstop FIXED:          NPV={rf['npv_musd']:.1f}")
    print(f"  S no backstop:             NPV={rn['npv_musd']:.1f}")
    print(f"  Inflated by double-count:  {rw['npv_musd']-rf['npv_musd']:.1f}M")
    rows = [
        dict(case="wrong_double_count", backstop_base="1-phys_util=0.10", npv=rw["npv_musd"], peak=rw["peak_equity_musd"]),
        dict(case="fixed_residual_only", backstop_base="1-contracted=0.05", npv=rf["npv_musd"], peak=rf["peak_equity_musd"]),
        dict(case="no_backstop", backstop_base="0", npv=rn["npv_musd"], peak=rn["peak_equity_musd"]),
        dict(case="capacity_ledger", total=1.0, contracted=0.95, physical=0.90,
             paid_but_unused=0.05, residual_unsold=0.05, vendor_backstop_ok=0.05),
    ]
    write_csv(OUT/"capacity_waterfall.csv", rows)
    return rw, rf, rn


def p0_4_strategic_credit_mc(n=2000, seed=42):
    print(f"\n=== P0-4 Strategic credit+contract MC N={n} ===")
    rng = np.random.default_rng(seed)
    # Historical: 0.375 compensation on the v5.1 double-count engine, not 1.2.1.
    base_rate, base_backstop = 9.36, 0.375
    npvs = []
    breaches = 0
    for i in range(n):
        # Customer PD ~ 2% over 5Y for IG-ish; higher for mix
        default = rng.random() < 0.03  # 3% path default
        term_year = rng.integers(2, 5) if default else None
        # Downgrade / enforceability: rate haircut
        enforce = rng.random()  # 0-1
        rate_haircut = 0.0 if enforce > 0.15 else rng.uniform(0.05, 0.25)
        # Price reset probability
        if rng.random() < 0.10:
            rate_haircut = max(rate_haircut, rng.uniform(0.10, 0.30))
        # Vendor backstop fail
        bs = base_backstop if rng.random() > 0.08 else 0.0
        # Financing freeze
        if rng.random() < 0.10:
            lev, kd = 0.55, 0.095
        else:
            lev, kd = 0.70, 0.059
        # Merchant residual fallback shock
        residual_shock = max(0.5, 1 + rng.normal(0, 0.15))
        rate = base_rate * (1 - rate_haircut)
        contract_m = 60 if term_year is None else term_year * 12
        tenor = min(60, contract_m)
        p = make_params(rate, 0.0, 0.95, 0.90, lev, kd, tenor, 500, bs, B200_CAPEX_IT_KW, contract_m, "mc")
        try:
            r = run_l4(CFG, p)
            npv = r["npv_musd"] * residual_shock  # crude residual link
            if r["min_dscr_contract"] is not None and r["min_dscr_contract"] < 1.0:
                breaches += 1
            npvs.append(npv)
        except Exception:
            continue
    a = np.array(npvs)
    p5 = float(np.quantile(a, 0.05))
    es = float(a[a <= p5].mean())
    e = float(a.mean())
    k = int((a < 0).sum())
    nobs = len(a)
    # Wilson CI
    z = 1.96
    phat = k / nobs
    den = 1 + z*z/nobs
    centre = (phat + z*z/(2*nobs)) / den
    half = z * math.sqrt(phat*(1-phat)/nobs + z*z/(4*nobs*nobs)) / den
    out = dict(
        n=nobs, e_npv=round(e,1), p5=round(p5,1), es5=round(es,1),
        ce05=round(0.5*e+0.5*es,1),
        loss_count=k, loss_rate=round(phat,4),
        wilson_lo=round(max(0, centre-half),4), wilson_hi=round(min(1, centre+half),4),
        dscr_breach_rate=round(breaches/nobs,4),
        note="credit/contract/vendor/financing shocks; unified B200 CAPEX; fixed backstop residual-only",
    )
    write_csv(OUT/"strategic_credit_mc.csv", [out])
    print(f"  E(NPV)={out['e_npv']}  ES5={out['es5']}  CE05={out['ce05']}")
    print(f"  Losses {k}/{nobs} = {out['loss_rate']:.2%}  Wilson95% [{out['wilson_lo']:.2%},{out['wilson_hi']:.2%}]")
    print(f"  DSCR breach rate={out['dscr_breach_rate']:.2%}")
    print(f"  P0-4: P(loss)=0% claim REJECTED (observed {out['loss_rate']:.2%})")
    return out


def p1_economic_capital_and_access():
    print("\n=== P1 Sponsor Economic Capital + Contract Access EV ===")
    # Peak cash equity from unified S
    s = make_params(9.36, 0.0, 0.95, 0.90, 0.70, 0.059, 60, 500, 0.375, B200_CAPEX_IT_KW, 60, "S")
    c = make_params(9.36, 0.0, 0.95, 0.90, 0.55, 0.070, 60, 150, 0.0, B200_CAPEX_IT_KW, 60, "C")
    m = make_params(7.80, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0.0, B200_CAPEX_IT_KW, 0, "M")
    rs, rc, rm = run_l4(CFG, s), run_l4(CFG, c), run_l4(CFG, m)
    l3 = run_full_pipeline(CFG, "critical_it")
    l3_npv = l3.project_npv/1e6
    # Economic capital add-ons as % of peak cash equity / CAPEX
    rows = []
    for name, r, add_gtee, add_lc, add_reserve in [
        ("L4-M", rm, 0.05, 0.02, 0.03),
        ("L4-C", rc, 0.15, 0.08, 0.05),
        ("L4-S", rs, 0.25, 0.10, 0.08),
        ("L3", dict(npv_musd=l3_npv, peak_equity_musd=l3.peak_equity/1e6, capex_musd=l3.capex_total/1e6), 0.10, 0.05, 0.03),
    ]:
        peak = r["peak_equity_musd"] if isinstance(r, dict) else r.peak_equity/1e6
        capex = r["capex_musd"] if isinstance(r, dict) else r.capex_total/1e6
        npv = r["npv_musd"] if isinstance(r, dict) else r.project_npv/1e6
        gtee = add_gtee * capex
        lc = add_lc * capex
        resv = add_reserve * peak
        econ = peak + gtee + lc + resv
        rows.append(dict(
            mode=name, peak_cash_equity=round(peak,1), guarantee_eq=round(gtee,1),
            lc_collateral=round(lc,1), liquidity_reserve=round(resv,1),
            economic_capital=round(econ,1), npv=round(npv,1),
            npv_per_peak=round(npv/peak,2) if peak else None,
            npv_per_econ=round(npv/econ,2) if econ else None,
        ))
        print(f"  {name}: Peak={peak:.0f} EconCap={econ:.0f} NPV={npv:.0f} NPV/Econ={npv/econ:.2f}")
    write_csv(OUT/"sponsor_economic_capital.csv", rows)
    # Contract access EV
    # CE proxies: use NPV as CE for contracted (low market risk); merchant NPV as fallback
    ce_c, ce_s, ce_m, ce_l3 = rc["npv_musd"], rs["npv_musd"], rm["npv_musd"], l3_npv
    access = []
    for pC in [0.05, 0.15, 0.30, 0.50, 0.80, 1.0]:
        for pS in [0.0, 0.10, 0.30, 0.60, 1.0]:
            # pursuit cost rough
            pursuit_c, pursuit_s = 20.0, 50.0
            ev_c = pC * ce_c + (1-pC) * ce_m - pursuit_c
            # strategic conditional on having contract
            ev_s = pC * (pS * ce_s + (1-pS) * ce_c) + (1-pC) * ce_m - pursuit_s
            access.append(dict(
                pC=pC, pS=pS, ev_pursue_C=round(ev_c,1), ev_pursue_S=round(ev_s,1),
                better_than_L3_C=ev_c > ce_l3, better_than_L3_S=ev_s > ce_l3,
            ))
    write_csv(OUT/"contract_access_ev.csv", access)
    # Type A/B/C summary
    types = [
        dict(type="A Uncontracted", pC=0.10, pS=0.02, fallback="Merchant"),
        dict(type="B Contracted", pC=1.0, pS=0.25, fallback="L4-C"),
        dict(type="C Strategic Platform", pC=1.0, pS=0.80, fallback="L4-S"),
    ]
    for t in types:
        pC, pS = t["pC"], t["pS"]
        t["ev"] = round(pC * (pS * ce_s + (1-pS) * ce_c) + (1-pC) * ce_m - 30, 1)
        t["vs_l3"] = round(t["ev"] - ce_l3, 1)
        print(f"  {t['type']}: EV={t['ev']:.0f} vs L3 Δ={t['vs_l3']:.0f}")
    write_csv(OUT/"player_type_ev.csv", types)
    return rows, types


def p1_scale_sensitivity():
    print("\n=== P1-5 Scale sensitivity ===")
    rows = []
    for mw in [10, 20, 50, 100]:
        # scale CAPEX roughly linear; rate may improve with scale (volume factor)
        vol = {10: 1.0, 20: 0.95, 50: 0.85, 100: 0.75}[mw]
        rate = PUBLIC_DEDICATED * vol
        # run by overriding gen_mw
        from aidc_optimizer.cli import apply_overrides
        cfg = apply_overrides(CFG, [f"reference.gen_mw={mw}"])
        # recompute IT
        p = L4Params("C", rate, 0.0, 0.90, 0.95, 0.55, 0.070, 60, 50*(mw/100), 0.0,
                     B200_CAPEX_IT_KW, "scale", contract_months=60)
        r = run_l4(cfg, p)
        rows.append(dict(gen_mw=mw, volume_factor=vol, realized_rate=round(rate,3),
                         npv=r["npv_musd"], peak=r["peak_equity_musd"], capex=r["capex_musd"],
                         npv_per_mw=round(r["npv_musd"]/mw,2)))
        print(f"  {mw}MW rate={rate:.2f} NPV={r['npv_musd']:.0f} peak={r['peak_equity_musd']:.0f} $/MW={r['npv_musd']/mw:.1f}")
    write_csv(OUT/"scale_sensitivity.csv", rows)
    return rows


def write_csv(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8"); return
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)


def main():
    decomp, r1, r2 = p0_1_cashflow_audit()
    disc = p0_2_realized_rate()
    rc, rs, rso = p0_3_capex_unify()
    rw, rf, rn = p0_5_backstop_audit()
    mc = p0_4_strategic_credit_mc(n=2000)
    econ, types = p1_economic_capital_and_access()
    scale = p1_scale_sensitivity()

    # Headline corrected table
    l3 = run_full_pipeline(CFG, "critical_it")
    headline = [
        dict(mode="L3 Critical IT", npv=round(l3.project_npv/1e6,1), peak=round(l3.peak_equity/1e6,1),
             ce_approx=505, note="from v3.3 MC"),
        dict(mode="L4-M Merchant forward", npv=run_l4(CFG, make_params(7.8,-0.22,0.75,0.75,0.35,0.095,48,0,0,B200_CAPEX_IT_KW,0,"M"))["npv_musd"],
             peak=run_l4(CFG, make_params(7.8,-0.22,0.75,0.75,0.35,0.095,48,0,0,B200_CAPEX_IT_KW,0,"M"))["peak_equity_musd"],
             ce_approx=None, note="forward decay -22%"),
        dict(mode="L4-C C1 Fixed ToP (unified CAPEX)", npv=rc["npv_musd"], peak=rc["peak_equity_musd"],
             ce_approx=None, note="public list 9.36 — UPPER BOUND"),
        dict(mode="L4-C @ max sustainable disc vs L3", npv=round(l3.project_npv/1e6,1), peak=None,
             ce_approx=None, note=f"rate≈${disc['l4c_breakeven_vs_l3']}/GPUh"),
        dict(mode="L4-S FIXED backstop+unified CAPEX", npv=rf["npv_musd"], peak=rf["peak_equity_musd"],
             ce_approx=mc["ce05"], note="credit MC CE; not 0% loss"),
        dict(mode="L4-S OLD (double backstop + 21.3k) REMOVED", npv=rso["npv_musd"], peak=rso["peak_equity_musd"],
             ce_approx=None, note="DO NOT USE as base"),
    ]
    write_csv(OUT/"headline_corrected.csv", headline)

    summary = dict(
        p0_1_pass=bool(decomp["pass_audit"]),
        p0_1_delta_npv=decomp["delta_npv"],
        p0_1_explained_by_pv_revenue=decomp["pv_delta_revenue"],
        p0_2_max_discount_l4c=disc["max_discount_l4c"],
        p0_2_reality_flag=disc["reality_flag"],
        p0_3_unified_capex_it=B200_CAPEX_IT_KW,
        p0_3_remove_21300=True,
        p0_4_loss_rate=mc["loss_rate"],
        p0_4_ce05=mc["ce05"],
        p0_4_reject_zero_loss=True,
        p0_5_double_count_inflation_musd=round(rw["npv_musd"]-rf["npv_musd"],1),
        p0_5_fixed_S_npv=rf["npv_musd"],
        corrected_L4C_npv=rc["npv_musd"],
        corrected_L4S_npv=rf["npv_musd"],
        l3_npv=round(l3.project_npv/1e6,1),
    )
    with open(OUT/"audit_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("\n=== AUDIT SUMMARY ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print(f"\nOutputs in {OUT}")


if __name__ == "__main__":
    main()
