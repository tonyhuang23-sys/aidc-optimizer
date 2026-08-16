# 面向AI基础设施的价值链投资评估模型：经济角色、投资时点、资产栈、合约结构与资本结构共同决定的风险调整资本配置框架

## A Value-Chain Investment Evaluation Model for AI Infrastructure: A Risk-Adjusted Capital Allocation Framework Determined by Role, Investment Vintage, Asset Stack, Contract Structure and Capital Structure

**作者**: WNT Energy 技术研究组  
**日期**: 2026年8月  
**状态**: 工作论文 **v6.0**（完整正文合并版）  
**版本记录**: v1–v3.3 建立 Role×Stack×Contract 框架、双引擎、CE-NPV/IRASR、2×2×2 与复现黄金结果；v4.0 将 L4 拆为 Merchant/Contracted/Strategic；v5.0–v5.2 引入 Investment Vintage，并修复 GPU 年化衰减被误作月化复利的 P0-0 频率错误；v5.3–v5.5 完成 All-risk CE 统一、Transfer Pricing、Matched Counterparty、IRASR_econ 主指标与 Access overlay。**v6.0 将上述数字与完整 Working Paper 结构合并，冻结核心算法叙事；后续仅更新市场参数与样本量。**

**代码与复现**: `https://github.com/tonyhuang23-sys/aidc-optimizer`（private）— `aidc_optimizer/`、`research_l4.py`、`research_v5_2_rerun.py`、`research_v5_4.py`、`research_v5_5.py`、`reproduce.py`。Headline 风险调整数字以 `research_outputs/v5_5/` 为准；确定性 / Vintage / Certainty Bridge 以 `research_outputs/v5_2_rerun/` 为准。

**口径纪律（读表前必读）**

1. **Peak Equity 禁止混用。** v5.0 全栈 Merchant Peak 约 $5.5B 对应频率 bug 下的深负路径；频率修复后 mix-ref $7.80 路径 Peak 为 **$2,362M**。本文 Headline 只用后者。  
2. **CE 体系禁止混用。** Headline 横比只用 All-risk CE（v5.5，$N=800$）。v3.3 独立租金 MC 的 L3 CE +$505M、v5.4 点估计 +$248M 不再作对外引用。  
3. **$7.02/GPU-h $=9.36\times 0.75$** 是作者 Illustrative Bulk 情景，**不是成交数据**。  
4. **七模式表与 2×2×2 的 L4 格子** 来自 v3.3 黄金路径（legacy YAML $\approx\$5.63/\mathrm{GPU\text{-}h}$），**不是** Headline $7.80$ 路径。两套数字并列时脚注必须同时出现。

---

## 摘要

人工智能数据中心（AIDC）投资常被简化为单一“数据中心 IRR”或静态“甜蜜点”。本文以统一 100 MW 参考项目为测试平台，将 **经济角色（Role）、投资时点（Investment Vintage）、资产栈（Asset Stack）、合约结构（Contract）、资本结构（Capital Structure）与市场状态（Market State）** 纳入同一套资产层—融资层双引擎，并用确定性等价

$$\mathrm{CE\text{-}NPV}=(1-\lambda)\,E(\mathrm{NPV})+\lambda\,\mathrm{ES}^-_{5\%}(\mathrm{NPV})$$

与增量风险调整股本回报

$$\mathrm{IRASR}_{\mathrm{econ}}=\frac{\Delta\mathrm{CE\text{-}NPV}}{\Delta\mathrm{Sponsor\ Economic\ Capital}}$$

作为 Sponsor 资本配置规则。决策分两步：先评估**资产本身**的 $V_i$，再叠加**该 Sponsor 获得该结构的概率、追逐成本与失败回退**。

在 2026-08 参数、频率修复后的年化衰减、统一 B200 系统口径（约 $60\mathrm{k}/\mathrm{GPU}$）以及 All-risk 蒙特卡洛（筛选级 $N=800$，Bootstrap 95% CI）下，主要结果是：

1. **电力层**市场一致组合（新建 CCGT + 投资级 tolling）Equity IRR 约 **14.1%**；广为引用的约 28% 来自“二手设备 × 溢价长约”套利，二者约 14 个百分点的差是可检验的市场命题，不是模型缺陷。  
2. **L3 Critical IT** 是无算力合同能力时的 **structural sweet spot**：项目 NPV 约 **+$707\mathrm{M}$**，All-risk CE 约 **+$299\mathrm{M}$**（CI **[$193\mathrm{M}$, $407\mathrm{M}$]**）。  
3. **全栈 Merchant（Power+DC+GPU）** 在 mix-ref $7.80/\mathrm{GPU\text{-}h}$、年化 $-22\%$ 衰减下点估计接近盈亏平衡（NPV 约 **+$78\mathrm{M}$**），但 All-risk CE 约 **$-1.03\mathrm{B}$**，IRASR\_econ 约 **$-0.55$**——**不是默认策略**。$7.80$ 是非现货公开报价的**产品组合参考**，不是纯现货中位。  
4. **GPU-only** 必须做转移定价：机房闲置（accounting）时 CE 约 **$-439\mathrm{M}$**；若机房可按 L3 市场租金 **$185/\mathrm{kW\text{-}月}$** 外租（economic），CE 约 **$-949\mathrm{M}$**。与 L3 的 CE 平价分别约 **$9.75$** 与 **$11.32/\mathrm{GPU\text{-}h}$**。**沉没成本 ≠ 零机会成本。**  
5. **合同化算力**（Illustrative bulk $7.02=0.75\times 9.36$，**作者情景假设，非成交数据**）：L4-C All-risk CE 约 **+$1.64\mathrm{B}$**（CI **[$1.51\mathrm{B}$, $1.77\mathrm{B}$]**），L4-S 约 **+$2.07\mathrm{B}$**（CI **[$1.93\mathrm{B}$, $2.21\mathrm{B}$]**）。同信用（Matched Counterparty）下 C 相对 L3 的 **layer 效应约 +$1.57\mathrm{B}$**，主要来自合同结构而非“客户更好”。  
6. **真正 $-6\%/\mathrm{年}$ 的 step-down** 并不摧毁合同：C2 NPV 约 **+$3.84\mathrm{B}$**，相对固定价 C1 的锁价溢价约 **+$0.92\mathrm{B}$**（频率 bug 修复前曾被夸大为 +$5.1\mathrm{B}$）。较快重定价 C3（$-15\%/\mathrm{年}$，list）仍约 **+$2.39\mathrm{B}$**。  
7. **资本配置主指标是 IRASR\_econ**（C 约 **$+0.72$**，S 约 **$+1.29$**）。Strategic 的 Peak IRASR $\approx 9.6$ 是杠杆压低现金股本的结果，**不得作对外口号**。  
8. **Sponsor overlay**：失败回退为继续做 L3 时，Pursuit $20\mathrm{M}$ 对应的盈亏平衡成功率仅约 **$1\%\text{–}1.5\%$**——值得花有限费用追 take-or-pay；拿不到则留在 L3，不必被迫做 Merchant。

