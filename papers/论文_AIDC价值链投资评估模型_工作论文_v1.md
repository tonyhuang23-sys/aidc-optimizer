# 面向AI基础设施的价值链投资评估模型：分层资产-融资双引擎建模、双锚点校准与风险调整决策框架

## A Value-Chain Investment Evaluation Model for AI Infrastructure: Two-Tier Asset-Financing Engine, Dual-Anchor Calibration, and a Risk-Adjusted Decision Framework

**作者**: WNT Energy 技术研究组
**日期**: 2026年8月
**状态**: 工作论文（Working Paper）

---

## 摘要

人工智能数据中心（AIDC）投资在实践与研究中常被简化为单一"数据中心IRR"问题，掩盖了从电力资产到算力工厂这条价值链上各商业模式的本质差异。本文提出并实现了一个**价值链投资评估模型**：以统一的100 MW参考项目为测试平台，将AIDC投资解构为七种可比较的商业模式（开发退出、Power-only tolling、Powered Shell、AI-ready Critical IT、GPU托管、算力出租、AI工厂）；模型采用**资产层与融资层分离的双引擎架构**，以月度频率模拟建设期资本提取、利息资本化、sculpted摊还、现金扫仓、客户资本与再融资，并输出Project IRR、Equity IRR、NPV/峰值股本、DSCR等统一指标；在风险维度引入蒙特卡洛模拟与五维评价矩阵（投资强度、回报、风险、敞口归属、融资能力）。模型以Greenlight（932 MW联合循环、CA$4.6B、60%债务）与TeraWulf–Anthropic（401 MW Critical IT、20年租约、名义约$19B）两个公开交易为锚点校准，校准偏差均在可接受区间。基准测算显示：在现货市场假设下，价值链中段的**Critical IT租赁与GPU托管层构成风险调整回报的"甜蜜点"**（NPV/MW最高且损失概率≤1%），而自持GPU的算力出租与AI工厂层在全栈新建口径下NPV显著为负；引入2026年8月市场短缺证据修正参数后，GPU层经济性大幅改善但仍未跨越盈亏平衡，其转正需同时满足多年期合约锁定衰减、棕地免建电力设施与厂商残值支持等条件中的至少两项。本文的贡献在于把分散于产业报告、信用研究与学术预印本中的方法论整合为一个可复现、可校准、可情景化的开源评估框架，并用双锚点验证了其数量级可信度。

**关键词**: AI基础设施；数据中心投资；价值链；项目融资；蒙特卡洛模拟；风险调整回报；蒙特卡洛DSCR；Critical IT Capacity；GPU经济学

---

## Abstract

AIDC investment is often reduced to a single "data center IRR", obscuring fundamental differences across business modes along the value chain from power assets to AI factories. This paper presents and implements a **value-chain investment evaluation model**: seven comparable business modes are evaluated on a unified 100 MW reference project, using a **two-tier asset-financing architecture** with monthly-resolution simulation of construction draws, IDC, sculpted amortization, cash sweep, customer capital and refinancing. The model is calibrated against two public transactions (Greenlight 932 MW / CA$4.6B / 60% debt; TeraWulf–Anthropic 401 MW / ~$19B / 20-year lease), with acceptable deviations. Baseline results show that **Critical IT leasing and GPU hosting constitute the risk-adjusted "sweet spot"** of the value chain, while full-stack greenfield GPU ownership is deeply NPV-negative under spot-market assumptions; corrections informed by the 2026 GPU shortage materially improve—but do not flip—GPU-layer economics. The contribution is a reproducible, calibrated, scenario-capable open framework integrating methodologies scattered across industry reports, credit research and academic preprints.

**Keywords**: AI infrastructure; data center investment; value chain; project finance; Monte Carlo; risk-adjusted return; Critical IT Capacity; GPU economics

---

## 1 引言

### 1.1 研究背景与问题

自2024年起，AI基础设施进入史无前例的资本扩张期。McKinsey估计到2030年全球数据中心相关资本需求约6.7万亿美元，其中AI相关约5.2万亿[1]；Morgan Stanley测算2025–2028年仅数据中心（不含电力设施）资本开支即达2.9万亿美元，其中约1.4万亿可由hyperscaler内部现金流承担，剩余约1.5万亿美元形成外部融资缺口[4]。与此同时，评级机构已对近1,000亿美元数据中心相关债进行评级[5]，NVIDIA等供应商通过担保、股权与容量回购形成的"循环支持"资本结构进一步放大了体系杠杆[7][9]。

