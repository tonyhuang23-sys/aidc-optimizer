# 面向AI基础设施的价值链投资评估模型：经济角色、投资时点、资产栈、合约结构、资本结构与市场状态共同决定的风险调整资本配置框架

## A Value-Chain Investment Evaluation Model for AI Infrastructure: A Risk-Adjusted Capital Allocation Framework Determined by Economic Role, Investment Vintage, Asset Stack, Contract Structure, Capital Structure and Market State

**作者**: WNT Energy 技术研究组  
**日期**: 2026年8月  
**状态**: 工作论文 **v6.1**（审稿必改项落地版）  
**版本记录**: v6.0 为完整正文合并快照，**核心经济框架与模块结构冻结**。v6.1 **不扩张框架**：在正确年化衰减 $(1+g)^{k/12}$ 下重跑 2×2×2；All-risk Headline 升至 $N=10{,}000$（seed=42，parameter version `v6.1-2026-08-15`，commit `e5fc8d7`）；EconCap 给 Low/Base/High 三档；C4 在修复路径上正式重跑；Matched Counterparty 与 Headline 共用同一 shock 流。数值校准、风险分布、Economic Capital 与验证层仍可滚动。

**代码与复现**: `https://github.com/tonyhuang23-sys/aidc-optimizer`（private）— 提供可复现的代码实现与黄金结果校验，**不是**公开发布的开源仓库。Headline 风险调整数字以 `research_outputs/v6_1/` 为准；确定性 / Vintage / Certainty Bridge 仍以 `research_outputs/v5_2_rerun/` 为准。2×2×2 以 `research_v6_factorial_fixed.py` 为准。

**口径纪律（读表前必读）**

1. **Peak Equity 禁止混用。** v5.0 全栈 Merchant Peak 约 $5.5B 对应频率 bug 下的深负路径；频率修复后 mix-ref $7.80 路径 Peak 为 **$2,362M**。本文 Headline 只用后者。  
2. **CE 体系禁止混用。** Headline 横比只用 All-risk CE（v6.1，$N=10{,}000$）。v5.5 的 $N=800$ 点估计（L3 +$299M 等）降为历史对照。  
3. **区间名称。** 文中 CI 一律为 **Simulation Bootstrap Interval (SBI), conditional on model assumptions**——只度量既定模型假设下的模拟抽样误差，**不是**真实项目价值的 95% 置信区间。它不覆盖 $7.02 成交价、PD/LGD、残值相关、EconCap 或 CAPEX 校准的不确定性。  
4. **$7.02/GPU-h $=9.36\times 0.75$** 是作者 Illustrative Bulk 情景，**不是成交数据**。交易锚定 realized rate **仍未校准**。  
5. **七模式表的 L4 行**已换成频率修复后同一 legacy YAML 路径（NPV **−$964M**，Peak **$755M**）。旧 −$3,351M 只在附录 Version Audit。Headline Forward Merchant 仍见 §7（$7.80，NPV +$78M，Peak **$2,362M**）。
6. **Headline S 与 1.2.1 引擎禁止混用。** 对外 +$2.11B / IRASR +2.37 冻结于 commit `e5fc8d7`、parameter version `v6.1-2026-08-15`，S 路径当时用 **legacy 0.375** 补偿旧引擎的 `1-phys` 双重计费。代码 1.2.1 已改为 residual-unsold only，活路径默认 **0.75**；`research_outputs/v6_1/` **不是** 1.2.1 + 0.75 的重跑结果。活 runner 写入 `research_outputs/v6_1_1/`，不得覆盖冻结包。本文 Headline 数字仍引用该冻结包，不在 1.2.1 上重估。

---

## 投资决策矩阵（读摘要前）

| Sponsor 状态 | 推荐策略 | 核心逻辑（v6.1） |
|---|---|---|
| 有 Power / Site，无 AI 客户 | 停留 **L3** | All-risk CE +$312M；无合同全栈 IRASR\_econ 为负 |
| 闲置、无可替代租户的 AI-ready 机房 | 先测 GPU-only **accounting** | 改善相对全栈 Merchant，但仍低于继续做 L3 |
| 可立刻外租的 AI-ready 机房 | Transfer Pricing 后再决策 | 经济口径 CE 平价约 $10.7–11.8/GPU-h（随 L3 租金 $125–250） |
| 已签约 5 年 take-or-pay | **L4-C** | CE +$1.67B；IRASR\_econ Base **+0.92**（Low 1.11 / High 0.83） |
| ToP + Vendor + 低成本融资 | **L4-S** | CE +$2.11B；IRASR\_econ Base **+2.37**（Peak 口径 9.8 **禁止作口号**） |
| 无合同、绿地全栈 | **不默认 L4-M** | CE −$980M；IRASR\_econ ≈ −0.59 |
| 3 年 tech-refresh 挂钩合同 | 低于 5 年锁价，仍可正 | C4 list CE +$1.13B；bulk $7.02 CE +$181M（禁止再用 v5.0 的 −$821） |

---

## 摘要

人工智能数据中心（AIDC）投资常被简化为单一“数据中心 IRR”或静态“甜蜜点”。本文以统一 100 MW 参考项目为测试平台，将 **经济角色（Role）、投资时点（Investment Vintage）、资产栈（Asset Stack）、合约结构（Contract）、资本结构（Capital Structure）与市场状态（Market State）** 纳入同一套资产层—融资层双引擎，并用自定义的 **tail-weighted certainty-equivalent proxy**

$$\mathrm{CE\text{-}NPV}=(1-\lambda)\,E(\mathrm{NPV})+\lambda\,\mathrm{ES}^-_{5\%}(\mathrm{NPV})$$

与增量风险调整股本回报

$$\mathrm{IRASR}_{\mathrm{econ}}=\frac{\Delta\mathrm{CE\text{-}NPV}}{\Delta\mathrm{Sponsor\ Economic\ Capital}}$$

作为 Sponsor 资本配置规则。**IRASR\_econ 是理论首选指标；本文以筛选级 Economic Capital 估算（Low / Base / High），并同时报告 Peak Equity 口径交叉验证。** 决策分两步：先评估**资产本身**的 $V_i$，再叠加**该 Sponsor 获得该结构的概率、追逐成本（含时滞与选择权）与失败回退**。

在 2026-08 参数、频率修复后的年化衰减、统一 B200 系统口径（约 $60\mathrm{k}/\mathrm{GPU}$）以及 All-risk 蒙特卡洛（**Headline $N=10{,}000$，seed=42，SBI conditional on model assumptions**）下，主要结果是：

1. **电力层**市场一致组合（新建 CCGT + 投资级 tolling）Equity IRR 约 **14.1%**；广为引用的约 28% 来自“二手设备 × 溢价长约”套利，二者约 14 个百分点的差是可检验的市场命题，不是模型缺陷。  
2. **L3 Critical IT** 是无算力合同能力时的 **structural sweet spot**：项目 NPV 约 **+$707\mathrm{M}$**，All-risk CE 约 **+$312\mathrm{M}$**（SBI **[$280\mathrm{M}$, $343\mathrm{M}$]**）。  
3. **全栈 Merchant（Power+DC+GPU）** 在 mix-ref $7.80/\mathrm{GPU\text{-}h}$、年化 $-22\%$ 衰减下点估计接近盈亏平衡（NPV 约 **+$78\mathrm{M}$**），但 All-risk CE 约 **$-980\mathrm{M}$**（SBI **[−$998\mathrm{M}$, −$961\mathrm{M}$]**），IRASR\_econ Base 约 **$-0.59$**——**不是默认策略**。$7.80$ 是非现货公开报价的**产品组合参考**，不是纯现货中位。  
4. **GPU-only** 必须做转移定价：机房闲置（accounting）时 CE 约 **$-390\mathrm{M}$**；若机房可按 L3 市场租金外租（economic），CE 约 **$-934\mathrm{M}$**。经济口径 CE 平价随转移租金 $125\to250/\mathrm{kW\text{-}月}$ 从约 **$10.72$** 升至 **$11.76/\mathrm{GPU\text{-}h}$**（基准 $185$ 对应 **$11.22$**）。**沉没成本 ≠ 零机会成本。**  
5. **合同化算力**（Illustrative bulk $7.02=0.75\times 9.36$，**作者情景假设，非成交数据**）：L4-C All-risk CE 约 **+$1.67\mathrm{B}$**（SBI **[$1.63\mathrm{B}$, $1.71\mathrm{B}$]**），L4-S 约 **+$2.11\mathrm{B}$**（SBI **[$2.07\mathrm{B}$, $2.15\mathrm{B}$]**）。同信用、同 shock（Matched Counterparty）下 C 相对 L3 的 **layer 效应约 +$1.49\mathrm{B}$**，主要来自合同结构而非“客户更好”。Headline L3 Generic **就是** +$312M，不再另给一套 +$248M。  
6. **真正 $-6\%/\mathrm{年}$ 的 step-down** 并不摧毁合同：C2 NPV 约 **+$3.84\mathrm{B}$**，相对固定价 C1 的锁价溢价约 **+$0.92\mathrm{B}$**。较快重定价 C3（$-15\%/\mathrm{年}$，list）仍约 **+$2.39\mathrm{B}$**。**C4（3 年 tech-refresh-linked）正式重跑**：list $9.36$ 确定性 NPV **+$1.92\mathrm{B}$**、All-risk CE **+$1.13\mathrm{B}$**；illustrative bulk $7.02$ 确定性 NPV **+$771\mathrm{M}$**、CE **+$181\mathrm{M}$**。v5.0 的 C4 −$821M **禁止 Headline**。  
7. **资本配置主指标是 IRASR\_econ**（筛选 EconCap Base：C 约 **$+0.92$**，S 约 **$+2.37$**；三档符号稳定）。Strategic 的 Peak IRASR $\approx 9.8$ 是杠杆压低现金股本的结果，**不得作对外口号**。  
8. **Sponsor overlay**：仅计现金 Pursuit $20\mathrm{M}$ 时 $p_C^{*}\approx 1.5\%$；计入 6–24 个月时滞与选择权后，$p^{*}$ 升至约 **2.6%–26.5%**——仍支持“花有限费用追 take-or-pay；拿不到则留在 L3”，但不再把 1% 写成可操作阈值。