**主结论：** 最优层级不是价值链的固定属性。同一张 GPU，因 Vintage、Stack、Contract 与 Capital Structure 不同，可以是高波动技术资产，也可以是可融资的 AI 基础设施资产。**GPU 部署应需求驱动（contract-first），而非库存驱动（buy-first）。**

**关键词**: AI 基础设施；Deliverable MW；Investment Vintage；Merchant / Contracted / Strategic；take-or-pay；All-risk CE；IRASR\_econ；Transfer Pricing；GPU-backed 融资

---

## Abstract

AIDC investment is often reduced to a single “data-center IRR.” This paper evaluates seven business modes on a unified 100 MW platform with a two-tier asset–financing engine and two decision metrics: certainty-equivalent NPV and incremental risk-adjusted sponsor return on **economic capital**. Asset value is $V_i=f(\mathrm{Role},\mathrm{Vintage},\mathrm{Stack},\mathrm{Contract},\mathrm{Capital},\mathrm{Market})$; sponsor choice overlays access probability, pursuit cost and fallback.

After correcting an annual-to-monthly decay bug, unifying B200 all-in CAPEX, restricting vendor backstop to residual unsold capacity, and scoring all modes on one All-risk taxonomy ($N=800$ screening; bootstrap CIs): the market-coherent power layer earns ~14.1% equity IRR; L3 Critical IT is the structural default (CE ~+$299\mathrm{M}$); full-stack Merchant at a **non-spot mix-reference** $7.80/\mathrm{GPU\text{-}h}$ is near NPV breakeven but deeply CE-negative; GPU-only improves the stack boundary but, once L3 market rent is charged, still fails L3 opportunity-cost parity below ~$11/\mathrm{GPU\text{-}h}$; illustrative bulk contracted/strategic compute ($7.02=0.75\times 9.36$, **author scenario**) remains CE-superior to L3, and a matched-counterparty test attributes most of the gap to **contract structure**, not better names. IRASR on economic capital is the headline allocation rule. GPU deployment should be demand-led.

---

## 1 引言

### 1.1 研究背景

自 2024 年起，AI 基础设施进入史无前例的资本扩张期：到 2030 年全球数据中心资本需求约 6.7 万亿美元（AI 相关约 5.2 万亿）[1]；2025–2028 年数据中心资本开支约 2.9 万亿美元、外部融资缺口约 1.5 万亿 [4]；评级机构已对近 1,000 亿美元数据中心相关债评级 [5]。与此同时，GPU 租赁出现 Spot / Instance / Dedicated Cluster 分层 [16][17]，NVIDIA 宣布动员超过 5,000 亿美元的第三方 compute financing platforms [11]，CoreWeave 等以多年期 take-or-pay 与 GPU-backed 债务运营 [5][7][9]。行业正在从“买卡赌周期”转向“合同化—信用化—金融化”。

对投资人更根本的问题是：**对同一可按时交付的兆瓦级电力与场址，应当投到哪一层、以何种资产栈与合约、在哪个时点进入、在哪个节点退出？**

### 1.2 研究问题

> **RQ1** 七种商业模式（含 L4-M/C/S）的投资强度、回报与风险敞口如何在统一口径下比较？  
> **RQ2** 价值链延伸的 IRASR 在何处由正转负？该拐点如何随 Vintage、Stack 与合同移动？  
> **RQ3** 最优层级在多大程度上由 Role、Vintage、Stack、Contract 与 Capital Structure 共同决定？  
> **RQ4** 公开市场价与 CoreWeave 式资本结构下，L4 何时从毁灭价值转为创造价值？  
> **RQ5** Historical Merchant 与 Forward Merchant 差多大？Contracted/Strategic 购买的是更高均值还是更高确定性？  
> **RQ6** 已有 L3 机房再装 GPU 时，是否应扣除放弃外租的机会成本？

### 1.3 贡献

本文不声称发明 CVaR、copula 或项目融资工具。贡献在于：（1）把分散在工程、云计算、项目融资与 AI 经济学中的工具整合成 **Sponsor 级资本配置框架**；（2）严格分离 Historical / Forward 回报，并将 L4 重构为 Merchant / Contracted / Strategic；（3）用 All-risk CE 与 IRASR\_econ 给出可横比的延伸规则，并用 Transfer Pricing 与 Matched Counterparty 防止“免费占用 L3”和“更好客户冒充更好层级”；（4）开源可复现实现与黄金结果校验。

### 1.4 本稿范围

v6.0 **不扩张框架**。它把 v3.3 完整实证表、v5.0 方法引擎说明、v5.3 频率修复后确定性结果与 v5.5 Headline 风险调整数字合并为一篇可独立阅读的 Working Paper。明确列为冻结后工作、本稿不重跑的项目：All-risk $N=10{,}000$、EconCap 校准、交易级样本外验证、L5a token 引擎、双轨贴现率归属的系统输出。

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

100 MW 发电、PUE 1.25 → 80 MW Critical IT。GPU 层同时报告 \$/IT-kW-h 与 \$/GPU-h。B200 换算 **0.533 GPU/IT-kW**；H100 约 0.78。All-in Compute CAPEX 统一为约 **\$60,000/GPU**（\$31,980/IT-kW）。原 Strategic 桥中的 \$21.3k/IT-kW **移出 Base**。GPU 折扣 0/10/20/30% 仅作 Sensitivity，无一手文件不得进入 Base。

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

