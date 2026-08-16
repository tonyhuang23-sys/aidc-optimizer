# 面向AI基础设施的价值链投资评估模型：经济角色、资产栈与合约结构共同决定的风险调整资本配置框架

## A Value-Chain Investment Evaluation Model for AI Infrastructure: A Risk-Adjusted Capital Allocation Framework Jointly Determined by Economic Roles, Asset Stacks, and Contract Structures

**作者**: WNT Energy 技术研究组
**日期**: 2026年8月
**状态**: 工作论文 v2.0（依审稿意见修订）

---

## 摘要

人工智能数据中心（AIDC）投资在实践与研究中常被简化为单一"数据中心IRR"问题，掩盖了两层结构性事实：其一，同一条价值链上各商业模式的现金流归属由**经济角色（Role）**决定；其二，同一层级的投资经济性由**资产栈（Asset Stack）与合约结构（Contract Structure）**共同决定。本文提出并实现一个价值链投资评估模型：以统一的100 MW参考项目为测试平台，将AIDC投资解构为七种可比较的商业模式；模型采用**资产层与融资层分离的双引擎架构**，以月度频率模拟建设期提款、利息资本化、sculpted摊还、现金扫仓、客户资本与再融资，并首次在该领域引入三项方法论改进——(i) 以**确定性等价CE-NPV=E(NPV)−λ·CVaR₉₅**给出风险调整净现值的标量定义；(ii) 以**IRASR（增量风险调整股本回报=ΔCE-NPV/Δ峰值股本）**作为价值链延伸决策的主指标；(iii) 采用**高斯copula相关性蒙特卡洛**刻画租金—残值—采购价—利用率的联动。验证采用三级体系：Level A参数锚定（Greenlight、TeraWulf–Anthropic两笔公开交易）、Level B内部验证（Sources=Uses恒等、债务滚动清零、IRR/NPV解析解）、Level C初步样本外检验（三项未参与定参的市场数据）。核心实验为一个**资产栈（绿地全栈/棕地）×合约结构（现货/长约）×GPU代际**的三维矩阵：结果显示合约结构是最大杠杆（+~$1.1B NPV）、资产栈次之（+~$0.25B）、GPU代际第三（+~$1.0B），但三个维度全部取最优后，租金模式下的自持GPU仍为NPV负值——其转正需token模式收入或模型层角色。基准情景下价值链中段的Critical IT租赁与GPU托管层构成风险调整"甜蜜点"（CE-NPV为正、损失概率<0.2%）。本文的主结论是：**最优投资层级不是价值链的固定属性，而是Role×Asset Stack×Contract & Capital Structure的函数**；对全栈开发商而言，L3–L3.5仍为基准停留点，GPU层的经济性本质上属于具备棕地资产、长约锁定能力或模型层角色的参与者。

**关键词**: AI基础设施；数据中心投资；价值链；项目融资；确定性等价；CVaR；相关性蒙特卡洛；资产栈；合约结构；Critical IT Capacity；GPU经济学

---

## Abstract

AIDC investment is often reduced to a single "data center IRR", obscuring two structural facts: cash-flow attribution along the value chain is determined by **economic roles**, and the economics of any single layer are jointly determined by the **asset stack** and **contract structure**. This paper implements a value-chain evaluation model on a unified 100 MW reference project with a two-tier asset-financing architecture at monthly resolution, and introduces three methodological advances: (i) a scalar risk-adjusted NPV defined as **CE-NPV = E(NPV) − λ·CVaR₉₅**; (ii) **IRASR** (incremental risk-adjusted sponsor return) as the headline metric for value-chain extension decisions; and (iii) **Gaussian-copula correlated Monte Carlo** linking rent, residual value, purchase price and utilization. Validation follows a three-level protocol: parameter anchoring (Greenlight; TeraWulf–Anthropic), internal validation (Sources=Uses identity; debt roll-forward to zero; analytical IRR/NPV tests), and preliminary out-of-sample checks. The core experiment is a **Greenfield/Brownfield × Merchant/Contracted × GPU-vintage** matrix: contract structure is the dominant lever, followed by asset stack and GPU vintage; yet even the best rental-mode cell remains NPV-negative, implying that positive GPU economics require token-mode revenue or a model-layer role. The headline conclusion: **the optimal layer is not a fixed property of the value chain but a function of Role × Asset Stack × Contract & Capital Structure.**

---

## 1 引言

### 1.1 研究背景与问题

自2024年起，AI基础设施进入史无前例的资本扩张期。McKinsey估计到2030年全球数据中心相关资本需求约6.7万亿美元，其中AI相关约5.2万亿[1]；Morgan Stanley测算2025–2028年仅数据中心资本开支即达2.9万亿美元，其中约1.4万亿可由hyperscaler内部现金流承担，剩余约1.5万亿美元形成外部融资缺口[4]；评级机构已对近1,000亿美元数据中心相关债进行评级[5]；NVIDIA等供应商通过担保、股权与容量回购形成的"循环支持"资本结构进一步放大了体系杠杆[7][9]。

在资本快速堆积的同时，一个对投资人更根本的问题悬而未决：**对于同一个可交付的MW级电力与场址资源，投资人应当投资到价值链的哪一层、以何种资产栈与合约结构、在哪个节点退出？**

### 1.2 研究问题

