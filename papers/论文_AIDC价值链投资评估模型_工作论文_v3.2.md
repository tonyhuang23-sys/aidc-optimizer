# 面向AI基础设施的价值链投资评估模型：经济角色、资产栈与合约结构共同决定的风险调整资本配置框架

## A Value-Chain Investment Evaluation Model for AI Infrastructure: A Risk-Adjusted Capital Allocation Framework Jointly Determined by Economic Roles, Asset Stacks, and Contract Structures

**作者**: WNT Energy 技术研究组
**日期**: 2026年8月
**状态**: 工作论文 v3.2
**版本记录**: v1.0 初稿；v2.0 依审稿意见一（8项）；v3.0 依评估意见二（P0×4全部修复、P1×5全部落实、P2部分落实）——主题为**删、校、证**：删除过度结论、校正数学与口径、增强实验设计与统计规范。v3.1 依评估意见三（3项方法学修订+2项表述强化）——主题为**口径与归属**：明确2×2×2为经济情景包效应（非单一因果归因）、说明CE-NPV与WACC的职责分工、重构融资价值归属的统一贴现率口径；并强化L5a结论边界与投资人决策逻辑表述。v3.2 依评估意见四（2项数值口径核查+3项表述收紧）——主题为**数值透明与表述限定**：明示IRASR分母的L3/L4峰值股本底层值（$316.5M/$755.3M，Δ=+438.8M，Peak Equity口径）并标注表4列口径跨层不一致；将Power CAPEX拆分为overnight与IDC并声明无IDC双计（P1下IDC≈$7M、占CAPEX 1.9%）；"显著负交互"改"经济上较大的负交互"、"八格全负"限定于2026-08参数与八个预设经济情景包、贡献声明删除"首次"。

---

## 摘要

人工智能数据中心（AIDC）投资在实践与研究中常被简化为单一"数据中心IRR"问题，掩盖了两层结构性事实：其一，同一条价值链上各商业模式的现金流归属由**经济角色（Role）**决定；其二，同一层级的投资经济性由**资产栈（Asset Stack）、合约结构与GPU代际**共同决定。本文将Role、Asset Stack、Contract、Project Finance、相关性风险模拟与Sponsor级资本配置系统整合进一个统一的价值链投资框架：以100 MW参考项目为测试平台解构七种商业模式，采用资产层与融资层分离的双引擎架构（月度频率模拟建设期提款、IDC、sculpted摊还、现金扫仓、客户资本与再融资），风险调整采用**确定性等价CE-NPV = (1−λ)·E(NPV) + λ·ES⁻₅%(NPV)**与**IRASR（增量风险调整股本回报）**两项自定义指标，并以高斯copula刻画租金—残值—采购价—利用率的联动。验证采用三级体系：Level A参数锚定（Greenlight、TeraWulf–Anthropic 2026-07-06公告的401 MW/20年/~$19B租约）、Level B内部验证（Sources=Uses恒等等六项）、Level C外部基准合理性检验。核心实验为完整的**2×2×2因子设计**（绿地/棕地×现货/长约×新卡/二手GPU，8格），并分解主效应与交互效应：**GPU代际（+$1.45B）＞合约结构（+$0.91B）≫资产栈（+$0.25B）**（上述效应按经济情景包口径报告，非单一因果归因），且合约×代际存在**经济上较大的负交互**（−$0.45B，次可加）；八格在**本文2026-08参数与八个预设经济情景包范围内**全部为NPV负值，即租金模式下自持GPU在该参数区间内均不成立（更低采购价、更高take-or-pay租金、客户预付或更强厂商残值担保等组合未在八格内检验，理论上有翻转可能），其转正需token模式收入或模型层角色。电力层的参数一致性检验表明：市场一致组合（新建CCGT+投资级tolling）的Equity IRR为13.6%，广为引用的28%来自"二手设备+溢价长约"的套利组合，两者约14个百分点的差值正是设备市场×合约市场套利空间的量化。基准情景下Critical IT租赁与GPU托管层构成风险调整"甜蜜点"（CE-NPV为正、观察损失率0/1500），且该结论对风险厌恶参数λ∈{0, 0.5, 1}稳健。本文主结论：**最优投资层级不是价值链的固定属性，而是Role×Asset Stack×Contract & Capital Structure×市场状态的函数**。

**关键词**: AI基础设施；数据中心投资；价值链；项目融资；确定性等价；期望短缺；相关性蒙特卡洛；因子实验；资产栈；合约结构；Critical IT Capacity

---

## Abstract