在 NPV Value Bridge 之上，逐步报告 $E(\mathrm{NPV})$、$ES_5^-$、CE-NPV、$P(\mathrm{loss})$、Peak Equity、合同窗 DSCR。步骤顺序固定为：Merchant 基准 → Dedicated list 价 → 5 年 Fixed ToP → Contracted 融资 → 预付 → residual-only backstop → GPU-backed 杠杆 → bulk / step-down 对照。目的是证明 Contracted/Strategic 购买的是 **risk-adjusted certainty**，而不只是更高平均收入。融资与预付在统一项目贴现率下 **不改变 Project NPV**，只压缩 Peak Equity。

### 4.5 Contract Financeability 引擎

输入：客户信用档、tenor、take-or-pay%、预付%、backstop、集中度。输出：max leverage、$K_d$、debt tenor、min DSCR。形成

$$\mathrm{Contract}\rightarrow\mathrm{Cashflow\ visibility}\rightarrow\mathrm{Bankability}\rightarrow\mathrm{Debt\ capacity}\rightarrow\mathrm{Peak\ Equity}$$

的传导。筛选映射：IG + 5 年 + 高 ToP + 预付 + backstop → lev $\approx 70\%$、$K_d\approx 5.9\%$、tenor 60 月；Unrated / 短约 / 无保底 → lev $\approx 35\%$、$K_d\approx 9.5\%$。Financeability 不是辅助维度，而是资产价值本身的构成部分。

续约悬崖（Renewal Cliff）：合同到期与 GPU 刷新周期（均约 3–5 年）重叠时，残值、续约重定价、refresh CAPEX 与剩余债务同时冲击，必须单独压力测试。

### 4.6 风险调整

$$ES^-_{5\%}(\mathrm{NPV})=E[\mathrm{NPV}\mid \mathrm{NPV}\le P_5],\quad
\mathrm{CE\text{-}NPV}=(1-\lambda)E(\mathrm{NPV})+\lambda\,ES^-_{5\%}.$$

分层 WACC 补偿系统性风险；$\lambda\cdot ES$ 补偿项目特异左尾，二者不重复惩罚。Headline 用 **All-risk** 分类（租户/客户违约、GPU 租金、利用率、残值、Vendor、再融资），各模式仅 **Exposure** 不同：

| Risk | L3 | L4-M | L4-C | L4-S |
|---|---|---|---|---|
| Tenant / customer default | ✓ | — | ✓ | ✓ |
| GPU rent | — | ✓ 高 | fallback / haircut | fallback / haircut |
| Utilization | — | ✓ 高 | ToP 锁定 | ToP 锁定 |
| Residual | — | ✓ 高 | 轻 | 轻 |
| Vendor failure | — | — | 低 | ✓ backstop |
| Refinancing | ✓ | ✓ | ✓ | ✓ |

筛选级 $N=800$；正式冻结建议 **$N=10{,}000$**。报告 Bootstrap 95% CI（2000 次）。$\lambda=0.5$ 为正文，并报告 $\lambda\in\{0,0.25,0.5,0.75,1\}$。

主资本配置指标

$$\mathrm{IRASR}_{\mathrm{econ}}=\frac{\Delta\mathrm{CE}}{\Delta\mathrm{EconCap}},\quad
\mathrm{EconCap}=\mathrm{PeakCashEquity}+\mathrm{GuaranteeEq}+\mathrm{LC}+\mathrm{Reserve}.$$

Peak IRASR 为次要。EconCap 附加项为筛选比例假设，**框架完成、校准待完成**。

### 4.7 价格命名纪律

| 标签 | \$/GPU-h | 含义 |
|---|---:|---|
| M1 Spot | 4.25 | 现货 [16] |
| M2 On-demand | 6.90 | 短周期实例 [17] |
| Mix-ref non-spot | 7.80 | 非现货公开报价**混合参考**，**不是纯现货中位** |
| M3 / list dedicated | 9.36 | Lambda 64-GPU cluster list [17]；合同 **上界** |
| **Illustrative bulk** | **7.02** | **$=9.36\times 0.75$，作者情景假设，非成交数据** |
| Legacy YAML | $\approx 5.63$ | `rate_per_kw_hr=3.0`，仅 reproduce 回归 |

**禁止再写：** “Merchant @ public median $7.8 接近盈亏平衡 = 现货市场可做”。  
**应写：** “在 mix-ref $7.8 与 $-22\%/\mathrm{年}$ 下全栈点估计接近 BE，但 All-risk CE 仍显著为负。”

### 4.8 实现

Python 双引擎约 2,000 行 + 研究脚本。`reproduce.py check` 校验 v3.3 黄金路径（频率修复后基准 L4 NPV 约 $-\$964\mathrm{M}$，IRASR 约 $-0.94$，对应 legacy YAML 租金，**不是** Headline $7.80$ 路径）。

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

### 5.2 Level B — 内部验证

Sources = Uses（偏差 $0.00$）、债务滚动期末清零、杠杆与 LTC 对齐（IDC 解释差额）、GPU 期限匹配、IRR/NPV 解析解 $<10^{-9}$、现金流符号转换次数 $\le 1$。频率审计：电力/租约 escalator 本就按年；GPU `rate_decay` 已改为 $(1+g)^{k/12}$。

### 5.3 Level C — 合理性检验

DGX 价格带、公开 GPU 租金、REIT/项目融资杠杆对照为 plausibility，**不是**交易级样本外预测。$\ge 5$ 笔未参与定参交易的 Prediction-vs-Actual 仍为后续工作。

### 5.4 证据等级

Level 1 监管/官方可作 Base；Level 2 高质量媒体必须标 proposed；Level 3 情报保留置信度。禁止将拟议担保写成已完成融资，禁止将未证实 GPU 折扣写成事实。

---

## 6 电力层与 L0–L3.5 结果

### 6.1 电力层参数一致性

v2.0 把 28% Equity IRR 当作电力层普遍基准，隐含“最低 CAPEX（二手 9E）+ 最高质量合同（溢价长约）”。现实中二者存在约束：二手设备对应更短剩余寿命与更高利差，投资级长约通常要求新建高规格资产。本文将该层拆为三个一致性情景。

**表 3 电力层参数一致性（100 MW，Alberta）**

| 情景 | 组合 | NPV \$M | Project IRR | Equity IRR | 经济性质 |
|---|---|---:|---:|---:|---|
| **P1 市场一致** | 新建 CCGT \$3,500/kW + IG tolling \$28/kW-月 + 5.8% | +104 | 11.0% | **14.1%** | Greenlight 型基础设施回报 |
| P2 桥接 | 二手 GT \$1,150 + 中期约 \$12/kW-月 + 8.5% | +129 | 16.9% | 19.2% | 商业燃机市场常态 |
| P3 套利 | 二手 GT + 溢价长约 \$18/kW-月 | +191 | 21.1% | **28.0%** | 设备 × 合约套利（upside） |

