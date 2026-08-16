# 面向AI基础设施的价值链投资评估模型：经济角色、投资时点、资产栈、合约结构与资本结构共同决定的风险调整资本配置框架

## A Value-Chain Investment Evaluation Model for AI Infrastructure: A Risk-Adjusted Capital Allocation Framework Jointly Determined by Economic Role, Investment Vintage, Asset Stack, Contract Structure and Capital Structure

**作者**: WNT Energy 技术研究组  
**日期**: 2026年8月  
**状态**: 工作论文 v5.0  
**版本记录**: v1.0–v3.3 完成 Role×Stack×Contract 框架、CE-NPV/IRASR、2×2×2因子、复现对齐；v4.0 将L4拆为Merchant/Contracted/Strategic并允许结论翻转。**v5.0 依《AIDC_v5升级完整指令》**——主题为**Investment Vintage × Contract × Strategic Finance**：正式加入第六维 Investment Vintage；严格分离 Historical Realized Return 与 Forward New-Investment Return；Merchant结论从“永不成立”改写为 Vintage-dependent；合同拆为C1–C4期限结构；Value Bridge升级为 Certainty Bridge（E/ES/CE/P(loss)/Peak/DSCR）；加入Contract Financeability、Counterparty Credit、Renewal Cliff；纳入NVIDIA $500B Compute Financing Platforms与OpenAI拟议credit wrapper（标注proposed）。代码：`research_v5.py` + `research_outputs/v5/`。

---

## 摘要

人工智能数据中心（AIDC）投资常被简化为单一“数据中心IRR”或静态“甜蜜点”问题。本文在 v1–v4 统一价值链框架（Role、Asset Stack、Contract、Project Finance、相关性风险模拟、Sponsor资本配置）之上，引入第六维 **Investment Vintage（投资时点）**，将决策函数升级为：

$$\boxed{Optimal\ Layer = f(Role,\ AssetStack,\ Contract,\ CapitalStructure,\ MarketState,\ InvestmentVintage)}$$

核心进展有四。第一，**Merchant 算力不是天然不能盈利，而是高度 Vintage-dependent**：历史低成本进入者可能享受 scarcity rent 与租金上行；但 2026 Forward 新进入者在高采购成本与重定价路径下显著恶化——Historical Winner ≠ Forward Winner。第二，**L4 必须拆为三模式**——市场型算力出租（L4-M）、长约型算力基础设施（L4-C）、战略型算力平台（L4-S）；其本质分别是 Technology Asset、Contract-backed Asset、Vendor-supported Financeable Infrastructure。第三，**5年固定价 take-or-pay（C1）是合同价值的主杠杆**（Certainty Bridge 中 NPV 从约 −3.1B 跃升至 +4.8B，CE-NPV 同步转正、P(loss)→0）；step-down（C2）与 benchmark repricing（C3）则大幅削弱甚至翻转该优势——“长约”≠“锁价”。第四，**Strategic 模式通过客户合同、NVIDIA 级 capacity backstop、GPU-backed 低成本融资与客户预付款，把 Peak Sponsor Equity 从约 $5.5B 压至约 $0.36B**，确定性 NPV 约 +$6.4B、CE-NPV 约 +$5.1B，超过 L3 Critical IT（+$0.71B / CE +$0.51B）；但风险从市场租金迁移为客户信用、Vendor 义务与结构化融资集中度——Strategic 不是消灭风险，而是再分配风险。

电力层市场一致基准 Equity IRR 约 14.1%；Merchant 2×2×2 因子主效应仍为 GPU 代际 ＞ 合约 ＞ 资产栈。全文主结论：**Role 决定现金流归属；Investment Vintage 决定进入成本与周期暴露；Contract 决定市场风险能否转化为信用风险；Capital Structure 与 Vendor Support 决定 Sponsor 最终承担多少风险资本。同一张 GPU，因 Vintage、Contract 与 Capital Structure 不同，可以是高波动技术资产，也可以是可融资的 AI 基础设施资产。**

**关键词**: AI基础设施；Investment Vintage；Merchant/Contracted/Strategic；take-or-pay；GPU-backed融资；Certainty Bridge；Historical≠Forward；Critical IT；NVIDIA Compute Financing

---

## Abstract