*(English abstract condensed; see Chinese version above for the authoritative text.)* This paper integrates economic roles, asset stacks, contract structures, project finance, correlated risk simulation and sponsor-level capital allocation into a unified value-chain framework. Key metrics include CE-NPV = (1−λ)·E(NPV) + λ·ES⁻₅%(NPV) and IRASR (incremental risk-adjusted sponsor return). The core experiment is a complete 2×2×2 factorial design (Greenfield/Brownfield × Merchant/Contracted × New/Used GPU) with main-effect decomposition (reported as economic-package effects, not single-variable causal attribution): **GPU vintage (+$1.45B) > contract structure (+$0.91B) ≫ asset stack (+$0.25B)**, with a materially large negative contract×vintage interaction; all eight cells remain NPV-negative within the paper's 2026-08 parameter range and eight preset economic-package scenarios. Parameter-coherence tests show the often-quoted 28% power-layer Equity IRR reflects an equipment×contract arbitrage combination; the market-coherent alternative yields 13.6%. Headline conclusion: **the optimal AIDC layer is a function of Role × Asset Stack × Contract & Capital Structure × market state.**

---

## 1 引言

### 1.1 研究背景与问题

自2024年起，AI基础设施进入史无前例的资本扩张期：到2030年全球数据中心资本需求约6.7万亿美元（其中AI相关约5.2万亿）[1]；2025–2028年数据中心资本开支约2.9万亿美元、外部融资缺口约1.5万亿[4]；评级机构已对近1,000亿美元数据中心相关债评级[5]；供应商"循环支持"结构进一步放大体系杠杆[7][9]。

对投资人而言更根本的问题：**对同一可交付的MW级电力与场址资源，应当投资到价值链的哪一层、以何种资产栈与合约结构、在哪个节点退出？**

### 1.2 研究问题

> **RQ1** 七种商业模式的投资强度、回报与风险敞口如何系统比较？
> **RQ2** 价值链延伸的增量风险调整股本回报（IRASR）在何处由正转负？
> **RQ3** 最优层级在多大程度上由资产栈、合约结构与GPU代际重新决定？

### 1.3 贡献声明（依评估意见二、四弱化首创性表述）

本文不声称发明CVaR、copula或增量回报指标；其贡献在于**将Role、Asset Stack、Contract、Project Finance、相关性风险模拟与Sponsor级资本配置系统整合进统一的AIDC价值链投资框架**，并以完整因子实验与三级验证支持其结论的可复现性。

---

## 2 AIDC生态系统、经济角色与资金流

### 2.1 底层资产的理论化：可交付容量（Deliverable MW @ COD）

对AIDC而言，MW本身不是完整商品。本文将底层稀缺资源定义为：

$$\text{AI Infrastructure Capacity} = f(\text{MW},\ \text{COD},\ \text{Availability},\ \text{Contractability},\ \text{Location})$$

Power、Critical IT、Compute各层本质上是对同一稀缺资源——**可按时交付的容量**——进行逐级价值转换：L1把燃料转换为可交付MW，L3把MW转换为可出租的Critical IT容量，L4把容量转换为算力小时。COD确定性具有独立价格（Time-to-Power Premium）——一兆瓦"2027Q4可交付"与"2030Q4可交付"是两种资产[5]。该定义构成贯穿全文的底层资产主线。

### 2.2 经济角色矩阵与三条资金闭环

*（沿用v2.0 §2框架：Role定义在交易而非公司名上。）*

| Role | 出售什么 | 向谁收费 | 主要资产 | 核心风险 |
|---|---|---|---|---|
| PowerCo | Firm MW @ COD | DC运营商 | 发电+燃料 | COD、可用性、气价(可转嫁) |
| DC Landlord | Critical IT MW | Tenant | 建筑+MEP | 建设、租户信用 |
| ComputeCo | GPU-hour | AI Lab | GPU+集群 | 利用率、残值、技术淘汰 |
| Managed Inference (L5a) | $/token托管推理 | 应用/企业 | 平台+运营 | 需求、毛利率 |
| Frontier Model (L5b) | Token/API/订阅 | 终端用户 | 模型IP+客户 | 变现能力 |

三条资金闭环：**Meta型**（广告现金流→自有基建→AI→广告效率，Captive模式，评价指标为增量企业FCF/CAPEX）；**Anthropic型**（多源采购算力+直锁Critical IT容量）；**CoreWeave型**（长期合同→融资能力→部署→交付→偿债，**客户合同本身是资本结构的一部分**[4][13]）。本文模型覆盖L0–L5a；L5b与Captive不属于基础设施投资人的回报函数，仅作价值归属证据（§5.5）。