> **RQ1** 同一100 MW电力资源在七种商业模式下的投资强度、回报与风险敞口如何系统比较？
> **RQ2** 价值链向下游延伸的**增量风险调整股本回报（IRASR）**在何处由正转负？
> **RQ3** 最优投资层级在多大程度上由资产栈（绿地/棕地）与合约结构（现货/长约）重新决定，而非价值链位置本身？

### 1.3 贡献

(1) 前置的Role–Contract–Money Flow生态分析框架（§2）；(2) 资产层与融资层分离的双引擎月度模型及CE-NPV/IRASR风险调整体系（§3）；(3) 三级验证协议（Level A锚定/Level B内部验证/Level C初步样本外检验，§4）；(4) 资产栈×合约结构×GPU代际的核心矩阵实验（§5.2），并据此将"GPU层不赚钱"的单一价值链结论升级为**Role×Stack×Contract三元结论**。

---

## 2 AIDC生态系统、经济角色与资金流

*（本节依审稿意见新增。核心原则：Role定义在"某一笔交易"上，而非公司名称——同一家公司可同时承担多个角色。）*

### 2.1 经济角色矩阵

| Role | 出售什么 | 向谁收费 | 主要资产 | 核心风险 | 代表 |
|---|---|---|---|---|---|
| PowerCo | Firm/Deliverable MW | DC运营商/租户 | 发电+变电+燃料 | COD延误、可用性、气价(可转嫁) | Greenlight |
| DC Landlord | Critical IT MW | Tenant | 建筑+MEP+冷却 | 建设、租户信用、COD | TeraWulf |
| ComputeCo | GPU-hour | AI Lab/企业 | GPU+集群+调度 | 利用率、残值、技术淘汰 | CoreWeave |
| Managed Inference Operator (L5a) | $/token、托管推理 | 应用/企业 | 推理平台+运营 | 需求波动、毛利率 | 独立推理服务商 |
| Frontier Model/App Owner (L5b) | Token/API/订阅/广告 | 终端用户 | 模型IP+客户 | 需求变现、模型经济学 | OpenAI/Anthropic/Meta |
| End Demand | AI产出 | 消费者/企业 | 业务平台 | 变现能力 | 企业客户 |

### 2.2 三条典型资金闭环

**Meta型（captive自用）**：广告现金流→CAPEX→自有DC/GPU/电力→AI提升广告效率→平台现金流。经济回报体现为**增量企业现金流/基建CAPEX**，而非对外租金——Meta不是靠token收入回收AIDC投资，须单列为Captive模式。

**Anthropic型（多源采购+直锁容量）**：客户/API收入+资本→CoreWeave/AWS/Google算力+TeraWulf 401 MW直租→Claude收入。分析重点是长约承诺、电力转嫁与对手方信用能否支撑项目融资。

**CoreWeave型（合同驱动资本循环）**：长期客户合同→收入积压→债务+ABF融资能力→GPU/DC部署→算力交付→偿债+股东回报。**客户合同本身是资本结构的一部分**[4][13]。

### 2.3 对本文的含义

七种商业模式的经济含义由此确立：L0–L1出售稀缺的MW与COD；L2–L3出售可出租的Critical IT容量；L3.5出售运维能力；L4出售GPU小时（承担残值与利用率风险）；L5a出售推理运营margin；L5b出售模型IP价值——**本文模型可评估L0–L5a；L5b（模型层）与Captive模式不属于基础设施投资人可获得的回报函数，仅作为价值归属的外部证据引用（§5.5）**。

---

## 3 模型与方法

*（本节合并原第3、4节并前移，含完整方法学与实现细节；全部经济参数的取值、来源与置信度见附录A。）*

### 3.1 价值链分层与统一物理口径

模型将AIDC项目解构为L0–L5六层、七种可比较商业模式（表1），每层独立核算（即使同属一个投资人亦模拟为独立SPV、按市场化内部价格结算）。物理口径统一为 **Critical IT MW = Generation MW / PUE**；PUE不仅是能效指标，更是价值链换算系数[2]。所有单位价值指标同时报告**$/Site MW（按发电容量）与$/Critical IT MW（按IT容量）双分母**，避免电力层与DC层分母混同。GPU层计价统一为**$/IT-kW-hr**并附$/GPU-hr换算（避免与电价$/kWh混淆；如GB300 NVL72为72 GPU/120 kW-IT=0.6 GPU/IT-kW，故$5.5/GPU-hr≈$3.3/IT-kW-hr）。

**表1 七种商业模式（v2.0将L5拆分为L5a/L5b）**

| 模式 | 层级 | 出售产品 | 计价单位 | 校准/参照锚点 |
|---|---|---|---|---|
| 开发退出 | L0 | Power-secured场址 | $/kW转让价 | 开发MOIC/XIRR |
| Power-only tolling | L1 | Firm MW | $/kW-月容量费 | Greenlight–Meta[8] |
| Powered Shell | L2 | 已通电壳体 | $/kW-月 | — |
| AI-ready Critical IT | L3 | Critical IT容量 | $/kW-月 | TeraWulf–Anthropic[8] |
| GPU托管（到机架） | L3.5 | 机架+电力+冷却+运维 | $/kW-月(含电费) | 匿名棕地项目实盘[14] |
| 算力出租 | L4 | GPU小时 | $/GPU-hr =$/IT-kW-hr | 市场价格指数[6][12] |
| Managed Inference（L5a） | L5a | 托管推理服务 | $/M token | 匿名棕地项目 GLM52模型[14] |
| *Frontier Model Owner（L5b）* | *L5b* | *Token/API/订阅* | *GP/GPU-hr* | *仅作价值归属证据（§5.5），不建模* |

