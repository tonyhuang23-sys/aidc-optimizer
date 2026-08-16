# 面向AI基础设施的价值链投资评估模型：经济角色、投资时点、资产栈、合约结构与资本结构共同决定的风险调整资本配置框架

## A Value-Chain Investment Evaluation Model for AI Infrastructure

**作者**: WNT Energy 技术研究组  
**日期**: 2026年8月  
**状态**: 工作论文 **v5.4**（All-risk CE 统一 + GPU-only 增量决策版）  
**版本记录**: v5.2 频率修复；v5.3 全量重跑。**v5.4 依《论文5.3版审查意见》**：①Headline CE 统一为 **All-risk Monte Carlo**（同一风险分类，模式暴露不同；N=800 筛选级，正式版目标 ≥5000）；②**GPU-only Merchant 进入主结论**并给出 **L3→L4 增量 IRASR 表**；③价格命名澄清（M1/M2/M3、mix-ref、illustrative bulk、legacy golden）；④Access EV / EconCap 用 All-risk CE 重算；⑤NPV 与 CE 双盈亏平衡。代码：`research_v5_4.py`；结果：`research_outputs/v5_4/`。

---

## 摘要

v5.3 在频率修复后给出了更可信的点估计，但 Headline 中的 CE 仍混用市场 MC / 信用 MC / 旧 L3 MC，**不可直接横比**。v5.4 建立统一 **All-risk** 风险分类（租户/客户违约、GPU 租金、利用率、残值、Vendor、再融资），各模式仅 **Exposure** 不同，得到可比较的 CE：

| 模式 | 确定性 NPV | **All-risk CE** | 观察损失率 |
|---|---:|---:|---:|
| L3 Critical IT | +$707M | **+$248M** | 2.3% |
| L4-M1 Spot $4.25 全栈 | −$1,623M | **−$2,233M** | 99% |
| L4-M2 On-demand $6.90 全栈 | −$353M | **−$1,333M** | 78% |
| L4-M mix-ref $7.80 全栈 | +$78M | **−$1,029M** | 60% |
| **L4-M GPU-only $7.80** | **+$667M** | **−$439M** | 36% |
| L4-M GPU-only $9.36 | +$1,415M | **+$86M** | 17% |
| L4-C Fixed *illustrative bulk* $7.02 | +$2,885M | **+$1,671M** | 0.4% |
| L4-S Fixed *illustrative bulk* $7.02 | +$3,278M | **+$2,067M** | 0.3% |

**L3→L4 增量 IRASR（All-risk CE / ΔPeak 与 ΔEconCap）：**

| 增量路径 | ΔCE $M | ΔPeak $M | IRASR_peak | IRASR_econ |
|---|---:|---:|---:|---:|
| → Spot Merchant 全栈 | −2,481 | +3,383 | **−0.73** | −0.66 |
| → mix-ref $7.80 全栈 | −1,277 | +2,046 | **−0.62** | −0.53 |
| → **GPU-only $7.80** | −687 | +1,533 | **−0.45** | −0.38 |
| → GPU-only $9.36 | −162 | +1,515 | **−0.11** | −0.09 |
| → Contracted illustrative bulk | +1,422 | +1,088 | **+1.31** | +0.76 |
| → Strategic illustrative bulk | +1,819 | +183 | **+9.92** | +1.32 |

**主结论改写：**

1. **无合同全栈 Merchant 风险调整后仍不应作为默认策略**（CE 深负，IRASR&lt;0）。  
2. **已有低成本电力与 AI-ready 机房的资产方（GPU-only）点估计可显著为正**，但 All-risk CE 在 $7.80 下仍为负；仅在接近 short-term dedicated 租金时 CE 转正——**栈改变边界，不自动等于“无合同可买卡”。**  
3. **Illustrative bulk（$7.02=0.75×list）** 下 Contracted/Strategic 的 All-risk CE 仍显著高于 L3；该价是**情景假设**，不是已校准成交价。  
4. **Type A（低合同可得性）ex-ante EV 最优仍为 L3**；Type B/C 在合同能力落实后最优转向 C/S。