*(Condensed; Chinese text is authoritative.)* This paper upgrades the AIDC value-chain investment framework by adding **Investment Vintage** as a sixth formal dimension. Merchant compute returns are **vintage-dependent**, not intrinsically negative: early low-entry-cost cohorts may earn scarcity rents, while 2026 forward new investment can be deeply impaired under high CAPEX and re-pricing paths—**Historical Winner ≠ Forward Winner**. L4 is split into Merchant / Contracted / Strategic modes. A 5-year fixed-price take-or-pay (C1) is the dominant contract lever (Certainty Bridge: NPV −3.1B → +4.8B; CE-NPV turns positive; P(loss)→0); step-down and benchmark re-pricing contracts destroy much of that value. Strategic packaging (customer contract + NVIDIA-style capacity backstop + GPU-backed financing + prepayment) compresses Peak Sponsor Equity from ~$5.5B to ~$0.36B and delivers CE-NPV ~+$5.1B, exceeding L3—but migrates risk to counterparty credit, vendor obligations and structured-finance concentration. Optimal layer = f(Role, Asset Stack, Contract, Capital Structure, Market State, **Investment Vintage**).

---

## 1 引言

### 1.1 研究背景

自2024年起，AI基础设施进入史无前例的资本扩张期：到2030年全球数据中心资本需求约6.7万亿美元（AI相关约5.2万亿）[1]；2025–2028年数据中心资本开支约2.9万亿、外部融资缺口约1.5万亿[4]。与此同时，GPU租赁市场出现期限结构与产品分层（Spot / Instance / Dedicated Cluster），NVIDIA 宣布动员超过 $500B 的第三方 compute financing platforms[11]，CoreWeave 等 Neocloud 以多年期 take-or-pay 与 GPU-backed 债务运营[5][9]。行业正在从“买卡赌周期”演化为“合同化—信用化—金融化”的基础设施市场。

### 1.2 研究问题

> **RQ1** 七种商业模式（含 L4 三子模式）的投资强度、回报与风险敞口如何系统比较？  
> **RQ2** 价值链延伸的 IRASR 在何处由正转负？该拐点如何随 Vintage 与合同结构移动？  
> **RQ3** 最优层级在多大程度上由资产栈、合约、资本结构与 **Investment Vintage** 共同决定？  
> **RQ4** 以2026-08公开市场价与 CoreWeave 式资本结构重估后，L4 何时从毁灭价值转为创造价值？  
> **RQ5（v5.0）** 历史 Merchant cohort 的估算回报与当前 Forward Return 差多大？Contracted/Strategic 真正购买的是更高均值，还是更高确定性？

### 1.3 贡献声明

本文不声称发明 CVaR、copula 或项目融资工具。贡献在于：（1）将 Role、Asset Stack、Contract、Project Finance、相关性风险、Sponsor 资本配置与 **Investment Vintage** 整合进统一 AIDC 框架；（2）严格分离 Historical / Forward 回报；（3）把 L4 重构为 Merchant / Contracted / Strategic，并以 Certainty Bridge 量化合同与战略融资的风险调整价值；（4）以可复现代码与黄金结果支持结论。

---

## 2 理论框架：六维决策函数与四阶段演化

### 2.1 底层资产：可交付容量

$$\text{AI Infrastructure Capacity} = f(\text{MW},\ \text{COD},\ \text{Availability},\ \text{Contractability},\ \text{Location})$$

Power / Critical IT / Compute 是对同一稀缺资源——**可按时交付的容量**——的逐级转换。

### 2.2 经济角色矩阵

| Role | 出售什么 | 向谁收费 | 主要资产 | 核心风险 |
|---|---|---|---|---|
| PowerCo | Firm MW @ COD | DC运营商 | 发电+燃料 | COD、可用性 |
| DC Landlord | Critical IT MW | Tenant | 建筑+MEP | 建设、租户信用 |
| ComputeCo（L4-M/C/S） | GPU-hour / 合同容量 | AI Lab / 企业 | GPU+集群±合同±Vendor | 见§2.3 |
| Managed Inference (L5a) | $/token 托管 | 应用/企业 | 平台+运营 | 需求、毛利率 |
| Frontier Model (L5b) | Token/API | 终端用户 | 模型IP+客户 | 变现能力 |

### 2.3 L4 三模式正式定义