### 3.2 资产层模型

月度频率生成各层SPV的收入、成本与资本序列：

**（1）tolling结构（L1）**。收入=容量费×MW+燃料/变动成本转嫁；燃料与碳pass-through下风险存在而经济敞口≈0，真实利润变量是Tolling Margin（$/kW-月）。碳排放按TIER强度-基准差值×碳价计（Alberta参数包），CER已暂停不重复计入[10]。

**（2）租约结构（L2/L3/L3.5）**。收入=租金×(1+递增率)^t；到机架增量按棕地改造实盘校准（DLC冷却$1.7k+网络$1.5k+存储$0.5k+软件$0.5k≈$4k/IT-kW）[14]。

**（3）GPU资产（L4/L5a）**。收入遵循RevPAGH逻辑：

$$RevPAGH_t = u_t \cdot R_0 \cdot f_{reset}^{\,c} \cdot (1+g)^{k}, \qquad u_t = u^* \cdot (0.65+0.35\,\tfrac{t}{T_{ramp}})$$

其中$g$为租金衰减率、$f_{reset}$为刷新代际租金重置系数、$c$为刷新周期序号。资本开支含48个月刷新事件（旧卡按残值率出售、新卡按折价系数采购）；利用率含24个月爬坡；**债务期限硬约束≤刷新周期**（48mo），故刷新点债务余额按构造为零、残值风险完全由股权承担。

**（4）税收**。直线折旧+亏损结转的简化公司税引擎，残值按资本利得计税。

### 3.3 融资层模型（与资产层严格分离）

- **建设期**：S曲线资本开支逐月pro-rata提款；利息资本化（IDC）计入债务余额；承诺费按未提取额；
- **运营期**：四种摊还（直线/年金/sculpted-to-DSCR/bullet）；现金扫仓在DSCR缓冲之上按比例提前还款；
- **资本来源**：Sponsor Equity+项目债务+客户资本（直接冲减股本需求）[4]；
- **再融资模块**：COD后按退出杠杆×EBITDA重置债务、释放股本（Capital Recycling）；
- **约束**：逐月DSCR、Min/Avg DSCR、LLCR、Debt Tenor ≤ 资产经济寿命[5]。

### 3.4 风险调整体系（v2.0新增定义）

**（1）确定性等价净现值**。为使"风险调整"具有标量定义而非定性评分，本文定义：

$$CE\text{-}NPV = E[NPV] - \lambda \cdot CVaR_{95}, \qquad CVaR_{95}=E[NPV \mid NPV \leq P5]$$

正文取λ=0.5（报告λ=0/1作敏感性）。该式为Certainty Equivalent形式：λ=0退化为期望NPV，λ=1对尾部完全悲观。

**（2）IRASR——增量风险调整股本回报（本文主指标）**：

$$IRASR_i = \frac{CE\text{-}NPV_{i+1} - CE\text{-}NPV_i}{PeakSponsorEquity_{i+1} - PeakSponsorEquity_i}$$

IRASR>0才构成向下一层延伸的必要条件——它直接对应理论目标max(风险调整NPV/峰值股本)，避免了ΔNPV/ΔCAPEX退回"项目资产回报"的问题（ΔNPV/ΔCAPEX保留为辅助指标）。

**（3）相关性蒙特卡洛**。GPU层四参数（租金率、刷新残值、采购价、利用率）通过高斯copula联合采样，相关矩阵取ρ(租金,残值)=0.6、ρ(租金,利用率)=ρ(租金,采购价)=ρ(残值,采购价)=0.3——短缺市场中租金与残值同向波动的经验证据见附录B。每个情景N≥800（正文注明），损失概率附二项95%置信区间；**不再使用"0%"表述，改报"<x%（95%CI a–b）"**。

**（4）融资审读指标（v2.0新增）**。鉴于GPU层可能出现"负Project NPV与高Equity IRR并存"，所有情景补充：Equity NPV@Ke、MIRR（融资率=债务利率、再投资率8%）、TVPI/MOIC、Peak Equity、现金流符号翻转计数；当Project NPV<0而Equity IRR>0时自动标记**Leverage-distorted IRR**；Min DSCR<covenant的情景标记**Not financeable under covenant**，其Equity IRR不作为投资收益展示。

### 3.5 实现与复现

Python实现（约2,000行，开源）：`core`（月度财务数学/税收）、`models`（七模式资产构建器）、`financing`（融资引擎）、`risk`（相关性MC/龙卷风）、`evaluate`（IRASR/增量/五维矩阵）、`report`、CLI。运行示例与全部结果复现命令见附录C。双辖区参数包（Alberta/Texas）差异参数均有出处标注[10][11]；分层WACC严格区分（Power 8%→L5a 19%），禁止统一贴现率。

---

## 4 校准与验证（三级体系）

*（依审稿意见重构：将原"双锚点校准"严格拆分为锚定与验证。）*

### 4.1 Level A——参数锚定（Parameter Anchoring）

两笔公开交易用于**确定参数区间**（非独立验证）：

**表2 Level A锚定结果**