---

## 1 审查意见对应关系

| 优先级 | 问题 | v5.4 处理 |
|---|---|---|
| P0 | Headline CE 混用 MC 体系 | **All-risk 统一表**（§3） |
| P0 | GPU-only 未进主结论 | **主摘要 + IRASR 增量表**（§4） |
| P1 | 三套基准价混淆 | **命名纪律**（§2） |
| P1 | $7.02 称 Recommended Base | 改为 **Illustrative Bulk Case** |
| P1 | Access/EconCap 未用修复后结果 | **All-risk CE 重算**（§5） |
| P1 | 仅有 NPV break-even | **NPV + CE 双阈值**（§6） |
| P2 | Historical 非真实回测 | 保持承认（不伪强化） |
| P2 | 单一 reproduce 脚本 | 仍分模块；正式发布前合并（已记） |

---

## 2 价格与命名纪律

| 标签 | $/GPUh | 含义 | 用途 |
|---|---:|---|---|
| **M1 Spot** | 4.25 | 现货/commodity | Merchant 下限 |
| **M2 On-demand** | 6.90 | 短周期实例 | Merchant 中枢候选 |
| **Mix-ref non-spot** | 7.80 | 非现货公开报价混合参考 | **不是纯现货**；仅作产品组合参考 |
| **M3 Short-term dedicated** | 9.36 | 短周期/小集群 dedicated list | Merchant 上沿 / 合同 list 上界 |
| **Illustrative bulk** | 7.02 | 0.75×list 的**假设**批量 5 年价 | 情景中枢，**未交易锚定** |
| **Legacy golden YAML** | ≈5.63 | `rate_per_kw_hr=3.0` 折算 | 仅 reproduce 回归，不作 Headline |

**禁止再写：** “Merchant @ public median $7.8 接近盈亏平衡 = 现货市场可做”。  
**应写：** “在 mix-ref $7.8 与 −22%/年下全栈点估计接近 BE，但 All-risk CE 仍显著为负。”

---

## 3 All-risk Monte Carlo（Headline 唯一 CE 来源）

### 3.1 风险分类与暴露

| Risk | L3 | L4-M | L4-C | L4-S |
|---|---|---|---|---|
| Tenant / customer default | ✓ | — | ✓ | ✓ |
| GPU rent | — | ✓ 高 | fallback / haircut | fallback / haircut |
| Utilization | — | ✓ 高 | ToP 锁定 | ToP 锁定 |
| Residual | — | ✓ 高 | 轻 | 轻 |
| Vendor failure | — | — | 低 | ✓ backstop |
| Refinancing | ✓ | ✓ | ✓ | ✓ |

同一分类框架；**Exposure 权重随模式变化**。筛选级 N=800；正式版目标 **N≥5000**。L3 的 All-risk CE（+$248M）**低于**旧独立租金 MC（+$505M），因纳入违约/再融资等冲击——**横比请只用本表**。

### 3.2 All-risk 结果（N=800）

| 标签 | E(NPV) | CE (λ=0.5) | Loss rate | Wilson 95% CI |
|---|---:|---:|---:|---|
| L3_allrisk | +657 | **+248** | 2.3% | — |
| L4M M1 Spot 4.25 | −1,755 | **−2,233** | 99.3% | 98.4–99.7% |
| L4M M2 6.90 | −567 | **−1,333** | 77.9% | 74.9–80.6% |
| L4M mix-ref 7.80 | −165 | **−1,029** | 60.4% | 56.9–63.7% |
| L4M M3 9.36 | +533 | **−503** | 35.3% | 32.0–38.6% |
| **L4M GPU-only 7.80** | +424 | **−439** | 36.0% | 32.8–39.4% |
| L4M GPU-only 9.36 | +1,122 | **+86** | 16.9% | 14.4–19.6% |
| L4C list 9.36 | +4,289 | **+3,127** | 0.13% | 0.02–0.70% |
| **L4C illustrative bulk 7.02** | +2,532 | **+1,671** | 0.37% | 0.13–1.1% |
| L4C bulk step −6%/yr | +1,894 | **+1,184** | 1.4% | 0.8–2.5% |
| L4S list 9.36 | +4,840 | **+3,661** | 0%* | 上界 0.48% |
| **L4S illustrative bulk 7.02** | +2,945 | **+2,067** | 0.25% | 0.07–0.91% |
| L4S downside 5.62 | +1,811 | **+1,114** | 1.3% | 0.7–2.3% |