---

## 3 模型与方法

### 3.1 分层、口径与单位纪律

七种商业模式（L0–L5a，表1）在统一100 MW参考项目上比较；Critical IT MW = Generation MW / PUE；单位价值指标双分母（$/Site-MW与$/IT-MW）；GPU层计价为$/IT-kW-hr并附$/GPU-hr换算。

**表1 七种商业模式**（同v2.0：dev/power/shell/critical_it/gpu_hosting/compute/L5a；L5b单列为价值归属证据；锚点见附录A）

### 3.2 资产层模型

月度频率：tolling结构（容量费+燃料/碳转嫁，真实利润变量为Tolling Margin）；租约结构（租金×递增率，到机架增量$4k/IT-kW按棕地实盘校准[14]）；GPU资产（RevPAGH=u_t·R_0·f_reset^c·(1+g)^k，48个月刷新事件，利用率24个月爬坡，债务期限≤刷新周期硬约束）；直线折旧简化公司税（其重要性边界已在§6.3量化）。

### 3.3 融资层模型

与资产层严格分离：S曲线逐月提款+IDC+承诺费；四种摊还（sculpted-to-DSCR为主）；现金扫仓；客户资本冲减股本；再融资模块；逐月DSCR/LLCR/期限匹配校验。

### 3.4 风险调整体系

**（1）确定性等价净现值（v3.0修正公式，依评估意见二§2.1）**。本文处理的是收益变量NPV的**左尾**，采用下尾期望短缺：

$$ES^-_{5\%}(NPV) = E[NPV \mid NPV \leq P5]$$

$$\boxed{CE\text{-}NPV = (1-\lambda)\cdot E(NPV) + \lambda \cdot ES^-_{5\%}(NPV)}$$

λ=0退化为风险中性期望，λ=1为完全尾部惩罚。正文取λ=0.5，**并报告λ∈{0, 0.5, 1}敏感性**（§5.4），以证明甜蜜点结论不依赖λ的人为选取。

**（1a）与WACC的职责分工（消除二次调整之疑）**：分层WACC负责市场要求的**系统性风险**补偿（资产按所处层级的市场beta与融资利差定价）；CE-NPV中的λ·ES⁻₅%惩罚负责sponsor对**项目特异性下行（左尾）**的额外厌恶。二者不构成重复调整：WACC回答"市场对同类资产的均衡回报要求"，λ·ES⁻₅%回答"该特定sponsor对这笔特定交易的尾部风险愿意放弃多少期望值"。λ=0时CE-NPV退化为E(NPV)，模型回到纯WACC口径；λ>0仅在WACC已定价的系统性风险之上，叠加一层未被分散化的特异风险惩罚。

**（2）IRASR——增量风险调整股本回报（本文核心决策指标）**：

$$IRASR_i = \frac{CE\text{-}NPV_{i+1} - CE\text{-}NPV_i}{PeakSponsorEquity_{i+1} - PeakSponsorEquity_i}$$

**经济含义：股东每新增投入1美元峰值风险资本，为价值链向下一层延伸所创造或毁灭的确定性等价价值。** 作为资本配置决策规则：IRASR>0——延伸创造风险调整价值；IRASR≈0——边际延伸，取决于战略协同；IRASR<0——延伸毁灭sponsor价值。本文所有IRASR基于未四舍五入的底层结果计算（表格展示值为四舍五入，二者可能存在尾差）。

**（3）相关性蒙特卡洛**。GPU四参数（租金率σ=0.25、残值σ=0.35、采购价σ=0.15、利用率σ=0.10）经高斯copula联合采样，相关矩阵ρ(租金,残值)=0.6、其余0.2–0.3。各表注明实际N；损失概率一律附**Wilson 95%置信区间**（如0/1500观察损失→95%CI 0–0.26%；800/800→95%CI 99.52–100%），不再表述为0%或100%。

**（4）融资审读指标**。Equity NPV@Ke、MIRR、TVPI/MOIC、Peak Equity、现金流符号翻转计数；Project NPV<0而Equity IRR>0时标记**Leverage-distorted IRR**；Min DSCR<covenant标记**Not financeable under covenant**。并定义**统一贴现率口径的融资价值归属分析**（financing-value attribution，§6.2）：在单一未杠杆贴现率下 NPV_proj = NPV_equity + NPV_debt 恒真，用于区分"价值创造"与"融资再分配"。

### 3.5 实现与复现

Python实现（约2,000行，开源）：七模块架构、双辖区参数包、分层WACC。复现命令见附录C。

---

## 4 校准与验证（三级体系）