在资本快速堆积的同时，一个对投资人而言更根本的问题悬而未决：**对于同一个可交付的MW级电力与场址资源，投资人究竟应当投资到价值链的哪一层、以何种结构融资、在哪个节点退出？** 现有研究分别回答了产业链角色（McKinsey[1]）、跨层技术指标传导（He[2]）、AI单位经济性（Curcio[3]）、资本供给（Morgan Stanley[4]）与债权人风险（KBRA[5]）等子问题，但没有一个框架能在**统一的物理口径、融资结构与风险度量**下对多种商业模式进行可比较的量化评估——这构成本文的研究缺口。

### 1.2 研究问题与贡献

本文的核心研究问题是：

> **RQ1** 同一100 MW电力资源在七种商业模式下的投资强度、回报与风险敞口如何系统比较？
> **RQ2** 价值链向下游延伸的增量资本效率（ΔNPV/ΔCAPEX）在何处由正转负？
> **RQ3** 市场条件（如2026年GPU短缺）如何改变上述结论的稳健性？

本文贡献有四：(1) 提出资产层与融资层严格分离的双引擎月度模型；(2) 以两个公开交易实现双锚点校准并报告偏差；(3) 建立增量收益分析与五维评价矩阵的决策框架；(4) 以2026年8月多源情报（含X平台87条结构化证据）对模型参数进行修正并检验结论稳健性。全部代码、参数包与校准测试开源可复现。

### 1.3 论文结构

第2节综述文献并定位理论框架；第3节给出模型设计；第4节说明实现；第5节报告校准；第6节呈现基准与情景结果；第7节讨论与文献的分歧及局限性；第8节结论。

---

## 2 文献综述与理论框架

### 2.1 五条割裂的研究脉络

现有AIDC研究可归为五个方向，各回答价值链问题的一段：

**（1）产业角色与资本流**。McKinsey将参与者拆为Builders/Energizers/Technology Developers/Operators/AI Architects五类，指出GPU与计算硬件约占AI基建直接资本开支的60%——资本强度最高、折旧最快的一层[1]。其Stage-gate投资建议（Land→Power Secured→Permitted→RTB→Tenant Signed→COD逐段重估）构成本文"开发退出"模式的理论基础。

**（2）跨层指标传导**。He提出6层×3域（物理设施/计算工作负载/经济可靠性）的统一指标架构与Metric Propagation Graph，形式化了"电价→设施成本→计算成本→$/GPU小时→NPV"的跨层传导[2]。本文吸收其单位纪律（Generation MW / Critical IT MW / GPU MW严格区分，PUE为换算系数），但指出其框架缺少合同与融资结构。

**（3）AI单位经济性**。Curcio借鉴能源行业LCOE提出LCOAI——生命周期CAPEX+OPEX除以有效AI产出，并论证API与自部署存在规模盈亏平衡点[3]。本文将此思想推广为全链单位换算链：$/MWh→$/kW-月→$/GPU小时→$/token，并指静态价格假设在快速衰减市场中的系统性偏差。

**（4）资本结构与循环支持**。Morgan Stanley给出五类资本来源量化（内部现金流$1.4tr、公司债~$200bn、ABS/CMBS~$150bn、Private Credit/ABF~$800bn、其他~$350bn），核心洞见是**客户合同本身可以金融化**——hyperscaler租约经资产支持融资（ABF）转化为债务承载能力[4]。本文的L4层利率参数即以其披露的CoreWeave $2bn高收益债9.25%定价为锚[4]。

**（5）信用风险与风险归属**。KBRA的项目融资九维风险框架（建设/技术/运维/资源/对手方/竞争地位/交易结构/财务/再融资）验证了本文风险矩阵的完备性；其"电力可获得性已从运营变量升级为信用变量"（即MW+COD框架）与"再融资风险不能被初期DSCR掩盖"两点分别对应本文的COD风险定价与期限匹配约束[5]。

**（6）循环支持的系统性风险**。内部研究[13]系统梳理了NVIDIA–OpenAI潜在$6,300亿总敞口（$250B担保+$350B芯片租赁+~$30B股权）、NVIDIA对CoreWeave的容量回购安排（至2032年）及Google以AA+信用为neocloud租约担保的变体，并给出"上升期增长加速器→拐点处风险放大器"的历史镜鉴。本文将其转化为模型中可测试的vendor backstop情景（担保增信→杠杆上限提高、利率下降）。