\*观察 0/800；Wilson 上界仍 &gt;0，不得写“零风险”。

---

## 4 GPU-only 与 L3→L4 增量决策（主结论）

### 4.1 产业含义

全栈 Greenfield Merchant（Power+DC+GPU）与 **GPU-only 增量**（电力与机房已沉没）是**不同决策**：

| 决策 | $7.80 mix-ref 点估计 NPV | All-risk CE |
|---|---:|---:|
| 全栈新建 Merchant | +$78M | **−$1,029M** |
| **GPU-only 增量** | **+$667M** | **−$439M** |
| GPU-only @ $9.36 short-ded | +$1,415M | **+$86M** |

因此：

> **不能简单说“没有长期合同就不要买卡”。**  
> 应说：对从零建设 Power+DC+GPU 的 Sponsor，无合同 Merchant 风险调整回报偏弱；对**已有低成本电力与 AI-ready 机房**的持有人，新增 GPU 的点估计可显著改善，但在 $7.80 产品组合参考租金下 All-risk CE 仍为负——需更高实现租金、更优残值或合同化，才在风险调整上站得住。

这与矿场转 AIDC、已建成 IDC、hyperscaler 内部机房 vs 绿地 Neocloud 的分野一致，并强化 **Asset Stack** 维度。

### 4.2 增量 IRASR 表（资本配置核心表）

基准 L3：All-risk CE **+$248M**，Peak **$317M**，EconCap（筛选）**~$442M**。

| 增量 L3→… | Rate | ΔCE $M | ΔPeak $M | **IRASR_peak** | **IRASR_econ** |
|---|---|---:|---:|---:|---:|
| Spot Merchant 全栈 | 4.25 | −2,481 | +3,383 | **−0.73** | −0.66 |
| Legacy YAML ~5.63 | ~5.63 | −2,013 | +2,688 | **−0.75** | −0.66 |
| On-demand 全栈 | 6.90 | −1,581 | +2,056 | **−0.77** | −0.66 |
| Mix-ref 全栈 | 7.80 | −1,277 | +2,046 | **−0.62** | −0.53 |
| **GPU-only** | 7.80 | −687 | +1,533 | **−0.45** | −0.38 |
| GPU-only | 9.36 | −162 | +1,515 | **−0.11** | −0.09 |
| **Contracted illustrative bulk** | 7.02 | **+1,422** | +1,088 | **+1.31** | **+0.76** |
| **Strategic illustrative bulk** | 7.02 | **+1,819** | +183 | **+9.92** | **+1.32** |

**读法：**

- 全栈 Merchant：每多占用 $1 Peak Equity，毁灭约 **$0.6–0.8** 确定性等价价值。  
- GPU-only：破坏减小，但仍 **IRASR&lt;0**（除非接近 M3 租金）。  
- Contracted/Strategic：IRASR **显著为正**——这是“再投下一美元”的主要正区域。  
- 旧 golden IRASR≈−0.94 对应 **legacy ~$5.63/GPUh 全栈路径**，与 Headline $7.80 **不是同一假设**；增量表已分列。

---

## 5 Access EV 与 EconCap（All-risk CE 重算）

使用 All-risk CE：CE_M(mix-ref)=−1029，CE_C(bulk)=+1671，CE_S(bulk)=+2067，CE_L3=+248。

