"""报告输出：对比表 CSV、气泡图、龙卷风图、蒙特卡洛分布图、Markdown 报告。"""

from __future__ import annotations

import os
from typing import Dict, List

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .core import LayerResult, format_summary_table
from .evaluate import risk_exposure_score, incremental_analysis, three_irr_view
from .risk import MCResult

plt.rcParams["font.family"] = ["DejaVu Sans"]


def bubble_chart(results: List[LayerResult], out_path: str, title: str = "AIDC Value Chain: Capital Intensity vs Return"):
    """核心输出图：X=Sponsor Equity/MW, Y=NPV/Peak Equity, bubble=风险敞口。"""
    fig, ax = plt.subplots(figsize=(11, 7.5))
    for r in results:
        mw = r.it_mw if r.it_mw > 0 else r.gen_mw
        x = r.sponsor_equity / mw / 1e6                      # $M / MW
        y = (r.project_npv / r.peak_equity if r.peak_equity > 0 else 0)
        risk = risk_exposure_score(r.layer)
        size = 300 + risk * 900
        color = plt.cm.RdYlGn(1 - risk / 3.0)
        ax.scatter(x, y, s=size, c=[color], alpha=0.75, edgecolors="k", zorder=3)
        irr = r.equity_irr if r.equity_irr is not None else r.project_irr
        ax.annotate(f"{r.name}\nEqIRR {irr:.1%}" if irr is not None else r.name,
                    (x, y), textcoords="offset points", xytext=(12, 8), fontsize=8.5)
    ax.set_xlabel("Sponsor Equity intensity ($M / MW)")
    ax.set_ylabel("NPV / Peak Sponsor Equity (x)")
    ax.set_title(title)
    ax.grid(alpha=0.3, zorder=0)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def tornado_chart(tor: List[dict], out_path: str, title: str = "Sensitivity Tornado (NPV $M)"):
    rows = [t for t in tor if t.get("npv_swing", 0) > 0][:10]
    if not rows:
        return
    labels = [t["path"] for t in rows][::-1]
    low = [t.get("npv_low", 0) for t in rows][::-1]
    high = [t.get("npv_high", 0) for t in rows][::-1]
    base = low[0]  # placeholder
    fig, ax = plt.subplots(figsize=(10, 0.6 * len(labels) + 2))
    y = np.arange(len(labels))
    for i, (l, h) in enumerate(zip(low, high)):
        ax.barh(i, h - min(l, h), left=min(l, h), color="#4C9BD6")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("NPV ($M), parameter ±15%")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def mc_histogram(mc: MCResult, out_path: str, title: str = "Monte Carlo NPV Distribution"):
    if mc.npv_samples is None or len(mc.npv_samples) == 0:
        return
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.hist(mc.npv_samples / 1e6, bins=40, color="#4C9BD6", alpha=0.8, edgecolor="white")
    for p, c in [(mc.npv_p10, "orange"), (mc.npv_p50, "green"), (mc.npv_p90, "purple")]:
        ax.axvline(p / 1e6, color=c, ls="--", lw=1.5,
                   label=f"{p/1e6:,.0f}")
    ax.axvline(0, color="red", lw=2)
    ax.set_xlabel("Project NPV ($M)")
    ax.set_title(f"{title}\nP(NPV<0)={mc.prob_npv_negative:.1%}  P10/P50/P90 ($M): "
                 f"{mc.npv_p10/1e6:,.0f} / {mc.npv_p50/1e6:,.0f} / {mc.npv_p90/1e6:,.0f}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def write_markdown_report(cfg: dict, results: List[LayerResult], mc: Dict[str, MCResult],
                          out_dir: str, jurisdiction: str) -> str:
    lines = []
    a = lines.append
    a(f"# AIDC 投资价值链评估报告 — {jurisdiction}")
    a("")
    a(f"**基准项目**: {cfg['reference']['gen_mw']:.0f} MW 发电容量, PUE {cfg['reference']['pue']}, "
      f"Critical IT ≈ {cfg['reference']['gen_mw']/cfg['reference']['pue']:.1f} MW")
    a("")
    a("## 1. 七模式统一对比（100 MW Reference Project）")
    a("")
    a("```")
    a(format_summary_table(results))
    a("```")
    a("")
    a("## 2. 增量收益分析（每多投一美元创造多少 NPV）")
    a("")
    inc = incremental_analysis(results)
    a("| From | To | ΔCAPEX $M | ΔNPV $M | ΔReturn | 边际决策 |")
    a("|---|---|---:|---:|---:|---|")
    for r in inc:
        a(f"| {r['From']} | {r['To']} | {r['ΔCAPEX $M']:,.1f} | {r['ΔNPV $M']:,.1f} | "
          f"{r['ΔReturn (ΔNPV/ΔCAPEX)']:.2f} | {r['边际决策']} |"
          if r['ΔReturn (ΔNPV/ΔCAPEX)'] == r['ΔReturn (ΔNPV/ΔCAPEX)'] else
          f"| {r['From']} | {r['To']} | {r['ΔCAPEX $M']:,.1f} | {r['ΔNPV $M']:,.1f} | — | {r['边际决策']} |")
    a("")
    a("## 3. 三个独立 IRR")
    a("")
    t = three_irr_view(results)
    for k, v in t.items():
        a(f"- **{k}**: {v:.1%}" if v is not None else f"- **{k}**: N/A")
    a("")
    a("## 4. 蒙特卡洛风险指标")
    a("")
    a("| Model | P50 NPV $M | P10 NPV $M | P90 NPV $M | P(NPV<0) | P(IRR<hurdle) | 敞口分 |")
    a("|---|---:|---:|---:|---:|---:|---:|")
    from .evaluate import risk_exposure_score
    for r in results:
        m = mc.get(r.layer)
        if m:
            a(f"| {r.name} | {m.npv_p50/1e6:,.1f} | {m.npv_p10/1e6:,.1f} | {m.npv_p90/1e6:,.1f} | "
              f"{m.prob_npv_negative:.1%} | {m.prob_irr_below_hurdle:.1%} | {risk_exposure_score(r.layer):.2f} |")
    a("")
    a("## 5. 输出图表")
    a("")
    a("![bubble](bubble_chart.png)")
    a("")
    for r in results:
        m = mc.get(r.layer)
        if m:
            safe = r.layer.lower()
            a(f"### {r.name}")
            a("")
            a(f"![mc](mc_{safe}.png)")
            a("")
    path = os.path.join(out_dir, "report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def export_csv(results: List[LayerResult], out_dir: str):
    import csv
    path = os.path.join(out_dir, "summary.csv")
    keys = list(results[0].summary().keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in results:
            row = {k: (f"{v:.6f}" if isinstance(v, float) else v) for k, v in r.summary().items()}
            w.writerow(row)
    return path