约 14 个百分点差额量化“能否以二手设备拿到投资级溢价长约”。**后续一律以 P1 为市场一致基准。** IDC 由融资层单独计（P1 约 \$7M，占 CAPEX 1.9%），overnight 与融资成本不双计。若将 Greenlight CA\$4.6B 解读为含融资全包，overnight 等价约 \$3,430/kW，P1 EqIRR 约 +0.2–0.3pp，结论不变。

### 6.2 七模式基准（Alberta；电力为 P1）

**表 4 基准结果（电力层 P1；2026-08 参数；Peak Equity 统一口径）**

| 模式 | CAPEX \$M | Peak Equity \$M | Project IRR | Equity IRR | NPV \$M | 观察损失率 [Wilson 95% CI] |
|---|---:|---:|---:|---:|---:|---|
| 开发退出† | 20 | 20 | — | — | +5 | 13.9% [12.2–15.7%] |
| Power-only（P1） | 368 | 133 | 11.0% | 14.1% | +104 (245) | 低 |
| Powered Shell | 469 | 238 | 12.5% | 14.4% | +87 (79) | 15.6% [13.9–17.5%] |
| AI-ready Critical IT | 773 | **317** | 20.1% | 26.0% | **+707** (647) | 0/1500 [0–0.26%] |
| GPU 托管（到机架） | 1,093 | 501 | 19.5% | 23.5% | +733 (655) | 0.3% [0.1–0.8%] |
| 算力出租（现货）‡ | 5,829 | 1,097 | −29.7% | — | **−3,351** (−3,381) | 800/800 [99.5–100%] |
| Managed Inference (L5a) | 5,533 | 895 | −35.9% | — | −2,784 (−2,817) | ~100% |

括号内为 Texas NPV。†开发退出报 MOIC $2.00\times$、年化 XIRR 36%、27 个月。‡**本行是 v3.3 黄金路径 / legacy YAML $\approx\$5.63/\mathrm{GPU\text{-}h}$，不是 Headline mix-ref \$7.80。** 频率修复后同一 YAML 路径 L4 NPV 约 **−\$964M**（`reproduce.py check`）；Headline Forward Merchant 见 §7.1（NPV +\$78M，Peak **\$2,362M**）。电力层 P1 的 MC 未单独跑满，正式版补齐。

辅助增量链（$\Delta\mathrm{NPV}/\Delta\mathrm{CAPEX}$，基于表 4）：Dev→Power **+0.28**；Power(P1)→Shell **−0.17**；Shell→Critical IT **+2.04**；Critical IT→Hosting **+0.08**；Hosting→GPU **−0.86**。市场一致电力基准下，壳体层几乎不创造增量价值。**价值创造重心在“可交付电力 → AI-ready Critical IT”。** L3：CAPEX 约 \$773M，Peak Equity 约 \$317M，NPV 约 **+$707M**，Equity IRR 约 26%。GPU Hosting（到机架、客户自持 GPU）NPV 与 L3 同量级、略高，损失率低。L5a 在收入等效（非严格 token 单位经济）下深度为负，边界不得外推至模型公司。

### 6.3 Merchant 因子实验（2×2×2）

**表 5 L4 算力出租全因子矩阵（Project NPV \$M / IRR / Peak Equity \$M）**

本表是 **v3.3 黄金路径 / legacy 租金包**，不是 Headline $7.80$ 路径。格子内“Contracted”同时改变租金、衰减与利用率，是**经济情景包**，不是单一因果处理。

| 资产栈 \ 合约 | Merchant × 新卡 | Merchant × 二手 | Contracted × 新卡 | Contracted × 二手 |
|---|---|---|---|---|
| **Greenfield** | −3,351 / −29.7% / 1,097 | −1,674 / −20.0% / 1,158 | −2,214 / −16.6% / 755 | −987 / −6.8% / 732 |
| **Brownfield** | −3,111 / −31.3% / 789 | −1,441 / −21.1% / 844 | −1,984 / −17.0% / 558 | **−757 / −5.4% / 535** |

租金（\$/IT-kW-h）：新卡现货 3.0 / 长约 3.2；二手现货 1.9 / 长约 2.0。二手 GPU \$12k/IT-kW、残值 0.30；长约衰减 −8%、利用率 95%。绿地 power \$1,150/kW + ready \$8,000/kW-IT；棕地 power \$150/kW + ready \$5,500/kW-IT。

**主效应与交互（NPV \$M，全因子均值分解）**

| 效应 | 量级 | 解读 |
|---|---:|---|
| **GPU 代际（二手 − 新卡）** | **+1,450** | 最大杠杆：采购价差主导 |
| **合约结构（长约 − 现货）** | **+909** | 第二：锁定衰减路径 |
| 资产栈（棕地 − 绿地） | +233 | 第三：电力/建筑沉没贡献有限 |
| 合约 × 代际交互 | **−446（次可加）** | 二手卡租金带较窄，长约溢价增量更小 |
| 合约 × 资产栈交互 | −6（≈0） | 两维度近似正交 |

排序：**GPU 代际 $>$ 合约 $\gg$ 资产栈**。八格在 **本文 2026-08 参数与该租金包** 内全部 NPV 为负；最优格（棕地 × 长约 × 二手）IRR 仍为 −5.4%。模型并未证明一切价格/残值/预付组合均不成立，只证明这八个情景包未翻转。频率修复后，Forward Merchant 在 mix-ref $7.80$ 下点估计不再被机械判死刑（§7.1），但 **All-risk CE 下全栈无合同延伸的 IRASR 仍为负**（§8–§9）。

---

## 7 L4：Merchant、合同期限、Vintage 与 Strategic

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
| L4-S Fixed \$9.36（backstop 已纠偏） | +5,285 | 438 |
| L4-S illustrative bulk \$7.02 | +3,278 | 500 |

