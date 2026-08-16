# 面向AI基础设施的价值链投资评估模型：经济角色、资产栈与合约结构共同决定的风险调整资本配置框架

## A Value-Chain Investment Evaluation Model for AI Infrastructure: A Risk-Adjusted Capital Allocation Framework Jointly Determined by Economic Roles, Asset Stacks, and Contract Structures

**作者**: WNT Energy 技术研究组
**日期**: 2026年8月
**状态**: 工作论文 v4.0
**版本记录**: v1.0 初稿；v2.0 依审稿意见一（8项）；v3.0 依评估意见二（P0×4全部修复、P1×5全部落实、P2部分落实）——主题为**删、校、证**；v3.1 依评估意见三——**口径与归属**（情景包因子、CE-NPV与WACC职责分工、融资价值归属贴现率口径、L5a边界）；v3.2 依评估意见四——**数值透明与表述限定**（IRASR分母底层值、CAPEX/IDC口径、"显著"改"经济上较大"、八格限定、删"首次"）；v3.3 依复现对齐——**代码=论文**（reproduce.py一键复现+黄金结果校验，表3/4/5/6与IRASR数字对齐当前代码，P1 EqIRR 14.1%、IRASR -5.76）。**v4.0 依L4研究指令**（《L4_GPU租金重新校准与CoreWeave式商业模式》）——主题为**L4三层重构与结论翻转**：以2026-08公开一手定价重校GPU租金（B200非Spot中位$7.8/GPUh、Dedicated $9.36/GPUh），将L4拆为Merchant/Contracted/Strategic三模式，引入GPU-aware融资（修复基础融资引擎对GPU采购资本不记账、低估L4峰值股本的缺陷）；结论：**Merchant L4永不成立；5年固定价take-or-pay下L4-C/S确定性NPV大幅翻正并超过L3**（+4.8B~+6.4B vs L3 +0.7B），旧"L3甜蜜点"结论限定于Merchant结构与重定价合同；同一张GPU因Role×Contract×Capital Structure不同可以成为完全不同的资产。新代码：`research_l4.py` + `research_outputs/`。

---

## 摘要

人工智能数据中心（AIDC）投资在实践与研究中常被简化为单一"数据中心IRR"问题，掩盖了两层结构性事实：其一，同一条价值链上各商业模式的现金流归属由**经济角色（Role）**决定；其二，同一层级的投资经济性由**资产栈（Asset Stack）、合约结构与GPU代际**共同决定。本文将Role、Asset Stack、Contract、Project Finance、相关性风险模拟与Sponsor级资本配置系统整合进一个统一的价值链投资框架：以100 MW参考项目为测试平台解构七种商业模式，采用资产层与融资层分离的双引擎架构，风险调整采用**确定性等价CE-NPV = (1−λ)·E(NPV) + λ·ES⁻₅%(NPV)**与**IRASR（增量风险调整股本回报）**两项自定义指标，并以高斯copula刻画租金—残值—采购价—利用率的联动。验证采用三级体系（Level A参数锚定 / Level B内部验证 / Level C外部基准合理性检验）。核心实验为完整的**2×2×2因子设计**（绿地/棕地×现货/长约×新卡/二手GPU，8格），主效应排序**GPU代际(+$1.45B)＞合约结构(+$0.91B)≫资产栈(+$0.23B)**（经济情景包口径），且合约×代际存在经济上较大的负交互（-$0.45B）。**v4.0按2026-08公开市场价重构L4：在Merchant结构下八格仍全部为NPV负值（该结论限定于Merchant+重定价合同）；但L4拆分为三模式后，5年固定价take-or-pay的Contracted/Strategic模式确定性NPV大幅翻正（+$4.8B~+$6.4B）并超过L3（+$0.7B）——L4的经济性由合同结构主导（价值桥：合同+$7.8B ≫ NVIDIA Backstop +$1.0B ≫ 采购条款+$0.6B ≫ 市场价+$0.3B），融资与客户资本不创造Project NPV、只压缩Peak Equity。** 电力层的参数一致性检验表明：市场一致组合（新建CCGT+投资级tolling）的Equity IRR为14.1%，广为引用的28%来自"二手设备+溢价长约"的套利组合。本文主结论：**最优投资层级不是价值链的固定属性，而是Role×Asset Stack×Contract & Capital Structure×市场状态的函数**——L4从"深负"到"超L3"的翻转正是该命题最强的实证。

**关键词**: AI基础设施；数据中心投资；价值链；项目融资；确定性等价；期望短缺；相关性蒙特卡洛；因子实验；资产栈；合约结构；GPU-backed融资；take-or-pay；Critical IT Capacity

