# Reproducibility Manifest

Everything needed to reproduce **every table** in the working paper
*A Value-Chain Investment Evaluation Model for AI Infrastructure* (v3.3) is in
this repository. One command:

```bash
python reproduce.py run     # recompute all outputs -> expected_outputs/alberta.json
python reproduce.py check   # compare against the committed golden file (exit 0 = pass)
```

## Environment pinning

| Component  | Version      | Reason                                     |
|------------|--------------|--------------------------------------------|
| Python     | >= 3.10      | f-strings, type annotations used           |
| numpy      | == 2.2.6     | `default_rng` stream + normal/lognormal draws must match exactly |
| PyYAML     | == 6.0.3     | config loading                             |
| matplotlib | == 3.10.8    | charts (not used by the golden check)      |

Install: `pip install -r requirements.txt`.

## Seed policy

All stochastic draws use `numpy.random.default_rng(seed)` with **fixed seeds**:

| Block                      | N    | seed | method                       |
|----------------------------|------|------|------------------------------|
| dev / shell / critical_it / hosting / ai_factory loss rates | 1500 | 42 | independent (config `mc` params) |
| L4 baseline / shortage CE-NPV | 800 | 42 | Gaussian-copula correlated MC  |

Because the seeds and numpy version are pinned, the Monte Carlo output is
bit-for-bit deterministic across machines.

## Correlated Monte Carlo (paper §3.4)

The GPU (L4) layer perturbs four parameters jointly via a Gaussian copula:
**rental rate** (σ=0.25), **residual value** (σ=0.35), **purchase price**
(σ=0.15), **utilization** (σ=0.10). The correlation matrix is

```
         rate   resid  capex  util
rate     1.0    0.6    0.25   0.25
resid    0.6    1.0    0.25   0.25
capex    0.25   0.25   1.0    0.25
util     0.25   0.25   0.25   1.0
```

Margins: rate/residual/capex are lognormal; utilization is normal with a 0.2
floor. `gpu.rate_decay` is left at its base value (not in the correlated set).
Implementation: `gpu_correlated_mc()` in `reproduce.py`.

## CE-NPV and IRASR

Lower-tail expected shortfall at the 5th percentile:

    ES⁻₅%(NPV) = E[NPV | NPV ≤ P5]

Certainty-equivalent NPV (λ = 0 / 0.5 / 1):

    CE-NPV = (1 − λ)·E(NPV) + λ·ES⁻₅%(NPV)

Incremental risk-adjusted sponsor return (Peak Equity = max cumulative equity
outflow, i.e. true peak risk capital):

    IRASR = ΔCE-NPV / ΔPeakSponsorEquity

Loss probabilities are reported with the **Wilson 95% confidence interval**,
never as bare 0% / 100%.

## Paper-table mapping

| Paper table / section                    | reproduce.py output key                          |
|------------------------------------------|--------------------------------------------------|
| Table 3 (P1/P2/P3 power coherence)       | `power_coherence`                                |
| Table 4 (baseline seven modes + loss)    | `baseline` + `baseline_risk`                     |
| Table 5 (2×2×2 factorial)                | `factorial_2x2x2`                                |
| Table 6 (λ sensitivity) + §5.4 IRASR     | `risk` + `irasr`                                 |
| §5.5 shortage / L5a corrected            | `shortage` + `l5a_shortage`                      |
| Texas parenthetical (Table 4)            | `expected_outputs/texas.json` (`--texas`)        |

## 2×2×2 factorial parameterization

| dimension | level       | overrides |
|-----------|-------------|-----------|
| Asset     | Greenfield  | `power.capex_per_kw=1150`, `dc.ready_capex_per_kw=8000` |
|           | Brownfield  | `power.capex_per_kw=150`,  `dc.ready_capex_per_kw=5500` |
| Contract  | Merchant    | `gpu.rate_decay=-0.22`, `gpu.utilization=0.75` |
|           | Contracted  | `gpu.rate_decay=-0.08`, `gpu.utilization=0.95` |
| Vintage   | New         | `gpu.capex_per_kw_it=32000`, `gpu.residual_pct_at_refresh=0.15` |
|           | Used        | `gpu.capex_per_kw_it=12000`, `gpu.residual_pct_at_refresh=0.30` |

Rental rate scheme ($/IT-kW-hr): new × merchant 3.0, new × contracted 3.2,
used × merchant 1.9, used × contracted 2.0.

## Golden-check tolerances

`reproduce.py check` compares every numeric field against the committed golden
file with tolerances defined in `TOL` (e.g. NPV ±1 $M, IRR ±0.1 pp,
CE-NPV ±5 $M). A strict identity check on all text/string fields is also made.