**主结论：** 最优层级不是价值链的固定属性。同一张 GPU，因 Vintage、Stack、Contract 与 Capital Structure 不同，可以是高波动技术资产，也可以是可融资的 AI 基础设施资产。**GPU 部署应需求驱动（contract-first），而非库存驱动（buy-first）。**

**关键词**: AI 基础设施；Deliverable MW；Investment Vintage；Merchant / Contracted / Strategic；take-or-pay；All-risk CE；IRASR\_econ；Transfer Pricing；GPU-backed 融资；Market State

---

## Abstract

AIDC investment is often reduced to a single “data-center IRR.” This paper evaluates seven business modes on a unified 100 MW platform with a two-tier asset–financing engine and two decision metrics: a **tail-weighted certainty-equivalent proxy** and incremental risk-adjusted sponsor return on **screening-level economic capital** (Low / Base / High). Asset value is $V_i=f(\mathrm{Role},\mathrm{Vintage},\mathrm{Stack},\mathrm{Contract},\mathrm{Capital},\mathrm{Market})$; sponsor choice overlays access probability, pursuit cost (cash + delay + option) and fallback.

After correcting an annual-to-monthly decay bug and unifying B200 all-in CAPEX, all modes are scored on one All-risk taxonomy ($N=10{,}000$; seed 42; **Simulation Bootstrap Intervals conditional on model assumptions**). The committed Headline pack still uses the **legacy 0.375 S-path compensation** on the pre-1.2.1 engine; residual-unsold-only billing is the 1.2.1 live default and has **not** been re-run at $N=10{,}000$. Under that frozen pack, the market-coherent power layer earns ~14.1% equity IRR; L3 Critical IT is the structural default (CE ~+$312\mathrm{M}$); full-stack Merchant at a **non-spot mix-reference** $7.80/\mathrm{GPU\text{-}h}$ is near NPV breakeven but deeply CE-negative; GPU-only improves the stack boundary but, once L3 market rent is charged, still fails L3 opportunity-cost parity below ~$11/\mathrm{GPU\text{-}h}$; illustrative bulk contracted/strategic compute ($7.02=0.75\times 9.36$, **author scenario**) remains CE-superior to L3, and a matched-counterparty test on the **same shock stream** attributes most of the gap to **contract structure**. A frequency-corrected $2\times 2\times 2$ ranks **contract $\gg$ vintage $>$ stack**. IRASR on screening economic capital is the headline allocation rule. GPU deployment should be demand-led.

---

## 1 引言

### 1.1 研究背景

自 2024 年起，AI 基础设施进入史无前例的资本扩张期：到 2030 年全球数据中心资本需求约 6.7 万亿美元（AI 相关约 5.2 万亿）[1]；2025–2028 年数据中心资本开支约 2.9 万亿美元、外部融资缺口约 1.5 万亿 [4]；评级机构已对近 1,000 亿美元数据中心相关债评级 [5]。与此同时，GPU 租赁出现 Spot / Instance / Dedicated Cluster 分层 [16][17]，NVIDIA 宣布动员超过 5,000 亿美元的第三方 compute financing platforms [11]，CoreWeave 等以多年期 take-or-pay 与 GPU-backed 债务运营 [5][7][9]。行业正在从“买卡赌周期”转向“合同化—信用化—金融化”。

对投资人更根本的问题是：**对同一可按时交付的兆瓦级电力与场址，应当投到哪一层、以何种资产栈与合约、在哪个时点进入、在哪个节点退出？**

### 1.2 研究问题

> **RQ1** 七种商业模式（含 L4-M/C/S）的投资强度、回报与风险敞口如何在统一口径下比较？  
> **RQ2** 价值链延伸的 IRASR 在何处由正转负？该拐点如何随 Vintage、Stack 与合同移动？  
> **RQ3** 最优层级在多大程度上由 Role、Vintage、Stack、Contract、Capital Structure 与 Market State 共同决定？  
> **RQ4** 公开市场价与 CoreWeave 式资本结构下，L4 何时从毁灭价值转为创造价值？  
> **RQ5** Historical Merchant 与 Forward Merchant 差多大？Contracted/Strategic 购买的是更高均值还是更高确定性？  
> **RQ6** 已有 L3 机房再装 GPU 时，是否应扣除放弃外租的机会成本？

### 1.3 贡献

本文不声称发明 CVaR、copula 或项目融资工具。贡献在于：（1）把分散在工程、云计算、项目融资与 AI 经济学中的工具整合成 **Sponsor 级资本配置框架**；（2）严格分离 Historical / Forward 回报，并将 L4 重构为 Merchant / Contracted / Strategic；（3）用 All-risk CE 与 IRASR\_econ 给出可横比的延伸规则，并用 Transfer Pricing 与 Matched Counterparty 防止“免费占用 L3”和“更好客户冒充更好层级”；（4）**提供可复现的代码实现与黄金结果校验**（仓库暂为 private）。

### 1.4 本稿范围

v6.1 **不扩张框架**。它在 v6.0 冻结的模块结构上完成审稿五项必改：频率修复后的 2×2×2、主表清除 bug 路径 L4、All-risk $N=10{,}000$、EconCap 三档、Matched 与 Headline 同 shock。明确仍属后续工作、本稿不重做的项目：交易级 realized-rate 校准、完整 OOS / historical cohort 回测、L5a token 引擎、双轨贴现率归属的系统输出、Financeability 网格的独立正式重跑、WACC-only / 统一未杠杆贴现 + CE 的完整三轨引擎（§4.6 用 $\lambda$ 端点作部分替代）。

---

## 2 AIDC 生态、经济角色与资金流

### 2.1 底层资产：可交付容量

兆瓦本身不是完整商品。本文将稀缺资源定义为

$$\text{AI Infrastructure Capacity}=f(\mathrm{MW},\ \mathrm{COD},\ \mathrm{Availability},\ \mathrm{Contractability},\ \mathrm{Location}).$$

Power、Critical IT、Compute 是对同一稀缺资源——**可按时交付的容量**——的逐级转换。一兆瓦“2027Q4 可交付”与“2030Q4 可交付”是两种资产 [5]。Time-to-Power Premium 因此具有独立价格。

### 2.2 经济角色矩阵

Role 定义在**交易**上，不定义在公司名上。同一主体（如 Meta）可同时是最终需求方、基础设施所有者和算力购买者。

| Role | 出售什么 | 向谁收费 | 主要资产 | 核心风险 |
|---|---|---|---|---|
| PowerCo | Firm MW @ COD | DC 运营商 | 发电+燃料 | COD、可用性、气价（可转嫁） |
| DC Landlord | Critical IT MW | Tenant | 建筑+MEP | 建设、租户信用 |
| ComputeCo（L4-M/C/S） | GPU-hour / 合同容量 | AI Lab / 企业 | GPU+集群±合同±Vendor | 见 §2.3 |
| Managed Inference (L5a) | \$/token 托管 | 应用/企业 | 平台+运营 | 需求、毛利率 |
| Frontier Model (L5b) | Token / API | 终端用户 | 模型 IP+客户 | 变现能力 |

三条资金闭环：**Meta 型**（广告现金流 → 自建基建，Captive）；**Anthropic 型**（多源采购算力 + 直锁 Critical IT）；**CoreWeave 型**（长期合同 → 融资能力 → 部署 → 偿债——**客户合同是资本结构的一部分** [4][5]）。本文覆盖 L0–L5a；L5b 与 Captive 不进入基础设施回报函数，仅作价值归属对照。

### 2.3 L4 三模式

| 模式 | 本质 | 下游合同 | Vendor | 融资 | 主要风险 |
|---|---|---|---|---|---|
| **L4-M Merchant** | 技术资产 + 市价收入 | Spot / on-demand / 短约 | 普通 PO | 低杠杆、高 $K_d$ | 租金、利用率、残值、技术淘汰 |
| **L4-C Contracted** | GPU + 客户合同 | 2–5 年 take-or-pay | 常与签约同步采购 | 合同支持的更高杠杆 | 客户信用、交付、续约重定价 |
| **L4-S Strategic** | 合同 + Vendor + 融资平台 | Lab / hyperscaler 多年期 | 股权、capacity backstop、生态 | GPU-backed、机构资本 | 集中度、结构化融资、循环支持 |

**Buy First vs Contract First：** Merchant 是先买后卖；Contracted 是先约后买；Strategic 是先约、增信、融资、再买。

### 2.4 行业四阶段

| Phase | 路径 | 主导逻辑 |
|---|---|---|
| 1 Early Scarcity / Merchant Alpha | 低成本进入 → scarcity rent → 租金上行 | 周期交易 |
| 2 High Entry Cost / Forward Uncertainty | 高 CAPEX + 高现价 + 不确定未来租金 | Merchant 风险↑ |
| 3 Contractualization | Customer Contract → 现金流可见性 → Bankability | 合同化 |
| 4 Strategic Ecosystem | Customer + Vendor + Institutional Capital | 金融化基础设施 |

