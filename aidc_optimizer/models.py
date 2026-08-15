"""
7 种商业模式资产模型（第四节~第十三节、第二十二节）
统一 100 MW Reference Project，全部换算到 MW 口径。

L0_Dev        Powered Land（开发退出）
L1_Power      Power-only（tolling 专用电厂）
L2_Shell      Powered Shell
L3_CriticalIT AI-ready Critical IT Capacity（TeraWulf 模式）
L35_Hosting   GPU Hosting（机柜托管，GPU 客户自有）
L4_Compute    ComputeCo（自持 GPU 出租算力）
L5_AI         AI Factory（出售 token/推理服务）

每个 build_* 返回 AssetCase（纯资产层数据），由 run_case 结合融资模型输出 LayerResult。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

import numpy as np

from .core import (
    LayerResult,
    TaxEngine,
    npv_monthly,
    irr_monthly,
    payback_months,
    s_curve_drawdown,
    uniform_drawdown,
)


# ---------------------------------------------------------------------------
# 资产层数据结构
# ---------------------------------------------------------------------------

@dataclass
class AssetCase:
    name: str
    layer: str
    gen_mw: float
    it_mw: float
    capex: np.ndarray                      # 月度资本投入（含开发费用，不含 IDC）
    revenue: np.ndarray                    # 月度收入（运营期）
    opex: np.ndarray                       # 月度运营成本（含燃料/电费/碳，不含税）
    residual: float = 0.0                  # 期末残值（资产出售/续期价值）
    notes: Dict = field(default_factory=dict)

    @property
    def months(self) -> int:
        return len(self.capex)


def _spread(total: float, start: int, duration: int, n_total: int, curve="s") -> np.ndarray:
    """把 total 摊到 start..start+duration-1 月。MC 扰动可能传入浮点，统一取整。"""
    n_total, start, duration = int(n_total), int(start), int(duration)
    arr = np.zeros(n_total)
    w = s_curve_drawdown(duration) if curve == "s" else uniform_drawdown(duration)
    arr[start:start + duration] = total * w
    return arr


def _ramp_utilization(m: int, start: int, steady: float, ramp_months: int = 24) -> float:
    """利用率爬坡：运营首年 65% 线性升至稳态。"""
    if ramp_months <= 0:
        return steady
    frac = min(1.0, (m - start + 1) / ramp_months)
    return steady * (0.65 + 0.35 * frac)


# ---------------------------------------------------------------------------
# L1 Power-only —— tolling 专用电厂（Greenlight 模式）
# ---------------------------------------------------------------------------

def build_power(cfg: dict) -> AssetCase:
    p = cfg["power"]
    gen_mw = cfg["reference"]["gen_mw"]
    cm = p["construction_months"]
    life = p["life_months"]
    n = cm + life

    # ---- CAPEX（开发费 S 曲线前置 6 个月 + 建设期 S 曲线）----
    dev = p.get("dev_capex_musd", 0.0) * 1e6
    epc = gen_mw * 1000 * p["capex_per_kw"]
    capex = np.zeros(n)
    if dev > 0 and cm >= 12:
        capex[:cm - 12] += _spread(dev, 0, cm - 12, n, curve="u")[:cm - 12]
    capex += _spread(epc, max(0, cm - 12), min(12, cm), n)

    # ---- 运营期收支 ----
    revenue = np.zeros(n)
    opex = np.zeros(n)
    avail = p["availability"]
    heat = p["heat_rate_gj_per_mwh"]
    gas0 = p["gas_price_gj"]
    gas_esc = p.get("gas_escalator", 0.0)
    cap_pay = p["capacity_payment_kw_mo"]
    vom = p["vom_per_mwh"]
    fom = p["fixed_om_kw_yr"] / 12
    cb = p.get("carbon", {}) or {}
    intensity = cb.get("intensity", 0.0)
    benchmark = cb.get("benchmark", 0.0)
    cprice = cb.get("price", 0.0)
    c_pass = cb.get("passthrough", False)
    fuel_pass = p.get("fuel_passthrough", True)

    for m in range(cm, n):
        yr = (m - cm) / 12
        mwh = gen_mw * 730 * avail
        gas = gas0 * (1 + gas_esc) ** yr
        fuel = mwh * heat * gas
        carbon = mwh * max(0.0, intensity - benchmark) * cprice * (1 + cb.get("escalator", 0.0)) ** yr
        rev = gen_mw * 1000 * cap_pay
        if fuel_pass:
            # tolling: 燃料/变动成本转嫁（风险存在但敞口≈0）
            rev += fuel + vom * mwh + (carbon if c_pass else 0)
            var_cost = vom * mwh + (0 if c_pass else carbon)
        else:
            var_cost = fuel + vom * mwh + carbon
        revenue[m] = rev
        opex[m] = var_cost + gen_mw * 1000 * fom

    residual = epc * p.get("residual_pct", 0.1)
    return AssetCase(
        name="Power-only (Tolling)", layer="L1_Power", gen_mw=gen_mw, it_mw=0.0,
        capex=capex, revenue=revenue, opex=opex, residual=residual,
        notes={"capex_per_kw": p["capex_per_kw"], "capacity_payment": cap_pay,
               "fuel_passthrough": fuel_pass},
    )


# ---------------------------------------------------------------------------
# L0 Powered Land —— 开发到 Power-secured 后退出
# ---------------------------------------------------------------------------

def build_dev_exit(cfg: dict) -> AssetCase:
    d = cfg["dev"]
    gen_mw = cfg["reference"]["gen_mw"]
    months = int(d["months"]) + 3
    total = (d["land_musd"] + d["ic_musd"] + d["permitting_musd"] + d.get("other_musd", 0)) * 1e6
    capex = _spread(total, 0, d["months"], months, curve="u")
    revenue = np.zeros(months)
    opex = np.zeros(months)
    exit_val = gen_mw * 1000 * d["exit_value_per_kw"]
    return AssetCase(
        name="Powered Land (Dev Exit)", layer="L0_Dev", gen_mw=gen_mw, it_mw=0.0,
        capex=capex, revenue=revenue, opex=opex, residual=exit_val,
        notes={"exit_value_per_kw": d["exit_value_per_kw"], "dev_months": d["months"]},
    )


# ---------------------------------------------------------------------------
# L2/L3/L35 数据中心层（壳 / AI-ready / GPU 托管）
# ---------------------------------------------------------------------------

def _build_dc_layer(
    cfg: dict, name: str, layer: str, capex_per_kw_it: float, rent_kw_mo: float,
    lease_months: int, include_power_cost: bool = False, hosting_margin: float = 0.0,
) -> AssetCase:
    ref = cfg["reference"]
    gen_mw = ref["gen_mw"]
    pue = ref["pue"]
    it_mw = gen_mw / pue
    dc = cfg["dc"]
    cm = dc["construction_months"]
    # 电力资产作为下沉投资（引用 Power 层 capex_per_kw）
    p = cfg["power"]
    power_capex = gen_mw * 1000 * p["capex_per_kw"] * p.get("dc_credit_pct", 1.0)
    infra_capex = it_mw * 1000 * capex_per_kw_it
    n = cm + lease_months

    capex = np.zeros(n)
    if p.get("dev_capex_musd", 0) > 0 and cm >= 12:
        capex[:cm - 12] += _spread(p["dev_capex_musd"] * 1e6, 0, cm - 12, n, curve="u")[:cm - 12]
    capex += _spread(power_capex + infra_capex, max(0, cm - 12), min(12, cm), n)

    revenue = np.zeros(n)
    opex = np.zeros(n)
    esc = dc.get("escalator", 0.0)
    dc_opex = dc["opex_kw_yr"] / 12
    power_price = cfg["dc"].get("power_cost_per_mwh", 0)  # 内部购电价
    availability = 1.0

    for m in range(cm, n):
        yr = (m - cm) / 12
        rent = rent_kw_mo * (1 + esc) ** yr
        revenue[m] = it_mw * 1000 * rent
        o = it_mw * 1000 * dc_opex * (1 + esc * 0.5) ** yr
        if include_power_cost:
            # GPU Hosting: 向租户收电费(含于 rent 中)，向下购电
            mwh = it_mw * pue * 730 * availability
            o += mwh * power_price
        opex[m] = o

    residual = (power_capex + infra_capex) * dc.get("residual_pct", 0.25)
    return AssetCase(
        name=name, layer=layer, gen_mw=gen_mw, it_mw=it_mw,
        capex=capex, revenue=revenue, opex=opex, residual=residual,
        notes={"capex_per_kw_it": capex_per_kw_it, "rent_kw_mo": rent_kw_mo,
               "lease_months": lease_months},
    )


def build_shell(cfg: dict) -> AssetCase:
    dc = cfg["dc"]
    return _build_dc_layer(cfg, "Powered Shell", "L2_Shell",
                           dc["shell_capex_per_kw"], dc["shell_rent_kw_mo"],
                           dc["shell_lease_months"])


def build_critical_it(cfg: dict) -> AssetCase:
    dc = cfg["dc"]
    return _build_dc_layer(cfg, "AI-ready Critical IT", "L3_CriticalIT",
                           dc["ready_capex_per_kw"], dc["ready_rent_kw_mo"],
                           dc["lease_months"])


def build_gpu_hosting(cfg: dict) -> AssetCase:
    dc = cfg["dc"]
    return _build_dc_layer(cfg, "GPU Hosting", "L35_Hosting",
                           dc["ready_capex_per_kw"] + dc["hosting_capex_increment_per_kw"],
                           dc["hosting_rent_kw_mo"], dc["lease_months"],
                           include_power_cost=True)


# ---------------------------------------------------------------------------
# L4 ComputeCo / L5 AI Factory —— GPU 资产层
# ---------------------------------------------------------------------------

def _build_gpu_layer(cfg: dict, name: str, layer: str, is_ai_factory: bool) -> AssetCase:
    ref = cfg["reference"]
    gen_mw = ref["gen_mw"]
    pue = ref["pue"]
    it_mw = gen_mw / pue
    dc = cfg["dc"]
    g = cfg["gpu" if not is_ai_factory else "ai"]
    p = cfg["power"]

    infra_ready_kw = dc["ready_capex_per_kw"] + dc["hosting_capex_increment_per_kw"]
    cm = dc["construction_months"]
    cycle = g["refresh_months"]
    cycles = 2
    life = cycles * cycle
    n = cm + life + 1

    # 基础设施（电厂+DC）建设期投入
    power_capex = gen_mw * 1000 * p["capex_per_kw"] * p.get("dc_credit_pct", 1.0)
    infra_capex = it_mw * 1000 * infra_ready_kw
    capex = np.zeros(n)
    if p.get("dev_capex_musd", 0) > 0 and cm >= 12:
        capex[:cm - 12] += _spread(p["dev_capex_musd"] * 1e6, 0, cm - 12, n, curve="u")[:cm - 12]
    capex += _spread(power_capex + infra_capex, max(0, cm - 12), min(12, cm), n)

    # GPU 采购：首期 COD 购入；每个刷新节点卖出旧卡、按折价买新卡
    gpu_unit = it_mw * 1000 * g["capex_per_kw_it"]
    refresh_factor = g.get("refresh_capex_factor", 0.85)
    gpu_capex_sched = []   # (month, amount)
    gpu_residual_sched = []  # (month, amount)
    for c in range(cycles):
        m_buy = cm + c * cycle
        gpu_capex_sched.append((m_buy, gpu_unit * (refresh_factor ** c)))
        if c > 0:
            m_sell = m_buy
            gpu_residual_sched.append((m_sell, gpu_unit * (refresh_factor ** (c - 1)) * g["residual_pct_at_refresh"]))
    for m, amt in gpu_capex_sched:
        capex[m] += amt
    # 期末残值：基础设施 + 最后一期 GPU
    residual = (power_capex + infra_capex) * dc.get("residual_pct", 0.25) + \
               gpu_unit * (refresh_factor ** (cycles - 1)) * g["residual_pct_at_refresh"]

    revenue = np.zeros(n)
    opex = np.zeros(n)
    rate0 = g["rate_per_kw_hr"]
    decay = g["rate_decay"]
    steady_u = g["utilization"]
    power_price = cfg["dc"].get("power_cost_per_mwh", 0)
    extra = g.get("extra_opex_kw_yr", 0) / 12
    ramp = g.get("ramp_months", 24)

    for m in range(cm, cm + life):
        c, k = divmod(m - cm, cycle)
        # 每代 GPU 上市价按 refresh_rate_factor 重置
        # rate_decay is ANNUAL; k is months → use k/12 (P0-0 frequency fix)
        rate = rate0 * (g.get("refresh_rate_factor", 0.8) ** c) * (1 + decay) ** (k / 12.0)
        u = _ramp_utilization(m, cm, steady_u, ramp) if c == 0 else steady_u
        hrs = 730
        revenue[m] = it_mw * 1000 * u * hrs * rate
        mwh = it_mw * pue * 730 * u
        opex[m] = mwh * power_price + it_mw * 1000 * (extra + dc["opex_kw_yr"] / 12)

    for m, amt in gpu_residual_sched:
        revenue[m] += amt  # 旧 GPU 出售收入

    return AssetCase(
        name=name, layer=layer, gen_mw=gen_mw, it_mw=it_mw,
        capex=capex, revenue=revenue, opex=opex, residual=residual,
        notes={"gpu_capex_per_kw_it": g["capex_per_kw_it"], "rate_per_kw_hr": rate0,
               "rate_decay": decay, "refresh_months": cycle,
               "utilization": steady_u},
    )


def build_compute(cfg: dict) -> AssetCase:
    return _build_gpu_layer(cfg, "ComputeCo (GPU Rental)", "L4_Compute", is_ai_factory=False)


def build_ai_factory(cfg: dict) -> AssetCase:
    return _build_gpu_layer(cfg, "AI Factory (Token/GP)", "L5_AI", is_ai_factory=True)


# ---------------------------------------------------------------------------
# WACC / Hurdle（分层贴现率）
# ---------------------------------------------------------------------------

DEFAULT_WACC = {
    "L0_Dev": 0.25,
    "L1_Power": 0.08,
    "L2_Shell": 0.09,
    "L3_CriticalIT": 0.085,
    "L35_Hosting": 0.10,
    "L4_Compute": 0.14,
    "L5_AI": 0.18,
}


# ---------------------------------------------------------------------------
# 统一运行入口：Asset Model
# ---------------------------------------------------------------------------

def run_asset(case: AssetCase, cfg: dict) -> LayerResult:
    tax_cfg = cfg.get("tax", {})
    engine = TaxEngine(rate=tax_cfg.get("rate", 0.23),
                       dep_life_months=tax_cfg.get("dep_life_months", 240),
                       method=tax_cfg.get("method", "straight_line"))
    wacc = cfg.get("wacc", DEFAULT_WACC).get(case.layer, 0.10)

    dep = engine.build_depreciation(case.capex)
    ebitda = case.revenue - case.opex
    at_ebitda = engine.after_tax_ebitda(ebitda, dep)
    # 期末残值（税后简化：按资本利得处理，残值 - 未折旧余额 计税）
    total_dep = dep.sum()
    book = case.capex.sum() - total_dep
    gain = case.residual - max(0.0, book)
    residual_at = case.residual - max(0.0, gain) * engine.rate

    ucf = at_ebitda - case.capex
    ucf[-1] += residual_at

    res = LayerResult(
        name=case.name, layer=case.layer, gen_mw=case.gen_mw, it_mw=case.it_mw,
        capex_total=float(case.capex.sum()), capex_by_month=case.capex.copy(),
        ebitda=ebitda, unlevered_fcf=ucf,
        project_irr=irr_monthly(ucf), project_npv=npv_monthly(wacc, ucf),
        revenue_y1=float(case.revenue[case.months // 2: case.months // 2 + 12].sum()),
        ebitda_y1=float(ebitda[case.months // 2: case.months // 2 + 12].sum()),
        payback_months=payback_months(ucf),
    )
    # 年化报告值改为首个运营年
    cod = int(np.argmax(case.revenue > 0)) if (case.revenue > 0).any() else 0
    if cod > 0:
        res.revenue_y1 = float(case.revenue[cod:cod + 12].sum())
        res.ebitda_y1 = float(ebitda[cod:cod + 12].sum())
    return res


BUILDERS = {
    "power": build_power,
    "dev": build_dev_exit,
    "shell": build_shell,
    "critical_it": build_critical_it,
    "gpu_hosting": build_gpu_hosting,
    "compute": build_compute,
    "ai_factory": build_ai_factory,
}