### 4.1 Level A——参数锚定

**表2 Level A结果**

| 锚点 | 公开事实 | 模型输出 | 性质 |
|---|---|---|---|
| TeraWulf–Anthropic（**2026-07-06公告**[8]，首批容量2027年末交付） | 401 MW IT、20年、名义~$19B、≈$197/kW-月 | 名义$19.0B；首年收入$0.96B | 恒等式复核（租金参数由该交易反推） |
| Greenlight[8] | 932 MW、CA$4.6B、~60%债务；全包CA$90–120/MWh；固定回收CA$60–80/MWh | 杠杆62%；EBITDA CA$81/MWh（上缘）；全包CA$105/MWh | 区间锚定，偏市场有利侧 |

*日期勘误（P0-3）：v2.0误记为"2025-10公告"；经TeraWulf投资者关系页面与GlobeNewswire原始新闻稿核实为**2026年7月6日**，全文已统一。*

### 4.2 Level B——内部验证

六项全部通过（同v2.0表3）：Sources=Uses恒等（偏差0.00e+00）、债务滚动期末清零、杠杆61.3% vs LTC 60%（IDC解释）、GPU期限匹配、IRR/NPV解析解<1e-9、现金流符号≤1次转换。

### 4.3 Level C——外部基准合理性检验（依评估意见二§5更名）

*v3.0起不再称"样本外验证"。* 三项检验（DGX B300价格带$400–500K vs 模型$480K；DigitalOcean H100按需$4.41/GPU-hr折算≈$3.5/IT-kW-hr vs 模型3.0–3.3；REIT/JV杠杆5.5–6.0× vs 模型项目融资口径2.6×）性质为**输入假设与隐含值的市场合理性核对**。真正的**交易级样本外验证**（≥5笔未参与定参的交易，预测CAPEX/MW、rent、NOI、leverage、implied valuation并报告MAE/MAPE/偏差）列为v4.0工作（§7后续工作）。

---

## 5 结果

### 5.1 电力层参数一致性检验（P1-3，先于基准表呈现）

v2.0基准的Power-only（28% EqIRR）隐含组合了"最低CAPEX（二手9E）+最高质量合同（Meta级溢价tolling）"——现实中二者存在约束：二手设备对应更短剩余寿命、中等可用性与更高的融资利差，投资级长约通常要求新建高规格资产。v3.0将该层重构为三个一致性情景：

**表3 电力层参数一致性（100 MW，Alberta）**

| 情景 | 组合 | NPV $M | Project IRR | Equity IRR | 经济性质 |
|---|---|---:|---:|---:|---|
| **P1 市场一致基准** | 新建CCGT($3,500/kW)+投资级tolling($28/kW-月)+低利差(5.8%) | +94 | 10.6% | 13.6% | Greenlight型基础设施回报 |
| P2 桥接合约 | 二手GT($1,150/kW)+中期合约($12/kW-月)+高利差(8.5%)+杠杆50% | +88 | 16.1% | 18.4% | 商业燃机市场常态 |
| P3 套利组合 | 二手GT($1,150/kW)+溢价长约($18/kW-月) | +191 | 21.1% | 28.0% | 设备×合约市场套利（upside） |

**结论修正**：v2.0把P3当作普遍基准高估了电力层；**本文后续一律以P1作为市场一致基准**，P3的28%仅为套利情景。P1与P3之间约14个百分点的Equity IRR差值，恰是对"能否以二手设备获取投资级溢价长约"这一命题的量化——**它不是模型的缺陷，而是一个可检验的市场命题**：若该套利可持续存在，其本身即是设备市场与合约市场分割的套利收益；若不可持续，P1才是定价基准。

**CAPEX口径与IDC边界（P-方法学2核查）**：P1的$3,500/kW按**overnight成本**（EPC+业主费用，不含建设期利息与融资费用）输入，融资引擎单独计算并资本化IDC——P1下IDC约$7M（CAPEX的1.9%），故不存在IDC双计。若将Greenlight公开的CA$4.6B口径解读为**含融资成本的全包数字**，则overnight等价约$3,430/kW，P1 Equity IRR约上移0.2–0.3pp、NPV约+$5M；无论取何种口径，P1均停留在基础设施回报量级（13.6–14.4%），与P3套利组合28%之间约14pp的差距结论不变。为可复现，本模型统一约定：**CAPEX输入=overnight（含EPC与业主费用、不含IDC与融资费用）；IDC与融资费用由融资层在Uses/Sources中单独处理**（§3.3、附录A）。

### 5.2 基准情景：七模式统一比较（Alberta；括号Texas）

