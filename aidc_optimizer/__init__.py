"""AIDC Investment Value-Chain Optimizer — 北美(Alberta/Texas)数据中心投资价值评估框架。"""

__version__ = "1.0.0"

from .core import LayerResult, npv_monthly, irr_monthly
from .models import BUILDERS, run_asset, DEFAULT_WACC
from .financing import DebtInputs, apply_financing
from .risk import run_full_pipeline, monte_carlo, tornado
from .evaluate import (five_dimension_table, incremental_analysis, three_irr_view,
                       RISK_MATRIX, RISK_OWNER)
from .report import (bubble_chart, mc_histogram, tornado_chart,
                     write_markdown_report, export_csv)

__all__ = [
    "LayerResult", "BUILDERS", "run_asset", "run_full_pipeline",
    "monte_carlo", "tornado", "DebtInputs", "apply_financing",
    "five_dimension_table", "incremental_analysis", "three_irr_view",
    "RISK_MATRIX", "RISK_OWNER", "bubble_chart", "mc_histogram",
    "tornado_chart", "write_markdown_report", "export_csv", "DEFAULT_WACC",
]