### 2.2 理论框架：Role、Risk与Exposure的三重分离

综合上述文献，本文的理论出发点是三个分离：

**Role与公司分离**——同一主体（如Meta）在单一交易中可同时承担最终需求方、基础设施所有者与算力购买者；经济分析必须定义在交易而非公司名上[1]。

**Risk与Exposure分离**——天然气价格上涨是风险（Risk），但在燃料转嫁（pass-through）合同下PowerCo的经济敞口（Exposure）≈0；优秀项目结构的本质是把每种风险配置给最有能力承担的主体。KBRA的租约结构分析（Triple/Double Net）为此提供信用侧佐证[5]。

**资产久期与技术久期分离**——电力设施20–30年、数据中心15–25年、GPU 3–5年、AI服务可预测期1–3年；债务期限不得超过资产经济寿命（Debt Tenor ≤ Economic Life），否则把技术残值风险推迟为再融资风险[5]。

在这三个分离之上，本文将AIDC投资决策形式化为：

$$\max \frac{\text{Risk-Adjusted NPV}}{\text{Peak Sponsor Equity}} \quad \text{s.t.} \quad DSCR_t \geq c,\ \ T_{debt} \leq T_{asset},\ \ L_t \geq L_{min}$$

---

## 3 模型设计

### 3.1 价值链分层与统一物理口径

模型将完整AIDC项目解构为L0–L5六层，每层独立核算（即使同属一个投资人亦模拟为独立SPV、按市场化内部价格结算），共构成七种可比较的商业模式（表1）。

**表1 七种商业模式与校准锚点**

| 模式 | 层级 | 出售产品 | 计价单位 | 校准锚点 |
|---|---|---|---|---|
| 开发退出（dev） | L0 | Power-secured场址 | $/kW转让价 | 开发MOIC/Dev IRR |
| Power-only（power） | L1 | Firm/Deliverable MW | tolling容量费$/kW-月 | Greenlight–Meta[8] |
| Powered Shell（shell） | L2 | 已通电壳体 | $/kW-月 | — |
| AI-ready Critical IT（critical_it） | L3 | Critical IT Capacity | $/kW-月 | TeraWulf–Anthropic[8] |
| GPU托管（gpu_hosting） | L3.5 | 机架+电力+冷却+运维 | $/kW-月（含电费） | CentHill实盘[14] |
| 算力出租（compute） | L4 | GPU小时 | $/GPU-hr | 市场价格指数[6][12] |
| AI工厂（ai_factory） | L5 | Token/推理 | $/M token | SemiAnalysis Tokenomics[6] |

物理口径统一为：Critical IT MW = Generation MW / PUE。所有收入、利润、资本与价值指标最终折算到$/MW口径，使七模式可比。PUE不仅是能效指标，更是**价值链转换系数**——从L1到L3的每一层都必须显式声明其MW口径[2]。

### 3.2 资产层模型

资产层在月度频率上生成每层SPV的收入、运营成本与资本开支序列：

**（1）tolling结构（L1）**。收入=容量费×MW+燃料/变动成本转嫁。在燃料与碳成本pass-through条款下，风险存在而经济敞口≈0（§2.2），PowerCo的真实利润变量是Tolling Margin（$/kW-月），而非全包电价的绝对水平[8]。

**（2）租约结构（L2/L3/L3.5）**。收入=租金×(1+递增率)^t；到机架增量成本依据棕地改造实盘数据校准（DLC冷却$1.7k+网络$1.5k+存储$0.5k+软件$0.5k≈$4k/kW-IT）[14]。

**（3）GPU资产（L4/L5）**。收入遵循类酒店RevPAR逻辑：

$$RevPAGH = Utilization_t \times Rate_t,\quad Rate_t = Rate_0 \cdot f_{reset}^{c} \cdot (1+g)^{k}$$

其中$g$为租金衰减率（基准-22%/年）、$f_{reset}$为刷新时新代单位算力租金重置系数、$c$为所处刷新周期序号。资本开支包含48个月刷新事件：旧GPU按残值率出售、新GPU按折价系数采购。利用率含24个月爬坡。资产经济寿命（48个月）与债务期限实施硬约束。

