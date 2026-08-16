# 面向AI基础设施的价值链投资评估模型：经济角色、投资时点、资产栈、合约结构与资本结构共同决定的风险调整资本配置框架

## A Value-Chain Investment Evaluation Model for AI Infrastructure: A Risk-Adjusted Capital Allocation Framework Jointly Determined by Economic Role, Investment Vintage, Asset Stack, Contract Structure and Capital Structure

**作者**: WNT Energy 技术研究组  
**日期**: 2026年8月  
**状态**: 工作论文 **v5.1**（审计修订版）  
**版本记录**: v1–v3.3 框架与复现；v4.0 L4 三模式翻转；v5.0 Investment Vintage × Certainty Bridge。**v5.1 依《AIDC_v5_1下一步修正与检查完整指令》做 P0/P1 现金流级审计——不扩张框架，集中校验决定 Headline 的合同、CAPEX、Backstop、风险资本与可得性口径。** 代码：`research_v5_1_audit.py` + `research_outputs/v5_1/`。

---

## 摘要

v5.0 建立了六维决策函数与 L4-M/C/S 结构，但若干翻转结论对关键参数过于敏感。v5.1 对五项 P0 审计后修正 Headline：

**（1）C1 vs C2 现金流数学通过。** 5Y Fixed（C1）NPV +$4.76B 与 5Y Step-down −6%/年（C2）−$0.35B 的约 $5.1B 差异，可由逐年价格路径解释：C2 到第5年有效租金衰减至约 $0.35/GPUh，累计收入差 $12.1B，收入差的现值约 $6.5B。固定价 take-or-pay 的价值应归因于**价格路径锁定**，而非笼统的“长约”。

**（2）公开 Dedicated $9.36/GPUh 不得作为 4.3 万卡、5 年批量合同的 Base Case。** 该价隐含 TCV/GPU ≈ $389k、TCV/Compute-CAPEX ≈ **6.5×**，对 hyperscale 批量采购不现实。引入 Realized Contract Rate = List × Volume × Term × Service 因子；相对 L3 的盈亏平衡约 **$4.30/GPUh（L4-C）/ $3.78（L4-S）**，即可承受最高约 **54–60%** 相对 list 的折扣。推荐 Base 采用 **Volume Factor 0.70–0.75**（约 $6.5–7.0/GPUh）作为 bulk 情景，list 价仅作上界。

**（3）B200 CAPEX 全模型统一为 ≈$60k/GPU（$31,980/IT-kW）。** v5.0 Strategic 桥中的 $21.3k/IT-kW（≈$40k/GPU）从 Base 移除；Strategic 相对 Contracted 的增量只允许来自融资、backstop、客户资本与**独立标注的**折扣 Sensitivity（0/10/20/30%）。

**（4）“Strategic P(loss)=0%”否决。** 纳入客户违约、价格重置、Vendor backstop 失效、融资冻结后，N=2000 信用/合同 MC 观察损失 **1/2000（0.05%，Wilson 95% CI 0.01–0.28%）**，CE-NPV 约 **+$3.57B**（仍远高于 L3 的 +$0.51B CE），但不得再报告 0% 损失。

**（5）NVIDIA 式 backstop 存在双重计费。** 原模型对 `1−phys_util` 计 backstop，把 take-or-pay 已付未用容量重复计入；修正为仅对 **residual unsold（1−contracted）** 计费后，L4-S NPV 从约 +$5.81B 降至 **+$5.28B**（虚增约 **$0.52B**）。

**修正后主结论（仍成立但更克制）：** Merchant Forward 深负；**在可获得的固定价 take-or-pay 与现实 bulk 折扣下，L4-C/S 确定性 NPV 仍可超过 L3**，但优势随成交价折扣、合同可获得概率与 Sponsor 经济资本（非仅 Peak Cash Equity）收窄。Type A（无合同）ex-ante EV 远低于 L3；Type B/C 在合同已落实时 EV 仍高于 L3。

**关键词**: 合同现金流审计；Realized Contract Rate；Sponsor Economic Capital；Backstop 容量账本；Contract Access Probability；Investment Vintage；take-or-pay

---

## Abstract