| 锚点 | 公开事实 | 模型输出 | 性质 |
|---|---|---|---|
| TeraWulf–Anthropic[8]（2025-10公告，2027H2首批交付） | 401 MW IT、20年、名义~$19B、≈$197/kW-月 | 名义$19.0B；首年收入$0.96B | 恒等式复核（租金参数即由该交易反推） |
| Greenlight[8] | 932 MW、CA$4.6B、~60%债务；全包CA$90–120/MWh；固定回收CA$60–80/MWh | 杠杆62%；EBITDA CA$81/MWh（区间上缘）；全包CA$105/MWh | 区间锚定；容量费偏市场有利侧，由MC覆盖 |

### 4.2 Level B——内部验证（Internal Validation）

**表3 Level B结果（tests/test_validation.py + 专项核查，全部通过）**

| 检查项 | 结果 |
|---|---|
| Sources=Uses恒等（L3） | 债务+股本+客户资本 vs 总投入：$780.3M vs $780.3M，偏差0.00e+00 |
| 债务滚动 | 期末余额$0.0M（sculpted保底清偿）；IDC $14.2M |
| 实现杠杆 vs 目标LTC | 61.3% vs 60%（+1.3pp由IDC入账解释） |
| GPU期限匹配 | L4债务48mo=刷新周期；刷新点债务余额=0（按构造） |
| IRR/NPV解析解单元测试 | <1e-9 |
| Equity CF符号结构 | 各层≤1次符号转换，无多根IRR风险 |

### 4.3 Level C——初步样本外检验（Out-of-sample, n=3）

使用**未参与定参**的市场数据检验模型预测（完整样本外验证列为后续工作）：

| 检验 | 外部数据（来源/置信度） | 模型隐含值 | 判定 |
|---|---|---|---|
| C1 GPU系统价 | DGX B300 8-GPU系统$400–500K（Spheron，0.70）[15] | $480K/台（$32k/IT-kW×15kW） | 带内 ✓ |
| C2 租金口径 | DigitalOcean H100按需$4.41/GPU-hr（2026-08，0.75）[15] → ≈$3.5/IT-kW-hr | 基准3.0（合约偏中）/短缺3.3 | 系统性低于按需价、介于合约与现货之间，方向一致 ✓ |
| C3 债务承载 | 公开DC REIT/机构take-out杠杆5.5–6.0× ND/EBITDA（EQIX–GIC/CPP JV语境）[4] | L3隐含≈2.6×（项目融资口径） | 保守；存在再融资释放空间（Capital Recycling上行）✓ |

---

## 5 结果

*（NPV均以$/Site-MW与$/IT-MW双分母口径存于结果文件；正文表格为总额。蒙特卡洛为相关性MC（L4）与独立MC（其余层），N与置信区间随表注明。）*

### 5.1 基准情景：七模式统一比较（Alberta；括号内Texas）

**表4 基准结果（2026-08参数）**

| 模式 | CAPEX $M | 峰值股本 $M | Project IRR | Equity IRR | NPV $M | P(NPV<0) [95%CI] |
|---|---:|---:|---:|---:|---:|---|
| 开发退出† | 20 | 20 | — | — | +5 | 15% [11–18%] |
| Power-only tolling | 133 | 45 | 21.1% | 28.0% | +186 (230) | <0.7% [0–0.7%] |
| Powered Shell | 469 | 230 | 12.5% | 14.4% | +85 (78) | 12% [8–16%] |
| AI-ready Critical IT | 773 | 287 | 20.1% | 26.0% | +676 (619) | <0.2% [0–0.2%] |
| GPU托管（到机架） | 837 | 368 | 21.7% | 26.2% | +707 (633) | ~1% [0–2%] |
| 算力出租（自持GPU） | 5,829 | 5,475 | -29.7% | 1.8% | -3,351 (-2,957) | 100% [100–100%] |
| Managed Inference (L5a) | 5,277 | 5,085 | -35.9% | 21.5%‡ | -2,784 (-2,590) | 100% [100–100%] |

†开发退出不再列示IRR于可比列，改报：**MOIC 2.00×、年化XIRR 36%、27个月退出**。
‡Leverage-distorted IRR标记（见5.3）。DSCR：Power/Shell/Critical IT均≥1.30×。

### 5.2 核心实验：资产栈 × 合约结构 × GPU代际（RQ3）

**表5 L4算力出租三维矩阵（Project NPV $M / Project IRR）**

| | Merchant现货（$3.0, -22%/yr, 75%） | Contracted长约（$3.2, -8%/yr, 95%） |
|---|---|---|
| **Greenfield全栈**（电厂$1,150/kW+DC$8k/kW） | **-3,351 / -29.7%**（Case A） | **-2,214 / -16.6%**（Case B） |
| **Brownfield棕地**（并网$150/kW+改造$5.5k/kW） | **-3,100 / -31.3%**（Case C） | **-1,973 / -16.9%**（Case D） |
| 棕地+长约+二手H100（$12k/IT-kW, $1.9） | — | **-794 / -6.5%**（最优租金格） |

三个发现：

**（1）合约结构是最大杠杆**：现货→长约使NPV改善约$1.1B（A→B），远大于资产栈的~$0.25B（A→C）与GPU代际的~$1.0B（D→最优格）。这与§5.4短缺情景的结论一致——**多年期take-or-pay的实质是锁定价格衰减路径，锁定衰减比提高利用率更主导**。

**（2）资产栈单独不足以翻盘**：棕地节省约$310M资本投入，但在GPU资本（$2.56B）占主导的层中只改善NPV约$250M——"二手GPU经济学只在棕地成立"的表述须修正为**"资产栈×合约×代际三者叠加仍不足以使租金模式转正"**。