C2 逐年价格：9.36 → 8.80 → 8.27 → 7.77 → 7.31。**温和 step-down 不摧毁合同；快速重定价才显著侵蚀。** C3 在真正年化 −15% 下仍约 +\$2.39B，高于 L3，但锁价溢价相对 C1 明显收窄。C4（3 年 tech-refresh-linked）在频率修复后**未作为独立四行表重跑**；v5.0 的 C4 NPV −\$821M 是 bug 路径，**禁止作为 Headline**。机制判断保留：更短 tenor + 技术刷新挂钩会同时释放价格风险并提前 refresh CAPEX，价值应低于 C1/C2，正式冻结前补跑。

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

**解读：** 最大单步仍是 **5 年固定价 ToP**（步骤 2，约 +\$3.9B），不是 list 价上调（步骤 1，约 +\$0.7B）。融资/预付把 Peak 从 \$2.2B 压到 \$0.44B——资本效率故事保留，但不是项目价值创造。Backstop 在 residual-only 口径下贡献约 +\$0.52B，不再是纠偏前的约 +\$1.0B。v5.0 桥从 Merchant −\$3,175 / Peak \$5,494 起跳，是频率 bug 产物，**不得与本表混读**。

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

采购锚来自 IREN [15]。**不得写成“2023 Merchant 一定暴利”。** 相对排序支持 Vintage dependency：早期 H100 在 GPU-only 栈下可为正；全栈绿地 Forward 仍弱。v5.0 同表 Greenfield 为 −2,156…−3,173，是频率 bug 路径，禁止引用。

### 7.5 Financeability、信用压力与续约悬崖

Financeability Score 将合同质量映射到杠杆与 $K_d$（§4.5）。**Headline 融资结构**用频率修复后数字：L4-S list Peak **\$438M**（NPV +\$5,285M）；bulk Peak **\$500M**（NPV +\$3,278M）。v5.0 的 L4-S +\$6,421 / Peak \$361 含未纠偏 backstop 与频率 bug，**不作 Headline**。

机制（确定性情景，方向成立、幅度待正式重跑）：

| 冲击 | 主要影响 | 读法 |
|---|---|---|
| 客户中途退出 | 收入跌回 Merchant / haircut | 信用风险，不是市场租金故事 |
| 去掉 NVIDIA backstop | 去掉 §7.2 步骤 5 的约 +\$524M | Vendor 义务有价 |
| 续约租金 −30% | 合同窗后现金流重定价 | Renewal Cliff |
| 融资冻结（$K_d$ 升、杠杆降） | **Project NPV 几乎不动**；Peak Equity 上升 | Sponsor 痛点是资本占用 |

**续约悬崖：** 5 年 ToP 到期与 3–5 年 GPU 刷新重叠时，残值、重定价、refresh CAPEX 与剩余债务同时出现。单项目 CE 为正不自动等于可在悬崖处再融资。

---

## 8 All-risk CE（Headline 唯一横比口径）

同一风险分类、不同暴露。$N=800$ 筛选级；CE 的 Bootstrap 95% CI 如下（v5.5）。L3 All-risk CE（+\$299M）低于旧独立租金 MC（+\$505M），因纳入违约/再融资——**横比只用本表**。

**表 8-1 All-risk CE 与 Bootstrap 区间**

| 模式 | 确定性 NPV | All-risk CE | Bootstrap 95% CI | Loss |
|---|---:|---:|---|---:|
| L3 Critical IT | +707 | **+299** | **[193, 407]** | 2.3% |
| 全栈 Merchant \$7.80 | +78 | **−1,029** | **[−1,087, −956]** | 60% |
| GPU-only accounting | +667 | **−439** | **[−497, −367]** | 36% |
| GPU-only economic（付 L3 租金） | — | **−949** | **[−1,009, −885]** | 61% |
| C illustrative bulk \$7.02 | +2,885 | **+1,639** | **[1,507, 1,769]** | 0.4% |
| S illustrative bulk \$7.02 | +3,278 | **+2,067** | **[1,930, 2,206]** | 0.3% |

C 与 S 的 CI 本轮不重叠，但弱于“C/S 相对 L3”（后者区间远不交叉）。可强说：**合同化算力显著优于 L3**。不得写 Strategic 损失率为零（观察 0.3%；Wilson 上界仍 $>0$）。正式冻结建议 $N=10{,}000$。

**表 8-2 $\lambda$ 敏感性（同一 All-risk 样本；CE 对 $\lambda$ 仿射，0.25/0.75 由端点内插）**

| 模式 | $\lambda=0$ | $\lambda=0.25$ | $\lambda=0.5$ | $\lambda=0.75$ | $\lambda=1$ |
|---|---:|---:|---:|---:|---:|
| L3 | +662 | +481 | **+299** | +118 | −64 |
| 全栈 M \$7.80 | −165 | −597 | **−1,029** | −1,461 | −1,893 |
| GO accounting | +424 | −8 | **−439** | −871 | −1,302 |
| GO economic | −147 | −548 | **−949** | −1,351 | −1,752 |
| C bulk | +2,523 | +2,081 | **+1,639** | +1,196 | +754 |
| S bulk | +2,945 | +2,506 | **+2,067** | +1,629 | +1,190 |

**C/S $>$ L3 在 $\lambda=0$ 到 $\lambda=1$ 均成立。** 高度风险厌恶不会推翻“合同化优于 L3”；只会削弱（仍为正）。全栈 Merchant 全 $\lambda$ 劣于 L3。$\lambda=1$ 时 L3 自身 CE 转负（尾部租户风险），C/S 仍为正。

---

## 9 增量资本配置

### 9.1 Transfer Pricing

内部价 = L3 市场租金 **\$185/kW-月**（配置 `ready_rent_kw_mo` / TeraWulf 量级锚定）。

**表 9-1 GPU-only 双口径**

| GPU-only 口径 | \$7.80 CE | \$7.80 $E[\mathrm{NPV}]$ | \$9.36 CE（经济口径） | CE 平价 vs L3 |
|---|---:|---:|---:|---:|
| Accounting（闲置、无租户） | **−439** [−497, −367] | +424 | — | **~\$9.75/GPU-h** |
| Economic（付 L3 租金） | **−949** [−1,009, −885] | −147 | **−395** | **~\$11.32/GPU-h** |

闲置矿场/无租户机房：Accounting 改善相对全栈 Merchant（CE −439 vs −1,029），但 **仍低于继续做 L3（+299）**。可出租 AI-ready 机房：自营 Merchant **明显劣于**把容量租出去。\$9.36 short-dedicated 在经济口径下仍约 −\$395M，**达不到**放弃 L3 的机会成本。