---

## Abstract

*(English abstract condensed; see Chinese version above for the authoritative text.)* This paper integrates economic roles, asset stacks, contract structures, project finance, correlated risk simulation and sponsor-level capital allocation into a unified value-chain framework. Key metrics include CE-NPV = (1−λ)·E(NPV) + λ·ES⁻₅%(NPV) and IRASR. The 2×2×2 factorial main effects are GPU vintage (+$1.45B) > contract (+$0.91B) ≫ asset stack (+$0.23B). **v4.0 recalibrates the ComputeCo (L4) layer to 2026-08 public market pricing and splits it into Merchant / Contracted / Strategic models. Merchant L4 remains deeply NPV-negative under any market rate; but a 5-year fixed-price take-or-pay contracted or strategic structure flips L4 strongly positive (+$4.8B–+$6.4B), exceeding L3 (+$0.7B). The L4 value bridge attributes ~+$7.8B to the take-or-pay contract, ~+$1.0B to NVIDIA-style capacity backstop, ~+$0.6B to purchase terms, and only ~+$0.3B to the market-rate recalibration itself; financing and customer capital create no project NPV but compress peak sponsor equity from ~$1.5B to ~$0.4B.** The market-coherent power layer yields 14.1% Equity IRR. Headline conclusion: **the optimal AIDC layer is a function of Role × Asset Stack × Contract & Capital Structure × market state** — the L4 flip is the strongest evidence yet.

---

## 1 引言

### 1.1 研究背景与问题

自2024年起，AI基础设施进入史无前例的资本扩张期：到2030年全球数据中心资本需求约6.7万亿美元（其中AI相关约5.2万亿）[1]；2025–2028年数据中心资本开支约2.9万亿美元、外部融资缺口约1.5万亿[4]；评级机构已对近1,000亿美元数据中心相关债评级[5]；供应商"循环支持"结构进一步放大体系杠杆[7][9]。

对投资人而言更根本的问题：**对同一可交付的MW级电力与场址资源，应当投资到价值链的哪一层、以何种资产栈与合约结构、在哪个节点退出？**

### 1.2 研究问题

> **RQ1** 七种商业模式的投资强度、回报与风险敞口如何系统比较？
> **RQ2** 价值链延伸的增量风险调整股本回报（IRASR）在何处由正转负？
> **RQ3** 最优层级在多大程度上由资产栈、合约结构与GPU代际重新决定？
> **RQ4（v4.0新增）** 以2026-08公开市场价与CoreWeave式资本结构重估后，L4（ComputeCo）何时从毁灭价值转为创造价值？其相对L3的排序由什么决定？

### 1.3 贡献声明（依评估意见二、四弱化首创性表述）

本文不声称发明CVaR、copula或增量回报指标；其贡献在于**将Role、Asset Stack、Contract、Project Finance、相关性风险模拟与Sponsor级资本配置系统整合进统一的AIDC价值链投资框架**，并以完整因子实验与三级验证支持其结论的可复现性；v4.0进一步把L4从单一"GPU租金"抽象重构为Merchant/Contracted/Strategic三模式的合同化资产结构。

---

## 2 AIDC生态系统、经济角色与资金流

### 2.1 底层资产的理论化：可交付容量（Deliverable MW @ COD）

对AIDC而言，MW本身不是完整商品。本文将底层稀缺资源定义为：

$$\text{AI Infrastructure Capacity} = f(\text{MW},\ \text{COD},\ \text{Availability},\ \text{Contractability},\ \text{Location})$$

Power、Critical IT、Compute各层本质上是对同一稀缺资源——**可按时交付的容量**——进行逐级价值转换。COD确定性具有独立价格（Time-to-Power Premium）[5]。该定义构成贯穿全文的底层资产主线。

### 2.2 经济角色矩阵与三条资金闭环

*（沿用v2.0 §2框架：Role定义在交易而非公司名上。）*

| Role | 出售什么 | 向谁收费 | 主要资产 | 核心风险 |
|---|---|---|---|---|
| PowerCo | Firm MW @ COD | DC运营商 | 发电+燃料 | COD、可用性、气价(可转嫁) |
| DC Landlord | Critical IT MW | Tenant | 建筑+MEP | 建设、租户信用 |
| ComputeCo | GPU-hour | AI Lab | GPU+集群 | 利用率、残值、技术淘汰 |
| Managed Inference (L5a) | $/token托管推理 | 应用/企业 | 平台+运营 | 需求、毛利率 |
| Frontier Model (L5b) | Token/API/订阅 | 终端用户 | 模型IP+客户 | 变现能力 |

