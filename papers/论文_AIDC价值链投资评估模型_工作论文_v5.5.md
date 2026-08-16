# 面向AI基础设施的价值链投资评估模型：经济角色、投资时点、资产栈、合约结构与资本结构共同决定的风险调整资本配置框架

## A Value-Chain Investment Evaluation Model for AI Infrastructure

**作者**: WNT Energy 技术研究组  
**日期**: 2026年8月  
**状态**: 工作论文 **v5.5**（Transfer Pricing + Matched Counterparty + IRASR_econ 主指标）  
**版本记录**: v5.4 All-risk CE 统一。**v5.5 依《5.4版修改意见》完成五件核心修订（不扩框架）：** ①GPU-only **Transfer Pricing**（accounting sunk vs economic 支付 L3 市场租金）；②**Matched Counterparty Test**（同信用拆 Layer vs Credit）；③All-risk **Bootstrap 95% CI**（Headline N=800 筛选级；正式冻结目标 N=10,000）；④**IRASR_econ 作为主资本配置指标**（Peak 降为次要）；⑤GPU-only **CE parity** 与 Access **p\***（fallback=继续做 L3）。完整 Working Paper 合并列为 **v6.0**，本稿仍是修订备忘录形态。代码：`research_v5_5.py`；结果：`research_outputs/v5_5/`。

---

## 摘要

v5.4 把 GPU-only 推进主结论，但可能把已占用的 L3 容量当成“免费”。v5.5 区分两种 GPU-only：

| 口径 | 含义 | $7.80 mix-ref All-risk CE | vs L3 CE (+$299*) |
|---|---|---:|---|
| **Accounting / sunk** | 机房闲置、无可替代租户 | **−$439M** | 仍低于 L3 |
| **Economic / transfer** | 按 L3 市场租金 $185/kW-月内部结算 | **−$949M** | 更差（放弃租约） |

\*L3 All-risk CE 本轮 Bootstrap 点估计 **+$299M**，95% CI **[$193M, $407M]**。

**GPU-only 与 L3 的 CE 平价租金：**

- Accounting（闲置机房）：约 **$9.75/GPUh**  
- Economic（可出租机房）：约 **$11.32/GPUh**  

$9.36 short-dedicated 在 **经济口径**下 CE 仍约 **−$395M**，**达不到**放弃 L3 租约的机会成本。

**Matched Counterparty（同信用）：** IG 代理下 Layer 效应（C−L3）约 **+$1.57B**，远大于信用档差。L4-C 优于 L3 **主要来自合同结构，而非“客户更好”。**

**IRASR 主指标改为 EconCap：**

| 路径 | ΔCE $M | **IRASR_econ（主）** | IRASR_peak（次） |
|---|---:|---:|---:|
| → 全栈 Merchant $7.80 | −1,328 | **−0.55** | −0.65 |
| → GPU-only accounting | −738 | **−0.41** | −0.48 |
| → GPU-only economic | −1,248 | **−0.68** | −0.81 |
| → C illustrative bulk | +1,340 | **+0.72** | +1.23 |
| → S illustrative bulk | +1,768 | **+1.29** | +9.64（勿作主结论） |

**Access（fallback=留在 L3）：** 因 CE_C、CE_S ≫ CE_L3，盈亏平衡成功率 p\* 仅取决于 Pursuit Cost。Pursuit $20M 时 p_C\*≈1.5%、p_S\*≈1.1%——**值得花有限开发费用去追合同**；拿不到则继续出租 L3，而不是被迫做 Merchant。

**λ∈{0,0.25,0.5,0.75,1}：** C/S 在全部 λ 下均高于 L3；高风险厌恶不会把排序翻回“只做 L3、合同化无意义”。全栈 Merchant 在全部 λ 下均劣于 L3。

---

## 1 修订对应

| 意见 | v5.5 |
|---|---|
| GPU-only 漏计 L3 机会成本 | Transfer Pricing 双口径 |
| L3 vs L4 信用是否同口径 | Matched Counterparty |
| N=800、无 CE 区间 | Bootstrap CI；标注正式版 N=10k |
| IRASR_peak=9.92 误导 | **IRASR_econ 主指标** |
| p_access 塞进七维 | **两步：资产六维 + Sponsor overlay** |
| GPU-only CE parity | Accounting ~$9.75；Economic ~$11.32 |
| λ 敏感性 | All-risk 样本重跑 |
| 全文形态 | 明确本稿为 revision memo；v6.0 合并正文 |