> 已有机房业主若放弃长期 L3 出租而自营 Merchant GPU，经济口径下需实现约 **\$11+/GPU-h** 的风险调整租金，才补偿所放弃的租约与额外技术/利用率风险。

### 9.2 IRASR\_econ（主）

L3：CE $+299\mathrm{M}$，Peak $\$317\mathrm{M}$。EconCap 为筛选比例假设。

**表 9-2 L3 → L4 增量 IRASR**

| L3 → | $\Delta$CE \$M | **IRASR\_econ（主）** | IRASR\_peak（次） |
|---|---:|---:|---:|
| 全栈 Merchant \$7.80 | −1,328 | **−0.55** | −0.65 |
| GPU-only accounting | −738 | **−0.41** | −0.48 |
| GPU-only economic | −1,248 | **−0.68** | −0.81 |
| C illustrative bulk | +1,340 | **+0.72** | +1.23 |
| S illustrative bulk | +1,768 | **+1.29** | +9.64（禁止作口号） |

**读法：** 全栈 Merchant 每多占用 1 美元经济资本，毁灭约 \$0.55 确定性等价价值。GPU-only accounting 破坏减小，仍为负。Contracted 每单位经济资本约创造 **\$0.72**；Strategic 约 **\$1.29**。9.64 是杠杆压低现金股本的结果，不再作 Headline。

reproduce 黄金 IRASR $\approx -0.94$ 对应 **legacy YAML $\approx\$5.63/\mathrm{GPU\text{-}h}$ 全栈路径**，与 Headline \$7.80 **不是同一假设**。v3.3 的 IRASR $-5.76$ 对应频率修复前 / 旧短缺路径，仅作历史对照。

### 9.3 盈亏平衡

| 指标 | L4-C Fixed | L4-S Fixed | L4-M $-22\%/\mathrm{年}$ |
|---|---:|---:|---:|
| NPV = NPV\_L3 | ~\$4.30 | ~\$4.02 | — |
| NPV = 0 | — | — | ~\$7.64 |
| Merchant NPV = L3 | — | — | ~\$9.11 |
| **CE = CE\_L3** | **~\$4.72** | **~\$4.22** | — |

决策优先 CE 阈值。表述应为：当 5 年 realized contract rate 高于约 \$4.7（C）或 \$4.2（S）时，在本模型 All-risk 设定下风险调整后优于 L3——**不是**主张真实成交价就是 \$7.02。

### 9.4 Matched Counterparty

固定信用档，拆开 Layer Effect 与 Counterparty Effect。

**表 9-3 同信用对照（All-risk CE \$M）**

| 对象 | 信用代理 | All-risk CE |
|---|---|---:|
| L3 | Generic tenant（PD ~2%） | +248 |
| L3 | IG / A–BBB+（PD ~0.8%） | +402 |
| L4-C bulk | Generic（PD ~4%） | +1,639 |
| L4-C bulk | **同 IG** | **+1,974** |

- **Layer effect（同 IG）**：1,974 − 402 $\approx$ **+\$1.57B**  
- L3 信用升级仅约 +\$154M；C 的结构溢价远大于“客户更好”。  
- L3 损失率高于 L4-C，在**同信用**下仍成立（20 年租约 vs 5 年 ToP 的期限/尾部差异），**不是**因为给 L4 偷偷用了更好客户。

第二套允许 Strategic 拥有更强客户，用来单独回答“商业生态优势又值多少钱”，本稿不把该溢价并入 Headline 排序。

---

## 10 Sponsor Access Overlay

失败回退 = 继续做 L3：

$$EV_C=p_C\,\mathrm{CE}_C+(1-p_C)\,\mathrm{CE}_{L3}-\mathrm{PursuitCost},\qquad
p_C^{*}=\frac{\mathrm{PursuitCost}}{\mathrm{CE}_C-\mathrm{CE}_{L3}}.$$

因 $\mathrm{CE}_C,\mathrm{CE}_S\gg\mathrm{CE}_{L3}$，任何正的 $p$ 都提高期望值；真正阈值只取决于 Pursuit Cost。

**表 10-1 盈亏平衡成功率（fallback = L3）**

| Pursuit \$M | $p_C^{*}$ | $p_S^{*}$ |
|---|---:|---:|
| 5 | 0.4% | 0.3% |
| 20 | **1.5%** | **1.1%** |
| 50 | 3.7% | 2.8% |
| 100 | 7.5% | 5.7% |

**表 10-2 类型化 Access EV（All-risk CE；v5.4 结构，CE 用 v5.5 点估计）**

使用 $\mathrm{CE}_M=-1029$，$\mathrm{CE}_C=+1639$，$\mathrm{CE}_S=+2067$，$\mathrm{CE}_{L3}=+299$。Type A/B/C 的 $p_C/p_S$ 为情景，不是估计的市场概率。

| 类型 | $p_C$ | $p_S$ | 含义 | 最优 |
|---|---:|---:|---|---|
| A Uncontracted | 0.10 | 0.02 | 低合同可得性 | **L3** |
| B Contract capability | 0.85 | 0.20 | 能拿 ToP，战略平台弱 | **S / C** |
| C Strategic platform | 0.95 | 0.70 | 合同 + Vendor + 融资 | **S** |

拿不到合同就留在 L3，**不必做 Merchant**。这比“小玩家不能碰 GPU”更接近开发商真实决策：为拿到 5 年 compute contract，最多值得花多少钱、等多久，由表 10-1 直接给出。

---

## 11 讨论

### 11.1 与文献

资本流向 $\neq$ 回报来源 [1]：宏观向 GPU 堆积与微观 Sponsor CE 为负可以并存。衰减具有时变性 [6]；频率修复后 Forward Merchant 在 mix-ref 附近脆弱平衡，与“过去有人赚钱”不再矛盾，也**不**支持今天无合同全栈新建为默认。技术变量在租约锁定后降为二阶 [2]。LCOAI 等单位成本指标 [3] 回答的是算力成本，不是 Sponsor 在哪一层配置风险资本。

### 11.2 融资再分配 ≠ 价值创造

Project NPV 与 Equity NPV 仅在**统一贴现率**下可加总：