NVIDIA 超过 5,000 亿美元 compute financing platforms [11] 表明第四阶段正在被**制度化**，但设备折旧更快、代际更短，不同于飞机租赁的稳态。

---

## 3 理论框架：资产六维与 Sponsor 叠加层

### 3.1 两步决策

资产价值

$$V_i=f(\mathrm{Role},\ \mathrm{Vintage},\ \mathrm{Stack},\ \mathrm{Contract},\ \mathrm{CapitalStructure},\ \mathrm{MarketState}).$$

Sponsor 决策

$$EV^{\mathrm{Sponsor}}=f\bigl(V_i,\ p_{\mathrm{access}},\ \mathrm{PursuitCost},\ \mathrm{Fallback}\bigr).$$

前六项回答“这个结构值多少”；$p_{\mathrm{access}}$ 回答“我是否拿得到”。二者属于不同层次，不再写成混在一起的“七维函数”。开发商更真实的 Fallback 是**继续做出租 L3**，不是被迫做 Merchant。

### 3.2 Investment Vintage

Vintage = GPU 资产首次形成不可逆资本承诺的时点。每一 Vintage 拥有独立的采购价、交付、初始租金、租金路径、利用率、残值、融资条件与竞争代际。必须分离三种回报：

| 类型 | 符号 | 回答的问题 |
|---|---|---|
| Historical Realized | $IRR_{\mathrm{Realized}}$ | 过去某 cohort 实际/估算赚了多少？ |
| Mark-to-Market / Cohort | 已实现 CF + 当前残值 | 今天重估这批卡值多少？ |
| Forward New-Investment | $IRR_{\mathrm{Forward}}$ | 今天新进入还值不值得？ |

$$\boxed{\mathrm{Historical\ Winner}\neq\mathrm{Forward\ Winner}}$$

### 3.3 双甜蜜点

- **Structural**：无算力合同能力时的稳健层级（L3）。  
- **Cyclical / 合同化**：特定 Vintage 或已落实 ToP 时的临时/条件最优（早期 H100 GPU-only；L4-C/S）。

不得再给跨周期的单一“固定甜蜜点”。

### 3.4 沉没成本 ≠ 零机会成本

$$\text{Buy GPU iff }\mathrm{CE}_{\mathrm{Compute}}-\mathrm{CE}_{\mathrm{Foregone\ L3}}>0.$$

闲置、无可替代租户 → accounting / sunk；可按市场租金外租 → economic / transfer（内部按 L3 租金结算）。矿场改 AIDC 与 Virginia/Texas 一座可立刻租给 Hyperscaler 的 AI-ready 厂房，适用完全不同的口径。

### 3.5 实践者分型（Type A/B/C）

- **Type A Uncontracted Sponsor**：有资本、无客户合同 → 默认停留 L3，不把 Merchant 当 Fallback。  
- **Type B Contracted Sponsor**：已获高质量 take-or-pay → 可进入 L4-C。  
- **Type C Strategic Platform**：Customer + Contract + Vendor + Financing + Ops → L4-S。

真正门槛是 **Customer + Contract + Capital + Vendor**，不是市值本身。

---

## 4 模型与方法

### 4.1 统一物理口径

100 MW 发电、PUE 1.25 → 80 MW Critical IT。GPU 层同时报告 \$/IT-kW-h 与 \$/GPU-h。B200 换算 **0.533 GPU/IT-kW** 为筛选假设：节点 IT 功率、网络/存储分摊与机柜开销并入 all-in compute system，**不是**裸加速器标价；冷却泵计入厂级 PUE 1.25，不在 GPU/kW 里再计一遍。All-in Compute CAPEX 统一为约 **\$60,000/GPU**（\$31,980/IT-kW）。原 Strategic 桥中的 \$21.3k/IT-kW **移出 Base**。GPU 折扣 0/10/20/30% 仅作 Sensitivity，无一手文件不得进入 Base。

七种商业模式：开发退出（L0）、Power-only（L1）、Powered Shell（L2）、AI-ready Critical IT（L3）、GPU Hosting / 到机架（L3.5）、算力出租（L4）、Managed Inference（L5a）。L4 在 Headline 中再拆为 M/C/S。

### 4.2 资产层

月度频率。Tolling：容量费 + 燃料/碳转嫁，利润变量为 Tolling Margin。租约：租金 $\times$ 递增；到机架增量按棕地实盘量级校准 [14]。GPU：

$$\mathrm{RevPAGH}=u_t\cdot R_0\cdot f_{\mathrm{reset}}^{c}\cdot(1+g)^{k/12},$$

其中 $g$ 为**年化**衰减，$k$ 为月序号。v5.2 修复前代码写成 $(1+g)^{k}$，把 $-6\%/\mathrm{年}$ 变成约 $-52\%/\mathrm{年}$、把 $-22\%/\mathrm{年}$ 变成约 $-95\%/\mathrm{年}$。电力/租约 escalator 本就用 $\mathrm{yr}=k/12$，未受影响。

L4-C/S：take-or-pay 按 billable 计费。容量账本：

$$\mathrm{Contracted}=\mathrm{Physical\ Used}+\mathrm{Paid\text{-}but\text{-}Unused},\qquad
\mathrm{Backstop}\le\mathrm{Residual\ Unsold}.$$

NVIDIA 式 backstop **仅作用于 residual unsold**，不得对已付未用容量双重计费。原模型对 $1-u_{\mathrm{phys}}$ 计费造成约 **\$0.52B** 虚增，已修正。

### 4.3 融资层

与资产层分离：S 曲线提款、IDC、sculpted/mortgage 摊还、现金扫仓、客户资本。**GPU-aware 融资**：债务按全部 capex（含运营期 GPU 采购）计杠杆，修复基础引擎漏记 GPU 权益投入、低估 Peak Equity 的缺陷。CAPEX 输入 = overnight（EPC+业主费用）；IDC 仅由融资层计算。P1 下 IDC 约 \$7M，占 CAPEX 1.9%。

### 4.4 Certainty Bridge 引擎

在 NPV Value Bridge 之上，逐步报告 $E(\mathrm{NPV})$、$ES_5^-$、CE-NPV、$P(\mathrm{loss})$、Peak Equity、合同窗 DSCR。步骤顺序固定为：Merchant 基准 → Dedicated list 价 → 5 年 Fixed ToP → Contracted 融资 → 预付 → residual-only backstop → GPU-backed 杠杆 → bulk / step-down 对照。目的是证明 Contracted/Strategic 购买的是 **risk-adjusted certainty**，而不只是更高平均收入。融资与预付在统一项目贴现率下 **不改变 Project NPV**，只压缩 Peak Equity。C4 正式重跑印证这一点：同一合同的 tcv15 预付与固定 $150M 预付，**All-risk CE 相同**，只改 Peak。

### 4.5 Contract Financeability 引擎

输入：客户信用档、tenor、take-or-pay%、预付%、backstop、集中度。输出：max leverage、$K_d$、debt tenor、min DSCR。形成

$$\mathrm{Contract}\rightarrow\mathrm{Cashflow\ visibility}\rightarrow\mathrm{Bankability}\rightarrow\mathrm{Debt\ capacity}\rightarrow\mathrm{Peak\ Equity}$$

的传导。筛选映射：IG + 5 年 + 高 ToP + 预付 + backstop → lev $\approx 70\%$、$K_d\approx 5.9\%$、tenor 60 月；Unrated / 短约 / 无保底 → lev $\approx 35\%$、$K_d\approx 9.5\%$。Financeability 不是辅助维度，而是资产价值本身的构成部分。

续约悬崖（Renewal Cliff）：合同到期与 GPU 刷新周期（均约 3–5 年）重叠时，残值、续约重定价、refresh CAPEX 与剩余债务同时冲击，必须单独压力测试。C4 把 tenor 压到 36 个月，正是对悬崖的合同化处理。

### 4.6 风险调整

本文定义一个自定义的 **tail-weighted certainty-equivalent proxy**（不是由显式效用函数导出的教科书 CE）：

$$ES^-_{5\%}(\mathrm{NPV})=E[\mathrm{NPV}\mid \mathrm{NPV}\le P_5],\quad
\mathrm{CE\text{-}NPV}=(1-\lambda)E(\mathrm{NPV})+\lambda\,ES^-_{5\%}.$$

分层 WACC 意图表达长期资本要求；$\lambda\cdot ES$ 意图表达 Sponsor 对模拟左尾的偏好。GPU 租金、残值、信用与再融资都可能同时具有系统性与项目特异性，**无法完全排除风险调整重叠**。Headline 口径是分层 WACC + $\lambda=0.5$ CE。稳健性用同一 All-risk 样本的 $\lambda$ 端点近似三轨：$\lambda=0$ 接近“只看期望（WACC 已在路径贴现中）”；$\lambda=1$ 接近“只看 5% ES”。**C/S $>$ L3 $>$ M 在 $\lambda=0$ 到 $\lambda=1$ 均成立**（表 8-2）。完整的“统一未杠杆贴现 + CE”引擎仍为后续工作。

Headline 用 **All-risk** 分类（租户/客户违约、GPU 租金、利用率、残值、Vendor、再融资），各模式仅 **Exposure** 不同：

| Risk | L3 | L4-M | L4-C | L4-S |
|---|---|---|---|---|
| Tenant / customer default | ✓ | — | ✓ | ✓ |
| GPU rent | — | ✓ 高 | fallback / haircut | fallback / haircut |
| Utilization | — | ✓ 高 | ToP 锁定 | ToP 锁定 |
| Residual | — | ✓ 高 | 轻 | 轻 |
| Vendor failure | — | — | 低 | ✓ backstop |
| Refinancing | ✓ | ✓ | ✓ | ✓ |