三条资金闭环：**Meta型**（广告现金流→自有基建→AI→广告效率，Captive模式）；**Anthropic型**（多源采购算力+直锁Critical IT容量）；**CoreWeave型**（长期合同→融资能力→部署→交付→偿债，**客户合同本身是资本结构的一部分**[4][13]）。本文模型覆盖L0–L5a；L5b与Captive不属于基础设施投资人的回报函数，仅作价值归属证据（§5.6）。

---

## 3 模型与方法

### 3.1 分层、口径与单位纪律

七种商业模式（L0–L5a，表1）在统一100 MW参考项目上比较；Critical IT MW = Generation MW / PUE；单位价值指标双分母（$/Site-MW与$/IT-MW）；GPU层计价为$/IT-kW-hr并附$/GPU-hr换算（v4.0按GPU代际单独建立GPU/kW转换，B200取0.533 GPU/IT-kW）。

**表1 七种商业模式**（同v3.3：dev/power/shell/critical_it/gpu_hosting/compute/L5a；v4.0将compute进一步拆为L4-M/C/S，§5.6）

### 3.2 资产层模型

月度频率：tolling结构（容量费+燃料/碳转嫁）；租约结构（租金×递增率，到机架增量$4k/IT-kW按棕地实盘校准[14]）；GPU资产（RevPAGH=u_t·R_0·f_reset^c·(1+g)^k，48个月刷新事件，利用率爬坡）；直线折旧简化公司税。v4.0为L4-C/S新增**take-or-pay保底收入**（合同期内按billable利用率0.95计费、价格路径锁定，而非physical utilization×衰减价格）与**NVIDIA式容量Backstop**（未售容量×市场价的75%）。

### 3.3 融资层模型

与资产层严格分离：S曲线逐月提款+IDC+承诺费；四种摊还；现金扫仓；客户资本冲减股本；再融资模块；逐月DSCR/LLCR/期限匹配校验。**v4.0融资修正（P-方法学5）**：基础引擎只对建设期capex借债，GPU采购发生在COD/刷新节点（运营期窗口外），导致GPU资本既不计入债务也不计入权益现金流——v3.x的L4峰值股本被系统性低估。v4.0引入**GPU-aware融资**：债务按全部capex（含GPU）计杠杆、GPU采购按杠杆借债+权益补足，用于L4三模式（§5.6）。

### 3.4 风险调整体系

**（1）确定性等价净现值**：下尾期望短缺 $ES^-_{5\%}(NPV) = E[NPV \mid NPV \leq P5]$，$CE\text{-}NPV = (1-\lambda)\cdot E(NPV) + \lambda \cdot ES^-_{5\%}(NPV)$。λ=0风险中性、λ=1完全尾部惩罚，正文取λ=0.5并报告λ∈{0,0.5,1}敏感性。

**（1a）与WACC的职责分工**：分层WACC负责系统性风险补偿，λ·ES⁻₅%负责sponsor对项目特异性左尾的额外厌恶，二者不构成重复调整。

**（2）IRASR**：$$IRASR_i = \frac{CE\text{-}NPV_{i+1} - CE\text{-}NPV_i}{PeakSponsorEquity_{i+1} - PeakSponsorEquity_i}$$，增量风险调整股本回报，作为资本配置决策规则。

**（3）相关性蒙特卡洛**：GPU四参数（租金率σ=0.25、残值σ=0.35、采购价σ=0.15、利用率σ=0.10）经高斯copula联合采样，ρ(租金,残值)=0.6、其余0.25。损失概率附**Wilson 95%置信区间**。

**（4）融资审读指标**：Equity NPV@Ke、MIRR、TVPI/MOIC、Peak Equity、Leverage-distorted IRR标记、Not financeable标记；统一贴现率口径的融资价值归属分析（§6.2）。

### 3.5 实现与复现

Python实现（开源）：七模块架构、双辖区参数包、分层WACC。`reproduce.py`一键复现v3.3全部表格并校验黄金结果；`research_l4.py`实现v4.0 L4三模式（含GPU-aware融资）。复现命令见附录C。

---

## 4 校准与验证（三级体系）

### 4.1 Level A——参数锚定

**表2 Level A结果**