**（4）税收**。直线折旧+亏损结转的简化公司税引擎；残值按资本利得计税。

### 3.3 融资层模型

融资层与资产层严格分离[4][5]，包含：

- **建设期**：按S曲线资本开支逐月pro-rata提款；利息资本化（IDC）计入债务余额；承诺费按未提取额计收；
- **运营期**：四种摊还（直线/年金/sculpted-to-DSCR/bullet），sculpted以CFADS/目标DSCR雕刻本金并保底在期限內还清；现金扫仓在DSCR缓冲之上按比例提前还款；
- **资本来源**：Sponsor Equity+项目债务+客户资本（租户定金/预付直接冲减股本需求）[4]；
- **再融资模块**：COD后按退出杠杆×EBITDA重置债务、释放股本（Capital Recycling）；
- **约束校验**：逐月DSCR、Min/Avg DSCR、LLCR、期限匹配（Debt Tenor ≤ 资产经济寿命，GPU层48mo=刷新周期）。

输出统一指标：Unlevered Project IRR、Levered Equity IRR、MOIC、NPV/峰值股本（跨模式比较的首要指标[4]）、Peak Sponsor Equity/MW。

### 3.4 三个独立IRR与增量收益分析

遵循开发-基建-技术三段资本逻辑[1]，模型输出三个独立IRR：Development IRR（Land→Exit）、Infrastructure IRR（Power+DC）、Compute IRR（GPU）。更关键的是**增量收益分析**：对价值链相邻两层计算

$$\Delta Return = \frac{NPV_{i+1}-NPV_i}{CAPEX_{i+1}-CAPEX_i}$$

ΔReturn>0才构成向下延伸的必要条件——投资人的真实决策不是"哪层收入最高"，而是"再投的每一美元创造多少NPV"。

### 3.5 风险引擎与五维评价矩阵

**蒙特卡洛**：按各层关键参数的对数正态/正态扰动（σ源自市场波动率，如租金率σ=0.25、气价σ=0.30），每次模拟重跑资产+融资全管线，输出NPV的P10/P50/P90、P(NPV<0)、P(IRR<hurdle)。

**静态风险敞口矩阵**：14类风险×7层的高/中/低/极高分级，每项风险标注Risk Owner与pass-through机制；层级综合敞口分（0–3）作为决策气泡图的尺寸变量。

**五维评价矩阵**：投资强度（CAPEX/股本/峰值股本/资本久期）、回报、风险（MC损失概率）、敞口归属、融资能力（杠杆、covenant缓冲、期限匹配）[1][4][5]。

---

## 4 实现

模型以Python实现（约2,000行，开源），架构为七个模块：`core`（月度财务数学：IRR/NPV/MOIC/年金/税收）、`models`（七模式资产层构建器）、`financing`（融资引擎）、`risk`（MC与龙卷风敏感性）、`evaluate`（增量分析与五维矩阵）、`report`（图表与报告）、CLI。运行示例：

```bash
python -m aidc_optimizer --config configs/alberta.yaml --mc 200 --tornado --out results/alberta
python -m aidc_optimizer --config configs/alberta.yaml --case compute \
    --set gpu.rate_decay=-0.05 gpu.residual_pct_at_refresh=0.30
```

**双辖区参数包**（YAML）：Alberta（AECO气价$1.6/GJ、TIER碳价CA$130/t及转嫁、9E级二手燃机$1,150/kW含业主费用、Bill 30审批时间线）与Texas（Henry Hub $2.85/GJ、无碳价、ERCOT口径），差异参数均有出处标注[10][11]。分层WACC严格区分（Power 8%→AI Factory 19%），禁止跨层使用统一贴现率。

---

## 5 校准与验证

### 5.1 双锚点校准

**表2 校准结果（测试：tests/test_validation.py，全部通过）**

| 锚点 | 公开事实 | 模型输出 | 偏差 | 判定 |
|---|---|---|---|---|
| TeraWulf–Anthropic[8] | 401 MW IT、20年、名义~$19B、≈$197/kW-月 | 名义合同$19.0B；首年收入$0.96B（锚$947M/yr） | <1% | ✓ |
| Greenlight[8] | 932 MW、CA$4.6B、~60%债务；Meta全包CA$90–120/MWh；固定成本回收CA$60–80/MWh | 杠杆62%；EBITDA CA$81/MWh；租户全包CA$105/MWh | 区间内/上缘 | ✓ |
| 期限匹配（KBRA[5]） | GPU债务期限≤刷新周期 | L4债务48mo=刷新48mo | 一致 | ✓ |
| 财务数学单元测试 | 已知现金流IRR/NPV | 解析解 | <1e-9 | ✓ |