Headline $N=10{,}000$（seed=42）。报告 Simulation Bootstrap Interval（2000 次，conditional on model assumptions）。$\lambda=0.5$ 为正文，并报告 $\lambda\in\{0,0.25,0.5,0.75,1\}$。

主资本配置指标

$$\mathrm{IRASR}_{\mathrm{econ}}=\frac{\Delta\mathrm{CE}}{\Delta\mathrm{EconCap}}.$$

筛选级 EconCap（**原型，非 term-sheet 校准**）：

$$\mathrm{GuaranteeEq}=g_{\mathrm{face}}\cdot\mathrm{CAPEX}\cdot h_{\mathrm{EL}},\qquad
h_{\mathrm{EL}}\in\{0.15,0.30,0.50\}.$$

流动性项：Low = reserve only；Base = $\max(\mathrm{LC},\mathrm{reserve})$（避免双计）；High = LC + reserve。

$$\mathrm{EconCap}=\mathrm{PeakCashEquity}+\mathrm{GuaranteeEq}+\mathrm{Liquidity}.$$

面值比例沿用 v5.4 筛选假设：L3 $(0.10,0.05,0.03)$，M/gpu $(0.05,0.02,0.03)$，C $(0.15,0.08,0.05)$，S $(0.25,0.10,0.08)$。Peak IRASR 为次要交叉验证。

### 4.7 价格命名纪律

| 标签 | \$/GPU-h | 含义 |
|---|---:|---|
| M1 Spot | 4.25 | 现货 [16] |
| M2 On-demand | 6.90 | 短周期实例 [17] |
| Mix-ref non-spot | 7.80 | 非现货公开报价**混合参考**，**不是纯现货中位** |
| M3 / list dedicated | 9.36 | Lambda 64-GPU cluster list [17]；合同 **上界** |
| **Illustrative bulk** | **7.02** | **$=9.36\times 0.75$，作者情景假设，非成交数据** |
| Legacy YAML | $\approx 5.63$ | `rate_per_kw_hr=3.0`，仅 reproduce 回归与表 5 |

**禁止再写：** “Merchant @ public median $7.8 接近盈亏平衡 = 现货市场可做”。  
**应写：** “在 mix-ref $7.8 与 $-22\%/\mathrm{年}$ 下全栈点估计接近 BE，但 All-risk CE 仍显著为负。”

### 4.8 实现

Python 双引擎约 2,000 行 + 研究脚本。`reproduce.py check` 校验 v3.3 黄金路径（频率修复后基准 L4 NPV 约 $-\$964\mathrm{M}$，对应 legacy YAML 租金，**不是** Headline $7.80$ 路径）。v6.1 脚本：`research_v6_factorial_fixed.py`、`research_v6_1.py`。

---

## 5 校准与验证

### 5.1 Level A — 参数锚定

| 锚点 | 公开事实 | 用途 |
|---|---|---|
| TeraWulf–Anthropic（**2026-07-06**）[8] | 401 MW IT / 20 年 / 名义约 \$19B / $\approx\$197/\mathrm{kW\text{-}月}$ | Critical IT 租金恒等式 |
| Greenlight [8] | 932 MW / CA\$4.6B / ~60% 债 | Power 层区间；overnight $\approx\$3{,}500/\mathrm{kW}$ |
| IREN SEC H100 [15] | 2023-08 248 卡约 \$10M；2024-02 568 卡约 \$22M | Historical Vintage 采购锚（约 \$38–40k/卡） |
| Lambda / CoreWeave 2026-08 [16][17] | B200 Spot $\approx\$4.26$；Instance $\approx\$6.7$–7.0；Dedicated $\approx\$8.9$–9.9 | Forward 分层 |
| CoreWeave S-1 / 10-K [5] | 约 96% committed；2–5 年 ToP；预付约 15–25% TCV | L4-C 结构 |
| CoreWeave–NVIDIA 8-K [7] | 约 \$6.3B order；residual capacity 至 2032 | L4-S backstop |
| DDTL 4.0 [9] | Fixed 约 5.9%；SOFR+2.25% | Strategic $K_d$ 锚（非通用） |
| NVIDIA \$500B platforms [11] | 官方 2026-08-10 | 行业金融化 |
| NVIDIA–OpenAI 拟议支持 [12][13] | 约 \$250B 讨论值，后报道首期少于 \$120B | **proposed / under discussion** |

关键参数的来源、证据等级与置信度见附录 D。**$7.02$ 的 evidence level 为 Author scenario，不得升格为 Level 1。**

### 5.2 Level B — 内部验证

Sources = Uses（偏差 $0.00$）、债务滚动期末清零、杠杆与 LTC 对齐（IDC 解释差额）、GPU 期限匹配、IRR/NPV 解析解 $<10^{-9}$、现金流符号转换次数 $\le 1$。频率审计：电力/租约 escalator 本就按年；GPU `rate_decay` 已改为 $(1+g)^{k/12}$。v6.1 Headline 固定 seed=42、parameter version `v6.1-2026-08-15`、commit `e5fc8d7`。

### 5.3 Level C — 合理性检验

DGX 价格带、公开 GPU 租金、REIT/项目融资杠杆对照为 plausibility，**不是**交易级样本外预测。$\ge 5$ 笔未参与定参交易的 Prediction-vs-Actual 仍为后续工作。

### 5.4 证据等级

Level 1 监管/官方可作 Base；Level 2 高质量媒体必须标 proposed；Level 3 情报保留置信度。禁止将拟议担保写成已完成融资，禁止将未证实 GPU 折扣写成事实。

---

## 6 电力层、L0–L3.5 与频率修复后的因子实验

### 6.1 电力层参数一致性

v2.0 把 28% Equity IRR 当作电力层普遍基准，隐含“最低 CAPEX（二手 9E）+ 最高质量合同（溢价长约）”。现实中二者存在约束：二手设备对应更短剩余寿命与更高利差，投资级长约通常要求新建高规格资产。本文将该层拆为三个一致性情景。

**表 3 电力层参数一致性（100 MW，Alberta）**

| 情景 | 组合 | NPV \$M | Project IRR | Equity IRR | 经济性质 |
|---|---|---:|---:|---:|---|
| **P1 市场一致** | 新建 CCGT \$3,500/kW + IG tolling \$28/kW-月 + 5.8% | +104 | 11.0% | **14.1%** | Greenlight 型基础设施回报 |
| P2 桥接 | 二手 GT \$1,150 + 中期约 \$12/kW-月 + 8.5% | +129 | 16.9% | 19.2% | 商业燃机市场常态 |
| P3 套利 | 二手 GT + 溢价长约 \$18/kW-月 | +191 | 21.1% | **28.0%** | 设备 × 合约套利（upside） |

约 14 个百分点差额量化“能否以二手设备拿到投资级溢价长约”。**后续一律以 P1 为市场一致基准。** IDC 由融资层单独计（P1 约 \$7M，占 CAPEX 1.9%），overnight 与融资成本不双计。

### 6.2 七模式基准（Alberta；电力为 P1）

**表 4 基准结果（电力层 P1；2026-08 参数；L4/L5a 已换为频率修复后同一 YAML 路径）**

| 模式 | CAPEX \$M | Peak Equity \$M | Project IRR | Equity IRR | NPV \$M | 观察损失率 |
|---|---:|---:|---:|---:|---:|---|
| 开发退出† | 20 | 20 | — | — | +5 | 13.9% |
| Power-only（P1） | 368 | 133 | 11.0% | 14.1% | +104 (245) | 低 |
| Powered Shell | 469 | 238 | 12.5% | 14.4% | +87 (79) | 15.6% |
| AI-ready Critical IT | 773 | **317** | 20.1% | 26.0% | **+707** (647) | 0/1500 |
| GPU 托管（到机架） | 1,093 | 501 | 19.5% | 23.5% | +733 (655) | 0.3% |
| 算力出租（legacy YAML）‡ | 5,829 | **755** | **3.18%** | — | **−964** | 见 §8 全栈 M |
| Managed Inference (L5a)§ | 5,533 | **850** | **35.5%** | — | **+927** | 非 Headline |

括号内为 Texas NPV。†开发退出报 MOIC $2.00\times$、年化 XIRR 36%、27 个月。  
‡**本行是频率修复后同一 legacy YAML（$\approx\$5.63/\mathrm{GPU\text{-}h}$，`run_scenario` compute），不是 Headline mix-ref \$7.80。** v3.3 的 −\$3,351 / Peak \$1,097 已移入附录 C。Headline Forward Merchant 见 §7.1（NPV +\$78M，Peak **\$2,362M**）。  
§L5a 仍是收入等效、**不是** token 单位经济引擎；+$927 只说明频率修复后同一 YAML 不再机械深负，**不得**解读为“托管推理已验证赚钱”。

辅助增量链（$\Delta\mathrm{NPV}/\Delta\mathrm{CAPEX}$）：Dev→Power **+0.28**；Power(P1)→Shell **−0.17**；Shell→Critical IT **+2.04**；Critical IT→Hosting **+0.08**；Hosting→GPU（频率修复后 legacy YAML）**−0.36**（旧 bug 路径曾为 −0.86）。市场一致电力基准下，壳体层几乎不创造增量价值。**价值创造重心在“可交付电力 → AI-ready Critical IT”。**

### 6.3 频率修复后的 2×2×2（经济情景包，非单变量因果）

格子同时改变租金、衰减与利用率，是 **Asset × Contract × Vintage 经济情景包**，不是对“代际”或“合约”的单一因果处理。引擎：`reproduce.run_scenario` + `gpu_correlated_mc`，$N_{\mathrm{CE}}=800$/格，seed=42，衰减 $(1+g)^{k/12}$。