| 锚点 | 公开事实 | 模型输出 | 性质 |
|---|---|---|---|
| TeraWulf–Anthropic（**2026-07-06公告**[8]，首批容量2027年末交付） | 401 MW IT、20年、名义~$19B、≈$197/kW-月 | 名义$19.0B；首年收入$0.96B | 恒等式复核（租金参数由该交易反推） |
| Greenlight[8] | 932 MW、CA$4.6B、~60%债务；全包CA$90–120/MWh | 杠杆62%；EBITDA CA$81/MWh（上缘） | 区间锚定，偏市场有利侧 |
| **v4.0 GPU租金[16][17]** | Lambda/CoreWeave B200：非Spot中位$7.8/GPUh、Dedicated $9.36 | 模型按产品层级分层定价（Spot/Instance/Dedicated） | 输入锚定（不再单一均值） |

### 4.2 Level B——内部验证

六项全部通过：Sources=Uses恒等（偏差0.00e+00）、债务滚动期末清零、杠杆61.3% vs LTC 60%（IDC解释）、GPU期限匹配、IRR/NPV解析解<1e-9、现金流符号≤1次转换。

### 4.3 Level C——外部基准合理性检验

三项检验（DGX B300价格带、DigitalOcean H100折算、REIT/JV杠杆）性质为输入假设与隐含值的市场合理性核对。真正的交易级样本外验证（≥5笔未参与定参的交易）列为v4.x工作。

---

## 5 结果

### 5.1 电力层参数一致性检验（P1-3）

**表3 电力层参数一致性（100 MW，Alberta）**

| 情景 | 组合 | NPV $M | Project IRR | Equity IRR | 经济性质 |
|---|---|---:|---:|---:|---|
| **P1 市场一致基准** | 新建CCGT($3,500/kW)+投资级tolling($28/kW-月)+低利差(5.8%) | +104 | 11.0% | 14.1% | Greenlight型基础设施回报 |
| P2 桥接合约 | 二手GT($1,150/kW)+中期合约($12/kW-月)+高利差(8.5%)+杠杆50% | +129 | 16.9% | 19.2% | 商业燃机市场常态 |
| P3 套利组合 | 二手GT($1,150/kW)+溢价长约($18/kW-月) | +191 | 21.1% | 28.0% | 设备×合约市场套利（upside） |

**结论修正**：P1与P3之间约14个百分点差值是设备市场×合约市场套利空间的量化。**CAPEX口径与IDC边界**：P1的$3,500/kW按overnight成本输入，融资层单独计IDC（P1下IDC≈$7M、占CAPEX 1.9%），不存在IDC双计；若Greenlight口径含融资成本，overnight等价约$3,430/kW，P1 EqIRR约+0.2–0.3pp，结论不变。

### 5.2 基准情景：七模式统一比较（Alberta；括号Texas）

**表4 基准结果（电力层为P1口径；2026-08参数）**

| 模式 | CAPEX $M | 峰值股本 $M | Project IRR | Equity IRR | NPV $M | 观察损失率 [Wilson 95%CI] |
|---|---:|---:|---:|---:|---:|---|
| 开发退出† | 20 | 20 | — | — | +5 | 13.9% [12.2–15.7%] |
| Power-only（P1口径） | 368 | 133 | 11.0% | 14.1% | +104 (245) | 低 |
| Powered Shell | 469 | 238 | 12.5% | 14.4% | +87 (79) | 15.6% [13.9–17.5%] |
| AI-ready Critical IT | 773 | 317 | 20.1% | 26.0% | +707 (647) | 0/1500 [0–0.26%] |
| GPU托管（到机架） | 1,093 | 501 | 19.5% | 23.5% | +733 (655) | 0.3% [0.1–0.8%] |
| 算力出租（现货）‡ | 5,829 | 1,097 | -29.7% | — | -3,351 (-3,381) | 800/800 [99.5–100%] |
| Managed Inference (L5a) | 5,533 | 895 | -35.9% | — | -2,784 (-2,817) | ~100% |

†开发退出报MOIC 2.00×、年化XIRR 36%、27个月。‡"峰值股本"列统一按Peak Equity口径报告（v3.3起）；**v4.0注意：本行L4峰值股本按基础融资引擎计算，未计入GPU采购权益资本投入，系统性低估——GPU-aware融资下的L4真实Peak Equity见§5.6（L4-M约$5.5B）**。L4的Project NPV不受融资口径影响（-3,351M对应Merchant结构）。

辅助增量链（ΔNPV/ΔCAPEX）：Dev→Power +0.28；Power(P1)→Shell −0.17；Shell→Critical IT +2.04；Critical IT→Hosting +0.08；Hosting→L4(Merchant) −0.86。价值创造重心在"电力→AI-ready"转换环节；L4-Merchant不构成延伸价值（§5.6将重新定义）。