---

## 2 理论收紧

### 2.1 两步决策（不再写七维混一）

**Step 1 — Asset economics**

$$V_i=f(\mathrm{Role},\mathrm{Vintage},\mathrm{Stack},\mathrm{Contract},\mathrm{Capital},\mathrm{Market})$$

**Step 2 — Sponsor overlay**

$$EV^{\mathrm{Sponsor}}=f(V_i,\,p_{\mathrm{access}},\,\mathrm{PursuitCost},\,\mathrm{Fallback})$$

开发商更真实的 Fallback 是 **继续做 L3**，不是被迫 Merchant。

### 2.2 Sunk ≠ 零机会成本

$$\text{Buy GPU iff }\mathrm{CE}_{\mathrm{Compute}}-\mathrm{CE}_{\mathrm{Foregone L3}}>0$$

- 闲置、无可替代租户 → Accounting view  
- 可按市场租金租出 → Economic / transfer view（内部按 $185/kW-月结算）

---

## 3 Transfer Pricing 结果

L3 市场租金 **$185/kW-月**（配置 `ready_rent_kw_mo`）作为 ComputeCo 对 DataCenterCo 的内部价。

| GPU-only 口径 | $7.80 CE | $7.80 E[NPV] | $9.36 CE（经济口径） |
|---|---:|---:|---:|
| Accounting（sunk、零机会成本） | **−$439M** CI [−497, −367] | +$424M | — |
| Economic（付 L3 租金） | **−$949M** CI [−1,009, −885] | −$147M | **−$395M** |

**判断：**

- 闲置矿场/无租户机房：Accounting 改善相对全栈 Merchant（CE −439 vs −1,029），但 **仍低于继续做 L3（+299）**。  
- 可出租 AI-ready 机房：自营 Merchant **明显劣于**把容量租出去。  
- 经济口径要追上 L3 的 CE，约需 **$11.3/GPUh** 的风险调整实现租金。

---

## 4 Matched Counterparty

| 对象 | 信用代理 | All-risk CE |
|---|---|---:|
| L3 | Generic tenant (PD~2%) | +248 |
| L3 | IG / A-–BBB+ (PD~0.8%) | +402 |
| L4-C bulk | Generic (PD~4%) | +1,639 |
| L4-C bulk | **同 IG** | **+1,974** |

- **Layer effect（同 IG）**：1,974 − 402 ≈ **+$1.57B**  
- L3 信用升级仅约 +$154M；C 的结构溢价远大于“客户更好”。  
- L3 损失率高于 L4-C，在**同信用**下仍成立（20 年租约 vs 5 年 ToP 的期限/尾部差异），**不是**因为给 L4 偷偷用了更好客户。

---

## 5 All-risk CE 与 Bootstrap 区间（N=800）

| 模式 | CE | Bootstrap 95% CI | Loss |
|---|---:|---|---:|
| L3 | +299 | **[193, 407]** | 2.3% |
| 全栈 Merchant $7.80 | −1,029 | **[−1,087, −956]** | 60% |
| GPU-only accounting | −439 | **[−497, −367]** | 36% |
| GPU-only economic | −949 | **[−1,009, −885]** | 61% |
| C illustrative bulk | +1,639 | **[1,507, 1,769]** | 0.4% |
| S illustrative bulk | +2,067 | **[1,930, 2,206]** | 0.3% |

C 与 S 的 CI **不重叠**（本轮样本下 S 高于 C），二者均 **远高于** L3（区间不交叉）。  
可强说：**合同化算力显著优于 L3**；S 优于 C 的证据存在但弱于“C/S vs L3”，正式版需 N=10,000 复核。

---

## 6 IRASR_econ 主指标