**表4 基准结果（电力层为P1口径；2026-08参数）**

| 模式 | CAPEX $M | 峰值股本 $M | Project IRR | Equity IRR | NPV $M | 观察损失率 [Wilson 95%CI] |
|---|---:|---:|---:|---:|---:|---|
| 开发退出† | 20 | 20 | — | — | +5 | 15% [12–18%] |
| Power-only（P1口径） | 353 | 130 | 10.6% | 13.6% | +94 (—) | 低 |
| Powered Shell | 469 | 230 | 12.5% | 14.4% | +85 (78) | 12% [8–16%] |
| AI-ready Critical IT | 773 | 287 | 20.1% | 26.0% | +676 (619) | 0/1500 [0–0.26%] |
| GPU托管（到机架） | 837 | 368 | 21.7% | 26.2% | +707 (633) | ~1% [0–2%] |
| 算力出租（现货） | 5,829 | 1,097 | -29.7% | — | -3,351 (-2,957) | 800/800 [99.5–100%] |
| Managed Inference (L5a) | 5,277 | — | -35.9% | — | -2,784 (-2,590) | ~100% |

†开发退出报MOIC 2.00×、年化XIRR 36%、27个月。电力层P1的MC未单独跑满（损失率由P3的0/2000与利差结构推断为低），正式版补齐并附CI。‡"峰值股本"列口径跨层不一致：L0–L3.5按Sponsor Equity（股本总额）报告，L4/L5按Peak Equity（累计股本流出峰值）报告——GPU层现金流前置致峰值高于股本总额（如L3 Sponsor $287M vs Peak $316.5M、L4短缺 $755M）。§5.4的IRASR一律采用Peak Equity口径并明示底层值，读者勿用本表列值相减复算IRASR。

辅助增量链（ΔNPV/ΔCAPEX，基于表内四舍五入值）：Dev→Power +0.79；Power(P1)→Shell −0.03（**边际**——市场一致电力基准下，壳体层几乎不创造增量价值）；Shell→Critical IT +1.94；Critical IT→Hosting +0.48；Hosting→GPU显著为负。与v2.0相比的重要变化：**电力层回到基础设施回报量级（13.6%）后，"Power→Shell无增量"的判断更加突出**，价值创造的重心明确落在"绿电→AI-ready"的转换环节。

### 5.3 核心实验：完整2×2×2因子设计（P1-2）

**表5 L4算力出租全因子矩阵（Project NPV $M / IRR / 峰值股本$M）**

| 资产栈\合约 | Merchant×新卡 | Merchant×二手 | Contracted×新卡 | Contracted×二手 |
|---|---|---|---|---|
| **Greenfield** | -3,351 / -29.7% / 1,097 | -1,674 / -20.0% / 1,158 | -2,214 / -16.6% / 755 | -987 / -6.8% / 732 |
| **Brownfield** | -3,100 / -31.3% / 776 | -1,429 / -21.1% / 831 | -1,973 / -16.9% / 550 | **-746 / -5.3% / 527** |

*二手GPU：$12k/IT-kW、残值0.30；现货租金$1.9、长约$2.0/IT-kW-hr；长约：$3.2（新卡）、衰减-8%、利用率95%；其余同基准。*

**主效应与交互（NPV $M，全因子均值分解）**：

| 效应 | 量级 | 解读 |
|---|---:|---|
| **GPU代际（二手−新卡）** | **+1,450** | 最大杠杆：GPU采购价差主导 |
| **合约结构（长约−现货）** | **+909** | 第二：锁定衰减路径的价值 |
| 资产栈（棕地−绿地） | +245 | 第三：电力/建筑沉没的贡献有限 |
| 合约×代际交互 | **−446（次可加）** | 二手卡的租金带较窄，长约溢价对其增量更小 |
| 合约×资产栈交互 | −6（≈0） | 两维度近似正交 |

**因子解读边界（P-方法学1）**：本实验中的"Contracted"与"Used GPU"并非单一因果处理变量，而是各改变一组联动参数的**经济情景包**——"Contracted"同时改变初始租金、价格衰减与利用率；"Used GPU"同时改变采购价、残值与租金水平。因此上表主效应应严格读作**合约经济情景包相对现货经济情景包的改善（约+$909M）**、**GPU代际经济情景包效应（约+$1.45B）**，而非"仅因签订合同"或"仅因改用二手卡"的因果归因。此界定不影响投资决策价值——对sponsor而言可投标的本身就是参数联动的整体情景包——但可避免把scenario decomposition误读为causal attribution。