**表 5 频率修复后的 L4 全因子矩阵（NPV \$M / Project IRR / Peak \$M / All-risk-lite CE \$M）**

| 资产栈 \ 合约 | Merchant × 新卡 | Merchant × 二手 | Contracted × 新卡 | Contracted × 二手 |
|---|---|---|---|---|
| **Greenfield** | −964 / 3.2% / 755 / **−1,660** | −175 / 11.7% / 732 / −587 | **+1,097** / 27.4% / 755 / −22 | +1,079 / 34.0% / 732 / +381 |
| **Brownfield** | −736 / 4.9% / 558 / −1,432 | **+52** / 16.2% / 535 / −359 | +1,324 / 31.8% / 558 / +206 | **+1,307 / 42.6% / 535 / +609** |

租金（\$/IT-kW-h）：新卡现货 3.0 / 长约 3.2；二手现货 1.9 / 长约 2.0。二手 GPU \$12k/IT-kW、残值 0.30；长约衰减 −8%、利用率 95%。绿地 power \$1,150/kW + ready \$8,000/kW-IT；棕地 power \$150/kW + ready \$5,500/kW-IT。

**主效应与交互（全因子均值分解，\$M）**

| 效应 | NPV | CE | 解读 |
|---|---:|---:|---|
| **合约结构（长约 − 现货）** | **+1,658** | **+1,303** | 最大杠杆：锁定衰减与利用率 |
| **GPU 代际（二手 − 新卡）** | **+386** | **+738** | 采购价差仍重要，但不再压过合约 |
| 资产栈（棕地 − 绿地） | +228 | +228 | 第三：电力/建筑沉没贡献有限 |
| 合约 × 代际交互 | **+806** | +670 | 新卡在无合同时被年化衰减打得更惨，长约的“保险价值”更大 |
| 合约 × 资产栈 / 代际 × 资产栈 | ≈0 | ≈0 | 近似正交 |

排序（频率修复后）：**合约 $\gg$ 代际 $>$ 资产栈**。旧表“代际 +1.45B $>$ 合约 +0.91B、交互 −446、八格全负”是 bug 路径，**只进附录 C**。修复后 **四格 NPV 为正**（全部 Contracted + 棕地×Merchant×二手）；CE 仍显示无合同新卡深度为负。模型并未证明一切价格组合均成立，只证明：**在正确年化衰减下，合同结构是第一杠杆，二手卡的 CAPEX 优势是第二杠杆。**

---

## 7 L4：Merchant、合同期限、Vintage、C4 与 Strategic

### 7.1 频率修复后的确定性路径

**表 7-1 Headline 确定性对照（频率修复后；B200 CAPEX 统一 \$60k/GPU）**

| 情景 | NPV \$M | Peak \$M |
|---|---:|---:|
| L3 | +707 | 317 |
| L4-M Spot \$4.25，$-22\%/\mathrm{年}$ | −1,623 | — |
| L4-M On-demand \$6.90 | −353 | — |
| L4-M mix-ref \$7.80，$-22\%/\mathrm{年}$ | **+78** | **2,362** |
| L4-M Dedicated \$9.36 | +826 | ~2,344 |
| C1 Fixed ToP \$9.36 | **+4,761** | 1,351 |
| C2 **真正** $-6\%/\mathrm{年}$ | **+3,844** | 1,351 |
| C1−C2 | **+917** | — |
| C3 **真正** $-15\%/\mathrm{年}$（list） | **+2,392** | 1,362 |
| C1 illustrative bulk \$7.02 | +2,885 | 1,404 |
| C2 bulk $-6\%/\mathrm{年}$ | +2,197 | 1,404 |
| **C4 3Y refresh-linked，list \$9.36** | **+1,915** | 527（tcv15）/ 1,373（cc150） |
| **C4 3Y refresh-linked，bulk \$7.02** | **+771** | 527（tcv15）/ 1,427（cc150） |
| L4-S Fixed \$9.36（backstop 已纠偏） | +5,285 | 438 |
| L4-S illustrative bulk \$7.02 | +3,278 | 500 |

C2 逐年价格：9.36 → 8.80 → 8.27 → 7.77 → 7.31。**温和 step-down 不摧毁合同；快速重定价才显著侵蚀。** C4 把 tenor 压到 36 个月并挂钩刷新：list 仍远高于 L3；bulk $7.02 点估计 +\$771M，但已明显低于 5 年锁价 C1/C2。**v5.0 C4 −\$821M 是频率 bug，禁止 Headline。**

tcv15 预付 = $15\%$ TCV（list 约 \$1,495M，bulk 约 \$1,121M），与 C1–C3 的 \$150M 预付不可比。**cc150 是与 C1–C3 对齐的资本口径**；Project NPV / All-risk CE 不随预付改变，只改变 Peak。对外引用 C4 的资本占用时，用 cc150。

融资与预付不改变 Project NPV，只压缩 Peak Equity。

### 7.2 Certainty Bridge（频率修复后）

**表 7-2 Certainty Bridge（v5.3 / `research_outputs/v5_2_rerun/`）**

| 步骤 | NPV \$M | $\Delta$NPV \$M | Peak Equity \$M |
|---|---:|---:|---:|
| 0 Merchant \$7.80 $-22\%/\mathrm{年}$ | +78 | — | 2,362 |
| 1 + Dedicated list \$9.36 $-22\%/\mathrm{年}$ | +826 | +747 | 2,344 |
| **2 + 5Y Fixed ToP \$9.36** | **+4,761** | **+3,936** | 2,206 |
| 3 + Contracted 融资 lev55 / $K_d$ 7 | +4,761 | 0 | 1,501 |
| 4 + Prepay ~\$150M | +4,761 | 0 | 1,351 |
| 5 + Backstop residual-only | +5,285 | +524 | 1,317 |
| 6 + GPU-backed lev70 / $K_d$ 5.9 | +5,285 | 0 | **438** |
| 7a Bulk \$7.02 Fixed C | +2,885 | — | 1,404 |
| 7b Bulk \$7.02 Fixed S | +3,278 | — | 500 |
| 8 C2 $-6\%/\mathrm{年}$ list \$9.36 | +3,844 | — | 1,351 |
| 9 C2 $-6\%/\mathrm{年}$ bulk \$7.02 | +2,197 | — | 1,404 |

**解读：** 最大单步仍是 **5 年固定价 ToP**（步骤 2，约 +\$3.9B），不是 list 价上调（步骤 1，约 +\$0.7B）。融资/预付把 Peak 从 \$2.2B 压到 \$0.44B——资本效率故事保留，但不是项目价值创造。v5.0 桥从 Merchant −\$3,175 / Peak \$5,494 起跳，是频率 bug 产物，**不得与本表混读**。

### 7.3 Vendor backstop

容量账本见 §4.2。原模型对 $1-u_{\mathrm{phys}}$ 计费造成约 **\$0.52B** 虚增，已修正。Backstop 是 Vendor 资产负债表上的或有义务，不是免费期权 [7][12][13]。

### 7.4 Investment Vintage（频率修复后）

**表 V1 Merchant Cohort（v5.3；租金路径为结构假设，置信度中等）**

| Vintage | 栈 | 入场 \$/GPU-h | NPV \$M | IRR |
|---|---|---:|---:|---:|
| H100-2023 | Greenfield | 4.50 | **−229** | 12.4% |
| H100-2024 | Greenfield | 3.80 | −749 | 6.1% |
| H100-2025 | Greenfield | 2.80 | −1,503 | −4.6% |
| H100-2026F | Greenfield | 3.20 | −1,531 | −6.9% |
| B200-2026F | Greenfield | 7.80 | **+78** | 16.0% |
| H100-2023 | GPU-only | 4.50 | **+360** | 20.6% |
| H100-2024 | GPU-only | 3.80 | −160 | 12.4% |
| B200-2026F | GPU-only | 7.80 | **+667** | 26.5% |
| B200-2026F dedicated | GPU-only | 9.36 | **+1,415** | 39.8% |

采购锚来自 IREN [15]。**不得写成“2023 Merchant 一定暴利”。** 相对排序支持 Vintage dependency。v5.0 同表 Greenfield 为 −2,156…−3,173，是频率 bug 路径，禁止引用。

### 7.5 C4 正式 All-risk（v6.1）

**表 7-3 C4 tech-refresh-linked（tenor=36，decay=−8%，billable=0.95，util=0.90；$N=10{,}000$）**

| 租金 | 预付口径 | 确定性 NPV | Peak | 客户资本 | All-risk CE | SBI | Loss |
|---|---|---:|---:|---:|---:|---|---:|
| list \$9.36 | tcv15 | +1,915 | 527 | 1,495 | **+1,128** | [1,116, 1,139] | 0.11% |
| list \$9.36 | **cc150** | +1,915 | **1,373** | 150 | **+1,128** | [1,116, 1,139] | 0.11% |
| bulk \$7.02 | tcv15 | +771 | 527 | 1,121 | **+181** | [172, 189] | 10.6% |
| bulk \$7.02 | **cc150** | +771 | **1,427** | 150 | **+181** | [172, 189] | 10.6% |

与 5 年 C1 list（确定性 +\$4,761）和 C bulk All-risk CE +\$1,670 相比，C4 明显更瘦：更短 tenor 提前释放价格风险，并与 refresh CAPEX 重叠。**仍远好于 v5.0 禁止引用的 −\$821；也仍低于 5 年锁价。** 对外资本占用用 cc150。

### 7.6 Financeability、信用压力与续约悬崖

**Headline 融资结构**用频率修复后数字：L4-S list Peak **\$438M**（NPV +\$5,285M）；bulk Peak **\$500M**（NPV +\$3,278M）。v5.0 的 L4-S +\$6,421 / Peak \$361 含未纠偏 backstop 与频率 bug，**不作 Headline**。