| 模式 | 中文 | 英文 | 本质 | 下游合同 | 上游/Vendor | 融资 | 主要风险 |
|---|---|---|---|---|---|---|---|
| **L4-M** | 市场型算力出租 | Merchant Compute | Technology Asset + Merchant Revenue | Spot / on-demand / 0–12月 | 普通 PO，无默认 backstop | 低杠杆、高 Kd | 租金、利用率、残值、技术淘汰 |
| **L4-C** | 长约型算力基础设施 | Contracted Compute | GPU + Customer Contract | 2–5年 take-or-pay，固定/阶梯价 | 常与客户签约同步采购 | 合同支持的更高杠杆 | 客户信用、交付、续约重定价 |
| **L4-S** | 战略型算力平台 | Strategic Neocloud | GPU + Contract + Vendor + Financing Platform | Hyperscaler/Lab 多年期 | Strategic equity、capacity backstop、生态协同 | GPU-backed、机构资本 | 客户/Vendor 集中度、结构化融资、循环支持 |

**Buy First vs Contract First：**

- Merchant：Buy First → Sell Later  
- Contracted：Contract First → Buy Later  
- Strategic：Contract First → Credit Enhance → Finance → Buy  

### 2.4 Investment Vintage

Investment Vintage = **GPU 资产首次形成不可逆资本承诺的时间点**（如 H100-2023、B200-2026F）。每一 Vintage 拥有独立的采购价、交付、初始租金、租金路径、利用率、残值、融资条件与竞争代际。

必须分离三种回报：

| 类型 | 符号 | 回答的问题 |
|---|---|---|
| Historical Realized | $IRR_{Realized}$ | 过去某 cohort 实际/估算赚了多少？ |
| Mark-to-Market / Cohort | 已实现 CF + 当前残值 | 今天重估这批卡值多少？ |
| Forward New-Investment | $IRR_{Forward}$ | 今天新进入还值不值得？ |

### 2.5 行业四阶段演化

| Phase | 路径 | 主导逻辑 |
|---|---|---|
| 1 Early Scarcity / Merchant Alpha | 低成本进入 → scarcity rent → 租金上行 | 周期交易 |
| 2 High Entry Cost / Forward Uncertainty | 高 CAPEX + 高现价 + 不确定未来租金 | Merchant 风险↑ |
| 3 Contractualization | Customer Contract → 现金流可见性 → Bankability | 合同化 |
| 4 Strategic Ecosystem | Customer + Vendor + Institutional Capital | 金融化基础设施 |

### 2.6 两个甜蜜点

- **Structural Sweet Spot**：不依赖短期周期的稳定优势层级（如 AI-ready Critical IT）。  
- **Cyclical Sweet Spot**：特定 Vintage/市场状态下的临时最优（如 Scarcity Boom 中的早期 H100 Merchant）。  

不得再给出单一、跨周期的“固定甜蜜点”。

---

## 3 模型与方法

### 3.1 统一物理口径

100 MW 参考项目，PUE 1.25 → 80 MW Critical IT；GPU 层 $/IT-kW-hr 与 $/GPU-hr 按代际换算（H100 ≈0.78 GPU/IT-kW；B200 ≈0.533）。

### 3.2 资产层与融资层

资产层月度：tolling / 租约 / GPU RevPAGH；L4-C/S 采用 take-or-pay 保底收入与可选 NVIDIA 式 capacity backstop。  
融资层：S曲线提款、IDC、sculpted/mortgage 摊还、现金扫仓、客户资本。**GPU-aware 融资**（v4.0 引入）：债务按全部 capex（含 GPU 采购）计杠杆，修复基础引擎对运营期 GPU 资本不记账、低估 Peak Equity 的缺陷。

### 3.3 风险调整

$$ES^-_{5\%}(NPV)=E[NPV\mid NPV\le P5],\quad CE\text{-}NPV=(1-\lambda)E(NPV)+\lambda\,ES^-_{5\%}(NPV)$$

$$IRASR=\frac{\Delta CE\text{-}NPV}{\Delta PeakSponsorEquity}$$

另定义 **Contract Conversion IRASR**（$IRASR_{M\to C}$、$IRASR_{C\to S}$）与 **Vintage IRASR**。损失概率附 Wilson 95% CI。

### 3.4 Certainty Bridge

在 v4.0 NPV Value Bridge 之上，逐步报告 E(NPV)、ES₅、CE-NPV、P(loss)、Peak Equity、DSCR，证明 Contracted/Strategic 购买的是 **risk-adjusted certainty**，而不只是更高平均收入。

### 3.5 Contract Financeability Engine