### 5.3 核心实验：完整2×2×2因子设计（P1-2）

**表5 L4算力出租全因子矩阵（Project NPV $M / IRR / 峰值股本$M）**——*该矩阵基于Merchant结构+重定价合同；§5.6将证明结论随合同结构翻转。*

| 资产栈\合约 | Merchant×新卡 | Merchant×二手 | Contracted×新卡 | Contracted×二手 |
|---|---|---|---|---|
| **Greenfield** | -3,351 / -29.7% / 1,097 | -1,674 / -20.0% / 1,158 | -2,214 / -16.6% / 755 | -987 / -6.8% / 732 |
| **Brownfield** | -3,111 / -31.3% / 789 | -1,441 / -21.1% / 844 | -1,984 / -17.0% / 558 | **-757 / -5.4% / 535** |

*GPU租金率（$/IT-kW-hr）：新卡现货$3.0/长约$3.2，二手现货$1.9/长约$2.0；二手GPU $12k/IT-kW、残值0.30；长约：衰减-8%、利用率95%；资产栈：绿地 power $1,150/kW+ready $8,000/kW-IT，棕地 power $150/kW+ready $5,500/kW-IT；其余同基准。*

**主效应与交互（NPV $M，全因子均值分解）**：

| 效应 | 量级 | 解读 |
|---|---:|---|
| **GPU代际（二手−新卡）** | **+1,450** | 最大杠杆：GPU采购价差主导 |
| **合约结构（长约−现货）** | **+909** | 第二：锁定衰减路径的价值 |
| 资产栈（棕地−绿地） | +233 | 第三：电力/建筑沉没的贡献有限 |
| 合约×代际交互 | **−446（次可加）** | 二手卡租金带较窄，长约溢价对其增量更小 |
| 合约×资产栈交互 | −6（≈0） | 两维度近似正交 |

**因子解读边界（P-方法学1）**：上述效应为**经济情景包效应**（"Contracted"同时改变租金/衰减/利用率；"Used GPU"同时改变采购价/残值/租金），非单一因果归因。**两项结论修正**：(1) 排序为GPU代际＞合约结构≫资产栈；(2) 合约×代际负交互（经济上较大，未做统计显著性检验）。**八格限定**：八格在本文2026-08参数与预设经济情景包范围内全部NPV为负（Merchant结构口径；§5.6的5年固定价take-or-pay将翻转此结论）。

### 5.4 λ敏感性与IRASR（P1-4、P0-2）

**表6 CE-NPV对风险厌恶参数λ的敏感性（$/M）**

| 情景 | λ=0（风险中性）E(NPV) | λ=0.5 | λ=1（完全尾部）ES⁻₅% |
|---|---:|---:|---:|
| L3 Critical IT（独立MC, N=1500） | +706 | **+505** | +304 |
| L4 短缺修正（相关MC, N=800） | -1,414 | **-2,024** | -2,633 |
| L4 基准现货（相关MC, N=800） | -3,349 | **-3,826** | -4,303 |

**L3>L4的排序在全部λ取值下不变**（该结论限于Merchant结构L4）。**IRASR（基于未四舍五入底层结果）**：

$$IRASR_{L3\to L4(短缺)} = \frac{-2,528.5}{+438.8} = \mathbf{-5.76}$$

分母底层值（Peak Equity口径）：L3 $316.5M vs L4短缺 $755.3M，Δ=+438.8M。表4"峰值股本"列自v3.3起统一Peak Equity口径（L3=317）。即股东每多投1美元峰值股本于Merchant结构GPU层，毁灭约5.8美元确定性等价价值。（注：正文一律采用底层精确值。）

### 5.5 L5拆分、价值归属与短缺情景

L5a（Managed Inference）：基准NPV -$2,784M、修正情景（$7.0/IT-kW-hr、衰减-10%）-$1,222M——**目前的$/IT-kW-hr输入是token经济学的收入等效折算，而非严格的token单位经济模型**（转换引擎列为v4.x工作）。L5b（Frontier Model Owner）：SemiAnalysis估计GB300集群上模型层可产生>$100B/GW-yr API收入vs ~$12B/GW-yr租金成本[6]——**8:1价值差归属模型层**，与Merchant结构L4/L5a负NPV互洽：GPU层的钱存在，但由Role决定归属。

**结论边界（P-表述强化1）**：本文对L4/L5a的负结论限定于"基础设施投资人自持GPU做Merchant Compute Rental"这一Role与收入函数；**v4.0证明Contracted/Strategic结构可翻转L4**（§5.6），故该负结论不可外推至合同化GPU资产参与者。

