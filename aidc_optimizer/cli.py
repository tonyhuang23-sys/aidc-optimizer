"""
CLI 入口。

用法:
  python -m aidc_optimizer --config configs/alberta.yaml --mc 300 --out results/alberta
  python -m aidc_optimizer --config configs/texas.yaml --case critical_it
  python -m aidc_optimizer --config configs/alberta.yaml --set dc.ready_rent_kw_mo=180 --case critical_it

项目评估时：复制 configs/project_template.yaml，改 reference/power/dc/gpu 参数后运行。
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import yaml

from .models import BUILDERS, DEFAULT_WACC
from .risk import run_full_pipeline, monte_carlo, tornado
from .evaluate import five_dimension_table, incremental_analysis, three_irr_view
from .report import bubble_chart, mc_histogram, tornado_chart, write_markdown_report, export_csv


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def apply_overrides(cfg: dict, overrides: list) -> dict:
    import copy
    cfg = copy.deepcopy(cfg)
    for ov in overrides or []:
        if "=" not in ov:
            raise ValueError(f"--set 需要 path=value 格式: {ov}")
        path, val = ov.split("=", 1)
        cur = cfg
        keys = path.split(".")
        for k in keys[:-1]:
            cur = cur.setdefault(k, {})
        try:
            cur[keys[-1]] = json.loads(val)
        except json.JSONDecodeError:
            cur[keys[-1]] = val
    return cfg


def main(argv=None):
    ap = argparse.ArgumentParser(description="AIDC 投资价值链评估引擎 (Alberta/Texas)")
    ap.add_argument("--config", required=True, help="YAML 参数包路径")
    ap.add_argument("--case", default="all",
                    choices=list(BUILDERS.keys()) + ["all"],
                    help="单一模式或全部七模式")
    ap.add_argument("--mc", type=int, default=0, help="蒙特卡洛模拟次数(0=跳过)")
    ap.add_argument("--tornado", action="store_true", help="输出龙卷风敏感性")
    ap.add_argument("--set", nargs="*", help="参数覆盖: path=value")
    ap.add_argument("--out", default=None, help="输出目录")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    cfg = apply_overrides(cfg, getattr(args, "set", None))
    jurisdiction = cfg.get("jurisdiction", "Custom")

    cases = list(BUILDERS.keys()) if args.case == "all" else [args.case]
    print(f"=== AIDC Value-Chain Optimizer | {jurisdiction} | "
          f"{cfg['reference']['gen_mw']:.0f} MW gen / PUE {cfg['reference']['pue']} ===\n")

    results, mc_results = [], {}
    for key in cases:
        r = run_full_pipeline(cfg, key)
        results.append(r)
        mc_results[r.layer] = None

    from .core import format_summary_table
    print(format_summary_table(results))
    print()

    # 三个 IRR
    if len(results) > 1:
        print("三个独立 IRR:")
        for k, v in three_irr_view(results).items():
            print(f"  {k}: {v:.1%}" if v is not None else f"  {k}: N/A")
        print()
        print("增量收益分析:")
        for row in incremental_analysis(results):
            dr = row["ΔReturn (ΔNPV/ΔCAPEX)"]
            print(f"  {row['From']} → {row['To']}: ΔCAPEX ${row['ΔCAPEX $M']:,.0f}M, "
                  f"ΔNPV ${row['ΔNPV $M']:,.0f}M, ΔReturn={dr:.2f} [{row['边际决策']}]"
                  if dr == dr else
                  f"  {row['From']} → {row['To']}: ΔCAPEX ${row['ΔCAPEX $M']:,.0f}M, ΔNPV ${row['ΔNPV $M']:,.0f}M")
        print()

    out_dir = args.out
    if args.mc > 0:
        print(f"蒙特卡洛 x{args.mc} ...")
        for key in cases:
            layer = BUILDERS[key](cfg).layer
            m = monte_carlo(cfg, key, n_sims=args.mc)
            mc_results[layer] = m
            print(f"  {key:14s} P50 NPV ${m.npv_p50/1e6:,.1f}M  P10 ${m.npv_p10/1e6:,.1f}M  "
                  f"P(NPV<0)={m.prob_npv_negative:.1%}  P(IRR<{m.hurdle:.0%})={m.prob_irr_below_hurdle:.1%}")
        print()

    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        export_csv(results, out_dir)
        if len(results) > 1:
            bubble_chart(results, os.path.join(out_dir, "bubble_chart.png"),
                         title=f"{jurisdiction} — Capital Intensity vs Return (bubble=Risk)")
        for r in results:
            m = mc_results.get(r.layer)
            if m:
                mc_histogram(m, os.path.join(out_dir, f"mc_{r.layer.lower()}.png"), title=r.name)
        if args.tornado and cases:
            for key in cases:
                layer = BUILDERS[key](cfg).layer
                t = tornado(cfg, key)
                if t:
                    tornado_chart(t, os.path.join(out_dir, f"tornado_{layer.lower()}.png"),
                                  title=f"{key} — NPV Sensitivity")
        if len(results) > 1:
            write_markdown_report(cfg, results, mc_results, out_dir, jurisdiction)
        print(f"输出已保存: {os.path.abspath(out_dir)}")
    return results


if __name__ == "__main__":
    main()