**（3）租金模式的最优格仍为负**（-6.5% IRR）：与内部选卡研究[14]报告的"二手H100 IRR 46%"的分歧由此彻底定位——后者是**token模式收入**（L5a口径，棕地+GLM52推理收入$846M/yr），非租金。GPU层的正经济性须以L5a/L5b角色实现。

**主结论（RQ3）**：**最优投资层级不是价值链的固定属性，而是Role×Asset Stack×Contract & Capital Structure的函数。**

### 5.3 短缺情景与融资指标审读

以高频市场情报（附录B）构造短缺情景（衰减-5%、残值0.30、$3.3/IT-kW-hr、利用率85%）：

**表6 L4短缺情景：完整指标组（修审稿#4）**

| 指标 | 短缺修正 | +Vendor Backstop(55%/8.5%) |
|---|---:|---:|
| Project NPV $M | -1,412 | -1,412 |
| Project IRR | -2.5% | -2.5% |
| Equity IRR | 58.6% **[Leverage-distorted]** | 61.1% **[Leverage-distorted]** |
| Equity NPV @Ke=15% | **+1,492** | — |
| MIRR | 25.9% | — |
| TVPI/MOIC | 6.38× | — |
| Peak Equity $M | 755 | 727 |
| Min DSCR | 1.48 | **0.90 → Not financeable under covenant** |
| 相关MC E[NPV] / CVaR₉₅ / CE-NPV(λ=.5) | -1,406 / -2,671 / **-2,038** | — |
| P(NPV<0) [95%CI] | 96% [94.6–97.4%] | — |

**审读**：Equity IRR 58.6%并非伪造——Equity NPV@Ke确为正（+$1.5B）、TVPI 6.4×、现金流仅一次符号转换（无多根IRR）。但其经济实质是**价值从债权人向股权的转移**：项目NPV@15%为-$1.4B而股权NPV@15%为+$1.5B，隐含债务NPV@15%约-$2.9B——债权人以8.5–9.5%利率为高波动资产融资，承担了被侵蚀的价值。真实的CoreWeave式定价（9.25%+GPU抵押+厂商容量回购[4][13]）正是市场对该风险的补偿。Vendor Backstop情景Min DSCR=0.90×<covenant，标记为**不可融资结构**，其61.1%的Equity IRR不作为投资收益展示。这组指标审读本身构成对KBRA"初期DSCR良好≠风险低"[5]的模型化实现。

### 5.4 IRASR：价值链延伸决策（RQ2）

以CE-NPV（λ=0.5，相关性MC）计算从L3继续向GPU层延伸的增量风险调整股本回报：

$$IRASR_{L3\to L4(短缺)} = \frac{-2,038-517}{755-287} \times \frac{1}{1}\,(每百万峰值股本) = \mathbf{-5.82}$$

即：**在最有利的短缺假设下，股东每向GPU层多投入1美元峰值股本，毁灭约5.8美元的确定性等价价值**。辅助口径ΔNPV/ΔCAPEX序列：开发→Power **+1.65** →Shell **-0.31** →Critical IT **+2.04** →托管 **+0.08** →自持GPU **-0.86**——两条口径一致指向L3–L3.5为基准停留点。

L3层自身的风险调整指标（独立MC, N=1500）：E[NPV]=+$719M，P5=+$379M，CVaR₉₅=+$315M，**CE-NPV(λ=.5)=+$517M**，P(NPV<0)<0.2% [95%CI 0–0.2%]——尾部仍为正，风险调整后依然稳健。

### 5.5 L5拆分与价值归属证据

**L5a（Managed Inference，本文建模）**：无模型IP的推理运营商，收入$/token但只获基础设施/运营margin——基准NPV -$2,784M、修正情景（$7.0/IT-kW-hr、衰减-10%）NPV -$1,222M，方向与L4一致。

**L5b（Frontier Model Owner，不建模）**：SemiAnalysis Tokenomics估计OpenAI/Anthropic在GB300集群上可产生>$100B/GW-yr的API收入，对应租金成本仅~$12B/GW-yr[6]——**8:1的价值差归属模型层**。这一外部证据与L4/L5a的深度负NPV互洽：GPU层的钱存在，但由Role决定归属。**Meta型captive模式**（§2.2）则根本不通过对外收费回收，其正确的评价指标是增量企业FCF/基建CAPEX，不属于第三方投资人可复制的机会。

---

## 6 讨论

### 6.1 与文献的分歧

**（1）资本流向≠回报来源**。McKinsey显示GPU层集中~60%资本开支[1]，本文显示该层（租金模式）NPV为负——宏观资本动员（含vendor循环支持[13]）与微观sponsor回报是两个问题；评级看下行保护、贷款人赚利差、股权担残值，同一资产对不同Role是完全不同的回报函数。

**（2）衰减假设的时变性**。文献默认长期衰减（-20~-25%/yr）[3][12]，但2025年末以来短缺使合约价反转（H100一年合约+40%）[6]、残值指数不降反升（附录B）。本文处理：-22%为长期结构假设、-5%~-10%为短缺情景、MC相关性（租金↔残值ρ=0.6）显式刻画该机制——静态LCOAI式分析[3]在结构转换期会系统性失真。

**（3）技术变量的二阶效应**。He强调上游技术变量传导[2]；本文龙卷风显示L3层NPV波动由租金（±15%→$400M）与造价（$151M）主导，PUE仅一次换算。裁定：租约锁定后市场变量主导（本文），GPU刷新重定价后技术变量主导（He）；效率降额参数列为后续工作。