短缺情景完整指标组（Merchant结构）：NPV -$1,412M、Project IRR -2.5%、Equity IRR 58.6%[Leverage-distorted]、Equity NPV@Ke +$1,492M、MIRR 25.9%、TVPI 6.38×、Min DSCR 1.48、Peak Equity $755M（基础融资口径，低估）；Vendor Backstop情景Min DSCR 0.90×→**Not financeable under covenant**。

### 5.6 L4三层重构：Merchant / Contracted / Strategic（依L4研究指令）

v3.x对L4的核心结论建立在**Merchant结构+合同期内价格衰减**的假设上。本轮依据2026-08公开一手定价（Lambda[17]、CoreWeave[16]）重构L4，并引入GPU-aware融资。

**GPU租金重校（B200，0.533 GPU/IT-kW）**：Spot $4.25/GPUh≈$2.27/IT-kW-hr；普通Instance $6.69–6.99≈$3.57–3.73；**非Spot公开中位 $7.8≈$4.16**；**Dedicated Cluster $9.36≈$4.99**。原模型基准$3.0/IT-kW-hr≈$5.63/GPUh，低于公开非Spot中位（Q1=是）。**L4-M租金重校独立效应很小**：即使$9.36/GPUh，Merchant结构NPV仍-3,056M vs 旧基准-3,351M——单纯抬租金翻不动L4（Q2=否）。

**表7 L4三模式（GPU-aware融资；确定性结果）**

| 模式 | 租金锚 | 合同 | 融资 | NPV $M | Peak $M | DSCR(合同窗) | 盈亏平衡 |
|---|---|---:|---:|---:|---:|---:|---:|
| **L4-M Merchant** | $7.8/GPUh | 无，decay -22%/年 | 杠杆35%/Kd 9.5% | **-3,175** | 5,494 | <0 | $30+/GPUh（不可达） |
| **L4-C Contracted** | $9.36/GPUh | 5年固定价take-or-pay | 杠杆55%/Kd 7.0% | **+4,760** | 1,352 | 5.3 | $3.42/GPUh |
| **L4-S Strategic** | $9.36/GPUh | 5年固定价take-or-pay | 杠杆70%/Kd 5.9%+客户资本$500M+Backstop+B200 capex | **+6,421** | 361 | 6.0 | $3.00/GPUh |

*稳健性：L4-C用市场中位价$7.8仍+3,509M；合同期内-3%/年温和衰减仍+1,112M（超L3）。L3对照：NPV +706.5M、Peak $316.5M。*

**（1）租金重校的独立效应很小**（Q2=否，见上）。**（2）合同结构是主导杠杆**：5年固定价take-or-pay把NPV从-3,056M推至+4,760M（Δ≈+$7.8B）——机制是同时锁定价格路径（消除合同期内衰减塌缩）与billable利用率（0.95保底），与"锁定衰减率比提高利用率更主导"一致但量级更大。**（3）融资与客户资本不改Project NPV，只改资本效率**：杠杆0.55→0.70、Kd 7.0→5.9%、客户资本$150M→$500M对NPV无贡献（融资中性），但把Peak Equity从1,352M压至361M——这是GPU-backed融资的意义，也是IRASR的载体。**（4）Vendor Backstop +$1,047M、采购条款（B200 capex $32k→$21.3k/kW-IT）+$613M**。

**L4 Value Bridge（§11）**：Merchant Base −3,351M → +市场价 +294M → **+take-or-pay +7,815M** → +融资/客户资本 Δ0（Peak 2,207→1,352M）→ +NVIDIA Backstop +1,047M → +B200 capex +613M = **Strategic NPV +6,421M**。

**Q1–Q5回答**：Q1=是（原模型≈$5.63/GPUh低于公开非Spot中位$7.8）；Q2=否（Merchant不翻正）；Q3=是（固定价take-or-pay下L4-C/S确定性NPV大幅超过L3，DSCR 4.5–6.0健康）；Q4=桥分解见上；Q5=主要是**B（Dedicated Cluster Premium）+C（长期合同锁价锁量）**，D/E（Vendor/融资）通过压缩Peak Equity与尾部风险起作用，A（租金本身）单独不足以翻正。

### 5.7 L4结论翻转的条件边界