$$\underbrace{\mathrm{NPV}_{\mathrm{proj}}}_{r=r_u}=\underbrace{\mathrm{NPV}_{\mathrm{equity}}}_{r=r_u}+\underbrace{\mathrm{NPV}_{\mathrm{debt}}}_{r=r_u}.$$

若 Project CF 按 WACC、Equity CF 按 $K_e$、Debt CF 按 $K_d$ 分别贴现，三个 NPV 一般不能直接相减推出“债权人损失”。融资/预付压缩 Peak，不创造项目价值。CoreWeave 式定价（高收益债 + 抵押 + 厂商回购）是对债务方承担转移风险的补偿 [4][9]。双轨系统输出（统一口径归属 vs 各 stakeholder 自身 hurdle）仍为冻结后工作。

任何商业模式都必须同时检查 Project、Equity 与 Debt 三个 NPV。仅报告 Equity IRR 的模型会系统性误导——尤其当 GPU-aware 杠杆把 Peak 压到极低时。

### 11.3 风险迁移与循环支持

| 模式 | 主要风险 |
|---|---|
| Merchant | 市场租金、利用率、技术、残值 |
| Contracted | 客户信用、合同执行、交付、续约 |
| Strategic | 客户/Vendor 信用与义务、结构化融资、集中度、循环支持 |

Market risk → Credit + Contract + Vendor + Structured-finance risk。NVIDIA 可能同时卖卡、入股、backstop、助力融资；需求下行时风险相关 [7][11][13]。拟议 OpenAI 支持从约 \$250B 讨论值缩减至首期少于 \$120B 的报道说明 backstop 对 Vendor 并非零成本（**proposed / under discussion**）。单项目 CE 为正不消除系统集中度。

路径

$$\text{GPU Hardware}\rightarrow\text{Usage-linked Revenue}\rightarrow\text{Institutional Underwriting}\rightarrow\text{Investable Infrastructure}$$

类似飞机租赁/能源项目融资，但设备折旧更快、技术代际更短。NVIDIA 超过 \$500B compute financing platforms [11] 表明 Strategic 不是单一例外，而正在被试图制度化。

### 11.4 税务与备付金

直线折旧相对 MACRS/CCA 偏保守约 2–5%；DSRA 约压 Equity IRR 90bp 量级；L4 税务项即使按更激进口径调整，也不翻转 All-risk 下“无合同全栈 Merchant IRASR 为负、合同化路径为正”的排序。银行级 MACRS/CCA 与 DSRA 实现列为后续工作。

### 11.5 L5 边界

L5a 的 \$/IT-kW-h 输入是 token 经济学的**收入等效**，不是 GPU→tokens→\$/M tokens 的完整单位经济。L5b 上模型层 API 收入与租金成本可呈数倍差 [6]——价值归属模型层，与 L4/L5a 基础设施回报为负互洽。**“基础设施投资人自持 GPU 做 Compute Rental”为负，不构成“AI Factory 不赚钱”。** Frontier Model 与 Captive AI 的经济性由模型层/最终业务层决定。

### 11.6 实践

对土地/电力/许可占优的开发商：

$$\mathrm{Power\text{-}secured}\rightarrow\mathrm{AI\text{-}ready}\rightarrow\mathrm{Tenant/Compute\ Contract}\rightarrow\mathrm{GPU}.$$

即 **GPU deployment should be demand-led, not inventory-led.** 闲置矿场用 Accounting 口径；可出租 Virginia/Texas AI-ready 厂房用 Economic 口径。Type A 默认 L3；Type B/C 在合同落实后进入 C/S。只有在特别低的采购成本、能锁定价格/利用率、或自身掌握模型与 Token 变现时，才向无合同 Compute 投入大量资本。

### 11.7 局限性

筛选级精度；$N=800$ All-risk；直线折旧；单一美元；相关矩阵经验设定（$\rho(\mathrm{rent},\mathrm{residual})=0.6$，其余 0.25）；Historical 租金路径非完整回测；Counterparty PD 为情景而非评级校准；EconCap 未校准；\$7.02 为作者假设；C4 未在频率修复后重跑独立表；Financeability 压力幅度待正式重跑；L5a 非严格 token 单位经济；交易级样本外验证未完成；P1 的 MC 样本量未与其他层对齐。

---

## 12 结论

**RQ1** 统一口径下：P1 电力为基础设施回报（EqIRR 14.1%）；L3 / Hosting 为无合同时的 structural 默认（NPV +\$707M / +\$733M）；全栈 Merchant 在 mix-ref 下点估计或近 BE（+\$78M），All-risk CE 为负（−\$1.03B）；C/S 在 illustrative bulk 下 CE 显著高于 L3。  
**RQ2** 全栈/经济口径 GPU-only 的 IRASR\_econ 为负（−0.55 / −0.68）；合同化路径为正（C $+0.72$，S $+1.29$）。表 4 增量链显示价值创造重心在 Shell→Critical IT（+2.04）。  
**RQ3** 最优层级是六维资产函数加 Sponsor overlay，不是固定一层。2×2×2 在 legacy 租金包内主效应为代际 $>$ 合约 $\gg$ 栈。  
**RQ4** L4 在 Merchant Forward 下风险调整偏弱；在可获得的固定价或温和 step-down ToP 下创造价值。真正危险的是快速重定价与合同不可得，不是任何价格下降。  
**RQ5** Vintage 与栈依赖支持 Historical $\neq$ Forward；C/S 购买的是确定性与资本效率（Certainty Bridge 主跳跃在 Fixed ToP，不在 list 价）。  
**RQ6** 可出租机房必须扣 L3 机会成本；经济口径 CE 平价约 \$11+/GPU-h。

**四句跨周期判断：** Role 决定现金流归属；Vintage 决定进入成本与周期暴露；Contract 决定市场风险能否变成信用风险；Capital Structure 与 Vendor Support 决定 Sponsor 占用多少经济资本。

$$\boxed{\mathrm{Asset\ Value}\neq\mathrm{Hardware\ Value}}$$

同一张 GPU：Merchant 下是高折旧、高波动的技术资产；Contracted 下是合同支持的算力基础设施；Strategic 下是 Vendor 支持、机构可融资的 AI 基础设施资产。

**后续（冻结算法之后）：** $N=10{,}000$ All-risk；交易锚定 realized rate；EconCap 校准；realized cohort 回测；C4 与 Financeability 网格在修复路径上正式重跑；L5a token 引擎；双轨贴现率归属输出。v6.0 数字随参数包滚动，不再改核心方程。