### 6.2 局限性

（1）筛选级精度：**税务与备付金简化的量化敏感性见§6.3**——直线折旧使基准结果系统性偏保守（L3约-5%），未建模DSRA使L3的Equity IRR高估约90bp，方向性结论不受影响；（2）参数为2026-08快照，波动率高；（3）USD单一币种；（4）相关性矩阵为经验设定（仅租金↔残值有较强证据）；5.4节IRASR的CE-NPV分母取独立MC（L3）与相关MC（L4）混合口径，严格版应统一；（5）Level C样本外检验n=3，非完整验证；（6）L5b与Captive模式未建模——它们不属于基础设施投资人的回报函数，但其存在意味着本文对"GPU层"的负结论**不能**外推到模型公司或hyperscaler的自建决策；（7）锚点为公开报道口径而非交易原始文件。

### 6.3 税务与备付金简化的量化敏感性（回应外部评估意见）

针对"税务与备付金简化"的评估意见，本文以模型内置的余额递减折旧引擎与DSRA注入法量化该简化的重要性边界（复现命令见附录C）：

**（1）折旧方法**。以余额递减法近似CCA/MACRS加速折旧（L1取20%DB、L3取15%DB、L4按5年期MACRS取40%DB）：

| 层 | 直线折旧NPV | 加速折旧NPV | ΔNPV | 偏差 |
|---|---:|---:|---:|---:|
| L1 Power | +191M | +195M | +4M | +2.1% |
| L3 Critical IT | +707M | +744M | +38M | +5.3% |
| L4（短缺情景） | -1,412M | -1,121M | +291M | +20.6% |

三个判断：(i) 基准直线折旧对可投资层（L1/L3）构成**系统性保守偏差约2-5%**，即真实经济性略优于正文报告值；(ii) 加速折旧对短寿命GPU资产的影响显著（折旧前置的税盾现值大），L4改善$291M后**仍为-$1,121M**——主结论（租金模式GPU层不成立）在税务最优假设下依然稳健；(iii) Tax Equity结构对本文资产类别不适用（燃气发电/DC/GPU无ITC/PTC等可转让税收抵免，tax equity主要服务于可再生能源与储能），故未建模不构成缺口。

**（2）DSRA机制**。以6个月偿债准备金注入法测算L3：债务$478M对应月偿债$3.6M，DSRA锁定$22M共228个月（不计利息收益，保守），Equity IRR由25.99%降至25.09%（**-90bp**）。影响真实但量级有限；正式可融资级模型应进一步计入DSRA的设立/释放时点与利息收益，并补充lease-tail/balloon覆盖测试[5]。

**（3）总评**。两项简化合计对L3的Equity IRR影响约-90bp至-1.5pp量级、对NPV影响+5%以内（保守方向），不改变本文任何方向性结论；对L4的税务影响虽大（+$291M）但不足以翻转符号。

---

## 7 结论

**RQ1**：七模式的风险调整排序为——Power-only（二手燃机+tolling，Equity IRR 28%，P损失<0.7%）与L3 Critical IT/L3.5托管（CE-NPV +$517M，P损失<0.2%）构成可投资区间；租金模式自持GPU在全部三维矩阵格中NPV为负。

**RQ2**：IRASR在L3→GPU层为-5.82（即使短缺情景），ΔNPV/ΔCAPEX同向印证；基准停留点L3–L3.5。

**RQ3**：最优层级由Role×Asset Stack×Contract & Capital Structure共同决定——合约结构（+$1.1B）>GPU代际（+$1.0B）>资产栈（+$0.25B），三者叠加仍不足以使租金模式转正；GPU层的正经济性属于具备棕地资产、长约能力与（关键地）模型层角色的参与者。

本文最具持久价值的三个思想：**Role决定现金流归属；Asset Stack决定经济性；Contract与Capital Structure决定sponsor最终承担的风险与回报。**"L3是甜蜜点"这一具体结论会随市场价格变化，但这三句话构成的分析框架不随行价波动。

后续工作：完整样本外验证（5+笔未定参交易）、参数相关性的事后校准、CME租金期货对冲模块（2026-10上市）、KBRA式lease-tail/balloon压力测试、L5a token收入端的正式建模、以及MACRS/CCA税务明细与DSRA动态机制的银行级实现（其重要性边界已在§6.3量化）。

---

## 参考文献