L4-C/S的翻正高度依赖**5年固定价take-or-pay**这一核心假设。其经济含义是：客户购买的已不是"一张GPU的市场租金"，而是**合同化的AI算力基础设施容量**。若合同采用市场重定价（-3%/年温和衰减），L4-C仍+1,112M（超L3）；若回到Merchant现货重定价，则深负。**确定性NPV翻正≠风险调整后占优**：L4-S在8年重定价口径下CE-NPV（λ=0.5）≈-$45M（P(NPV<0)=26%），仍低于L3的+$505M；5年固定价合同的风险主要在**合同对手方信用与续约重定价**，不在GPU市场波动。合同现金流可见性→bankability→杠杆的传导（§6.3）是L4-S真正超越L3的机制。

---

## 6 讨论

### 6.1 与文献的分歧（资本流向≠回报来源；衰减假设的时变性；技术变量二阶效应）

### 6.2 融资价值归属 ≠ 价值创造

短缺情景呈现Project NPV(-$1.4B，按WACC)与Equity NPV@Ke(+$1.5B)并存。**只有当股权与债务现金流采用同一贴现率时，NPV才满足加总恒等**。本文采用**统一未杠杆贴现率口径的融资价值归属分析**：$NPV_{proj}=NPV_{equity}+NPV_{debt}$（现金流可加性恒真），-1.4B=+1.5B+(-2.9B)表明融资合同把项目总价值从债务方再分配给股权方，而非创造价值。v4.0的L4价值桥同样体现此原则：融资/客户资本对Project NPV贡献为零（融资中性），只改Peak Equity。

### 6.3 融资能力作为核心解释变量

Financeability是**资产价值本身的构成部分**：优质合约同时改善收入确定性、尾部风险、债务承载、股本需求、资本成本与再融资机会。Contract→现金流可见性→Bankability→杠杆→Sponsor资本效率的传导链，是AIDC与一般科技投资最大的区别，也是L4-S翻正（§5.6）与v3.3合约主效应（+$909M）的深层机制。

### 6.4 税务与备付金简化的量化敏感性（直线折旧保守偏差2–5%、DSRA约-90bp、L4税务+$291M仍不翻转）

### 6.5 局限性

（1）筛选级精度；（2）参数2026-08快照；（3）USD单一币种；（4）相关矩阵为经验设定；（5）Level C为合理性检验而非样本外预测验证（v4.x目标：≥5笔交易的Prediction-vs-Actual）；（6）L5a为收入等效折算而非token单位经济模型；（7）L5b/Captive不建模；（8）电力层P1的MC样本量未与其他层对齐；（9）**v4.0新增：L4-C/S的5年固定价take-or-pay是核心假设，其风险在合同对手方信用与续约重定价而非GPU市场波动，本模型未建模对手方违约/预付机制（KBRA式lease-tail/balloon压力测试列为v4.x工作）；（10）GPU-aware融资已用于L4三模式（§5.6），但v3.3其余表格的L4峰值股本仍为基础融资口径（低估），未全局重跑。**

---

## 7 结论

**RQ1**：市场一致口径下（电力层P1），Merchant结构下七模式排序为Critical IT租赁与GPU托管（CE-NPV +$505M、观察损失0/1500）＞Power-only基础设施回报（14.1% EqIRR）≈Shell（边际）；Merchant L4与L5a在基准下深度为负。**v4.0把L4重构为三模式后，Contracted/Strategic L4确定性NPV（+$4.8B~+$6.4B）大幅超过L3**——排序本身变成Role与合同结构的函数。

**RQ2**：IRASR在L3→Merchant-GPU为**-5.76**；但该指标随合同结构翻转——5年固定价take-or-pay下L4-C/S的增量风险调整回报显著为正（确定性NPV +4.8B~+6.4B vs 增量Peak Equity 1.0B~1.4B）。价值创造重心在"电力→AI-ready→合同化算力"的转换环节。

**RQ3**：完整2×2×2因子实验给出主效应排序**GPU代际(+$1.45B)＞合约结构(+$0.91B)≫资产栈(+$0.23B)**（Merchant口径）；v4.0证明合约结构在固定价take-or-pay下的量级放大一个数量级（+$7.8B），合约×代际次可加同样成立。

**RQ4（v4.0）**：以2026-08公开市场价与CoreWeave式资本结构重估后，L4从"毁灭价值"（Merchant，-$3.2B）翻转为"创造价值"（Contracted/Strategic，+$4.8B~+$6.4B），条件是**多年期固定价take-or-pay + （NVIDIA级）Vendor Support + GPU-backed融资**。Merchant L4永不成立（盈亏平衡$30+/GPUh不可达）；Contracted盈亏平衡仅$3.42/GPUh，Strategic $3.00/GPUh——远低于公开价，价格不再是约束，合同可获得性与融资结构才是。