| 类型 | p_C | p_S | EV 追 C | EV 追 S | 最优 |
|---|---:|---:|---:|---:|---|
| A Uncontracted | 0.10 | 0.02 | −779 | −808 | **L3** |
| B Contract capability | 0.85 | 0.20 | +1,246 | +1,283 | **S** |
| C Strategic platform | 0.95 | 0.70 | +1,516 | +1,749 | **S** |

EconCap 为筛选级（Peak + guarantee/LC/reserve 比例假设），**框架完成、校准待完成**。IRASR_econ 已并列给出。

---

## 6 盈亏平衡：NPV 与 CE 双阈值

| 指标 | 模式 | 阈值 $/GPUh（约） |
|---|---|---:|
| NPV_L4 = NPV_L3 | L4-C Fixed | ~4.30 |
| NPV_L4 = NPV_L3 | L4-S Fixed | ~4.02 |
| NPV_L4 = 0 | L4-M −22%/yr | ~7.64 |
| **CE_L4 = CE_L3** | **L4-C Fixed** | **~$4.72** |
| **CE_L4 = CE_L3** | **L4-S Fixed** | **~$4.22** |

CE 平价高于 NPV 平价：风险调整后需要略高的实现合同价。正式决策应优先 **CE 阈值** 与 **IRASR**，而非仅 NPV。

Illustrative bulk $7.02 高于上述 CE 阈值 → 在**该假设价**下 C/S 的 All-risk CE 优于 L3；真实成交价需交易反推，结论应表述为：

> **当 5 年 realized contract rate 高于约 $4.7/GPUh（C）或 $4.2（S）时，风险调整后优于 L3（本模型 All-risk 设定下）。**

---

## 7 理论框架（沿用并收紧）

六维函数 + 合同可获得概率：

$$\mathrm{Optimal}=f(\mathrm{Role},\mathrm{Vintage},\mathrm{Stack},\mathrm{Contract},\mathrm{Capital},\mathrm{Market},p_{\mathrm{access}})$$

**Buy First vs Contract First**、**Historical ≠ Forward**、**双甜蜜点**、**风险迁移**、**demand-led GPU** 均保留。

**表述禁令（v5.4）：**

- 不用混用体系的 CE 横比  
- 不把 $7.80 叫作“现货中位”  
- 不把 $7.02 叫作“推荐真实 Base”  
- 不把 GPU-only 正 NPV 写成“无合同可放心买卡”  
- 不把 Peak Cash Equity 写成完整风险资本  

---

## 8 结论

1. **All-risk CE 下，全栈无合同 Merchant 不应作为默认策略**（CE 深负，IRASR&lt;0）。  
2. **GPU-only 改变边界**：沉没电力/机房后点估计可大幅改善；$7.80 下 CE 仍负，$9.36 下 CE 转正——栈与实现租金共同决定。  
3. **Illustrative bulk 合同化路径 IRASR 显著为正**；Access 概率低时 ex-ante 仍应留在 L3。  
4. **频率修复 + 统一 CE + 增量 IRASR** 后，论文资本配置逻辑首次在同一度量下闭合。

**一句话：**

> 再投下一美元是否进入 GPU，取决于你是绿地还是 GPU-only、实现的是 Spot 还是合同价、以及有没有合同可获得性——用 All-risk CE 与 IRASR 回答，而不是用混用的单点 NPV。

---

## 附录 A — 产出与复现

```bash
python research_v5_4.py
# → research_outputs/v5_4/
#    allrisk_ce_table.csv
#    l3_to_l4_incremental_irasr.csv
#    headline_allrisk.csv
#    break_evens_npv_ce.csv
#    access_ev_allrisk_ce.csv
#    v5_4_summary.json
python reproduce.py check   # golden regression (legacy YAML path)
```

**样本量说明：** Headline All-risk 为 **N=800 筛选级**；正式对外/期刊级建议 **N≥5000** 并固定种子报告。  
**模型仓库：** `https://github.com/tonyhuang23-sys/aidc-optimizer`  
**利益声明 / AI 披露：** 同前；v5.4 数字以 `research_outputs/v5_4/` 为准。