输入：客户信用、tenor、take-or-pay%、预付%、backstop、集中度 → 输出：max leverage、Kd、debt tenor、min DSCR。形成 Contract → Bankability → Debt Capacity → Peak Equity 传导。

### 3.6 实现与复现

- `aidc_optimizer`：七模式双引擎  
- `research_l4.py`：L4-M/C/S + GPU-aware 融资  
- `research_v5.py`：Vintage / Term Structure / Certainty Bridge / Financeability / Credit  
- `reproduce.py check`：v3.3 黄金结果校验  
- 输出目录：`research_outputs/v5/`

---

## 4 校准与验证

### 4.1 Level A 参数锚定

| 锚点 | 公开事实 | 模型用途 |
|---|---|---|
| TeraWulf–Anthropic（2026-07-06） | 401 MW IT / 20年 / ~$19B | Critical IT 租金恒等式 |
| Greenlight | 932 MW / CA$4.6B / ~60%债 | Power 层区间锚定 |
| IREN SEC H100 采购 | 2023-08 248卡~$10M；2024-02 568卡~$22M | Historical Vintage 采购锚（~$38–40k/GPU） |
| Lambda / CoreWeave 2026-08 | B200 Spot~$4.26；Instance~$6.7–7.0；Dedicated~$8.9–9.9 | Forward 租金分层 |
| CoreWeave S-1/10-K | 96% committed；2–5年 ToP；预付15–25% TCV | L4-C 合同结构 |
| CoreWeave–NVIDIA 8-K | $6.3B order；residual capacity 义务至2032 | L4-S backstop |
| CoreWeave DDTL 4.0 | Fixed ~5.9%；SOFR+2.25% | Strategic Kd 锚点（非通用） |
| NVIDIA $500B platforms | 官方 2026-08-10 | 行业金融化证据 |

### 4.2 Level B 内部验证

Sources=Uses、债务滚动、期限匹配、IRR/NPV 解析解等六项通过。

### 4.3 Level C 合理性检验

输入参数与公开价格带/杠杆带核对；非交易级样本外预测（≥5笔 Prediction-vs-Actual 仍为后续工作）。

### 4.4 证据等级

- **Level 1** Primary/Regulatory：SEC、NVIDIA 官方、CoreWeave IR、Lambda 官方 → 可作 Base Parameter  
- **Level 2** High-quality Press：Reuters/WSJ → 拟议结构必须标注 proposed / under discussion  
- **Level 3** Market Intelligence：SemiAnalysis 等 → 价格曲线，保留 confidence  
- **禁止**：将媒体报道的拟议 $250B 担保写成已完成融资；将未证实 GPU 折扣写成事实（仅 Sensitivity 0/10/20/30%）

---

## 5 结果

### 5.1 电力层与基准七模式（沿用 v3.3/v4.0 复现结果）

市场一致 Power-only（P1）：Equity IRR **14.1%**，NPV +$104M。  
七模式排序（Merchant 口径 L4）：Critical IT / Hosting（CE-NPV +$505M 量级）＞ Power-only ≈ Shell（边际）＞ Merchant L4 / L5a（深负）。  
表4峰值股本列统一 Peak Equity；**Merchant L4 在 GPU-aware 融资下真实 Peak Equity 约 $5.5B**（远高于基础引擎口径的 ~$1.1B）。

### 5.2 Merchant 2×2×2 因子（Merchant 结构）

主效应：**GPU 代际（+$1.45B）＞ 合约（+$0.91B）≫ 资产栈（+$0.23B）**，合约×代际负交互 −$0.45B。八格在 Merchant + 重定价假设下全部 NPV 为负——该结论**限定于 Merchant 结构与 Forward 路径**，不得外推为“GPU 永远不赚钱”。

### 5.3 Investment Vintage：Historical vs Forward（RQ5）

**表 V1 Merchant Cohort 估算（筛选级；租金路径为结构假设，置信度 0.55–0.70）**

| Vintage | 栈 | 采购$/GPU | 入场$/GPUh | NPV $M（Greenfield） | 说明 |
|---|---|---:|---:|---:|---|
| H100-2023 | Greenfield | ~40,300 | 4.50 | −2,156 | 早期 scarcity 路径；仍难覆盖全栈新建 |
| H100-2024 | Greenfield | ~38,700 | 3.80 | −2,327 | IREN 采购锚 |
| H100-2025 | Greenfield | ~35,000 | 2.80 | −2,863 | 租金低谷后反弹路径 |
| H100-2026F | Greenfield | ~32,000 | 3.20 | −2,942 | Forward，decay −22%/年 |
| B200-2026F | Greenfield | ~60,000 | 7.80 | −3,173 | Forward 公开中位租金 |