---

## 参考文献

[1] McKinsey & Company. *The Cost of Compute: A $7 Trillion Race to Scale Data Centers*. 2025-04-28.  
[2] He, Q. *A Unified Metric Architecture for AI Infrastructure*. arXiv:2511.21772, 2025.  
[3] Curcio, E. *Introducing LCOAI*. arXiv:2509.02596, 2025.  
[4] Morgan Stanley Research. *Bridging a $1.5tr Data Center Financing Gap*. 2025-07-16.  
[5] CoreWeave. Form S-1 / 10-K：committed contracts、take-or-pay、预付、asset-level debt.  
[6] SemiAnalysis. GPU rental / Tokenomics；H100 一年期合约价约 \$1.70→\$2.35（约 +40%）.  
[7] CoreWeave–NVIDIA Form 8-K：residual unsold capacity 义务，至 2032.  
[8] TeraWulf–Anthropic，2026-07-06（IR / GlobeNewswire）；Greenlight Electricity Centre 公开报道口径.  
[9] CoreWeave DDTL 4.0：约 5.9% fixed / SOFR+2.25%.  
[10] NVIDIA \$2B CoreWeave 投资. 2026-01.  
[11] NVIDIA. Compute Financing Platforms（超过 \$500B）. 2026-08-10.  
[12] Reuters / WSJ. NVIDIA–OpenAI 拟议约 \$250B 支持. 2026-07-26.（**proposed**）  
[13] Reuters / WSJ. 拟议支持缩减至首期少于 \$120B. 2026-08-14.（**proposed / under discussion**）  
[14] WNT. 到机架增量 / 匿名棕地项目口径（内部实盘，公开包已脱敏）.  
[15] IREN. SEC 披露 H100 采购（2023-08；2024-02）.  
[16] CoreWeave Pricing. HGX H100/B200 On-demand 与 Spot. 2026-08 检索. https://www.coreweave.com/pricing  
[17] Lambda Pricing / 1-Click Clusters. H100/B200 Instance 与 Dedicated. 2026-08 检索. https://lambda.ai/pricing  

**\$7.02/GPU-h $=9.36\times 0.75$：作者 Illustrative Bulk 假设，不是市场成交事实。**

---

## 附录 A — 复现

```bash
cd aidc-optimizer
python reproduce.py check          # 黄金回归（legacy YAML 路径）
python research_v5_2_rerun.py      # Certainty Bridge / Vintage / 信用 MC
python research_v5_4.py            # All-risk 统一表、增量 IRASR
python research_v5_5.py            # Transfer pricing、CI、IRASR_econ、p*
```

| 文件 | 内容 |
|---|---|
| `research_outputs/v5_2_rerun/certainty_bridge_fixed.csv` | 表 7-2 |
| `research_outputs/v5_2_rerun/merchant_vintage_fixed.csv` | 表 V1 |
| `research_outputs/v5_2_rerun/headline_fixed.csv` | 确定性 Headline |
| `research_outputs/v5_5/allrisk_ce_bootstrap_ci.csv` | 表 8-1 |
| `research_outputs/v5_5/irasr_econ_primary.csv` | 表 9-2 |
| `research_outputs/v5_5/lambda_sensitivity_allrisk.csv` | 表 8-2 端点 |
| `research_outputs/v5_5/gpuonly_ce_parity.csv` | 表 9-1 平价 |
| `research_outputs/v5_5/access_pstar_l3_fallback.csv` | 表 10-1 |
| `research_outputs/v5_5/matched_counterparty.csv` | 表 9-3 |
| `expected_outputs/alberta.json` | v3.3 黄金（表 3/4/5） |

## 附录 B — 模型审计摘要（已关闭的 P0）

| 项 | 状态 |
|---|---|
| GPU 年化衰减按月指数 | **已修** $(1+g)^{k/12}$ |
| Backstop 双重计费 | **已修** residual unsold only |
| B200 \$21.3k/IT-kW Base | **已移除** |
| List \$9.36 作 4 万卡成交价 | **降为上界** |
| Strategic P(loss)=0% | **否决**；报 CI |
| Peak IRASR 9.6× 作 Headline | **降级**；主用 IRASR\_econ |
| GPU-only 免费占用 L3 | **已加** transfer / economic view |
| L3 vs L4 信用不同口径 | **已加** Matched Counterparty |
| Headline 混用 CE 体系 | **已统一** All-risk |
| v5.4 形态像 revision memo | **本稿合并全文** |

## 附录 C — 数字来源对照（防混用）

| 数字 | 来源 | 可否作 Headline |
|---|---|---|
| L3 NPV +707 / Peak 317 | v3.3 表 4 = v5.3 | 是 |
| L3 All-risk CE +299 [193, 407] | v5.5 | 是（唯一 L3 CE） |
| Merchant \$7.80 NPV +78 / Peak 2,362 | v5.3 Bridge | 是 |
| Merchant All-risk CE −1,029 | v5.5 | 是 |
| C1 +4,761 / C2 +3,844 / Δ +917 | v5.2/v5.3 | 是 |
| C3 −15%/年 +2,392 | v5.2 | 是（list；未进 All-risk 主表） |
| C4 −821 | v5.0 | **否**（频率 bug） |
| L4-S list +5,285 / Peak 438 | v5.3 | 是 |
| L4-S +6,421 / Peak 361 | v5.0 | **否**（未纠偏 backstop + 频率 bug） |
| 表 4 算力出租 −3,351 / Peak 1,097 | v3.3 legacy YAML | 仅作七模式结构表，脚注必写 |
| IRASR −5.76 | v3.3 旧短缺路径 | 仅历史对照 |
| IRASR_econ C +0.72 / S +1.29 | v5.5 | 是（主指标） |

---

**利益声明**：作者所属机构从事北美 BTM 电力与数据中心开发；P3 套利情景与业务方向相关，已与市场一致 P1 分离。参数含机构实盘造价的脱敏公开包。

**AI 辅助披露**：模型、分析与文稿由 AI 辅助；数值可由随附代码复现。v6.0 合并 v3.3 完整结构、v5.0 方法引擎与 v5.3/v5.5 Headline 数字；筛选级 $N=800$；正式对外建议提高样本量并滚动市场参数，不改核心方程。