机制（确定性情景，方向成立）：

| 冲击 | 主要影响 | 读法 |
|---|---|---|
| 客户中途退出 | 收入跌回 Merchant / haircut | 信用风险，不是市场租金故事 |
| 去掉 NVIDIA backstop | 去掉 §7.2 步骤 5 的约 +\$524M | Vendor 义务有价 |
| 续约租金 −30% | 合同窗后现金流重定价 | Renewal Cliff |
| 融资冻结（$K_d$ 升、杠杆降） | **Project NPV 几乎不动**；Peak Equity 上升 | Sponsor 痛点是资本占用 |

**续约悬崖：** 5 年 ToP 到期与 3–5 年 GPU 刷新重叠时，残值、重定价、refresh CAPEX 与剩余债务同时出现。C4 把该重叠写进合同，代价是更低 CE。

---

## 8 All-risk CE（Headline 唯一横比口径）

同一风险分类、不同暴露。**$N=10{,}000$，seed=42，commit `e5fc8d7`。** 区间为 Simulation Bootstrap Interval，conditional on model assumptions。Headline L3 Generic CE **就是**表 8-1 的 +\$312M——Matched 不再另给一套 Generic。

**表 8-1 All-risk CE 与 SBI（v6.1）**

| 模式 | 确定性 NPV | $E[\mathrm{NPV}]$ | All-risk CE | SBI | Loss |
|---|---:|---:|---:|---|---:|
| L3 Critical IT | +707 | +672 | **+312** | **[280, 343]** | 1.87% |
| 全栈 Merchant \$7.80 | +78 | −143 | **−980** | **[−998, −961]** | 60.6% |
| GPU-only accounting | +667 | +446 | **−390** | **[−409, −371]** | 34.7% |
| GPU-only economic（付 L3 租金） | — | −92 | **−934** | **[−953, −915]** | 58.5% |
| C illustrative bulk \$7.02 | +2,885 | +2,534 | **+1,670** | **[1,632, 1,706]** | 0.42% |
| S illustrative bulk \$7.02 | +3,278 | +2,949 | **+2,112** | **[2,073, 2,147]** | 0.18% |

C 与 S 的 SBI 本轮不重叠，但弱于“C/S 相对 L3”（后者区间远不交叉）。可强说：**合同化算力显著优于 L3**。不得写 Strategic 损失率为零（观察 0.18%；Wilson 上界仍 $>0$）。相对 v5.5 $N=800$，点估计平移约 +\$13M（L3）、+\$49M（M）、+\$31M（C）、+\$45M（S）——排序不变，尾部估计更稳（5% ES 现由约 500 个样本决定，不再是约 40 个）。

**表 8-2 $\lambda$ 敏感性（同一 $N=10{,}000$ All-risk 样本；对 $\lambda$ 仿射）**

| 模式 | $\lambda=0$ | $\lambda=0.25$ | $\lambda=0.5$ | $\lambda=0.75$ | $\lambda=1$ |
|---|---:|---:|---:|---:|---:|
| L3 | +672 | +492 | **+312** | +132 | −48 |
| 全栈 M \$7.80 | −143 | −562 | **−980** | −1,398 | −1,816 |
| GO accounting | +446 | +28 | **−390** | −808 | −1,226 |
| GO economic | −92 | −513 | **−934** | −1,355 | −1,776 |
| C bulk | +2,534 | +2,102 | **+1,670** | +1,238 | +806 |
| S bulk | +2,949 | +2,531 | **+2,112** | +1,693 | +1,275 |

**C/S $>$ L3 $>$ M 在 $\lambda=0$ 到 $\lambda=1$ 均成立。** 高度风险厌恶不会推翻“合同化优于 L3”；只会削弱（仍为正）。全栈 Merchant 全 $\lambda$ 劣于 L3。$\lambda=1$ 时 L3 自身 CE 转负（尾部租户风险），C/S 仍为正。这是对“WACC-only / CE-only / WACC+CE”的部分稳健性替代，不是完整三轨引擎。

---

## 9 增量资本配置

### 9.1 Transfer Pricing

内部价默认 = L3 市场租金 **\$185/kW-月**（配置 `ready_rent_kw_mo` / TeraWulf 量级锚定）。该租金**不是**所有市场的统一机会成本。

**表 9-1 GPU-only 双口径（\$7.80；v6.1 $N=10{,}000$）**

| GPU-only 口径 | CE | $E[\mathrm{NPV}]$ | Loss | 相对 L3 |
|---|---:|---:|---:|---|
| Accounting（闲置、无租户） | **−390** [−409, −371] | +446 | 34.7% | 仍低于 L3 +312 |
| Economic（付 \$185/kW-月） | **−934** [−953, −915] | −92 | 58.5% | 明显劣于外租 |

**表 9-1b 经济口径 CE 平价随 L3 转移租金（$N_{\mathrm{grid}}=300$/点）**

| L3 转移租金 \$/kW-月 | GPU-only 经济口径 CE 平价 \$/GPU-h |
|---:|---:|
| 125 | **10.72** |
| 150 | 10.92 |
| **185（基准）** | **11.22** |
| 225 | 11.55 |
| 250 | **11.76** |

闲置矿场/无租户机房：Accounting 改善相对全栈 Merchant（CE −390 vs −980），但 **仍低于继续做 L3（+312）**。可出租 AI-ready 机房：自营 Merchant **明显劣于**把容量租出去。平价是一条缓升曲线，不是单点 \$11.32。

> 已有机房业主若放弃长期 L3 出租而自营 Merchant GPU，经济口径下需实现约 **\$10.7–11.8/GPU-h** 的风险调整租金（随所放弃的 L3 租金），才补偿租约与额外技术/利用率风险。

### 9.2 IRASR\_econ（主；三档筛选 EconCap）

L3：CE $+312\mathrm{M}$，Peak $\$317\mathrm{M}$。**IRASR\_econ 是理论首选；分母是筛选级 EconCap，不是已校准的银行经济资本。**

**表 9-2 L3 → L4 增量 IRASR（v6.1）**

| L3 → | $\Delta$CE \$M | IRASR\_econ Low | **Base（主）** | High | IRASR\_peak（次） |
|---|---:|---:|---:|---:|---:|
| 全栈 Merchant \$7.80 | −1,292 | −0.60 | **−0.59** | −0.56 | −0.63 |
| GPU-only accounting | −702 | −0.44 | **−0.43** | −0.41 | −0.46 |
| GPU-only economic | −1,246 | −0.77 | **−0.75** | −0.72 | −0.81 |
| C illustrative bulk | +1,358 | +1.11 | **+0.92** | +0.83 | +1.25 |
| S illustrative bulk | +1,800 | +5.31 | **+2.37** | +1.88 | +9.82（禁止作口号） |

三档符号稳定：无合同延伸全为负，合同化全为正。S 的 Low→High 从 5.31 收到 1.88，说明 **Strategic 对“担保/LC 是否双计”极度敏感**——这正是必须同时报三档、且禁止用 Peak 9.8 作口号的原因。C 相对稳健（1.11 / 0.92 / 0.83）。

reproduce 黄金 IRASR $\approx -0.94$ 对应 **legacy YAML $\approx\$5.63/\mathrm{GPU\text{-}h}$ 全栈路径**，与 Headline \$7.80 **不是同一假设**。

### 9.3 盈亏平衡（口径沿用 v5.5 确定性网格；CE 阈值方向不变）

| 指标 | L4-C Fixed | L4-S Fixed | L4-M $-22\%/\mathrm{年}$ |
|---|---:|---:|---:|
| NPV = NPV\_L3 | ~\$4.30 | ~\$4.02 | — |
| NPV = 0 | — | — | ~\$7.64 |
| Merchant NPV = L3 | — | — | ~\$9.11 |
| **CE = CE\_L3** | **~\$4.72** | **~\$4.22** | — |

决策优先 CE 阈值。表述应为：当 5 年 realized contract rate 高于约 \$4.7（C）或 \$4.2（S）时，在本模型 All-risk 设定下风险调整后优于 L3——**不是**主张真实成交价就是 \$7.02。

### 9.4 Matched Counterparty（同 shock，只改 PD）

Headline L3 Generic（PD 2%）**就是** +\$312M。IG 对照只把 PD 改为 0.8%，其余冲击流不变。

**表 9-3 同信用对照（All-risk CE \$M；$N=10{,}000$，同 seed）**

| 对象 | 信用代理 | All-risk CE |
|---|---|---:|
| L3 | Generic tenant（PD 2%，= Headline） | **+312** |
| L3 | IG / A–BBB+（PD 0.8%） | +434 |
| L4-C bulk | Generic（PD 4%，= Headline） | **+1,670** |
| L4-C bulk | **同 IG**（PD 0.8%） | **+1,922** |

- **Layer effect（同 IG）**：1,922 − 434 $=$ **+\$1,488M**  
- **Credit effect**：L3 升级 +\$122M；C 升级 +\$252M  
- L3 损失率（1.87%）高于 L4-C（0.42%），在**同信用**下仍成立（20 年租约 vs 5 年 ToP 的期限/尾部差异），**不是**因为给 L4 偷偷用了更好客户。

v5.5 表 9-3 的 L3 Generic +\$248M 来自另一套函数/种子，**作废**。

---

## 10 Sponsor Access Overlay

失败回退 = 继续做 L3：

$$EV_C=p_C\,\mathrm{CE}_C+(1-p_C)\,\mathrm{CE}_{L3}-\mathrm{PursuitCost},\qquad
p_C^{*}=\frac{\mathrm{PursuitCost}}{\mathrm{CE}_C-\mathrm{CE}_{L3}}.$$