*(Condensed.)* v5.1 audits v5.0’s headline flips without expanding the framework. C1−C2 ΔNPV ≈$5.1B is cashflow-explained by compounded step-down pricing. Public Dedicated $9.36/GPUh is an **upper bound**, not a 42k-GPU 5Y base (TCV/CAPEX ≈6.5×); break-even vs L3 is ~$4.3/GPUh (L4-C). B200 CAPEX is unified at ~$60k/GPU; the $21.3k/IT-kW Strategic base is removed. Strategic “0% loss” is **rejected** under credit/contract MC (0.05% observed losses, CE-NPV ~+$3.57B). NVIDIA-style backstop is corrected to residual-unsold only (−$0.52B double-count). Corrected conclusion: Merchant Forward remains weak; Contracted/Strategic can still beat L3 under realistic bulk fixed-price ToP, but only if contract access probability and economic capital (not just peak cash equity) are recognized.

---

## 1 引言与本轮目标

v5.0 的贡献是理论结构（六维函数、Vintage、L4 三模式、Certainty Bridge）。v5.1 的目标是：

> **把决定 L4-C/L4-S 翻转的关键参数做现金流级、合同级、融资级和风险级审计；未通过的 Headline 必须降级或撤下。**

研究问题沿用 RQ1–RQ5，并增加审计问题：

> **AQ1** 固定价相对 step-down 的 ~$5B NPV 差是否有现金流解释？  
> **AQ2** 官网 Dedicated 价能否代表 4 万卡级 5 年成交价？  
> **AQ3** Strategic 的 0% 损失与 Peak Equity $361M 是否低估真实风险？

---

## 2 理论框架（沿用 v5.0，表述收紧）

六维决策函数、L4-M/C/S 定义、Investment Vintage、Historical ≠ Forward、双甜蜜点、风险迁移、Buy First vs Contract First **全部保留**。

**v5.1 强制收紧的表述规则：**

| 禁止再写 | 改为 |
|---|---|
| Merchant GPU 永远不成立 | Merchant **Forward** 在 2026 参数与全栈口径下偏弱；回报 **Vintage-dependent** |
| Strategic P(loss)=0% | 市场风险锁定后损失率**很低**，但信用/合同 MC 下 **非零**（本轮 0.05%） |
| L4-S Peak Equity $361M 为完整风险资本 | 此为 **Peak Cash Equity**；须并列 **Sponsor Economic Capital** |
| 公开 $9.36 为 Base 成交价 | **List / upper bound**；Base 用 Realized Contract Rate（含 volume/term 因子） |
| 固定价 ToP 创造 +$7.8B | 相对 **step-down 路径** 的价格锁定价值；非相对“无合同”的通用溢价 |

---

## 3 模型与审计方法

### 3.1 统一 B200 CAPEX（P0-3）

| 项目 | 取值 | 说明 |
|---|---|---|
| All-in Compute CAPEX / GPU | **$60,000** | silicon+server+network 等系统口径（筛选级） |
| GPU / IT-kW | 0.533 | B200 近似 |
| CAPEX / IT-kW | **$31,980** | 全模型 L4-C 与 L4-S **同一**基础硬件成本 |
| 原 $21.3k/IT-kW | **移出 Base** | 不得再称 “B200-consistent” |
| GPU Discount | 0/10/20/30% Sensitivity | 无一手文件不得进入 Base |

### 3.2 Realized Contract Rate（P0-2）

$$
R_{\mathrm{realized}} = R_{\mathrm{list}} \times f_{\mathrm{vol}} \times f_{\mathrm{term}} \times f_{\mathrm{svc}} \times f_{\mathrm{credit}}
$$

100 MW / 80 MW IT ≈ **42,640** B200。  
List $9.36 × 8760 × 0.95 × 5 ≈ **$389k/GPU** 名义 TCV；总 TCV ≈ **$16.6B** vs Compute CAPEX ≈ **$2.6B**（**6.5×**）→ Reality Flag。

### 3.3 Backstop 容量账本（P0-5）

$$
\begin{aligned}
\mathrm{Total} &= \mathrm{Contracted} + \mathrm{ResidualUnsold} \\
\mathrm{Contracted} &= \mathrm{PhysicalUsed} + \mathrm{PaidButUnused} \\
\mathrm{VendorBackstop} &\le \mathrm{ResidualUnsold}
\end{aligned}
$$

