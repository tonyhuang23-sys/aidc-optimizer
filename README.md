# AIDC Value-Chain Investment Optimizer

A reproducible, screening-grade evaluation engine for AI data-center (AIDC)
investment decisions. It answers three questions on a unified **100 MW reference
platform** (PUE 1.25 → 80 MW Critical IT):

1. **Which layer of the value chain to invest in?**
   Powered Land → Power-only tolling → Powered Shell → AI-ready Critical IT →
   GPU Hosting → ComputeCo (own-GPU rental) → AI Factory.
2. **At which node to exit?**
3. **Which risks to retain?** (vs. pass through via contracts)

It combines an asset-layer model and a strictly separated financing-layer model
(monthly draws, IDC, sculpted amortization, cash sweep, customer capital,
refinancing), Monte Carlo risk (independent and Gaussian-copula correlated),
and two risk-adjusted decision metrics: a **tail-weighted CE-NPV proxy**
and **IRASR_econ** (incremental CE per unit of screening Economic Capital).

> Current working paper: **v6.1**
> (*A Value-Chain Investment Evaluation Model for AI Infrastructure*).
> Headline All-risk numbers are the **frozen** pack in `research_outputs/v6_1/`
> (N = 10,000, seed = 42, parameter version `v6.1-2026-08-15`, commit `e5fc8d7`).
> That pack has **not** been re-run on the 1.2.1 residual-unsold + 0.75 S-path.
> The v3.3 golden path remains `python reproduce.py check`.

## Quick start

```bash
pip install -r requirements.txt      # numpy==2.2.6, PyYAML==6.0.3, matplotlib==3.10.8

python reproduce.py check             # v3.3 golden regression (exit 0 = pass)
python tests/test_validation.py       # Greenlight / TeraWulf calibration tests
python research_v6_factorial_fixed.py # Table 5 (frequency-fixed 2x2x2)
python research_v6_1.py --stage l3    # live 1.2.1 writes to research_outputs/v6_1_1/
# then m / go / c / s / matched / c4a-d / post. Does not overwrite frozen v6_1/.
```

To evaluate a custom project:

```bash
python -m aidc_optimizer --config configs/alberta.yaml --case critical_it \
    --set dc.ready_rent_kw_mo=180 reference.gen_mw=200
```

## Structure

```
aidc_optimizer/        Python package: core, models, financing, risk, evaluate, report, cli
configs/               Alberta + Texas parameter packs (sanitized public versions)
papers/                Working-paper versions + popular-science rewrite
papers/reviews/        Review notes that drove revisions
reproduce.py           v3.3 reproduction runner + golden check
research_v6_1.py       Headline All-risk / IRASR / C4 / access runner (staged + resume)
research_v6_factorial_fixed.py
research_outputs/v6_1/ Frozen Headline pack (e5fc8d7 + legacy 0.375; do not overwrite)
research_outputs/v6_1_1/ Live 1.2.1 residual-unsold + 0.75 writes (not a published Headline)
expected_outputs/      Committed golden JSON (alberta full, texas baseline)
docs/REPRODUCIBILITY.md
```

## The seven business modes

| case           | layer  | business mode                  | calibration anchor        |
|----------------|--------|--------------------------------|---------------------------|
| dev            | L0     | Powered Land (dev exit)        | Dev IRR / MOIC            |
| power          | L1     | Power-only tolling             | Greenlight–Meta           |
| shell          | L2     | Powered Shell                  | —                         |
| critical_it    | L3     | AI-ready Critical IT lease     | TeraWulf–Anthropic        |
| gpu_hosting    | L3.5   | GPU hosting (client-owned GPU) | —                         |
| compute        | L4     | ComputeCo (own-GPU rental)     | H100/B200 market rentals  |
| ai_factory     | L5     | AI Factory (token/GPU-hr)      | income-equivalent only    |

L4 Headline cases are further split into Merchant / Contracted / Strategic.

## Headline results (v6.1, 2026-08 parameters)

These are screening numbers on the 100 MW reference plant. They are **not**
a forecast for any named project.

- **Default with power and site, no AI tenant: stay at L3.**
  All-risk CE ≈ **+$312 M** (Simulation Bootstrap Interval [280, 343]).
- **Do not treat greenfield full-stack Merchant as the default.**
  Mix-ref $7.80 / GPU-h has a near-breakeven point estimate, but All-risk CE
  ≈ **−$980 M**; IRASR_econ ≈ **−0.59**.
- **Buy GPUs after a financeable contract, not because you own power and a hall.**
  Illustrative bulk $7.02 Contracted CE ≈ **+$1.67 B** (IRASR_econ ≈ **+0.92**);
  Strategic ≈ **+$2.11 B** (IRASR_econ ≈ **+2.37**).
  **$7.02 = 9.36 × 0.75 is an author scenario, not a transacted rate.**
  These Headline N=10,000 figures are the frozen `research_outputs/v6_1`
  pack. The S-path in that pack used a **legacy 0.375 backstop** to offset a
  then double-counting (`1-phys`) engine. Engine **1.2.1** bills residual
  unsold only and the live `research_v6_1.py` default is **0.75**;
  **+$2.11 B is not a 1.2.1 residual-unsold + 0.75 rerun.** Live reruns write
  to `research_outputs/v6_1_1/` and must not replace the frozen pack. L4
  default CAPEX is B200 all-in ~$60k/GPU.
- After the annual-decay frequency fix, the 2×2×2 ranking is
  **contract ≫ vintage > asset stack**. Four of eight cells are NPV-positive.
- Power-only under market-coherent **P1** is an infrastructure-style Equity IRR
  of about **14.1%**. The 28% figure is a used-equipment × premium-contract
  arbitrage case, not the base.

## Buy-GPU rule (plain language)

A take-or-pay contract that locks price and utilization is the first gate.
A hall that can be leased to someone else must charge itself a transfer rent
(CE parity about $10.7–11.8 / GPU-h). Buy only the contracted capacity.
Access is not a seventh asset dimension: if you cannot win the contract,
the fallback is L3, not Merchant GPU.

## Boundary conditions

Screening-grade model: monthly cash flows, straight-line depreciation tax
approximation, USD single currency. It is **not** a bankable underwriting model.
Parameters are a 2026-08 market snapshot and must be updated per project.
Reported intervals are **Simulation Bootstrap Intervals, conditional on model
assumptions** — they measure sampling error inside the model, not parameter
uncertainty.

## License

**Apache License 2.0 with Commons Clause.** See [LICENSE](LICENSE).

This is **not** OSI-approved open source. You may use, study, modify,
and redistribute the code and papers for personal use, academic
research, and internal evaluation, if you keep the copyright and
license notices.

You may **not Sell** the Software. "Sell" includes charging a third
party for a product, hosted service, or consulting whose value
derives substantially from this repository. That requires a separate
commercial license from Tony Huang (`tonyhwong@wntenergy.ca`).
