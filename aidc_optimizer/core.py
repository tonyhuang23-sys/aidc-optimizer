"""
AIDC Investment Value-Chain Optimizer
核心财务数学引擎：月度现金流、IRR/NPV/MOIC、税收与折旧

设计原则（对应第三十九节）：
- Asset Model 与 Financing Model 严格分离
- 所有层统一换算到 MW 口径（Generation MW / Critical IT MW，PUE 为转换系数）
- 月度频率建模，支持建设期逐月提款、GPU 中期刷新、再融资等时点事件
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# 基础财务数学（月度频率）
# ---------------------------------------------------------------------------

def annuity_factor(monthly_rate: float, n_months: int) -> float:
    """年金现值系数（月度）。"""
    if monthly_rate == 0:
        return n_months
    return (1 - (1 + monthly_rate) ** -n_months) / monthly_rate


def npv_monthly(discount_annual: float, cf: np.ndarray) -> float:
    """月度现金流 NPV，年贴现率转月度复利。cf[0] 为第 0 月。"""
    r_m = (1 + discount_annual) ** (1 / 12) - 1
    n = len(cf)
    t = np.arange(n)
    return float(np.sum(cf / (1 + r_m) ** t))


def irr_monthly(cf: np.ndarray, lo: float = -0.05, hi: float = 0.10) -> Optional[float]:
    """月度现金流 IRR（二分法），返回年化 IRR。失败返回 None。"""
    def f(r):
        t = np.arange(len(cf))
        return float(np.sum(cf / (1 + r) ** t))

    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        fm = f(mid)
        if abs(fm) < 1e-9:
            break
        if flo * fm < 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
    irr_m = (lo + hi) / 2
    return (1 + irr_m) ** 12 - 1


def payback_months(cf: np.ndarray) -> Optional[int]:
    """累计现金流首次转正的月份。"""
    cum = np.cumsum(cf)
    idx = np.argmax(cum > 0)
    if cum[idx] > 0:
        return int(idx)
    return None


# ---------------------------------------------------------------------------
# 税收与折旧（简化：直线折旧 + 亏损结转，可选余额递减 CCA 近似）
# ---------------------------------------------------------------------------

@dataclass
class TaxEngine:
    rate: float = 0.23                    # 综合企业所得税率
    dep_life_months: int = 240            # 税务折旧年限（月）
    method: str = "straight_line"         # straight_line | declining_balance
    db_rate: float = 0.20                 # 余额递减年率（加拿大 CCA 类 8/43 近似）

    def build_depreciation(self, capex_by_month: np.ndarray) -> np.ndarray:
        """返回与 capex_by_month 等长的月度折旧数组（尾部长度=len(capex)）。"""
        n = len(capex_by_month)
        dep = np.zeros(n)
        if self.method == "straight_line":
            rate_m = 1.0 / self.dep_life_months
            for m, c in enumerate(capex_by_month):
                if c > 0:
                    dep[m:] += c * rate_m
        else:  # declining balance（每笔资产池近似独立递减）
            rate_m = 1 - (1 - self.db_rate) ** (1 / 12)
            for m, c in enumerate(capex_by_month):
                if c > 0:
                    remaining = c
                    for k in range(m, n):
                        d = remaining * rate_m
                        dep[k] += d
                        remaining -= d
        return dep

    def after_tax_ebitda(
        self,
        ebitda: np.ndarray,
        depreciation: np.ndarray,
        interest: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """税后净现金流（不含 capex）：EBITDA - tax，含亏损结转。"""
        n = len(ebitda)
        tax = np.zeros(n)
        cfl = 0.0  # 亏损结转
        for m in range(n):
            ded = depreciation[m] + (interest[m] if interest is not None else 0.0)
            taxable = ebitda[m] - ded
            if taxable < 0:
                cfl += -taxable
                continue
            use = min(cfl, taxable)
            cfl -= use
            tax[m] = (taxable - use) * self.rate
        return ebitda - tax


# ---------------------------------------------------------------------------
# 建设期提款曲线
# ---------------------------------------------------------------------------

def s_curve_drawdown(n_months: int, shape: float = 2.5) -> np.ndarray:
    """Beta-ish S 曲线月度资本开支权重。"""
    x = (np.arange(1, n_months + 1) - 0.5) / n_months
    w = x ** (shape - 1) * (1 - x) ** (shape - 1)
    return w / w.sum()


def uniform_drawdown(n_months: int) -> np.ndarray:
    return np.full(n_months, 1.0 / n_months)


# ---------------------------------------------------------------------------
# 统一层级结果结构
# ---------------------------------------------------------------------------

@dataclass
class LayerResult:
    """单个价值链层级的完整计算结果（Asset + Financing 双层）。"""
    name: str
    layer: str                                   # L1_Power / L0_Dev / L2_Shell / L3_CriticalIT / L35_GPUHosting / L4_ComputeCo / L5_AIFactory
    gen_mw: float = 0.0
    it_mw: float = 0.0
    # ---- Asset Model ----
    capex_total: float = 0.0                    # 全部资本投入（不含 IDC）
    capex_by_month: np.ndarray = field(default_factory=lambda: np.zeros(1))
    ebitda: np.ndarray = field(default_factory=lambda: np.zeros(1))
    unlevered_fcf: np.ndarray = field(default_factory=lambda: np.zeros(1))
    project_irr: Optional[float] = None
    project_npv: float = 0.0
    revenue_y1: float = 0.0
    ebitda_y1: float = 0.0
    payback_months: Optional[int] = None
    # ---- Financing Model ----
    debt_amount: float = 0.0
    idc: float = 0.0
    sponsor_equity: float = 0.0
    peak_equity: float = 0.0                    # 峰值占用（含未回收）
    customer_capital: float = 0.0
    levered_fcf_equity: np.ndarray = field(default_factory=lambda: np.zeros(1))
    equity_irr: Optional[float] = None
    moic: float = 0.0
    min_dscr: Optional[float] = None
    avg_dscr: Optional[float] = None
    llcr: Optional[float] = None
    # ---- 单位指标 ----
    def per_mw(self, key: str, use_it: bool = False) -> float:
        base = self.it_mw if (use_it and self.it_mw > 0) else (self.gen_mw or 1.0)
        return float(getattr(self, key)) / base

    def summary(self) -> Dict[str, object]:
        mw = self.it_mw if self.it_mw > 0 else self.gen_mw
        return {
            "Model": self.name,
            "Layer": self.layer,
            "MW(IT/Gen)": f"{self.it_mw:.0f}/{self.gen_mw:.0f}",
            "CAPEX $M": self.capex_total / 1e6,
            "CAPEX $/kW": self.capex_total / (mw * 1000),
            "Equity $M": self.sponsor_equity / 1e6,
            "Equity $/kW": self.sponsor_equity / (mw * 1000),
            "Rev Y1 $/MW-yr": self.revenue_y1 / mw / 1e6,
            "EBITDA Y1 $/MW-yr": self.ebitda_y1 / mw / 1e6,
            "Project IRR": self.project_irr,
            "Equity IRR": self.equity_irr,
            "NPV $M": self.project_npv / 1e6,
            "NPV $/MW": self.project_npv / mw / 1e6,
            "NPV/Equity": (self.project_npv / self.sponsor_equity) if self.sponsor_equity > 0 else np.nan,
            "MOIC": self.moic,
            "Min DSCR": self.min_dscr,
            "Payback (mo)": self.payback_months,
        }


def _fmt_pct(v) -> str:
    return f"{v:.1%}" if v is not None and v == v else "—"


def _fmt_num(v, nd: int = 1) -> str:
    return f"{v:,.{nd}f}" if v is not None and v == v else "—"


def format_summary_table(results: List[LayerResult]) -> str:
    """统一对比表（纯字符串，不依赖 pandas）。"""
    rows = [r.summary() for r in results]
    if not rows:
        return ""
    headers = list(rows[0].keys())
    formatted = []
    for row in rows:
        out = dict(row)
        out["Project IRR"] = _fmt_pct(row["Project IRR"])
        out["Equity IRR"] = _fmt_pct(row["Equity IRR"])
        out["MOIC"] = _fmt_pct(row["MOIC"])
        for c in ["CAPEX $M", "Equity $M", "Rev Y1 $/MW-yr", "EBITDA Y1 $/MW-yr", "NPV $M", "NPV $/MW"]:
            out[c] = _fmt_num(row[c], 1)
        for c in ["CAPEX $/kW", "Equity $/kW"]:
            out[c] = _fmt_num(row[c], 0)
        out["NPV/Equity"] = _fmt_num(row["NPV/Equity"], 2)
        out["Min DSCR"] = _fmt_num(row["Min DSCR"], 2)
        pb = row["Payback (mo)"]
        out["Payback (mo)"] = str(int(pb)) if pb is not None and pb == pb else "—"
        formatted.append(out)
    widths = {h: max(len(h), *(len(str(r[h])) for r in formatted)) for h in headers}
    line = " ".join(h.ljust(widths[h]) for h in headers)
    body = [" ".join(str(r[h]).rjust(widths[h]) for h in headers) for r in formatted]
    return "\n".join([line, *body])