**不得**对 Paid-but-Unused（take-or-pay 已付）再计 backstop。

### 3.4 Strategic 信用/合同 MC（P0-4）

随机变量：客户违约/提前终止、enforceability 折价、价格重置、backstop 失效、融资冻结；N=2000；报告 E、P5、ES₅、CE、损失计数与 Wilson CI。

### 3.5 Sponsor Economic Capital（P1-1）

$$
\mathrm{EconCap} = \mathrm{PeakCashEquity} + \mathrm{GuaranteeEq} + \mathrm{LC/Collateral} + \mathrm{LiquidityReserve}
$$

并列报告 $\mathrm{NPV}/\mathrm{Peak}$ 与 $\mathrm{NPV}/\mathrm{EconCap}$。

### 3.6 Contract Access EV（P1-4）

$$
EV_{L4\text{-}C}=p_C\cdot CE_C+(1-p_C)\cdot CE_M-\mathrm{PursuitCost}
$$

Type A/B/C 映射 $p_C,p_S$。

---

## 4 校准与证据等级

沿用 v5.0 Level A/B/C 与 Level 1–3 证据分级。NVIDIA–OpenAI 相关数字一律 **proposed / under discussion**。GPU 采购折扣无一手文件时仅 Sensitivity。

---

## 5 结果

### 5.1 P0-1：C1 vs C2 逐年现金流审计 — **通过（有条件保留 Headline）**

| Year | C1 Rate | C1 Rev $M | C2 Rate | C2 Rev $M | ΔRev $M |
|---|---:|---:|---:|---:|---:|
| 1 | 9.36 | 3,321 | 6.81 | 2,418 | 904 |
| 2 | 9.36 | 3,321 | 3.24 | 1,151 | 2,171 |
| 3 | 9.36 | 3,321 | 1.54 | 548 | 2,774 |
| 4 | 9.36 | 3,321 | 0.73 | 261 | 3,061 |
| 5 | 9.36 | 3,321 | 0.35 | 124 | 3,197 |
| **合计** | | **16,607** | | **4,500** | **12,107** |

- C1 NPV **+$4,761M**；C2 **−$347M**；ΔNPV **+$5,108M**  
- PV(ΔRevenue) ≈ **+$6,542M**（L4 WACC）  
- 合同均止于 60 月，**无错误延期**；billable/CAPEX 一致  
- **通过标准**：差异可由价格路径解释 → 固定价价值 Headline **保留**，但必须写清是相对 **step-down 路径** 的锁价价值，不是“任意长约 +$7.8B”

### 5.2 P0-2：Realized Contract Rate — **List 价不得作 Base**

| 校验 | 数值 |
|---|---|
| N GPU (100 MW) | ≈42,640 |
| TCV/GPU @ $9.36 | ≈$389k |
| TCV / Compute CAPEX | **6.5×** |
| L4-C 相对 L3 盈亏平衡 | **$4.30/GPUh**（max discount **54%**） |
| L4-S 相对 L3 盈亏平衡 | **$3.78/GPUh**（max discount **60%**） |

**修正后情景（统一 CAPEX，Fixed ToP）：**

| 情景 | Rate $/GPUh | NPV $M | Peak $M | vs L3 (+707) |
|---|---:|---:|---:|---|
| L4-C list（上界） | 9.36 | +4,761 | 1,351 | 超过 |
| L4-C bulk vol 0.75 | 7.02 | +2,885 | 1,404 | 超过 |
| L4-C bulk vol 0.60 | 5.62 | +1,759 | 1,436 | 超过 |
| L4-C @ BE vs L3 | 4.30 | ≈+707 | — | 持平 |

### 5.3 P0-3：CAPEX 统一 — **$21.3k/IT-kW 移出 Base**

| 配置 | CAPEX/IT-kW | NPV $M | Peak $M |
|---|---:|---:|---:|
| L4-C 统一 | 31,980 | +4,761 | 1,351 |
| L4-S 统一 + 修正 BS | 31,980 | +5,285 | 438 |
| ~~L4-S 旧 21.3k~~ | 21,300 | +6,421 | 361 | ← **Base 禁用** |