Greenlight锚的EBITDA落在基准区间上缘（CA$81 vs 60–80），提示容量费参数（$28/kW-月）取值偏市场有利侧，敏感性已由MC覆盖。

### 5.2 数据可信度分级

模型参数按三源核实报告的置信度分级选取[15]：H100/H200采购价（0.85–0.88强支持）、B300~$53K（0.70）、GB300 NVL72 $3.5M/柜（0.65）、MI355X（0.55，仅情景）；被剔除数据（SiliconData $7.20/hr ticker、MI450估算）在配置注释中留痕。二手H100取经纪报价带$15K/卡并注明"非清算价"。

---

## 6 结果

### 6.1 基准情景：七模式统一比较（Alberta，100 MW/PUE 1.25/80 MW IT）

**表3 基准结果（2026-08参数；括号内为Texas）**

| 模式 | CAPEX $M | 股本 $M | Project IRR | Equity IRR | NPV $M | MC P(NPV<0) |
|---|---:|---:|---:|---:|---:|---:|
| 开发退出 | 20 | 20 | 55.1%* | — | +5 | 15% |
| Power-only tolling | 133 | 45 | 21.1% | 28.0% | +186 (230) | 0% |
| Powered Shell | 469 | 230 | 12.5% | 14.4% | +85 (78) | 12% |
| AI-ready Critical IT | 773 | 287 | 20.1% | 26.0% | +676 (619) | 0% |
| GPU托管（到机架） | 837 | 368 | 21.7% | 26.2% | +707 (633) | 1% |
| 算力出租（自持GPU） | 5,829 | 5,475 | -29.7% | 1.8% | -3,351 (-2,957) | 100% |
| AI工厂 | 5,277 | 5,085 | -35.9% | 21.5% | -2,784 (-2,590) | 100% |

*开发IRR为时点IRR，非年化可比口径。DSCR：Power/Shell/CriticalIT均≥1.30x。

**增量收益分析**（ΔNPV/ΔCAPEX）：开发退出→Power **+1.65**（值得延伸）→Shell **-0.31**（增值不足）→Critical IT **+2.04**（值得延伸）→GPU托管 **+0.08**（边际）→自持GPU **-0.86**（不延伸）。

三个独立IRR：Development 55%、Infrastructure（Critical IT杠杆口径）26%、Compute 1.8%——三者数量级分化本身就是"分层决策"的实证。

**基准结论**：价值链中段（L3 Critical IT与L3.5到机架托管）构成风险调整回报的甜蜜点；Power-only在二手燃机+市场tolling费率假设下资本效率极高（其成立前提正是WNT式"低成本中国设备+北美市场费率"的套利）；自持GPU在全栈新建+现货市场假设下不成立。

### 6.2 短缺修正情景（X情报，2026-08）

以87条X平台结构化证据[15]修正参数（衰减-22%→-5%、刷新残值0.15→0.30、租金$3.3/kW-hr、利用率85%），依据为：黄仁勋亲证H100一年合约$1.70→$2.35[6]、Silicon Data残值指数显示H100/B200在2026年升值、供给端13家供应商零B200可租等。

**表4 L4算力出租：基准vs短缺修正**

| 情景 | NPV $M | Project IRR | Equity IRR | Min DSCR | P(NPV<0) |
|---|---:|---:|---:|---:|---:|
| 基准 | -3,351 | -29.7% | 1.8% | -0.39（违约） | 100% |
| 短缺修正 | -1,412 | -2.5% | 58.6% | 1.48 | 98% |
| +Vendor Backstop（杠杆55%/利率8.5%） | -1,412 | -2.5% | 61.1% | 0.90 | 98% |

短缺修正使GPU层从"深度毁灭"修复到"逼近平衡"，但NPV仍为负。盈亏平衡扫描显示NPV=0需持续租金≥$6/kW-hr（≈GB300按需价撑满8年）；合约化测试（利用率95%+衰减-10%）反而更差（NPV -$2,248M）——**锁定衰减率比提高利用率更主导**，多年期take-or-pay的实质是锁定价格衰减路径。