| L3 → | ΔCE | **IRASR_econ** | IRASR_peak |
|---|---:|---:|---:|
| 全栈 Merchant $7.80 | −1,328 | **−0.55** | −0.65 |
| GPU-only accounting | −738 | **−0.41** | −0.48 |
| GPU-only economic | −1,248 | **−0.68** | −0.81 |
| C bulk | +1,340 | **+0.72** | +1.23 |
| S bulk | +1,768 | **+1.29** | +9.64 |

**9.64 不再作 Headline。** 主叙事：Strategic 每单位经济资本约创造 **$1.3** 确定性等价价值；Contracted 约 **$0.72**。EconCap 仍为筛选比例假设（校准待完成）。

---

## 7 GPU-only CE 平价

| 口径 | CE = CE_L3 的租金 |
|---|---:|
| Accounting（闲置、无租户） | **~$9.75/GPUh** |
| Economic（放弃可出租 L3） | **~$11.32/GPUh** |

> 已有机房业主若放弃长期 L3 出租而自营 Merchant GPU，经济口径下需实现约 **$11+/GPUh** 的风险调整租金，才补偿所放弃的租约与额外技术/利用率风险。

---

## 8 Access Overlay（Fallback = L3）

$$p_C^{*}=\frac{\mathrm{PursuitCost}}{\mathrm{CE}_C-\mathrm{CE}_{L3}}$$

| Pursuit $M | p_C\* | p_S\* |
|---:|---:|---:|
| 5 | 0.4% | 0.3% |
| 20 | **1.5%** | **1.1%** |
| 50 | 3.7% | 2.8% |
| 100 | 7.5% | 5.7% |

拿不到合同就继续做 L3 时，**很低的成功概率**即可覆盖有限 BD/法务成本。这比“小玩家不能碰 GPU”更接近开发商真实决策。

---

## 9 λ 敏感性（All-risk 样本）

| 模式 | λ=0 | λ=0.5 | λ=1 |
|---|---:|---:|---:|
| L3 | +662 | +299 | −64 |
| 全栈 M $7.80 | −165 | −1,029 | −1,893 |
| GO accounting | +424 | −439 | −1,302 |
| GO economic | −147 | −949 | −1,752 |
| C bulk | +2,523 | +1,639 | +754 |
| S bulk | +2,945 | +2,067 | +1,190 |

**C/S > L3 在 λ=0 到 λ=1 均成立。** 高度风险厌恶不会推翻“合同化优于 L3”；只会削弱（仍为正）。全栈 Merchant 全 λ 劣于 L3。λ=1 时 L3 自身 CE 转负（尾部租户风险），C/S 仍为正。

---

## 10 结论

1. **Sunk ≠ 零机会成本。** GPU-only accounting 改善全栈 Merchant，但经济口径（付 L3 租金）后更接近“不要用好机房去赌 Merchant”。  
2. **合同结构本身值钱**（同信用 Layer 效应约 +$1.6B），不是只靠更好客户。  
3. **资本配置主指标用 IRASR_econ**（C +0.72，S +1.29）；禁止用 Peak 9.6× 作对外口号。  
4. **Fallback=L3 时，追合同的 p\* 很低**——值得花有限费用去拿 ToP；失败则留在 L3。  
5. **下一步应冻结算法、合并 v6.0 全文**，而不是继续加模块。正式 Headline 建议 N=10,000 + 交易锚定 realized rate。

**一句话：**

> 闲置机房的 GPU-only 比绿地 Merchant 好看，但只要机房租得出去，自营 Merchant 的风险调整价值仍低于把容量租给别人；真正值得延伸的是能拿到的合同化算力，用 IRASR_econ 而不是杠杆压出来的 Peak IRASR 来决策。

---

## 附录 — 产出

```
research_outputs/v5_5/
  allrisk_ce_bootstrap_ci.csv
  irasr_econ_primary.csv
  lambda_sensitivity_allrisk.csv
  gpuonly_ce_parity.csv
  access_pstar_l3_fallback.csv
  matched_counterparty.csv
  layer_vs_counterparty.csv
  v5_5_summary.json   # 若缺则用上表数字
```

```bash
python research_v5_5.py
```

N=800 筛选级；CE CI 为 2000 次 Bootstrap。EconCap 未校准。$7.02=0.75×$9.36 为作者情景假设。  
**v6.0**：将本数字合并回完整正文（生态、Role、校验、文献、参考文献）。