**两项结论修正（相对v2.0）**：(1) v2.0摘要"合约>代际>资产栈"基于不完整格子；完整因子分解的正确排序为**GPU代际＞合约结构≫资产栈**（P0-4勘误）；(2) 新发现**合约×代际负交互**（经济上较大，未做统计显著性检验）——长约与二手卡的价值来源部分重叠（都是抗衰减），不可叠加受益。**八格在本文2026-08参数与预设经济情景包范围内全部NPV为负**：即使最优格（棕地×长约×二手，-5.3% IRR）仍未跨越盈亏平衡。需强调该结论限定于当前可观察/设定的参数区间——模型并未数学证明所有可能的GPU价格、租金、利用率、残值与客户支持组合均不成立，更低采购价、更高take-or-pay租金、客户预付款或更强厂商残值担保等理论上仍可能翻转结果；本文证明的仅是八格在本文参数区间内均未翻转，该结论已足够支撑决策判断——租金模式自持GPU的转正需token模式收入（L5a口径，§5.5）或模型层角色（L5b）。

### 5.4 λ敏感性与IRASR（P1-4、P0-2）

**表6 CE-NPV对风险厌恶参数λ的敏感性（$/M）**

| 情景 | λ=0（风险中性）E(NPV) | λ=0.5 | λ=1（完全尾部）ES⁻₅% |
|---|---:|---:|---:|
| L3 Critical IT（独立MC, N=1500） | +719 | **+517** | +315 |
| L4 短缺修正（相关MC, N=800） | -1,406 | **-2,038** | -2,671 |
| L4 基准现货（相关MC, N=800） | -3,363 | **-3,818** | -4,273 |

**L3>L4的排序在全部λ取值下不变**——甜蜜点结论不是λ=0.5人为选取的结果（λ从0到1仅使L3的CE-NPV从+719收窄至+315，始终为正；L4在全部λ下为负）。

**IRASR（基于未四舍五入底层结果）**：

$$IRASR_{L3\to L4(短缺)} = \frac{-2,555.9}{+438.8} = \mathbf{-5.83}$$

分母的两个底层值（**Peak Equity口径**）：L3峰值股本$316.5M、L4短缺情景峰值股本$755.3M，Δ=+438.8M（未四舍五入值$316.511M与$755.294M）。若读者用表4"峰值股本"列值相减（755−287=468）会得到-5.46——差异根源是**表4该列口径跨层不一致**（DC层按Sponsor Equity报告287、GPU层按Peak Equity报告），而IRASR统一采用Peak Equity口径（累计股本流出峰值，即风险资本占用的真实峰值）。即股东每多投1美元峰值股本于GPU层，毁灭约5.8美元确定性等价价值。（注：若用表内四舍五入值手工复算会得到-5.46；差异源于表格展示精度，正文一律采用底层精确值。）

### 5.5 L5拆分、价值归属与短缺情景

L5a（Managed Inference）：基准NPV -$2,784M、修正情景（$7.0/IT-kW-hr、衰减-10%）-$1,222M——**目前的$/IT-kW-hr输入是token经济学的收入等效折算，而非严格的token单位经济模型**；完整的GPU数量→tokens/GPU-hr→有效tokens→$/M tokens→净收入（扣除模型许可分成、serving开销、存储/网络/编排、获客与支持、模型刷新）转换引擎列为v4.0工作（评估意见二§7）。L5b（Frontier Model Owner）：SemiAnalysis估计GB300集群上模型层可产生>$100B/GW-yr API收入vs ~$12B/GW-yr租金成本[6]——**8:1价值差归属模型层**，与L4/L5a负NPV互洽：GPU层的钱存在，但由Role决定归属。

**结论边界（P-表述强化1）**：本文对L4/L5a的负结论严格限定于"基础设施投资人自持GPU做Compute Rental"这一Role与收入函数，**不构成"AI Factory不赚钱"的判断**——Frontier Model（L5b）与Captive AI（Meta型）的经济性由模型层/最终业务层收入决定，不属于本文基础设施回报函数，其存在恰恰意味着GPU层负结论不可外推至模型公司与hyperscaler自建决策（§6.5(7)）。

短缺情景完整指标组（修v2.0表6数据，结论不变）：NPV -$1,412M、Project IRR -2.5%、Equity IRR 58.6%[Leverage-distorted]、Equity NPV@Ke +$1,492M、MIRR 25.9%、TVPI 6.38×、Min DSCR 1.48、**Peak Equity $755M**；Vendor Backstop情景Min DSCR 0.90×→**Not financeable under covenant**。

---

## 6 讨论