值得注意的是短缺修正情景中Equity IRR（58.6%）与负Project NPV并存：杠杆放大了前置现金流，而第二刷新周期后价值转弱。这正是KBRA"初期DSCR良好≠风险低"的模型化呈现[5]。

### 6.3 二手H100反例与资产栈效应

在本文全栈口径下（电厂+绿地DC+到机架+二手GPU@$12k/kW-IT、租金$2.1/kW-hr），二手H100车队NPV=-$1,454M、IRR=-16.7%、P(NPV<0)=100%。这与内部选卡研究[14]报告的"二手H100 IRR 46%、回收期1.0年"形成显著分歧。追溯表明分歧根源**不在价格而在资产栈**：后者为棕地矿场改造（电力与建筑沉没、GPU仅$7k/kW-IT）且收入按token折算。由此得到资产栈效应命题：**二手GPU经济学只在（a）棕地已通电场址或（b）token工厂收入模式下成立；对从电力开始全栈开发的投资人，基准结论（停留在L3.5）不变**。

### 6.4 价值归属的证据

SemiAnalysis Tokenomics模型显示，OpenAI/Anthropic可在GB300集群上产生超过$100B/GW-yr的API收入，而租金成本仅约$12B/GW-yr[6]——8:1的价值差归属模型层而非基础设施层。本文L5 AI工厂层在修正情景下NPV仍为-$1,222M，与该外部证据互洽：**GPU层的钱存在，但由Role决定归属**[1]，为框架"Role决定回报归属"论点提供量化佐证。

---

## 7 讨论

### 7.1 与文献的三处分歧

**（1）资本流向≠回报来源**。McKinsey指出GPU层集中~60%资本开支[1]——产业确实在向下游投；本文测算显示该层在现货假设下NPV为负。两者并不矛盾：宏观资本动员（含vendor循环支持的杠杆化表达[13]）与微观sponsor回报是两个问题。评级机构看下行保护、贷款人赚利差、股权承担残值——同一资产对不同Role意味着完全不同的回报函数。

**（2）衰减假设的时变性**。文献默认GPU租金长期衰减（-20~-25%/年）[3][12]，但2025年末以来的短缺使合约价反转上涨（H100一年合约+40%）[6][15]、残值指数不降反升。本文的处理是将-22%保留为长期结构假设、以-0.05~-0.10作为短缺情景，并用MC加宽衰减率分布（σ=0.05→建议0.08）——单一时点的静态LCOAI式分析[3]在此市场结构下会系统性失真。

**（3）技术变量的二阶效应**。He的Metric Propagation强调上游技术变量（散热约束→降频→吞吐→收入）的主导性[2]；本文龙卷风敏感性显示L3层NPV波动主要由租金（±15%→swing $400M）与造价（$151M）驱动，PUE仅一次线性换算。裁定：租约锁定后市场变量主导（本文结果），GPU刷新重新定价后技术变量主导（He）——模型应增加效率降额参数作为后续工作。

### 7.2 局限性

（1）**筛选级精度**：月度现金流+直线折旧简化税务（未建模CCA/MACRS明细与DSRA机制），不替代银行可融资级模型；（2）**参数时效**：GPU价格与租金取2026年8月快照，市场波动率高，正式评估前应刷新；（3）**单一币种**：USD口径，Alberta的CAD输入按0.714折算，未建模汇率风险；（4）**MC独立性假设**：参数间相关性（如租金与残值同涨同跌）未建模，短缺情景下该假设偏保守；（5）**增量分析依赖同场址假设**：跨项目不可直接比较；（6）校准锚点为公开报道口径，非交易原始文件，Greenlight锚EBITDA落区间上缘提示容量费参数偏乐观。

---

## 8 结论

本文构建、实现并校准了一个AIDC价值链投资评估模型，回答了三个研究问题：

**RQ1**：在统一的100 MW/80 MW IT测试平台上，七种商业模式呈现清晰的风险调整回报排序——Power-only（EqIRR 28%，P损失=0）与L3/L3.5（NPV $676-707M，P损失≤1%）构成可投资区间；自持GPU与AI工厂在全栈新建+现货假设下NPV深度为负（P损失=100%）。

**RQ2**：增量收益在"Critical IT→GPU托管"处降至边际（+0.08）、在"GPU托管→自持GPU"处显著转负（-0.86），价值链最优停留点位于L3–L3.5；Power-only→Shell亦为负（-0.31），提示单纯壳体投资的增量价值有限。