在 **GPU-only 增量栈**（电力与建筑沉没）下，各 Vintage NPV 改善约 $0.5–0.6B，但在本模型的路径假设下仍为负。含义：

1. **历史高回报不能直接写成已证实事实**——需更完整的 realized 租金/利用率序列与系统级 CAPEX 拆分；当前结果是可检验假设的量化边界。  
2. **相对排序支持 Vintage dependency**：早期 H100 cohort 的估算 NPV 系统性好于 2026 Forward（差距约 $0.8–1.0B 量级）。  
3. **Forward Merchant 在 2026 参数下偏弱**——与“单纯抬公开价翻不动 Merchant”的 v4.0 结论一致。  
4. 因此：**Historical Winner ≠ Forward Winner**；不能用过去 12 个月的 GPU 盈利证明未来 48 个月新购 GPU 的投资价值。

Vintage Surface（采购价 × 租金）显示：仅在极低采购价与极高持续租金的组合角点，Merchant 全栈新建才接近盈亏平衡——这是周期角落，不是稳态。

### 5.4 合同期限结构 C1–C4

**表 V2 Compute Term Structure（B200 Dedicated $9.36/GPUh 锚）**

| 合同 | 结构 | NPV $M | Peak $M | DSCR(合同窗) |
|---|---|---:|---:|---:|
| **C1** | 5Y Fixed Take-or-pay | **+4,760** | ~527–1,102* | 5.3 |
| **C2** | 5Y Step-down ~−6%/年 | −348 | ~527 | 0.08 |
| **C3** | Benchmark Repricing | −1,799 | ~1,243 | <0 |
| **C4** | 3Y Tech-refresh-linked | −821 | ~527 | — |

\*Peak 随预付比例与杠杆变化。  

**关键含义**：“5年合同”远不等于“5年锁价”。价格锁定价值与利用率保底价值必须拆开：C1 同时锁定二者；C2/C3 释放价格风险后，合同溢价大部分消失。真实 AI 合同中客户锁的是 capacity 还是 technology-adjusted price，是下一阶段实证重点。

### 5.5 L4 三模式与 Certainty Bridge

**表 V3 模式比较（GPU-aware 融资）**

| 模式 | NPV $M | Peak Equity $M | 合同窗 DSCR | 相对 L3 |
|---|---:|---:|---:|---|
| L4-M Merchant（$7.8，decay −22%） | −3,175 | 5,494 | <0 | 远低于 |
| L4-C Contracted（C1 + 预付） | +4,760 | ~1,102 | 5.3 | 超过 |
| L4-S Strategic（+Backstop + GPU-backed + B200 capex） | **+6,421** | **361** | 6.0 | 大幅超过 |
| L3 Critical IT | +707 | 317 | ≥1.3 | — |

**Certainty Bridge（逐步；MC n=120）**

| 步骤 | NPV $M | CE-NPV $M | P(loss) | Peak $M |
|---|---:|---:|---:|---:|
| 0 Merchant base | −3,175 | −3,302 | 100% | 5,494 |
| 1 + Dedicated 市场价 9.36 | −3,056 | −3,203 | 100% | 5,375 |
| **2 + 5Y Fixed take-or-pay** | **+4,760** | **+3,454** | **0%** | 2,207 |
| 3 + Contracted 融资 lev55/kd7 | +4,760 | +3,454 | 0% | 1,502 |
| 4 + 预付 ~20% TCV | +4,760 | +3,454 | 0% | 1,102 |
| 5 + NVIDIA backstop 75% | +5,807 | +4,454 | 0% | 1,034 |
| 6 + GPU-backed lev70/kd5.9 | +5,807 | +4,454 | 0% | 405 |
| 7 + B200-consistent capex | **+6,421** | **+5,068** | **0%** | **361** |

解读：

