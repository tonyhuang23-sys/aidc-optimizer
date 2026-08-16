# 面向AI基础设施的价值链投资评估模型：经济角色、投资时点、资产栈、合约结构与资本结构共同决定的风险调整资本配置框架

## A Value-Chain Investment Evaluation Model for AI Infrastructure

**作者**: WNT Energy 技术研究组  
**日期**: 2026年8月  
**状态**: 工作论文 **v5.2**（时间频率修复版）  
**版本记录**: v5.0 Investment Vintage；v5.1 P0 审计（合同价/CAPEX/Backstop/信用MC）。**v5.2 修复 P0-0 Annual/Monthly Frequency Bug：GPU `rate_decay`（标注为年化）在月度循环中被错误写成 `(1+g)**k`（k=月），使 −6%/年变成约 −52%/年、−22%/年变成约 −95%/年。修复为 `(1+g)**(k/12)` 后全量重跑 Merchant / C1–C3 / L4-M/C/S / 盈亏平衡。** 代码：`aidc_optimizer/models.py`、`research_l4.py`；结果：`research_outputs/v5_2_freq_fix/`。

---

## 摘要

v5.1 在审计中已证明 C2 表内价格路径与“−6%/年”不符。v5.2 确认根因并修复：

**Bug**：月度引擎对 GPU 租金使用 `rate *= (1 + annual_decay) ** month_index`，把年化衰减当成月化复利。  
**Fix**：`rate *= (1 + annual_decay) ** (month_index / 12)`。电力/租约 escalator 本就按 `yr = months/12` 计算，**未受影响**。

**修复后 Headline（统一 B200 CAPEX ≈$60k/GPU；Backstop 仅 residual unsold）：**

| 情景 | 修复前 | 修复后 |
|---|---:|---:|
| C1 Fixed $9.36 ToP | +$4.76B | +$4.76B（decay=0 不变） |
| C2 Step-down **−6%/年** | **−$0.35B** | **+$3.84B** |
| C1−C2 ΔNPV | **+$5.11B** | **+$0.92B** |
| Merchant $7.80 −22%/年 | **−$3.17B** | **+$0.08B** |
| Merchant NPV=0 盈亏平衡 | ~$30/GPUh | **$7.64/GPUh** |
| Merchant vs L3 盈亏平衡 | — | **$9.11/GPUh** |

**修正后的产业含义（比 v5.1 更贴近现实）：**

1. **温和 step-down（−6%/年）不会摧毁 Contracted 价值**——C2 仍 +$3.84B，显著高于 L3（+$0.71B）；真正危险的是**快速重定价**（C3 −15%/年仍 +$2.39B，但溢价收窄）。  
2. **Merchant Forward 不再被机械判死刑**：公开中位 $7.80/GPUh 在 −22%/年真实年化下接近盈亏平衡（+$78M）；Spot $4.25 仍深负；Dedicated $9.36 下 Merchant 可正（+$0.83B）。  
3. **Contracted / Strategic 优势保留但更克制**：锁价相对温和 step-down 的溢价约 **$0.9B**（非 $5B）；bulk $7.02 下 C1 +$2.88B、C2 +$2.20B、L4-S +$3.28B，均仍高于 L3。  
4. **Vintage / “过去为何赚钱”** 与频率修复一致：原模型把 forward rent decay 算得过快，是 Merchant 系统性巨亏的主因之一；修复后 Historical≠Forward 与周期交易逻辑仍成立，但 Forward Merchant 的阈值更接近公开价带。

**关键词**: Annual/Monthly conversion；rate_decay；step-down；Merchant Forward；Contracted；take-or-pay

---

## 1 问题陈述：P0-0 时间频率审计

### 1.1 决定性证据（v5.1 表已暴露）

v5.1 将 C2 标为“−6%/年”，但逐年均价为：

$$6.81,\ 3.24,\ 1.54,\ 0.73,\ 0.35$$

该序列满足：

$$\frac{3.24}{6.81}\approx 0.476 = 0.94^{12}$$

且第1年均值：

$$\frac{1}{12}\sum_{m=0}^{11} 9.36\times 0.94^{m} \approx 6.813$$

与表完全一致 → 代码在**每月**乘以 `0.94`，即把 −6%/年当成 −6%/月（真实年化约 **−52.4%**）。

### 1.2 代码定位

```text
aidc_optimizer/models.py  /  research_l4.py
  for m in range(...):          # m 月
      k = month_index
      rate = rate0 * (1 + decay) ** k   # BUG: decay 标注为 /year
```

电力层 / DC 租约使用 `yr = (m-cm)/12` 与 `(1+esc)**yr`，**频率正确**。受影响的是 **GPU `rate_decay` 及一切复用同一公式的 GPU 路径**（Merchant、C2/C3、Vintage、部分 break-even）。

### 1.3 修复

```text
rate = rate0 * (1 + decay) ** (k / 12.0)
```