[1] McKinsey & Company. *The Cost of Compute: A $7 Trillion Race to Scale Data Centers*. 2025-04-28.
[2] He, Q. *A Unified Metric Architecture for AI Infrastructure*. arXiv:2511.21772, 2025.
[3] Curcio, E. *Introducing LCOAI*. arXiv:2509.02596, 2025.
[4] Morgan Stanley Research. *Bridging a $1.5tr Data Center Financing Gap*. 2025-07-16.
[5] KBRA. *Data Centers: Developments and Trends in Project Finance*. 2026-01-13.
[6] SemiAnalysis. *The Great GPU Shortage* / H100 1-Year Rental Index / Tokenomics. 2026.
[7] NVIDIA Corporation. Form 10-K FY2026. SEC.
[8] 公开交易与公司公告口径：Greenlight Electricity Centre（932 MW一期/CA$4.6B/60%债务/Meta长期tolling）；TeraWulf–Anthropic 401 MW Critical IT租约（**2025-10公告**，首批容量2027H2交付，名义~$19B）。
[9] Wall Street Journal. NVIDIA–OpenAI ~$250B融资担保谈判报道. 2026-07-26.
[10] Canada–Alberta Energy MOU. 2025-11-27；Alberta Bill 30, 2026.
[11] JEFFXI Grand Prairie项目实盘造价. WNT内部资料, 2026.
[12] Epoch AI / SemiAnalysis GPU Pricing Index / AIMultiple（2026-08检索）.
[13] WNT技术研究组. *AI基础设施融资中的循环支持模式*（v3.1）. 内部研究, 2026.
[14] WNT技术研究组. *万卡集群选卡分析*；*20MW矿场改造AIDC方案设计v4.0*（匿名棕地项目实盘）及*20MW GLM52推理工厂经济模型v1*. 内部研究, 2026.
[15] WNT技术研究组. *GPU价格租金三源核实报告*. 2026-08-15.

---

## 附录A 参数全量溯源表（经济性指标·来源·取值方法）

来源代码：**[S1]** JEFFXI实盘造价[11]｜**[S2]** TeraWulf–Anthropic[8]｜**[S3]** Greenlight[8]｜**[S4]** 匿名棕地项目 v4.0实盘[14]｜**[S5]** 三源核实报告[15]｜**[S6]** Morgan Stanley[4]｜**[S7]** 加阿能源MOU/Bill 30[10]｜**[S8]** 万卡集群选卡[14]｜**[S9]** 行业基准数据库（aidc-scheme-design skill，北美区间）。置信度沿用[15]的0–1评分。

### A.1 参考项目与税务

| 参数 | Alberta | Texas | 来源 | 置信度 | 取值方法 |
|---|---|---|---|---|---|
| 发电容量 | 100 MW | 100 MW | 框架约定 | — | 标准测试平台 |
| PUE | 1.25 | 1.25 | [S9] | 0.8 | 液冷+寒冷气候中值；IT MW=80 |
| 税率 | 23% | 23% | 联邦15%+省8%/联邦21%+TX~2% | 0.9 | 法定税率相加 |
| 折旧 | 直线240mo | 同 | 简化 | — | CCA/MACRS近似 |

### A.2 电力层（L1）

| 参数 | 取值 | 来源 | 置信度 | 取值方法 |
|---|---|---|---|---|
| capex_per_kw | $1,150 (AB) / $1,050 (TX) | [S1] | 0.85 | 9E CC设备$765/kW+业主费用/物流/60Hz余量上浮50%；德州供应链略低 |
| heat_rate | 7.6 GJ/MWh (HHV) | OEM参数 | 0.8 | 9E CC HHV口径；德州SC取9.5 |
| gas_price | $1.60/GJ AECO / $2.85 HH | [S5] | 0.8 | AECO≈CA$2.2/GJ×0.714；Henry Hub $3.0/MMBtu÷1.055 |
| 碳价/强度/基准 | $95/t; 0.42; 0.37 tCO₂/MWh | [S7] | 0.9 | TIER CA$130/t×0.714；强度-基准差值计税，转嫁租户 |
| capacity_payment | $18/kW-月 (AB) | [S3] | 0.7 | Meta全包CA$90-120/MWh扣燃料后折算；TX取$17 |
| availability | 92% | [S1] | 0.8 | 9E机队运行实绩 |
| FOM/VOM | $22/kW-yr / $3.5/MWh | [S1] | 0.85 | 实盘O&M预算 |
| 寿命/残值 | 360mo / 10% | 行业 | 0.8 | 重型燃机惯例 |

### A.3 开发层（L0）

| 参数 | 取值 | 来源 | 取值方法 |
|---|---|---|---|
| 开发成本 | AB$20M（地2.5+互联10+审批4+其他3.5）/ TX$19.5M | [S1][S9] | AUC Rule007+EPEA+互联研究+土地期权分项 |
| 开发周期 | AB 24mo（Bill 30合格可压缩至~12）/ TX 18mo | [S7] | Bill 30需≥$250M门槛，取未合格基线 |
| 退出价 | $400/kW (AB) / $430 (TX) | 市场参照 | power-secured+许可稀缺性溢价；MC σ=0.25 |

### A.4 数据中心层（L2/L3/L3.5）

| 参数 | 取值 | 来源 | 置信度 | 取值方法 |
|---|---|---|---|---|
| shell_capex / rent | $4.2k/kW / $78 | [S9] | 0.6 | 北美壳体区间 |
| ready_capex | $8.0k (AB) / $7.3k (TX) | [S9] | 0.7 | 北美Tier III液冷就绪$6-9k中值；AB加冬季措施费 |
| ready_rent | $185/kW-月 | [S2] | 0.85 | TeraWulf $197保守折让 |
| **到机架增量** | **$4.0k/kW** | [S4] | 0.85 | DLC$1.7k+网络$1.5k+存储$0.5k+软件$0.5k（$632M/12MW全案分解） |
| hosting_rent | $300/kW-月 | [S9] | 0.6 | 到机架含电费托管溢价 |
| opex / escalator | $30/kW-yr / 2% | [S9] | 0.7 | 行业基准 |
| 内部购电价 | $58/MWh | 模型LCOE口径 | — | 自家PowerCo成本加成 |

### A.5 GPU层（L4/L5a）