**RQ3**：短缺修正使GPU层Project IRR从-29.7%修复至-2.5%、DSCR从违约修复至1.48x，但NPV转正需持续租金≥$6/kW-hr或满足"长约锁衰减+棕地+厂商担保"三条件之二——结论对市场条件改善具有方向稳健性。

对实践者的启示凝练为框架的三个原始问题：**投到哪一层**（L3/L3.5，除非具备棕地或合约优势）；**何时退出**（开发阶段IRR 55%与基建阶段26%的分野支持"开发→租约锁定→再融资退出"的资本回收路径）；**承担什么风险**（在自己有优势的环节承担——对电力背景投资人即电力与COD风险，把技术残值与利用率风险留给更有能力对冲的对手方）。

后续工作：引入参数相关性MC与CME租金期货对冲模块（2026年10月上市）、KBRA式lease-tail/balloon压力测试、GPU效率降额传播参数、以及以真实交易数据滚动再校准。

---

## 参考文献

[1] McKinsey & Company. *The Cost of Compute: A $7 Trillion Race to Scale Data Centers*. 2025-04-28. https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/the-cost-of-compute-a-7-trillion-dollar-race-to-scale-data-centers

[2] He, Q. *A Unified Metric Architecture for AI Infrastructure: A Cross-Layer Taxonomy Integrating Economics, Performance, and Efficiency*. arXiv:2511.21772, 2025.

[3] Curcio, E. *Introducing LCOAI: A Standardized Economic Metric for Evaluating AI Deployment Costs*. arXiv:2509.02596, 2025.

[4] Morgan Stanley Research. *Bridging a $1.5tr Data Center Financing Gap*. 2025-07-16.

[5] KBRA. *Data Centers: Developments and Trends in Project Finance*. 2026-01-13.

[6] SemiAnalysis. *The Great GPU Shortage* 及 H100 1-Year Rental Contract Price Index / Tokenomics 模型. 2026. https://newsletter.semianalysis.com/p/the-great-gpu-shortage-rental-capacity

[7] NVIDIA Corporation. Form 10-K FY2026（设施租赁担保~$3.5B、投资承诺~$11.4B、云服务承诺~$27B）. SEC.

[8] 公开交易报道口径：Greenlight Electricity Centre（932 MW一期/CA$4.6B/60%债务/Meta长期tolling）；TeraWulf–Anthropic（401 MW Critical IT/20年/名义~$19B，2025）。经内部框架文档整理。

[9] Wall Street Journal. *NVIDIA与OpenAI商谈约$250B融资担保（俄亥俄10GW园区）*. 2026-07-26.

[10] Canada–Alberta Energy MOU（CER暂停、TIER最低有效价CA$130/t）. 2025-11-27；及Alberta Bill 30 — Expedited 120-Day Approvals Act, 2026.

[11] JEFFXI Grand Prairie项目实盘造价（9E三阶段$299M等）. WNT内部资料, 2026.

[12] Epoch AI / SemiAnalysis GPU Pricing Index / AIMultiple Cloud GPU Index（2026-08检索）.

[13]  WNT技术研究组. *AI基础设施融资中的循环支持模式：结构、历史镜鉴与风险展望*（v3.1）. 内部研究, 2026.

[14] WNT技术研究组. *万卡集群，我们该如何选卡？——九种GPU方案在北美AIDC中的工程设计与投资经济性全景分析*；及 *20MW矿场改造AIDC方案设计v4.0*（CentHill Sherbrooke实盘口径）. 内部研究, 2026.

[15] WNT技术研究组. *GPU价格租金三源核实报告*（web权威源+Reddit+X平台87条结构化证据，附置信度评分）. 2026-08-15.

**模型与数据可得性**：aidc_optimizer v1.1（Python开源，含alberta/texas参数包、Greenlight/TeraWulf校准测试、蒙特卡洛与情景脚本），位于《数据中心投资评估框架/aidc_optimizer》。

**利益声明**：作者所属机构从事北美BTM电力与数据中心开发业务，模型参数包含机构自有实盘造价数据；校准与测试脚本公开以便独立复核。

**AI辅助披露**：本文模型实现、数据分析与初稿写作由AI辅助完成，全部数值结果可由随附代码复现，校准锚点与引用均经人工核对。