**v4.0核心翻转**：旧结论"L3–L3.5为风险调整甜蜜点"应限定为**Merchant结构与重定价合同**下的结果。同一张GPU，因Role（Merchant vs Strategic）、Contract（现货 vs 固定价take-or-pay）、Capital Structure（高息低杠杆 vs GPU-backed低息高杠杆）不同，NPV从-3,175M到+6,421M——L4的翻转是"**最优投资层级不是价值链的固定属性，而是Role×Asset Stack×Contract×Capital Structure×市场状态的函数**"这一框架命题的最强实证。

**实践者的决策逻辑**：对能源/基础设施开发商，若无多年期take-or-pay合同与Vendor Support，停留于L3（控制可交付MW→AI-ready Critical IT）仍是稳健选择；对CoreWeave类参与者（具备客户合同、融资、厂商支持与规模采购），L4-S是价值链上确定性回报最高的环节。二者并不矛盾——它们处于不同的Role。

后续工作（v4.x，按优先级）：**(1) 交易级样本外验证集**（≥5笔/层，含CoreWeave公开财务的粗粒度单位经济对账）；**(2) 合同对手方信用与take-or-pay违约/预付建模**（KBRA式lease-tail/balloon压力测试）；**(3) L5a的GPU→Token单位经济转换引擎**；**(4) GPU-aware融资向全模型其余表格全局重跑**。

---

## 参考文献

[1] McKinsey & Company. *The Cost of Compute: A $7 Trillion Race to Scale Data Centers*. 2025-04-28.
[2] He, Q. *A Unified Metric Architecture for AI Infrastructure*. arXiv:2511.21772, 2025.
[3] Curcio, E. *Introducing LCOAI*. arXiv:2509.02596, 2025.
[4] Morgan Stanley Research. *Bridging a $1.5tr Data Center Financing Gap*. 2025-07-16.
[5] KBRA. *Data Centers: Developments and Trends in Project Finance*. 2026-01-13.
[6] SemiAnalysis. *The Great GPU Shortage* 及 Tokenomics 模型. 2026.
[7] NVIDIA Corporation. Form 10-K FY2026. SEC.
[8] 公开交易报道口径：Greenlight Electricity Centre（932 MW/CA$4.6B/60%债务/Meta长期tolling）；TeraWulf–Anthropic（401 MW Critical IT/20年/名义~$19B，**2026-07-06公告**）。经内部框架文档整理。
[9] Wall Street Journal. *NVIDIA与OpenAI商谈约$250B融资担保*. 2026-07-26.
[10] Canada–Alberta Energy MOU；Alberta Bill 30 — Expedited 120-Day Approvals Act, 2026.
[11] JEFFXI Grand Prairie项目实盘造价. WNT内部资料, 2026.
[12] Epoch AI / SemiAnalysis GPU Pricing Index / AIMultiple Cloud GPU Index（2026-08检索）.
[13] WNT技术研究组. *AI基础设施融资中的循环支持模式*. 内部研究, 2026.
[14] WNT技术研究组. *万卡集群选卡分析* 及 *20MW矿场改造AIDC方案设计v4.0*（匿名棕地项目口径）. 内部研究, 2026.
[15] WNT技术研究组. *GPU价格租金三源核实报告*. 2026-08-15.
[16] **CoreWeave Pricing / 官方定价与融资披露**（HGX H100/B200 On-demand与Spot报价、S-1/投资者关系committed contracts与NVIDIA capacity backstop）. 2026-08检索. https://www.coreweave.com/pricing
[17] **Lambda Pricing / 1-Click Clusters**（H100/B200 Instance与Dedicated Cluster公开报价）. 2026-08检索. https://lambda.ai/pricing

**模型与数据可得性**：开源仓库 `aidc-optimizer`（GitHub，private；Python包、脱敏参数包、`reproduce.py`一键复现v3.3黄金结果、`research_l4.py`实现v4.0 L4三模式、`research_outputs/`）。复现：`pip install -r requirements.txt && python reproduce.py check`。

**利益声明**：作者所属机构从事北美BTM电力与数据中心开发业务，模型参数含机构自有实盘造价数据；P3套利情景与机构业务方向相关，已在§5.1显式分离于市场一致基准P1。

**AI辅助披露**：模型实现、数据分析与初稿写作由AI辅助完成，全部数值结果可由随附代码复现；v3.0–v3.3依外部评估意见二/三/四与复现对齐修订，数字经代码重跑校验；v4.0依L4研究指令修订，L4三模式与价值桥由 `research_l4.py` 计算（GPU-aware融资、2026-08公开市场价、5年固定价take-or-pay假设），结论允许翻转且已翻转。