| 参数 | 取值 | 来源 | 置信度 | 取值方法 |
|---|---|---|---|---|
| capex_per_kw_it | $32k | [S5][S8] | 0.65 | GB300 NVL72 $3.85M/120kW=32.1k；B300整机36.7k；DGX B300 20-23k（区间带外检验C1通过） |
| rate_per_kw_hr | $3.0/IT-kW-hr | [S5] | 0.8 | ≈B200/B300合约($3.68/GPUh×0.533=$1.96)与现货($6-8.3)之间；折算$5.0-5.6/GPUh |
| rate_decay | -22%/yr | [S8][S5] | 0.8 | H100两年-65~70%年化；短缺情景-5%~-10%（黄仁勋/SemiAnalysis亲证反弹，附录B） |
| utilization | 75%（爬坡24mo） | [S8] | 0.7 | neocloud中值；短缺85% |
| refresh | 48mo；新卡×0.85；租金重置×0.8 | [S8] | 0.6 | 代际价格与单位算力租金经验 |
| residual_at_refresh | 15%（短缺0.30） | [S5] | 0.7 | 二手H100=新品40%佐证；Silicon Data 2026残值升值为上调依据 |
| L5a rate | $6.0→短缺$7.0/IT-kW-hr | [S8] | 0.5 | token收入折算，波动大 |

### A.6 融资层（按层级）

| 层 | 杠杆 | 利率 | 期限 | 摊还 | 依据 |
|---|---|---|---|---|---|
| L1 Power | 65% | 6.2% (AB)/5.8% (TX) | 240mo | sculpted 1.35× | Greenlight 60%锚+项目融资惯例[3]；IG YTW 5.1%+利差[6] |
| L2 Shell | 50% | 7.0% | 180mo | sculpted | 无租约现金流弱 |
| L3 CriticalIT | 60% | 6.5% | 228mo | sculpted 1.30× | hyperscaler租约增信[4][5] |
| L35 Hosting | 55% | 7.5% | 180mo | sculpted | — |
| L4 Compute | 35% | **9.5%** | **48mo=刷新** | mortgage | **CoreWeave $2bn HY 9.25%实盘[6]**；期限匹配硬约束 |
| L5a | 25% | 11.5% | 36mo | mortgage | 高不确定性 |
| WACC | Power 8%→L5a 19%分层 | 文献+市场 | 0.8 | 禁止统一贴现率（§3.5） |
| 客户资本 | L3 $15M | [4] | — | — | 租户定金/预付冲减股本 |

### A.7 风险参数（MC）

各层σ：租金率0.15-0.25、造价0.15-0.20、气价0.30、利用率0.10（正态）、残值0.35；GPU四参数相关矩阵见§3.4；来源[15]经验波动率。hurdle=分层WACC。

---

## 附录B 高频市场情报与置信度评分（摘要）

*（依审稿意见自正文降级至此。完整87条证据与评分见[15]及x_intel_raw.txt。）*

**核心数据点**：H100一年合约$1.70(2025-10)→$2.35(2026-03)，黄仁勋2026-08-10帖亲证（置信0.92）；8月实时带H100 $2.70-2.76/H200 $3.30-3.37/B200 $4.88-5.00/B300 $5.64-5.85每GPU小时（日更账号，0.75）；Silicon Data残值指数显示H100/B200 2026年升值、到期H100以原经济性95%续租（0.80）；现货与合约倒挂（marketplace $1.03-1.91 < 合约$2.35）；hyperscaler溢价~120%；NVIDIA残值担保上限25%+$500B融资平台[7][9]；中国B300整机现货RMB 1,200-1,450万vs海外成本~300万（中文单源0.45-0.60，仅作情景）。冲突记录：合约上涨vs现货下跌并存（口径分裂，非矛盾）；SiliconData H100 $7.20 ticker与SemiAnalysis差3×（方法学差异，剔除）。

---

## 附录C 复现命令

```bash
# 基准七模式 + 相关MC + 图表
python -m aidc_optimizer --config configs/alberta.yaml --mc 200 --tornado --out results/alberta
# 短缺情景（§5.3）
python -m aidc_optimizer --case compute --set gpu.rate_decay=-0.05 \
  gpu.residual_pct_at_refresh=0.30 gpu.rate_per_kw_hr=3.3 gpu.utilization=0.85
# 2×2矩阵（§5.2）：棕地 = power.capex_per_kw=150 dc.ready_capex_per_kw=5500 power.dev_capex_musd=6
#                长约 = gpu.rate_per_kw_hr=3.2 gpu.rate_decay=-0.08 gpu.utilization=0.95
# 税务敏感性（§6.3）：--set tax.method=declining_balance tax.db_rate=0.40（L4按5yr MACRS近似）
# DSRA注入法（§6.3）：对equity现金流在COD月-DSRA、到期月+DSRA后重算IRR（脚本见结果目录）
# 校准与验证：python tests/test_validation.py
```

---

**模型与数据可得性**：aidc_optimizer v1.1（含双辖区参数包、Level A/B测试、相关性MC与2×2矩阵脚本），位于《数据中心投资评估框架/aidc_optimizer》。

**利益声明**：作者所属机构从事北美BTM电力与数据中心开发业务，模型参数含机构自有实盘造价数据；校准与测试脚本公开以便独立复核。

**AI辅助披露**：本文模型实现、数据分析与初稿写作由AI辅助完成，全部数值结果可由随附代码复现；v2.0依外部审稿意见修订，校准锚点与引用经人工核对。