- **ΔNPV 主贡献来自固定价 take-or-pay（步骤2，约 +$7.8B）**，不是公开市场价上调（步骤1，仅 +$0.1B 量级）。  
- **融资与预付几乎不改变 Project NPV**（融资中性），但把 Peak Equity 从 $2.2B 压到 $0.36B——这是 IRASR 与 Sponsor 资本效率的核心。  
- **Backstop 贡献约 +$1.0B NPV 与 +$1.0B CE**；采购口径（B200-consistent）再贡献约 +$0.6B。  
- CE-NPV 与 P(loss) 证明：Contracted/Strategic 购买的是**确定性**，而不只是更高期望收入。

### 5.6 Contract Financeability 与 Credit Stress

Financeability Score 将 IG 客户 + 5年 + 高 take-or-pay + 预付 + backstop 映射到 lev≈70%、Kd≈5.9%、tenor 60月；Unrated/短约/无保底则退回 lev≈35%、Kd≈9.5%。  

Strategic 信用压力（确定性情景）：

| 情景 | NPV $M | Peak $M |
|---|---:|---:|
| Base L4-S | +6,421 | 361 |
| 客户第3年退出 | +3,912 | 361 |
| 无 NVIDIA backstop | +5,373 | 361 |
| 续约租金 −30% | +3,855 | 361 |
| 融资冻结（Kd 9.5%、lev55） | +6,421* | 534 |

\*Project NPV 对 Kd 不敏感（融资中性）；Peak Equity 上升才是 Sponsor 痛点。  
**续约悬崖（Renewal Cliff）**：合同到期 × GPU 刷新周期（均约 3–5 年）重叠时，残值、续约重定价、refresh CAPEX 与剩余债务同时冲击——必须单独压力测试。

### 5.7 与 L3 的比较及双甜蜜点

- **Structural Sweet Spot**：L3 AI-ready Critical IT——在无多年期算力合同、无 Vendor 支持时，仍是电力/开发背景 Sponsor 的稳健停留点（CE-NPV 稳健为正）。  
- **Cyclical / Structural（合同化）Sweet Spot**：当 Sponsor 具备 C1 级合同与战略融资能力时，L4-C/S 的确定性 NPV 与 CE-NPV 可超过 L3。  
- **Cyclical Merchant Sweet Spot**：仅在特定历史 Vintage + Scarcity 状态下可能成立；**不能**外推为 2026 Forward 的默认策略。

---

## 6 讨论

### 6.1 Historical Winner ≠ Forward Winner

早期 Vintage 可能享受：低进入 CAPEX + 租金通胀 + scarcity rent + 较强残值。  
当前新进入者可能面对：高进入 CAPEX + 高现价 + 技术刷新 + 不确定未来租金。  
因此过去 GPU 盈利能力不能直接证明未来新购 GPU 的投资价值。

### 6.2 风险迁移而非风险消失

| 模式 | 主要风险 |
|---|---|
| Merchant | 市场租金、利用率、技术、残值 |
| Contracted | 客户信用、合同执行、交付、续约 |
| Strategic | 客户/Vendor 信用与义务、结构化融资、集中度、循环支持 |

Strategic 把风险再分配给资本实力更强的参与者；NVIDIA 将拟议 OpenAI 支持从约 $250B 讨论值缩减至首期少于 $120B 的报道，说明 backstop 对 Vendor 资产负债表并非零成本（标注：proposed / under discussion）[12][13]。

### 6.3 From GPU Financing to Compute as an Asset Class

NVIDIA 2026-08-10 宣布的超过 $500B compute financing platforms[11] 表明：Strategic 模式不是 CoreWeave 的单一例外，而正在被试图**制度化**。路径为：

$$\text{GPU Hardware} \rightarrow \text{Usage-linked Revenue} \rightarrow \text{Institutional Underwriting} \rightarrow \text{Investable Infrastructure}$$

类似飞机租赁/能源项目融资，但设备折旧更快、技术代际更短。

### 6.4 Circular Support Risk

NVIDIA 可能同时：卖 GPU、战略入股、capacity backstop、助力融资。需求下行时风险高度相关。Strategic Finance 提高单项目 Financeability，但可能增加系统层面的相关性与 Vendor 集中风险。

### 6.5 实践含义：玩家类型而非“大小”

- **Type A Uncontracted Sponsor**：有资本、无客户合同 → 默认 L4-M 风险  
- **Type B Contracted Sponsor**：已获高质量 take-or-pay → 可进入 L4-C  
- **Type C Strategic Platform**：Customer + Contract + Vendor + Financing + Ops → L4-S  

真正门槛是 **Customer + Contract + Capital + Vendor**，不是市值本身。  
对土地/电力/许可占优的开发商：

