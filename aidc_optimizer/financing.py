"""
融资模型

能力：
- 建设期逐月债务提取（pro-rata）+ IDC 资本化 + 承诺费
- 摊还：straight_line / mortgage / sculpted(DSCR目标) / bullet
- DSCR 逐月计算、Min/Avg DSCR、LLCR
- Cash sweep 提前还款
- Customer-backed Capital（客户预付/定金，降低 Sponsor Equity）
- 再融资模块（COD 后按退出杠杆释放股本，Capital Recycling）
- 输出 Equity IRR / MOIC / Peak Sponsor Equity

债务期限约束：Debt Tenor ≤ 资产经济寿命，校验由 evaluate 层完成。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .core import TaxEngine, annuity_factor, irr_monthly, npv_monthly
from .models import AssetCase


@dataclass
class DebtInputs:
    leverage: float = 0.6                 # Loan-to-Cost
    rate: float = 0.065                   # 年利率
    tenor_months: int = 240               # 运营期摊还期限
    amort: str = "sculpted"               # sculpted|straight_line|mortgage|bullet
    target_dscr: float = 1.35
    min_dscr_covenant: float = 1.20
    commitment_fee: float = 0.004         # 年化，未提取额
    upfront_fee: float = 0.01             # 一次性，按承诺额
    cash_sweep: float = 0.50              # 超额现金流扫仓比例
    dsra_months: int = 6                  # 债务储备（从首笔分配中扣留）
    refi_enable: bool = False
    refi_month: int = 0                   # COD 后月数
    refi_exit_multiple: float = 0.0       # Net Debt/EBITDA
    refi_rate: float = 0.06
    refi_fee: float = 0.01


@dataclass
class FinancingResult:
    debt_amount: float = 0.0
    idc: float = 0.0
    fees: float = 0.0
    sponsor_equity: float = 0.0
    peak_equity: float = 0.0
    customer_capital: float = 0.0
    equity_cf: np.ndarray = None
    equity_irr: Optional[float] = None
    moic: float = 0.0
    min_dscr: Optional[float] = None
    avg_dscr: Optional[float] = None
    llcr: Optional[float] = None
    refi_release: float = 0.0
    debt_outstanding_at_end: float = 0.0


def apply_financing(
    case: AssetCase,
    debt_in: DebtInputs,
    tax: TaxEngine,
    customer_capital: float = 0.0,
    wacc_for_llcr: float = 0.08,
) -> FinancingResult:
    n = case.months
    capex = case.capex
    cod = int(np.argmax(case.revenue > 0)) if (case.revenue > 0).any() else 0
    if cod == 0 and case.layer != "L0_Dev":
        cod = n  # 无运营期（纯开发退出）

    r_m = (1 + debt_in.rate) ** (1 / 12) - 1
    commit = debt_in.leverage * capex.sum()
    upfront = debt_in.upfront_fee * commit

    # ---------- 建设期：逐月提款 + IDC 资本化 + 承诺费 ----------
    debt_balance = 0.0
    idc = 0.0
    debt_draw = np.zeros(n)
    equity_draw = np.zeros(n)
    fee_cash = np.zeros(n)
    drawn_so_far = 0.0

    for m in range(min(cod, n)):
        d = debt_in.leverage * capex[m]
        debt_draw[m] = d
        drawn_so_far += d
        interest_m = debt_balance * r_m
        idc += interest_m
        debt_balance += d + interest_m
        # 承诺费（未提取部分），由股本支付
        fee_cash[m] = (commit - drawn_so_far) * debt_in.commitment_fee / 12
    term_debt = debt_balance + idc * 0  # idc 已入余额
    term_debt = debt_balance

    # ---------- Uses & Sources ----------
    uses = capex.sum() + fee_cash.sum() + upfront
    sources = term_debt + customer_capital
    sponsor_equity_total = uses - sources
    # 股本提取：非债务部分逐月 + 客户资本在 COD 到账（冲减前期投入）
    equity_gross = np.zeros(n)
    for m in range(min(cod, n)):
        equity_gross[m] = (1 - debt_in.leverage) * capex[m] + fee_cash[m]
    equity_gross[0] += upfront
    if customer_capital > 0:
        equity_gross[min(cod, n - 1)] -= customer_capital

    # ---------- 摊还计划 ----------
    op_months = max(0, n - cod)
    tenor = min(debt_in.tenor_months, op_months)
    principal_sched = np.zeros(n)
    if tenor > 0 and term_debt > 0:
        if debt_in.amort == "straight_line":
            pay = np.full(tenor, term_debt / tenor)
        elif debt_in.amort == "mortgage":
            ds = term_debt / annuity_factor(r_m, tenor)
            pay = np.zeros(tenor)
            bal = term_debt
            for k in range(tenor):
                p = ds - bal * r_m
                pay[k] = p
                bal -= p
        elif debt_in.amort == "bullet":
            pay = np.zeros(tenor)
            pay[-1] = term_debt
        else:  # sculpted：由 CFADS/target_dscr 决定，保底 tenor 内还清
            ebitda = case.revenue - case.opex
            dep = tax.build_depreciation(capex)
            pay = np.zeros(tenor)
            bal = term_debt
            for k in range(tenor):
                m = cod + k
                interest = bal * r_m
                at = tax.after_tax_ebitda(ebitda[m:m + 1], dep[m:m + 1],
                                          np.array([interest]))[0]
                p = max(0.0, at / debt_in.target_dscr - interest)
                # 确保末期前还清
                rem = tenor - k
                if rem == 1:
                    p = bal
                else:
                    p = min(p, bal)
                pay[k] = p
                bal -= p
        principal_sched[cod:cod + tenor] = pay

    # ---------- 运营期现金流 ----------
    ebitda = case.revenue - case.opex
    dep = tax.build_depreciation(capex)
    interest_arr = np.zeros(n)
    principal_arr = principal_sched.copy()
    balance = term_debt
    dscr_list = []
    levered_cf = np.zeros(n)
    swept = np.zeros(n)

    for m in range(n):
        interest = balance * r_m
        interest_arr[m] = interest
        principal = principal_arr[m]
        if m >= cod and (case.revenue[m] > 0 or m == n - 1):
            at = tax.after_tax_ebitda(ebitda[m:m + 1], dep[m:m + 1], np.array([interest]))[0]
            cfads = at
            ds = interest + principal
            if ds > 0:
                dscr_list.append(cfads / ds)
                # cash sweep：DSCR 高于 covenant+buffer 的部分扫仓
                buffer_ds = ds * (debt_in.min_dscr_covenant + 0.25)
                if cfads > buffer_ds and balance > 0:
                    sweep = debt_in.cash_sweep * min(cfads - buffer_ds, balance)
                    swept[m] = sweep
                    principal += sweep
            levered_cf[m] = cfads - interest - principal
            balance -= principal
        else:
            # 建设期股本投入
            levered_cf[m] = 0.0
            balance -= 0

    equity_cf = -equity_gross.copy()
    equity_cf[cod:] += levered_cf[cod:]
    # 期末残值归属股本（扣除剩余债务）
    residual = case.residual
    equity_cf[-1] += residual - max(0.0, balance)

    # ---------- 再融资（Capital Recycling） ----------
    refi_release = 0.0
    if debt_in.refi_enable and debt_in.refi_exit_multiple > 0 and cod < n:
        rm = cod + debt_in.refi_month
        if rm < n:
            ebitda_ann = float(np.mean(ebitda[max(cod, rm - 12):rm]) * 12) if rm > cod else 0
            new_debt = debt_in.refi_exit_multiple * ebitda_ann
            if new_debt > balance:
                refi_release = (new_debt - balance) * (1 - debt_in.refi_fee)
                equity_cf[rm] += refi_release

    peak_equity = float(-np.min(np.cumsum(equity_cf))) if len(equity_cf) else 0.0
    invested = float(-np.minimum(equity_cf, 0).sum())
    returned = float(np.maximum(equity_cf, 0).sum())

    # LLCR：运营期 CFADS 现值 / COD 时点债务
    llcr = None
    if term_debt > 0 and cod < n:
        cfads_arr = levered_cf[cod:] + 0  # 近似：levered_cf + debt service
        ds_arr = interest_arr[cod:] + principal_arr[cod:] + swept[cod:]
        cfads_arr = levered_cf[cod:] + ds_arr
        disc = npv_monthly(wacc_for_llcr, cfads_arr)
        llcr = disc / term_debt if term_debt > 0 else None

    dscr_arr = np.array(dscr_list) if dscr_list else None
    return FinancingResult(
        debt_amount=term_debt,
        idc=idc,
        fees=float(fee_cash.sum() + upfront),
        sponsor_equity=sponsor_equity_total,
        peak_equity=peak_equity,
        customer_capital=customer_capital,
        equity_cf=equity_cf,
        equity_irr=irr_monthly(equity_cf),
        moic=(returned / invested) if invested > 0 else 0.0,
        min_dscr=float(np.nanmin(dscr_arr)) if dscr_arr is not None and len(dscr_arr) else None,
        avg_dscr=float(np.nanmean(dscr_arr)) if dscr_arr is not None and len(dscr_arr) else None,
        llcr=llcr,
        refi_release=refi_release,
        debt_outstanding_at_end=float(max(0.0, balance)),
    )
