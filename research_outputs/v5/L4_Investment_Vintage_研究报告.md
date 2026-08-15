# L4 Investment Vintage 研究报告

## 1. 核心命题

Merchant Compute 的回报是 **Investment-Vintage-dependent** 的，而不是天然永远为负。
Historical Realized Return（过去 cohort 的实际/估算回报）与 Forward New-Investment Return
（今天新进入的前瞻回报）必须严格分离。

$$\mathrm{Historical\ Winner} \neq \mathrm{Forward\ Winner}$$

## 2. Merchant Cohort 结果（筛选级估算）

| Vintage | 采购$/GPU | CAPEX $/IT-kW | 入场租金 | NPV $M | Project IRR | Peak $M | 置信度 |
|---|---:|---:|---:|---:|---:|---:|---:|
| H100-2023 | 40,300 | 31,434 | 4.50 | -2,156 | -14.1% | 4,313 | 0.55 |
| H100-2024 | 38,700 | 30,186 | 3.80 | -2,326 | -17.0% | 4,417 | 0.55 |
| H100-2025 | 35,000 | 27,300 | 2.80 | -2,863 | -27.2% | 4,884 | 0.60 |
| H100-2026F | 32,000 | 24,960 | 3.20 | -2,942 | -30.0% | 4,807 | 0.65 |
| B200-2026F | 60,000 | 31,980 | 7.80 | -3,173 | -28.4% | 5,491 | 0.70 |

### 解读

1. **早期 H100 vintage（2023/2024）** 在较低采购成本 + scarcity 租金路径下，Merchant NPV 显著好于 2026 Forward。
2. **H100-2026 Forward 与 B200-2026 Forward** 在 -22%/年衰减假设下仍深负——这是 *Forward Return*，不能用历史 cohort 外推。
3. 置信度 0.55–0.70：采购锚点来自 IREN SEC 与公开报价，租金路径为结构假设，不是完整 realized cashflow 回测。

## 3. 行业四阶段演化

| Phase | 特征 | 主导模式 |
|---|---|---|
| 1 Early Scarcity | 低进入成本、租金上行 | Merchant Alpha |
| 2 High Entry Cost | 高 CAPEX + 不确定未来租金 | Merchant Risk↑ |
| 3 Contractualization | 客户合同 → 可融资 | Contracted |
| 4 Strategic Ecosystem | Customer+Vendor+Capital | Strategic Neocloud |

## 4. 结论改写

> Merchant GPU 不是天然不能盈利，而是高度依赖 Investment Vintage 与市场周期。
> 过去某些低成本买卡、随后租金上行的 cohort 可能获得高回报；
> 但当前新进入者的 Forward Return 可能显著恶化。
> Contracted / Strategic 模式的本质，是把对未来租金、利用率和融资市场的押注
> 逐步转换为可锁定、可融资的合同现金流。