$$\text{Power-secured} \rightarrow \text{AI-ready} \rightarrow \text{Tenant/Compute Contract} \rightarrow \text{GPU}$$

即 **GPU deployment should be demand-led, not inventory-led.**

### 6.6 局限性

筛选级精度；参数 2026-08 快照；Historical cohort 租金路径为结构假设（非完整 realized 回测）；Counterparty PD/LGD 为情景而非评级校准；L5a 仍为收入等效；交易级样本外验证仍待完成；GPU 折扣无公开证据时仅 Sensitivity。

---

## 7 结论

**RQ1** Merchant 口径下 L3/Hosting 仍优于 Power 与 Merchant L4；一旦具备 C1 合同与战略融资，L4-C/S 确定性回报可超过 L3。  

**RQ2** Merchant 延伸的 IRASR 深负（约 −5.8）；$IRASR_{M\to C}$ 与 $IRASR_{C\to S}$ 在 Peak Equity 压缩与 CE 转正下显著为正。  

**RQ3** 最优层级是六维函数；Vintage 与合同结构可改变排序。  

**RQ4** L4 在 Merchant Forward 下毁灭价值；在 5Y Fixed take-or-pay ± Strategic 包装下创造价值并可达 CE-NPV 优于 L3。  

**RQ5** 历史 cohort 相对 Forward 的排序支持 Vintage dependency，但历史“高回报”在本模型全栈口径下仍需更高质量 realized 数据验证——故保持为**可检验假设**，不写成定论。Certainty Bridge 表明 Contracted/Strategic 的核心购买物是**确定性**。

**四句跨周期判断：**

1. **Role 决定现金流归属。**  
2. **Investment Vintage 决定进入成本与周期暴露。**  
3. **Contract 决定未来现金流能否从市场风险转化为信用风险。**  
4. **Capital Structure 与 Vendor Support 决定 Sponsor 最终承担多少风险资本。**  

$$\boxed{\text{Asset Value} \neq \text{Hardware Value}}$$

同一张 GPU：Merchant 下是高折旧、高波动的技术资产；Contracted 下是合同支持的算力基础设施；Strategic 下是 Vendor 支持、机构可融资的 AI 基础设施资产。

**后续工作**：交易级样本外验证；评级校准的违约/回收模型；完整 realized cohort 回测；L5a token 单位经济；lease-tail / balloon 银行级压力；GPU-aware 融资向全表全局重跑。

---

## 参考文献（节选）

[1] McKinsey. *The Cost of Compute*. 2025.  
[4] Morgan Stanley. *Bridging a $1.5tr Data Center Financing Gap*. 2025.  
[5] CoreWeave S-1 / 10-K：committed contracts、take-or-pay、预付、asset-level debt.  
[6] SemiAnalysis GPU rental / Tokenomics.  
[7] CoreWeave–NVIDIA 8-K：residual capacity backstop 至 2032.  
[8] TeraWulf–Anthropic 2026-07-06；Greenlight Electricity Centre.  
[9] CoreWeave DDTL 4.0：~5.9% fixed / SOFR+2.25%.  
[10] NVIDIA $2B CoreWeave investment. 2026-01.  
[11] NVIDIA Compute Financing Platforms（>$500B）官方发布. 2026-08-10.  
[12] Reuters/WSJ：NVIDIA–OpenAI 拟议 ~$250B 支持. 2026-07-26.（**proposed**）  
[13] Reuters/WSJ：拟议支持缩减至首期 <$120B. 2026-08-14.（**proposed / under discussion**）  
[15] IREN SEC：H100 采购锚点（2023/2024）.  
[16][17] CoreWeave / Lambda 2026-08 公开定价页.

**模型与数据**：`https://github.com/tonyhuang23-sys/aidc-optimizer`（private）— `research_v5.py`、`research_outputs/v5/`、`reproduce.py check`。  

**利益声明**：作者机构从事北美 BTM 电力与数据中心开发；P3 套利情景与业务方向相关，已与市场一致 P1 分离。  

**AI 辅助披露**：模型、分析与初稿由 AI 辅助；数值可由随附代码复现。v5.0 依 v5 升级指令修订：Investment Vintage、Certainty Bridge、C1–C4、Financeability、Credit Stress、Strategic casebook；Historical cohort 为结构假设下的筛选级估算，置信度已标注。