$$\mathrm{PursuitCost}=\mathrm{Cash}+\mathrm{Delay}+\mathrm{OptionValueLost}+\mathrm{CommittedCapacityCost}.$$

因 $\mathrm{CE}_C,\mathrm{CE}_S\gg\mathrm{CE}_{L3}$，任何正的 $p$ 都提高期望值；真正阈值取决于全部追逐成本，不只是顾问费。

**表 10-1 盈亏平衡成功率（fallback = L3；v6.1 CE）**

仅现金：

| Pursuit 现金 \$M | $p_C^{*}$ | $p_S^{*}$ |
|---|---:|---:|
| 5 | 0.4% | 0.3% |
| 20 | **1.5%** | **1.1%** |
| 50 | 3.7% | 2.8% |
| 100 | 7.4% | 5.6% |

计入时滞与选择权（筛选加项，不是市场估计）：

| 现金 \$M | 时滞 | 时滞+选择权 \$M | 追逐合计 | $p_C^{*}$ | $p_S^{*}$ |
|---:|---:|---:|---:|---:|---:|
| 20 | 6 个月 | 15 | 35 | **2.6%** | **1.9%** |
| 50 | 12 个月 | 40 | 90 | 6.6% | 5.0% |
| 100 | 18 个月 | 80 | 180 | 13.3% | 10.0% |
| 200 | 24 个月 | 160 | 360 | **26.5%** | **20.0%** |

**1%–1.5% 只对应“纯现金顾问费、忽略等待”**。把土地承载、设备预留、设计冻结、排他期和错过的替代租户算进去，$p^{*}$ 立刻进入数个百分点到四分之一。结论方向不变——值得花有限费用追 ToP——但 **1% 不再是可操作的开发阈值**。

**表 10-2 类型化 Access EV（情景 $p$，不是估计的市场概率）**

使用 $\mathrm{CE}_M=-980$，$\mathrm{CE}_C=+1670$，$\mathrm{CE}_S=+2112$，$\mathrm{CE}_{L3}=+312$。

| 类型 | $p_C$ | $p_S$ | 含义 | 最优 |
|---|---:|---:|---|---|
| A Uncontracted | 0.10 | 0.02 | 低合同可得性 | **L3** |
| B Contract capability | 0.85 | 0.20 | 能拿 ToP，战略平台弱 | **S / C** |
| C Strategic platform | 0.95 | 0.70 | 合同 + Vendor + 融资 | **S** |

拿不到合同就留在 L3，**不必做 Merchant**。

---

## 11 讨论

### 11.1 与文献

资本流向 $\neq$ 回报来源 [1]：宏观向 GPU 堆积与微观 Sponsor CE 为负可以并存。衰减具有时变性 [6]；频率修复后 Forward Merchant 在 mix-ref 附近脆弱平衡，与“过去有人赚钱”不再矛盾，也**不**支持今天无合同全栈新建为默认。技术变量在租约锁定后降为二阶 [2]。LCOAI 等单位成本指标 [3] 回答的是算力成本，不是 Sponsor 在哪一层配置风险资本。

### 11.2 融资再分配 ≠ 价值创造

Project NPV 与 Equity NPV 仅在**统一贴现率**下可加总。若 Project CF 按 WACC、Equity CF 按 $K_e$、Debt CF 按 $K_d$ 分别贴现，三个 NPV 一般不能直接相减推出“债权人损失”。融资/预付压缩 Peak，不创造项目价值。C4 的 tcv15 与 cc150 共享同一 CE，是这条会计恒等式的直接证据。

任何商业模式都必须同时检查 Project、Equity 与 Debt 三个 NPV。仅报告 Equity IRR 的模型会系统性误导——尤其当 GPU-aware 杠杆把 Peak 压到极低时。

### 11.3 风险迁移与循环支持

| 模式 | 主要风险 |
|---|---|
| Merchant | 市场租金、利用率、技术、残值 |
| Contracted | 客户信用、合同执行、交付、续约 |
| Strategic | 客户/Vendor 信用与义务、结构化融资、集中度、循环支持 |

Market risk → Credit + Contract + Vendor + Structured-finance risk。NVIDIA 可能同时卖卡、入股、backstop、助力融资；需求下行时风险相关 [7][11][13]。单项目 CE 为正不消除系统集中度。

### 11.4 税务与备付金

直线折旧相对 MACRS/CCA 偏保守约 2–5%；DSRA 约压 Equity IRR 90bp 量级；L4 税务项即使按更激进口径调整，也不翻转 All-risk 下“无合同全栈 Merchant IRASR 为负、合同化路径为正”的排序。

### 11.5 L5 边界

L5a 的 \$/IT-kW-h 输入是 token 经济学的**收入等效**，不是 GPU→tokens→\$/M tokens 的完整单位经济。表 4 频率修复后 L5a YAML 路径转为 +\$927，**只说明旧深负是 bug 路径的连带产物**，不构成托管推理的 Headline 结论。L5b 上模型层 API 收入与租金成本可呈数倍差 [6]——价值归属模型层，与 L4/L5a 基础设施回报为负互洽。**“基础设施投资人自持 GPU 做 Compute Rental”为负，不构成“AI Factory 不赚钱”。**

### 11.6 实践

对土地/电力/许可占优的开发商：

$$\mathrm{Power\text{-}secured}\rightarrow\mathrm{AI\text{-}ready}\rightarrow\mathrm{Tenant/Compute\ Contract}\rightarrow\mathrm{GPU}.$$

即 **GPU deployment should be demand-led, not inventory-led.** 闲置矿场用 Accounting 口径；可出租 Virginia/Texas AI-ready 厂房用 Economic 口径。Type A 默认 L3；Type B/C 在合同落实后进入 C/S。

### 11.7 局限性

筛选级精度；直线折旧；单一美元；相关矩阵经验设定（$\rho(\mathrm{rent},\mathrm{residual})=0.6$，其余 0.25）；Gaussian copula 会低估联合尾部（需求塌 + GPU 崩 + 电价飙），student-t / vine 为后续工作；Historical 租金路径非完整回测；Counterparty PD 为情景而非评级校准；EconCap 为三档筛选原型、非 term-sheet；$7.02$ 为作者假设、realized rate 未校准；Financeability 压力网格未独立正式重跑；L5a 非严格 token 单位经济；交易级样本外验证未完成；WACC 与 CE 的重叠无法完全排除；Pursuit 时滞加项为情景。模型默认 **powered / permitted land 为给定输入**，并网排队、电网升级、审批与 NVIDIA 分配等执行风险未定价。SBI **不**覆盖上述参数不确定性。Headline S 的 +$2.11B 冻结于 legacy 0.375 补偿，不是 1.2.1 residual-unsold + 0.75 的重跑。

---

## 12 结论

把发现拆成两类。第一类跨周期成立，不随 2026-08 参数包滚动；第二类是当前参数下的点估计，市场一变就更新。

### 12.1 Structural Findings（跨周期）

- **Role** 决定现金流归属。  
- **Stack** 决定机会成本（沉没成本 ≠ 零机会成本）。  
- **Vintage** 决定进入成本与周期暴露；Historical Winner ≠ Forward Winner。  
- **Contract** 把 market risk 转化为 credit / execution / renewal risk。  
- **Capital Structure** 与 Vendor Support 决定 Sponsor 占用多少经济资本；融资再分配 ≠ 价值创造。  
- **Market State** 决定 Forward 租金、衰减与利用率路径。  
- **Access** 决定某个 Sponsor 是否能获得该结构；失败回退是 L3，不是 Merchant。  
- 在正确年化衰减下，**合同结构是第一杠杆**；代际/采购价是第二杠杆；资产栈第三且近似正交。

### 12.2 2026-08 Parameter Findings（随市场滚动）

- L3 All-risk CE **+$312M** [280, 343]。  
- 全栈 Merchant $7.80 CE **−$980M** [−998, −961]；IRASR\_econ Base **−0.59**。  
- GPU-only accounting CE **−$390M**；economic **−$934M**；经济口径平价 **$10.7–11.8/GPU-h**。  
- C bulk $7.02 CE **+$1,670M** [1,632, 1,706]；IRASR\_econ Base **+0.92**（Low 1.11 / High 0.83）。  
- S bulk $7.02 CE **+$2,112M** [2,073, 2,147]；IRASR\_econ Base **+2.37**（High 仍 +1.88）。  
- Matched layer effect（同 IG）**+$1,488M**。  
- C4 list CE **+$1,128M**；bulk CE **+$181M**。  
- 计入时滞后 $p_C^{*}$ 从现金 1.5% 升至 2.6%–26.5%。  
- 电力层 P1 EqIRR **14.1%**；L3 确定性 NPV **+$707M** / Peak **$317M**。

**RQ1–RQ6（压缩）** 统一口径下 P1 是基础设施回报，L3 是无合同 structural 默认，全栈 Merchant 点估计或近 BE 但 CE/IRASR 为负，C/S 在 illustrative bulk 下 CE 显著高于 L3。延伸拐点在“有没有可融资的合同”，不在“卡新不新”。2×2×2 修复后主效应为合约 $\gg$ 代际。C/S 购买的是确定性与资本效率。可出租机房必须扣 L3 机会成本。

$$\boxed{\mathrm{Asset\ Value}\neq\mathrm{Hardware\ Value}}$$

同一张 GPU：Merchant 下是高折旧、高波动的技术资产；Contracted 下是合同支持的算力基础设施；Strategic 下是 Vendor 支持、机构可融资的 AI 基础设施资产。