### 6.1 与文献的分歧（同v2.0三处：资本流向≠回报来源；衰减假设的时变性；技术变量二阶效应）

### 6.2 融资价值归属 ≠ 价值创造（依评估意见三重构贴现率口径）

短缺情景呈现Project NPV(-$1.4B，按WACC)与Equity NPV@Ke(+$1.5B)并存。判断其属"价值创造"还是"价值再分配"，必须先固定贴现率口径（P-方法学3）：**只有当股权与债务现金流采用同一贴现率时，NPV才满足加总恒等**。若Project CF按WACC、Equity CF按Ke、Debt CF按Kd分别贴现，三个NPV一般不能直接相加——本文当前报告的-1.4B与+1.5B即分属WACC与Ke两种口径，不能直接相减推出"Debt NPV=-2.9B"。

本文因此将本节定性为**融资价值归属分析**（financing-value attribution / cash-flow redistribution analysis），并声明其贴现率约定：归属度量应在**同一未杠杆贴现率**下进行，此时

$$\underbrace{NPV_{proj}}_{r=r_u} = \underbrace{NPV_{equity}}_{r=r_u} + \underbrace{NPV_{debt}}_{r=r_u}$$

因现金流可加性而恒真；若在该统一口径下Debt NPV为负，才表明**融资合同把项目总价值的一部分从债务持有方再分配给了股权持有方**。反之，若仅把债务现金流按15%的equity hurdle贴现得出负值，则该数值不是"债权人损失"——真实贷款人的要求收益率可能仅9.5%，其自身口径的经济损益须按Kd另行评估。两个对象必须区分：统一口径下的归属度量（回答"价值在谁之间转移"），与各stakeholder按自身要求收益率评估的经济损益（回答"各方各赚多少"）——前者用于本节的归属判断，后者报告于§5融资审读指标，二者不得混用。无论何种口径，任何商业模式都必须同时检查Project、Equity与Debt三个NPV；仅报告Equity IRR的模型（市场上大量存在）会系统性误导。这对GPU/private-credit/vendor-backstop模式尤为重要——真实的CoreWeave式定价（9.25%+GPU抵押+厂商容量回购）正是市场对债务方承担上述价值转移风险的补偿[4][13]。统一口径归属度量的系统双轨输出列为v4.0工作（§7）。

### 6.3 融资能力作为核心解释变量（依评估意见二§12提升）

Financeability不是五维矩阵的辅助维度，而是**资产价值本身的构成部分**：优质合约同时改善收入确定性、尾部风险、债务承载、股本需求、资本成本与再融资机会——Contract→现金流可见性→Bankability→杠杆→Sponsor资本效率的传导链，是AIDC与一般科技投资最大的区别之一，也是本文观察到的合约主效应（+$909M）与短缺修正下DSCR从违约修复至1.48×的深层机制。

### 6.4 税务与备付金简化的量化敏感性（同v2.0 §6.3：直线折旧保守偏差2–5%、DSRA约-90bp、L4税务+$291M仍不翻转）

### 6.5 局限性

（1）筛选级精度（重要性已量化于§6.4）；（2）参数2026-08快照；（3）USD单一币种；（4）相关矩阵为经验设定；（5）Level C为合理性检验而非样本外预测验证（v4.0目标：≥5笔交易的Prediction-vs-Actual，报告MAE/MAPE/偏差）；（6）L5a为收入等效折算而非token单位经济模型；（7）L5b/Captive不建模（其存在意味着GPU层负结论不可外推至模型公司与hyperscaler自建决策）；（8）电力层P1的MC样本量未与其他层对齐。

---

## 7 结论

**RQ1**：市场一致口径下（电力层P1），七模式排序为Critical IT租赁与GPU托管（CE-NPV +$517M、观察损失0/1500）＞Power-only基础设施回报（13.6% EqIRR）≈Shell（边际）；租金模式自持GPU与L5a在基准下深度为负。

**RQ2**：IRASR在L3→GPU层为**-5.83**（短缺情景、未四舍五入值）；辅助增量链显示Power(P1)→Shell已近零（-0.03）——价值创造重心在"电力→AI-ready"转换环节，基准停留点L3–L3.5。

**RQ3**：完整2×2×2因子实验给出主效应排序**GPU代际(+$1.45B)＞合约结构(+$0.91B)≫资产栈(+$0.25B)**（经济情景包口径），且合约×代际存在经济上较大的负交互（-$0.45B，次可加）；八格在本文参数范围内全负，三维全部最优仍不翻转租金模式——GPU层正经济性属于具备模型层角色或token变现能力的参与者。

