# 面向AI基础设施的价值链投资评估模型：经济角色、投资时点、资产栈、合约结构与资本结构共同决定的风险调整资本配置框架

## A Value-Chain Investment Evaluation Model for AI Infrastructure

**作者**: WNT Energy 技术研究组  
**日期**: 2026年8月  
**状态**: 工作论文 **v5.3**（频率修复后全量重跑版）  
**版本记录**: v5.0 Investment Vintage；v5.1 P0 审计；v5.2 确认并修复 Annual/Monthly Frequency Bug。**v5.3 在频率修复路径上完成 Certainty Bridge、Strategic/Contracted 信用 MC（list/bulk/downside）、Merchant Vintage、模式对照表；并更新 reproduce 黄金结果（L4 基准 NPV 约 −$0.96B，IRASR 约 −0.94）。** 代码：`research_v5_2_rerun.py`；结果：`research_outputs/v5_2_rerun/`；黄金：`expected_outputs/alberta.json`。

---

## 摘要

v5.2 修复了 GPU 年化衰减被误作月化复利的 P0-0 Bug。v5.3 在**同一修复路径**上重跑全部关键表，形成可对外引用的统一数字：

**合同：** C1 Fixed ToP @ list $9.36 → NPV **+$4.76B**；真正 −6%/**年** step-down（C2）→ **+$3.84B**（非 −$0.35B）；C1−C2 锁价溢价约 **+$0.92B**（非 +$5.1B）。bulk $7.02 下 C1 **+$2.88B**、C2 **+$2.20B**，均显著高于 L3（+$0.71B）。

**Merchant Forward：** $7.80 中位租金、−22%/**年** → NPV **+$0.08B**（修复前 −$3.17B）；市场 MC CE 约 **−$0.68B**、P(loss)≈53%——点估计接近盈亏平衡，但风险调整后仍弱于 L3。Spot $4.25 仍深负；Dedicated $9.36 可持续租金下可为正。

**Strategic / Contracted 风险调整（信用 MC，N=2000）：**

| 情景 | E(NPV) | CE-NPV | 观察损失率 (Wilson 95% CI) |
|---|---:|---:|---|
| L4-S list $9.36 | +$4.85B | **+$3.70B** | 0/2000；上界 0.19% |
| L4-S bulk $7.02 | +$2.95B | **+$2.10B** | 0.20% [0.08–0.51%] |
| L4-S downside $5.62 | +$1.81B | **+$1.14B** | 1.30% [0.89–1.90%] |
| L4-C bulk $7.02 | +$2.53B | **+$1.69B** | 0.35% [0.17–0.72%] |
| L3（对照 CE） | — | **+$0.51B** | 0/1500 |

**结论（数据驱动，不维护旧结论）：**  
（1）频率修复后，温和 step-down **不摧毁** Contracted 价值；真正危险的是快速重定价与合同不可得。  
（2）Merchant Forward 在公开中位附近**脆弱地**接近盈亏平衡，但 CE 与高 Peak Equity 使其仍非默认策略。  
（3）在 bulk 成交价与信用冲击下，L4-C/S 的 CE 仍 **>$1.1B–$2.1B**，高于 L3 的 +$0.51B——前提是合同已落实（Type B/C），而非 Type A 无合同 Sponsor。  
（4）reproduce 黄金结果已同步：基准 L4 NPV 约 **−$0.96B**（yaml $3.0/IT-kW-hr 路径），IRASR 约 **−0.94**。

**关键词**: frequency fix；Certainty Bridge；credit MC；bulk contract rate；Merchant Forward；IRASR

---

## Abstract

*(Condensed.)* v5.3 re-runs all headline tables on the corrected annual→monthly GPU decay path. Mild −6%/yr step-down contracts remain strongly positive (+$3.84B); C1−C2 lock-in premium is ~$0.92B not $5.1B. Merchant at $7.80/−22%/yr is ~+$0.08B NPV but market-MC CE ~−$0.68B. Strategic/Contracted credit MC at bulk $7.02 yields CE ~+$2.10B / +$1.69B vs L3 CE ~+$0.51B, with non-zero but low loss rates. Golden outputs updated (baseline L4 NPV ~−$0.96B; IRASR ~−0.94). Framework unchanged: Optimal layer = f(Role, Vintage, Stack, Contract, Capital, Market, access probability).

---

## 1 本轮范围

v5.3 **不扩张框架**，只做频率修复后的全量重跑与数字统一：

1. Certainty Bridge（确定性逐步桥）  
2. 模式级市场 MC（n=200）  
3. Strategic/Contracted 信用 MC（N=2000；list / bulk / downside）  
4. Merchant Vintage（Greenfield + GPU-only）  
5. Headline 对照表  
6. `reproduce.py` 黄金结果更新  

沿用 v5.1/v5.2 已确认的：B200 CAPEX 统一 $60k/GPU、Backstop 仅 residual unsold、list 价为上界、EconCap/Access 框架。

---

## 2 频率修复（回顾）

| 项目 | 内容 |
|---|---|
| Bug | `(1+g_annual)**month` 把年化当月化 |
| Fix | `(1+g_annual)**(month/12)` |
| 文件 | `aidc_optimizer/models.py`、`research_l4.py` |
| 未受影响 | 电力/租约 escalator（本就用 `yr=months/12`） |

---

## 3 结果

### 3.1 Certainty Bridge（频率修复后）

| 步骤 | NPV $M | ΔNPV $M | Peak Equity $M |
|---|---:|---:|---:|
| 0 Merchant $7.80 −22%/yr | +78 | — | 2,362 |
| 1 + Dedicated list $9.36 −22%/yr | +826 | +747 | 2,344 |
| **2 + 5Y Fixed ToP $9.36** | **+4,761** | **+3,936** | 2,206 |
| 3 + Contracted 融资 lev55/kd7 | +4,761 | 0 | 1,501 |
| 4 + Prepay ~$150M | +4,761 | 0 | 1,351 |
| 5 + Backstop residual-only | +5,285 | +524 | 1,317 |
| 6 + GPU-backed lev70/kd5.9 | +5,285 | 0 | **438** |
| 7a Bulk $7.02 Fixed C | +2,885 | — | 1,404 |
| 7b Bulk $7.02 Fixed S | +3,278 | — | 500 |
| 8 C2 −6%/yr list $9.36 | +3,844 | — | 1,351 |
| 9 C2 −6%/yr bulk $7.02 | +2,197 | — | 1,404 |

**解读：**

- 主跳跃仍是 **Fixed ToP**（步骤 2，约 +$3.9B），不是 list 价上调（步骤 1，约 +$0.7B）。  
- 融资/预付 **不改 Project NPV**，只压 Peak Equity（2.2B→0.44B）——资本效率故事保留。  
- C2 温和 step-down 在 list/bulk 下均为 **+$2.2B–$3.8B**，不再是“轻微降价即摧毁合同”。

### 3.2 模式对照 + 市场 MC

| 模式 | 确定性 NPV $M | 市场 MC CE $M | 市场 MC P(loss) |
|---|---:|---:|---:|
| L4-M $7.80 −22%/yr | +78 | **−676** | **53%** |
| L4-C Fixed list $9.36 | +4,761 | +3,503 | 0%* |
| L4-C Fixed bulk $7.02 | +2,885 | +1,942 | 0%* |
| L4-C Step −6%/yr bulk $7.02 | +2,197 | +1,369 | 0%* |
| L4-S Fixed list $9.36 | +5,285 | +3,939 | 0%* |
| L4-S Fixed bulk $7.02 | +3,278 | +2,268 | 0%* |

\*市场 MC 主要扰动租金/利用率；合同已锁价锁量时损失率接近 0 是预期行为。信用风险见下一节。

**关键点：** Merchant 点估计虽接近盈亏平衡，但 **CE 为负、损失率约一半**——不得把 +$78M 写成“Merchant 已成立”。

### 3.3 信用 / 合同 MC（N=2000）— 推荐 Base 带

| 情景 | E(NPV) $M | CE-NPV $M | 损失 | Wilson 95% CI |
|---|---:|---:|---:|---|
| L4-S list $9.36 | 4,846 | **3,703** | 0/2000 | [0, 0.19%] |
| **L4-S bulk $7.02** | 2,950 | **2,098** | 4/2000 (0.20%) | [0.08%, 0.51%] |
| L4-S downside $5.62 | 1,815 | **1,137** | 26/2000 (1.30%) | [0.89%, 1.90%] |
| **L4-C bulk $7.02** | 2,528 | **1,693** | 7/2000 (0.35%) | [0.17%, 0.72%] |
| L3 CE（对照） | — | **505** | 0/1500 | [0, 0.26%] |

冲击设定（情景，非评级校准）：客户违约路径约 3–4%；价格 haircut / reset；backstop 失效约 8%；融资冻结约 10–12%。

**含义：**

- bulk 下 L4-S CE **约 +$2.1B**、L4-C CE **约 +$1.7B**，均 **>$1B 且高于 L3 CE**。  
- 损失率 **非零**；list 上界下观察为 0，但 Wilson 上界仍 >0——不得写“0% 风险”。  
- downside $5.62 时 CE 仍约 +$1.1B，但损失率升至约 1.3%。

### 3.4 Merchant Vintage（频率修复后）

| Vintage | 栈 | 入场 $/GPUh | NPV $M | IRR |
|---|---|---:|---:|---:|
| H100-2023 | Greenfield | 4.50 | −229 | 12.4% |
| H100-2024 | Greenfield | 3.80 | −749 | 6.1% |
| H100-2025 | Greenfield | 2.80 | −1,503 | −4.6% |
| H100-2026F | Greenfield | 3.20 | −1,531 | −6.9% |
| B200-2026F | Greenfield | 7.80 | +78 | 16.0% |
| H100-2023 | GPU-only | 4.50 | **+360** | 20.6% |
| H100-2024 | GPU-only | 3.80 | −160 | 12.4% |
| B200-2026F | GPU-only | 7.80 | **+667** | 26.5% |
| B200-2026F dedicated | GPU-only | 9.36 | **+1,415** | 39.8% |

**解读：**

- 早期 H100 在 **GPU-only（电力/建筑沉没）** 下可为正；全栈绿地仍难。  
- **Historical ≠ Forward** 与 **栈依赖** 同时成立。  
- 租金路径仍为结构假设（置信度中等）；不得写成“2023 Merchant 一定暴利”。

### 3.5 Headline 总表（v5.3 对外引用）

| 模式 | NPV $M | CE $M | Peak $M | 备注 |
|---|---:|---:|---:|---|
| L3 Critical IT | +707 | +505 | 317 | Structural sweet spot |
| L4-M $7.80 −22%/yr | +78 | −676* | 2,362 | 点估计≈BE；CE 弱 |
| L4-C Fixed list $9.36 | +4,761 | +3,503* | 1,351 | 上界 |
| **L4-C Fixed bulk $7.02** | **+2,885** | **+1,693†** | 1,404 | **推荐 Base** |
| L4-C Step −6%/yr bulk $7.02 | +2,197 | +1,369* | 1,404 | 温和降价仍 > L3 |
| L4-S Fixed list $9.36 | +5,285 | +3,703† | 438 | 上界 |
| **L4-S Fixed bulk $7.02** | **+3,278** | **+2,098†** | 500 | **推荐 Base** |
| L4-S downside $5.62 | +2,077 | +1,137† | 537 | 压力 |

\*市场 MC CE  †信用/合同 MC CE

### 3.6 reproduce 黄金结果（已更新）

| 项 | 频率修复前 | v5.3 黄金 |
|---|---:|---:|
| 基准 L4 NPV（yaml $3.0/IT-kW-hr） | 约 −$3,351M | **约 −$964M** |
| IRASR (L3→L4 短缺) | 约 −5.76 | **约 −0.94** |
| L3 CE | +505 | +505（不变） |

```bash
python reproduce.py run     # 重算 expected_outputs/alberta.json
python reproduce.py check   # 应 exit 0
```

---

## 4 讨论

### 4.1 三层结论强度

1. **硬结论（频率修复后稳健）**  
   - 年化参数必须按月转换。  
   - 温和 step-down 不摧毁 C；快速重定价才显著侵蚀。  
   - Fixed ToP 仍是最大单步价值来源。  
   - 融资压 Peak、不造 Project NPV。

2. **条件结论（依赖合同可得与 bulk 价）**  
   - bulk $7.02 下 C/S 的 CE 仍高于 L3。  
   - Type A 无合同 Sponsor 的 ex-ante EV 仍应默认 L3。

3. **仍待加强**  
   - bulk volume factor 需交易反推锚定。  
   - 信用 MC 的 PD/LGD 需评级校准。  
   - EconCap 仍为 prototype。  
   - Historical 租金路径需 realized 数据。

### 4.2 与“过去为何赚钱”的闭合

频率 bug 把 −22%/年算成约 −95%/年，是 Merchant 系统性巨亏的主因之一。修复后：中位租金附近脆弱平衡 + GPU-only/早期 Vintage 可为正，与产业 anecdotal 证据同向，同时 **不** 支持“今天无合同全栈新建 GPU 是默认最优”。

### 4.3 六维函数（不变）

$$\mathrm{Optimal\ Layer}=f(\mathrm{Role},\ \mathrm{Vintage},\ \mathrm{Stack},\ \mathrm{Contract},\ \mathrm{Capital},\ \mathrm{Market},\ p_{\mathrm{access}})$$

---

## 5 结论

**v5.3 一句话：**

> 在正确的年化衰减下，Merchant Forward 接近盈亏平衡但风险调整仍弱；温和 step-down 的 Contracted 与 bulk 情景下的 Strategic 在信用 MC 后 CE 仍显著高于 L3——前提是合同已落实。锁价溢价约 $0.9B 量级，不是 $5B 神话。黄金结果已与修复后代码对齐。

**对外引用请优先使用：**

- 合同/模式：§3.5 Headline 表  
- 风险调整：§3.3 信用 MC（bulk $7.02）  
- 复现：`python reproduce.py check`  
- 明细：`research_outputs/v5_2_rerun/`

---

## 附录 A — 产出清单

| 文件 | 内容 |
|---|---|
| `research_outputs/v5_2_rerun/certainty_bridge_fixed.csv` | 逐步桥 |
| `research_outputs/v5_2_rerun/mode_market_mc.csv` | 模式市场 MC |
| `research_outputs/v5_2_rerun/strategic_credit_mc_fixed.csv` | 信用 MC list/bulk/downside + C bulk |
| `research_outputs/v5_2_rerun/merchant_vintage_fixed.csv` | Vintage |
| `research_outputs/v5_2_rerun/headline_fixed.csv` | Headline |
| `research_outputs/v5_2_rerun/rerun_summary.json` | 摘要 |
| `research_outputs/v5_2_freq_fix/v5_2_core_results.csv` | 核心对照 |
| `expected_outputs/alberta.json` | 黄金结果（已更新） |

## 附录 B — 复现

```bash
cd aidc-optimizer
python research_v5_2_rerun.py    # 全量重跑 v5.3 表
python reproduce.py run          # 更新黄金
python reproduce.py check        # 校验
```

**模型**：`https://github.com/tonyhuang23-sys/aidc-optimizer`  
**利益声明 / AI 披露**：同前；v5.3 数字以 `research_outputs/v5_2_rerun/` 与更新后黄金文件为准。