GPU 折扣 Sensitivity（统一 CAPEX）：0% → +5,808*；10% → +5,992；20% → +6,175；30% → +6,358（*含未修正 BS 时；修正 BS 后水平下移约 $0.5B）。

### 5.4 P0-5：Backstop 双重计费 — **已修正**

| 容量水位 | 比例 | Backstop？ |
|---|---:|---|
| Customer contracted | 95% | — |
| Physical used | 90% | 否 |
| Paid-but-unused (ToP) | 5% | **否** |
| Residual unsold | 5% | **是** |

原模型对 `1−phys=10%` 计费 → 虚增约 **$524M** NPV。  
修正后 L4-S（list）NPV **+$5,285M**（非 +$5,808M）。

### 5.5 P0-4：Strategic 信用 MC — **否决 0% 损失**

| 指标 | N=2000 信用/合同 MC |
|---|---|
| E(NPV) | +$4,827M |
| ES₅ | +$2,319M |
| CE-NPV (λ=0.5) | **+$3,573M** |
| 观察损失 | **1 / 2000 = 0.05%** |
| Wilson 95% CI | **0.01% – 0.28%** |
| DSCR breach | 1.15% |

相对 L3 CE ~+$505M，Strategic 在信用 MC 下 **仍显著更优**，但：

> **不得再写 “P(loss)=0%”。** 应写 “在本轮信用/合同冲击设定下观察损失率极低（0.05%，95% CI 上界 0.28%），CE-NPV 仍约 +$3.6B”。

### 5.6 修正后模式比较（Headline 表）

| 模式 | NPV $M | Peak Cash Equity $M | Econ Capital $M* | NPV/EconCap | 备注 |
|---|---:|---:|---:|---:|---|
| L3 Critical IT | +707 | 317 | ~442 | 1.60 | Structural sweet spot |
| L4-M Forward | −3,173 | 5,491 | ~6,064 | −0.52 | Vintage-dependent；Forward 弱 |
| L4-C Fixed ToP @ list 9.36 | +4,761 | 1,351 | ~2,258 | 2.11 | **上界** |
| L4-C Fixed ToP @ bulk 7.02 | +2,885 | 1,404 | — | — | **推荐 Base 带** |
| L4-S 修正 BS @ list | +5,285 | 438 | ~1,751 | 3.02 | 上界；CE~3.6B（信用 MC） |
| L4-S 修正 BS @ bulk 7.02 | +3,278 | 500 | — | — | 推荐 Base 带 |

\*Guarantee/LC/Reserve 为筛选级比例假设（见 `sponsor_economic_capital.csv`）。

### 5.7 Contract Access 与玩家类型（P1-4）

| 类型 | p_C | p_S | Ex-ante EV $M | vs L3 |
|---|---:|---:|---:|---:|
| A Uncontracted Sponsor | 0.10 | 0.02 | **−2,408** | 远低于 |
| B Contracted Sponsor | 1.0 | 0.25 | **+4,862** | 超过 |
| C Strategic Platform | 1.0 | 0.80 | **+5,150** | 超过 |

**关键含义：** L4-C/S 的高 ex-post NPV **不是菜单选项**。若 $p_C$ 很低，Pursuit EV 可远差于 L3——这是对 v5.0 “小玩家别碰 GPU” 的概率化改写。

### 5.8 Scale（P1-5）

10→100 MW 下，若 volume factor 随规模恶化（1.0→0.75），L4-C NPV/MW 从约 $46M 降至约 $29M，仍为正；规模并不自动消灭合同价值，但 **大单折扣会侵蚀 list 情景的夸张溢价**。

### 5.9 Investment Vintage（沿用 v5.0，措辞不变）

Historical cohort 仍为结构假设下的筛选级估算；相对排序支持 Vintage dependency；**不得**写成“2023/24 Merchant 一定暴利”。Forward Merchant 在统一 CAPEX 下仍深负。

---

## 6 讨论

### 6.1 审计后仍成立的结论