三个跨周期判断保持为全文主线：**Role决定现金流归属；Asset Stack决定经济性起点；Contract与Capital Structure决定sponsor承担的风险与资本效率。** 最优层级 = f(Role, Asset Stack, Contract, Capital Structure, 市场状态)。

**实践者的决策逻辑（依评估意见三§8提炼）**：对能源/基础设施开发商，优先控制可交付MW，进而把MW转换为长期可融资的Critical IT Capacity（L3）；**只有在拥有特别低的GPU采购成本、能够锁定长期价格/利用率、或自身掌握模型与Token变现能力时，才向Compute层投入大量资本**——纵向一体化到GPU并非默认最优。对CoreWeave类Compute Operator，自持GPU可以合理，因其同时具备客户合同、利用率、融资、厂商支持与规模采购能力，是与普通Power/DC Sponsor完全不同的Role。对OpenAI/Anthropic/Meta，模型层或最终业务层价值使基础设施层单独看IRR普通、但企业整体投资依然合理。三者的并存恰是"不能脱离Role讨论哪一层赚钱"的印证。

后续工作（v4.0，按优先级）：**(1) 交易级样本外验证集**——≥5笔未参与定参的交易/层，报告MAE/MAPE/偏差（最重要）；**(2) 融资价值归属的贴现率数学彻底理顺**——统一口径归属度量与各stakeholder自身口径损益的双轨系统输出；**(3) L5a的GPU→Token单位经济转换引擎**（GPU数量→tokens/GPU-hr→有效tokens→$/M tokens→净收入，扣除模型许可分成、serving开销、存储/网络/编排、获客与支持、模型刷新）。其余：参数相关性事后校准、lease-tail/balloon压力测试、CME租金期货对冲、MACRS/CCA与DSRA银行级实现。

---

## 参考文献

（同v2.0 [1]–[15]，其中[8]更正为：TeraWulf–Anthropic 401 MW Critical IT租约，**2026-07-06公告**（TeraWulf投资者关系/GlobeNewswire原始新闻稿），首批容量2027年末交付；Greenlight Electricity Centre口径不变。）

## 附录A 参数全量溯源表

（同v2.0附录A；新增P1情景参数：新建CCGT $3,500/kW取Greenlight CA$4.6B/932MW×0.714折算[8]，置信0.85。注明$3,500/kW为**overnight口径**（EPC+业主费用，不含IDC与融资费用）；融资层单独计IDC，P1下IDC≈$7M（CAPEX的1.9%）。若将Greenlight口径解读为含融资成本的全包数字，overnight等价约$3,430/kW，P1 EqIRR约+0.2–0.3pp、NPV约+$5M，结论不变。）

## 附录B 高频市场情报与置信度评分（摘要）

（同v2.0附录B。）

## 附录C 复现命令

```bash
python -m aidc_optimizer --config configs/alberta.yaml --mc 200 --tornado --out results/alberta
# 2×2×2全因子（§5.3）：组合 power.capex_per_kw∈{1150,150} dc.ready_capex_per_kw∈{8000,5500} ×
#   gpu.rate_decay∈{-0.22,-0.08} gpu.utilization∈{0.75,0.95} × gpu.capex_per_kw_it∈{32000,12000}
# 电力一致性（§5.1）：P1 = power.capex_per_kw=3500 power.capacity_payment_kw_mo=28 finance.L1_Power.rate=0.058
#   P2 = capacity 12 availability 0.88 rate 0.085 leverage 0.50；P3 = 基准
# λ敏感性/IRASR/Wilson CI：相关MC脚本（结果目录sensitivity_v3.py）
python tests/test_validation.py
```

---

**模型与数据可得性**：aidc_optimizer v1.1+（含全因子、电力一致性、λ敏感性与Wilson CI脚本）。

**利益声明**：作者所属机构从事北美BTM电力与数据中心开发业务，模型参数含机构自有实盘造价数据；P3套利情景与机构业务方向相关，已在§5.1显式分离于市场一致基准P1。

**AI辅助披露**：模型实现、数据分析与初稿写作由AI辅助完成，全部数值结果可由随附代码复现；v3.0依外部评估意见二修订，P0项（公式、算术、日期、排序）已逐项核对；v3.1依评估意见三修订，聚焦口径与归属（情景包因子界定、CE-NPV与WACC职责分工、融资价值归属贴现率口径、L5a结论边界）；v3.2依评估意见四修订，聚焦数值透明与表述限定（IRASR分母底层值披露、Power CAPEX/IDC口径拆分、"显著"改"经济上较大"、八格结论限定、删除"首次"）。