**后续（结构已冻、校准继续）：** 交易锚定 realized rate；EconCap 的 term-sheet 校准；realized cohort / OOS；Financeability 网格正式重跑；L5a token 引擎；双轨贴现率归属；完整 WACC-only / 未杠杆+CE 三轨。

---

## 参考文献

[1] McKinsey & Company. *The Cost of Compute: A $7 Trillion Race to Scale Data Centers*. 2025-04-28. https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/the-cost-of-compute-a-7-trillion-dollar-race-to-scale-data-centers  
[2] He, Q. *A Unified Metric Architecture for AI Infrastructure*. arXiv:2511.21772, 2025. https://arxiv.org/abs/2511.21772  
[3] Curcio, E. *Introducing LCOAI*. arXiv:2509.02596, 2025. https://arxiv.org/abs/2509.02596  
[4] Morgan Stanley Research. *Bridging a $1.5tr Data Center Financing Gap*. 2025-07-16.  
[5] CoreWeave, Inc. Form S-1 (initial public offering registration) and Form 10-K: committed contracts, take-or-pay, customer prepayments, asset-level debt. U.S. SEC.  
[6] SemiAnalysis. GPU rental / Tokenomics notes; reported H100 1-year contract ~\$1.70→\$2.35 (~+40%). Accessed 2026-08.  
[7] CoreWeave, Inc. Form 8-K (NVIDIA residual unsold capacity obligation through 2032). U.S. SEC.  
[8] TeraWulf Inc. *TeraWulf and Anthropic Announce 20-Year, 401 MW AI Infrastructure Agreement*. Investor release / GlobeNewswire, 2026-07-06；Greenlight Electricity Centre public reporting (932 MW / CA\$4.6B).  
[9] CoreWeave DDTL 4.0 facility: ~5.9% fixed / SOFR+2.25% (lender materials / company disclosure).  
[10] NVIDIA Corporation. \$2B strategic investment in CoreWeave. 2026-01.  
[11] NVIDIA Corporation. Compute Financing Platforms announcement (>$500B third-party platforms). 2026-08-10.  
[12] Reuters / The Wall Street Journal. Reporting on a proposed NVIDIA–OpenAI support package of about \$250B. 2026-07-26. (**proposed**)  
[13] Reuters / The Wall Street Journal. Subsequent reporting that an initial tranche may be less than \$120B. 2026-08-14. (**proposed / under discussion**)  
[14] WNT Energy. Rack-ready increment / anonymized brownfield calibration (internal actuals; public bundle anonymized).  
[15] IREN Limited. SEC disclosures of H100 purchases (August 2023; February 2024).  
[16] CoreWeave. *Pricing* (HGX H100/B200 On-demand and Spot). Retrieved 2026-08. https://www.coreweave.com/pricing  
[17] Lambda. *Pricing / 1-Click Clusters* (H100/B200 Instance and Dedicated). Retrieved 2026-08. https://lambda.ai/pricing  

**\$7.02/GPU-h $=9.36\times 0.75$：作者 Illustrative Bulk 假设，不是市场成交事实。**

---

## 附录 A — 复现

```bash
cd aidc-optimizer
python reproduce.py check                 # 黄金回归（legacy YAML；L4 ≈ −$964M）
python research_v6_factorial_fixed.py     # 表 5
python research_v6_1.py --stage l3        # 其后 m / go / c / s / matched / c4a–d / post
python research_v5_2_rerun.py             # 表 7-2 / V1（确定性，未改）
```

| 文件 | 内容 |
|---|---|
| `research_outputs/v6_1/factorial_2x2x2_fixed.csv` | 表 5 八格 |
| `research_outputs/v6_1/factorial_effects_fixed.csv` | 表 5 主效应 |
| `research_outputs/v6_1/allrisk_n10000.csv` | 表 8-1 |
| `research_outputs/v6_1/lambda_sensitivity_n10000.csv` | 表 8-2 |
| `research_outputs/v6_1/irasr_econ_bands.csv` | 表 9-2 |
| `research_outputs/v6_1/transfer_rent_parity_curve.csv` | 表 9-1b |
| `research_outputs/v6_1/matched_counterparty.csv` | 表 9-3 |
| `research_outputs/v6_1/access_pstar_delay.csv` | 表 10-1 时滞档 |
| `research_outputs/v6_1/v6_1_summary.json` | Headline 汇总（含 commit/seed） |
| `research_outputs/v5_2_rerun/certainty_bridge_fixed.csv` | 表 7-2 |
| `expected_outputs/alberta.json` | v3.3 黄金（表 3；表 4 的 L0–L3.5） |

## 附录 B — 模型审计摘要

| 项 | 状态 |
|---|---|
| GPU 年化衰减按月指数 | **已修** $(1+g)^{k/12}$ |
| 2×2×2 在修复路径上重跑 | **v6.1 已完成**；排序改为合约 ≫ 代际 |
| 表 4 L4 −\$3,351 | **已换** −\$964 / Peak \$755；旧值进附录 C |
| All-risk $N=10{,}000$ | **v6.1 Headline** |
| EconCap Low/Base/High | **已给**；仍为筛选原型 |
| Matched 与 Headline 同 shock | **已统一**；L3 Generic = +312 |
| C4 正式重跑 | **已完成**；禁止 −821 |
| Backstop 双重计费 | **已修** residual unsold only |
| Transfer rent 曲线 | **已给** \$125–250 |
| Access 时滞/选择权 | **已给** 6–24 个月档 |
| Bootstrap 改称 SBI | **已改** |
| “开源” vs private repo | **已改**为可复现实现 |
| “冻结核心算法” | **已改**为冻结核心结构 |
| Realized bulk rate | **未校准**（刻意不编造） |

## 附录 C — 数字来源对照（防混用）

| 数字 | 来源 | 可否作 Headline |
|---|---|---|
| L3 NPV +707 / Peak 317 | v3.3 表 4 | 是 |
| L3 All-risk CE +312 [280, 343] | v6.1 $N=10\mathrm{k}$ | **是（唯一 L3 CE）** |
| L3 All-risk CE +299 [193, 407] | v5.5 $N=800$ | 历史对照 |
| Merchant \$7.80 NPV +78 / Peak 2,362 | v5.3 Bridge | 是 |
| Merchant All-risk CE −980 [−998, −961] | v6.1 | **是** |
| C bulk CE +1,670 / S +2,112 | v6.1 | **是** |
| IRASR\_econ C +0.92 / S +2.37（Base） | v6.1 三档 | **是（注明筛选 EconCap）** |
| 表 5 合约 +1,658 / 代际 +386 / 栈 +228 | v6.1 factorial | **是** |
| 表 5 旧代际 +1,450 / 合约 +909 / 交互 −446 | v3.3 bug 路径 | **否** |
| 表 4 L4 −964 / Peak 755 | 频率修复 YAML | 七模式结构表 |
| 表 4 旧 L4 −3,351 / Peak 1,097 | v3.3 bug 路径 | **否** |
| C4 list CE +1,128 / bulk +181 | v6.1 | **是** |
| C4 −821 | v5.0 | **否** |
| C1 +4,761 / C2 +3,844 / Δ +917 | v5.2/v5.3 | 是 |
| L4-S list +5,285 / Peak 438 | v5.3 | 是 |
| L3 Generic +248（v5.5 Matched） | 不同 seed | **否** |

## 附录 D — Parameter Source（节选）

| parameter | base | unit | source | date | evidence | confidence | low | high | notes |
|---|---:|---|---|---|---|---|---:|---:|---|
| ready_rent_kw_mo | 185 | \$/kW-mo | TeraWulf–Anthropic ≈197；config | 2026-07 | Level 2 | med | 125 | 250 | 表 9-1b 已做曲线 |
| gpu all-in | 60,000 | \$/GPU | screening；0.533 GPU/IT-kW | 2026-08 | Level 3 | med | — | — | 系统价，非裸卡 |
| mix-ref rate | 7.80 | \$/GPU-h | non-spot public blend [16][17] | 2026-08 | Level 2 | med | 6.90 | 9.36 | **不是现货中位** |
| illustrative bulk | 7.02 | \$/GPU-h | $9.36\times 0.75$ | 2026-08 | **Author** | low | — | — | **未交易锚定** |
| merchant decay | −0.22 | /year | structural long-run | 2026-08 | Level 3 | low | −0.30 | −0.05 | 短缺市可更浅 |
| C/S decay | 0 / −0.08 | /year | contract / C4 | 2026-08 | Level 3 | med | — | — | C4 用 −8% |
| L3 PD | 0.02 | — | screening | 2026-08 | Author | low | 0.008 | 0.04 | Matched 只改此项 |
| C PD | 0.04 | — | screening | 2026-08 | Author | low | 0.008 | 0.08 | 同上 |
| λ | 0.50 | — | Sponsor tail weight | — | Author | — | 0 | 1 | 表 8-2 |
| EL haircut | 0.30 | — | EconCap Base | — | Author | low | 0.15 | 0.50 | 三档已报 |
| seed / N / commit | 42 / 10k / e5fc8d7 | — | `research_v6_1.py` | 2026-08-15 | — | — | — | — | 可复现标签 |

---

**利益声明**：作者所属机构从事北美 BTM 电力与数据中心开发；P3 套利情景与业务方向相关，已与市场一致 P1 分离。参数含机构实盘造价的脱敏公开包。

**AI 辅助披露**：模型、分析与文稿由 AI 辅助；Headline 数值可由 `research_v6_1.py` / `research_v6_factorial_fixed.py` 复现（seed=42，commit `e5fc8d7`）。v6.0 保留为合并快照；v6.1 只滚动校准与样本量，不改核心方程。