1. **Role × Vintage × Contract × Capital Structure** 决定最优层。  
2. **价格路径锁定**（非笼统长约）是 C1 相对 C2 的价值来源。  
3. **Contracted/Strategic 购买确定性与资本效率**；在 bulk 现实折扣下仍可优于 L3。  
4. **Historical ≠ Forward**；Merchant 是周期交易资产。  
5. **GPU deployment should be demand-led, not inventory-led.**

### 6.2 审计后必须降级的结论

1. ~~Strategic 观察损失率 0%~~ → 极低但非零；须报 CI。  
2. ~~Peak Equity $361M 为完整风险资本~~ → 仅 Cash Equity；EconCap 显著更高。  
3. ~~$9.36 为 5 年批量成交价~~ → list/上界；Base 用 realized rate。  
4. ~~$21.3k/IT-kW B200 Base~~ → 移除。  
5. ~~Backstop +$1.0B 量级~~ → 修正双重计费后约减半贡献。

### 6.3 风险迁移（重申）

Market risk → Credit + Contract + Vendor + Structured-finance risk。  
循环支持与 Vendor 集中度仍是系统风险，不因单项目 CE 为正而消失。

### 6.4 局限性

P2 项未完：Historical 月度 realized 回测、全模型 GPU-aware 全局重跑、t-copula 尾部、完整 renewal cliff。Counterparty PD 为情景设定。EconCap 附加项为比例假设。筛选级精度。

---

## 7 结论

**AQ1** 通过：C1−C2 差异有逐年收入路径解释。  
**AQ2** List Dedicated 价 **不能** 直接作 4 万卡 5 年 Base；bulk 折扣后 L4-C/S **仍可** 超过 L3，直至约 54–60% 折扣触及 L3 盈亏平衡。  
**AQ3** 0% 损失否决；EconCap > Peak Cash Equity；修正 backstop 后 L4-S 仍强但更克制。

**v5.1 一句话：**

> 固定价 take-or-pay 与战略融资仍可把 GPU 从高波动技术资产转为可融资基础设施资产，但成交价必须反映批量与期限折扣，损失率与风险资本必须按信用/合同真实冲击计量，合同可获得性必须进入 ex-ante 决策——否则 v5.0 的 Headline 会高估普通 Sponsor 的可达回报。

$$\boxed{Optimal\ Layer = f(Role,\ Vintage,\ Stack,\ Contract,\ Capital,\ Market,\ p_{access})}$$

---

## 附录 A — v5.1 审计清单状态

| 编号 | 状态 | 产出 |
|---|---|---|
| P0-1 C1/C2 现金流 | **通过** | `contract_cashflow_audit.csv`, `c1_c2_year_compare.csv`, `c1_c2_decomp.csv` |
| P0-2 Realized Rate | **List 降级为上界** | `realized_contract_rate_grid.csv`, `contract_discount_break_even.csv` |
| P0-3 CAPEX 统一 | **$21.3k 移除** | `b200_capex_unified.csv`, `gpu_discount_sensitivity.csv` |
| P0-4 Strategic MC | **0% 损失否决** | `strategic_credit_mc.csv` |
| P0-5 Backstop 账本 | **双重计费修正 −$0.52B** | `capacity_waterfall.csv`, `capacity_ledger.csv` |
| P1-1 EconCap | **完成** | `sponsor_economic_capital.csv` |
| P1-2 Prepay usable | 部分（EV 中简化） | 后续 |
| P1-3 Net Contract Value | 未完（P2） | — |
| P1-4 Access EV | **完成** | `contract_access_ev.csv`, `player_type_ev.csv` |
| P1-5 Scale | **完成** | `scale_sensitivity.csv` |
| P2-* | 未完 | 正式版前 |

## 附录 B — 复现

```bash
cd aidc-optimizer
python research_v5_1_audit.py   # 生成 research_outputs/v5_1/*
python research_v5.py           # v5.0 vintage/term/bridge 套件
python reproduce.py check       # v3.3 黄金结果
```

**模型与数据**：`https://github.com/tonyhuang23-sys/aidc-optimizer`（private）。  

**利益声明**：作者机构从事北美 BTM 电力与数据中心开发。  

**AI 辅助披露**：v5.1 审计由 AI 辅助执行；P0 五项均有可复现 CSV；Headline 数字以 `research_outputs/v5_1/headline_corrected.csv` 与 `audit_summary.json` 为准。