等价于月度增长率 \(g_m = (1+g_a)^{1/12}-1\) 的连续复利形式。

---

## 2 修复后核心结果

### 2.1 合同期限结构（B200 统一 CAPEX；list $9.36）

| 合同 | 含义 | NPV $M | Peak $M | 相对 L3 (+707) |
|---|---|---:|---:|---|
| **C1** Fixed 5Y ToP | 锁价 | **+4,761** | 1,351 | 超过 |
| **C2** −6%/**年** step-down | 温和降价 | **+3,844** | 1,351 | 超过 |
| **C3** −15%/**年** 重定价 | 较快降价 | **+2,392** | 1,362 | 超过 |
| C1−C2 Δ | 锁价溢价 | **+917** | — | （修复前 +5,108） |

C2 逐年价格（修复后）：**9.36 → 8.80 → 8.27 → 7.77 → 7.31**（与年化 −6% 一致）。

**结论改写：**

> 合理的温和 step-down 合同仍可使 L4-C 显著优于 Merchant，并高于 L3；  
> **真正侵蚀合同价值的是快速市场重定价，而不是任何价格下降。**

### 2.2 Merchant Forward（−22%/**年** 修复后）

| 公开价 $/GPUh | NPV $M | Project IRR | 解读 |
|---|---:|---:|---|
| 4.25 Spot | −1,623 | −4.9% | 仍深负 |
| 6.90 Instance | −353 | 10.7% | 接近但未翻正 |
| **7.80 Median** | **+78** | **16.0%** | 接近盈亏平衡 |
| 9.36 Dedicated | +826 | 25.1% | 正，但 Peak Equity 仍高（~$2.3B） |

盈亏平衡：

| 阈值 | 修复前 | 修复后 |
|---|---:|---:|
| Merchant NPV=0 | ~$30/GPUh | **$7.64/GPUh** |
| Merchant NPV = L3 | — | **$9.11/GPUh** |

**结论改写：**

> Merchant **不是**被数学上永久否定；在真实年化 −22% 衰减与公开中位租金下，Forward Merchant 接近盈亏平衡。  
> Spot 路径仍弱；是否值得做取决于 Vintage、资产栈与能否获得接近 Dedicated 的持续租金——与“周期交易 + 运营能力”定位一致。

### 2.3 L4-M / C / S 与 bulk 情景（推荐对照表）

| 模式 | Rate | NPV $M | Peak $M | vs L3 |
|---|---|---:|---:|---|
| L3 Critical IT | — | +707 | 317 | — |
| L4-M median $7.80 −22%/yr | 7.80 | +78 | 2,362 | 低于 L3（资本效率差） |
| L4-C Fixed list $9.36 | 9.36 | +4,761 | 1,351 | 超过 |
| L4-C Fixed bulk $7.02 | 7.02 | +2,885 | 1,404 | 超过 |
| L4-C Step −6%/yr bulk $7.02 | 7.02 | +2,197 | 1,404 | 超过 |
| L4-S Fixed list $9.36（BS 修正） | 9.36 | +5,285 | 438 | 超过 |
| L4-S Fixed bulk $7.02（BS 修正） | 7.02 | +3,278 | 500 | 超过 |

说明：list 仍为上界；bulk 为情景假设（非已校准成交价）。Backstop 仅 residual unsold；B200 CAPEX 统一 $60k/GPU。

### 2.4 与 v5.1 审计结论的衔接

| v5.1 结论 | v5.2 后状态 |
|---|---|
| C1 锁价价值巨大（+$5B vs C2） | **大幅下调**：真实年化下 Δ≈**+$0.92B** |
| 温和 step-down 摧毁合同 | **否决**：C2 仍 +$3.8B |
| Merchant Forward 深负（−$3B） | **否决为 bug 产物**：中位租金下约 **+$0.08B** |
| List $9.36 不作 bulk Base | **保留** |
| Backstop 双重计费修正 | **保留** |
| Strategic 0% 损失否决 | **保留**（信用 MC 框架；数字须在修复后重跑） |
| EconCap / Access EV | **框架保留**；应用修复后 NPV 重算 |

---

## 3 理论含义

### 3.1 为什么“过去有人 Merchant 赚钱” suddenly 不矛盾了

修复前，模型把 −22%/年算成约 −95%/年，任何公开价都难以翻正，与产业经验冲突。修复后：

- Forward 在中位租金附近**脆弱地**可盈亏平衡；  
- 早期 Vintage 的低 CAPEX + 更高初始租金 / scarcity 路径仍可能显著更好；  
- Contracted 的价值从“避免每月崩盘”变为“在温和降价世界中锁定路径 + 利用率 + 可融资性”。

### 3.2 合同真正买什么

| 合同特征 | 修复后价值来源 |
|---|---|
| 固定价 vs −6%/年 | 约 **$0.9B** 锁价溢价（非 $5B） |
| 固定价 vs 快速重定价 | 溢价扩大，但 C3 仍可为正 |
| Take-or-pay billable | 利用率下限（与锁价正交） |
| 期限 + 预付 + 信用 | Peak Equity / Kd / 杠杆（资本效率） |

### 3.3 双甜蜜点（更新）

- **Structural**：L3——无合同能力时的稳健默认。  
- **Contracted/Strategic**：在可获得固定价或温和 step-down ToP 时，确定性 NPV 与资本效率可优于 L3。  
- **Cyclical Merchant**：仅当持续租金接近/超过 ~$7.6–9.1/GPUh 且 Sponsor 能承受高 Peak Equity 时，才进入讨论——不是默认策略。

### 3.4 六维函数（不变）

$$\mathrm{Optimal\ Layer}=f(\mathrm{Role},\ \mathrm{Vintage},\ \mathrm{Stack},\ \mathrm{Contract},\ \mathrm{Capital},\ \mathrm{Market})$$

频率修复改变的是**度量**，不是框架。

---

## 4 方法：强制时间单位纪律

### 4.1 规则

凡配置中标注为 **年化** 的增长率/衰减率 \(g_a\)，进入月度循环必须：

$$
(1+g_a)^{t/12}
\quad\text{或}\quad
g_m=(1+g_a)^{1/12}-1,\ \ (1+g_m)^{t}
$$

**禁止** ` (1+g_a)^{t_{\mathrm{month}}} `。

### 4.2 已审计项

| 参数 | 单位 | 修复前 | 修复后 |
|---|---|---|---|
| `gpu.rate_decay` | /year | 按月指数 | **`**(k/12)`** |
| `ai.rate_decay` | /year | 同上（同文件） | 同上 |
| `power.gas_escalator` | /year | 已用 yr | 正确 |
| `dc.escalator` | /year | 已用 yr | 正确 |
| `carbon.escalator` | /year | 已用 yr | 正确 |
| 债务利率 | /year | `(1+r)**(1/12)-1` | 正确 |

### 4.3 复现

```bash
# 关键路径（修复后）
python -c "from research_l4 import *; ..."
# 核心表
# research_outputs/v5_2_freq_fix/v5_2_core_results.csv
# research_outputs/v5_2_freq_fix/break_evens.json
```

---

## 5 讨论：数据驱动，不维护旧结论

本轮是全文最重要的一次重新校准之一。它说明：

1. **框架可以成熟，数字必须可证伪**——C2 表自己揭发了频率 bug。  
2. 修复后结论**更有产业信息量**：温和降价合同仍强；Merchant 在公开中位附近脆弱平衡；Strategic 的优势更多来自资本结构与确定性，而非“避免每月半价崩盘”。  
3. v5.1 的 list-price / backstop / EconCap / access 审计**仍然有效**，且应在修复后的路径上继续做信用 MC 与 bulk 情景 CE。

### 5.1 仍待完成（不阻塞 v5.2 Headline）

- 用修复后路径重跑 Strategic 信用 MC（N≥2000）与 Certainty Bridge  
- Historical Vintage 在正确 −22%/年下的 cohort 表  
- `reproduce.py` 黄金结果是否受 GPU decay 影响（基准 L4 merchant 会变）  
- EconCap 校准、Access EV 改用 CE  

---

## 6 结论

**P0-0 已修复。** GPU 年化衰减不得再按月指数。

**修复后主结论：**

1. **C1 相对真正 −6%/年 C2 的锁价溢价约 $0.9B**（非 $5B）；温和 step-down 的 L4-C 仍可 **+$3.8B** 并高于 L3。  
2. **Merchant Forward 在 $7.80 中位租金、−22%/年下约 +$0.08B**——接近盈亏平衡，而非 −$3B；Spot 仍弱；Dedicated 可持续租金下可为正。  
3. **Contracted/Strategic 在 bulk 情景下仍优于 L3**，优势来自锁价+利用率保底+可融资性，而非频率 bug 制造的假性崩盘。  
4. **框架六维与 demand-led GPU 原则不变**；变的是度量诚实性。

$$\boxed{\text{Annual parameters must not be applied as monthly exponents.}}$$

---

## 附录 — 修复前后对照（核心）

| 指标 | v5.1（有 bug） | v5.2（已修） |
|---|---:|---:|
| C2 Y1–Y5 均价路径 | 6.81→…→0.35 | 9.36→…→7.31 |
| C2 NPV | −$0.35B | **+$3.84B** |
| C1−C2 Δ | +$5.11B | **+$0.92B** |
| Merchant $7.80 NPV | −$3.17B | **+$0.08B** |
| Merchant BE (NPV=0) | ~$30 | **$7.64** |
| L4-S bulk $7.02 | +$3.28B | +$3.28B（decay=0 不变） |

**模型**：`https://github.com/tonyhuang23-sys/aidc-optimizer`  
**利益声明 / AI 披露**：同前；v5.2 数字以 `research_outputs/v5_2_freq_fix/` 为准。
