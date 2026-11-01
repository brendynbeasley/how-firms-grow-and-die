# Technical notes

This is the technical companion to the [README](README.md). It covers the original study, the data, the rules,
every test statistic and how to reproduce the results. All tables are in [results/FINDINGS.md](results/FINDINGS.md).

## The original study

Tor Jakob Klette and Samuel Kortum, "Innovating Firms and Aggregate Innovation," *Journal of Political Economy*
112(5), 2004, pp. 986–1018. A theory paper with no data of its own. A firm is a portfolio of $`n`$ product lines;
it adds lines at Poisson rate $`\lambda n`$ through R&D and loses each line at rate $`\mu`$ to rivals. Its exact
predictions, the paper's headline results, are R&D proportional to revenue, $`R = n\,c(\lambda)`$ (p. 993), Gibrat's
law in expectation (eq. 11, p. 996), growth variance $`(\lambda+\mu)/n_0`$ per unit time for small horizons (eq. 12
and note 10, p. 997), exit within $`t`$ with probability $`p_0(t;1)^{n}`$ (p. 995), an exit hazard by age that starts
at $`\mu`$ and falls toward $`\mu-\lambda`$ (eq. 8, p. 995), and a logarithmic steady-state size distribution
(eq. 17, p. 1001). Note 11 concedes that growth variance falls less steeply than $`1/n`$ in the data; note 9 concedes
an independent age effect on exit.

## Headline results

| Prediction | Model | US data | Source |
|---|---|---|---|
| Elasticity of R&D to revenue, revenue ≥ $10M | 1 | 0.80 (s.e. 0.013) | SEC, 15,707 firm-years |
| Same, revenue ≥ $1B | 1 | 0.97 (0.037) | SEC, 4,294 firm-years |
| Same, within firms | 1 | 0.56 (0.027) | SEC, 15,457 firm-years |
| Slope of Δ log R&D on log R&D | 0 | −0.0009 (0.0014) | SEC, 12,854 |
| Growth on log revenue, larger half | 0 | −0.0093 (0.0014) | SEC, 17,611 |
| Elasticity of growth volatility to size | −0.5 | −0.15 (0.005) | SEC, 35,221 |
| Exit, geometric in size | halves every 4.1 employees | power law, elasticity −0.48 | BDS 2015–19 |
| Age effect at given size (death rate age 1 / age 26+) | 1 | 2.5 to 7.2 | BDS 2015–19 |
| Extension: $`\mu`$, 1980s → 2010s | | 0.324 → 0.239 (−26%) | BDS 1978–2023 |

## Data

- **SEC Financial Statement Data Sets**, quarterly zips 2012q1–2026q2 from
  `https://www.sec.gov/files/dera/data/financial-statement-data-sets/{quarter}.zip`, read November 2026.
  `src/build_sec_panel.py` reduces them to `data/raw/sec_firm_years.csv.gz` (70,115 firm-years, 10,165 filers,
  fiscal 2011–2024; revenue and R&D in dollars) and `data/raw/sec_firms.csv` (SIC code, name, country). The zips
  (about 5.5 GB) are not committed.
- **Census Business Dynamics Statistics, 2023 release**, from
  `https://www2.census.gov/programs-surveys/bds/tables/time-series/2023/`, downloaded November 2026:
  `bds2023.csv` (economy), `bds2023_fa.csv` (firm age), `bds2023_ifz.csv` (initial firm size),
  `bds2023_fa_ifz.csv` (age by initial size), `bds2023_sec_fa.csv` (sector by age). Committed in `data/raw/bds/`.
  Initial size is employment in year $`t-1`$. A firm death is a firm all of whose establishments close.

## Method (rules fixed before seeing results)

- **SEC sample.** 10-K filings only; consolidated full-year US-dollar us-gaap values; fiscal year by the SEC
  frames convention; revenue is the largest of five revenue tags, R&D the largest of three R&D tags; the
  as-first-reported value wins. US business address; SIC 6000–6999 dropped; revenue ≥ $10 million (the same floor
  as my Bain (1951) repository). R&D tests use firm-years with positive R&D only, as in Cohen and Klepper (1996).
- **Growth.** $`g_{i,t+1} = \ln(S_{i,t+1}/S_{it})`$ for consecutive fiscal years. The $10 million floor applies to
  year $`t`$ only; $`S_{i,t+1}`$ comes from the full US non-financial panel, so the 529 pairs that end below
  $10 million stay in. Firm-years with no revenue the next year (5,400) cannot be used. Top and bottom 1% trimmed
  (720 of 35,941 pairs); $`\tilde{u}`$ is growth minus the year mean.
- **Estimating equations**, all with standard errors clustered by company:

```math
\begin{aligned}
\ln R_{it} &= \alpha_{s(i)} + \tau_t + \beta \ln S_{it} + \varepsilon_{it}, & H_0:\ \beta = 1 \\
g_{i,t+1} &= \tau_t + \gamma \ln S_{it} + u_{i,t+1}, & H_0:\ \gamma = 0 \\
\ln \lvert \tilde{u}_{i,t+1} \rvert &= a + \delta \ln S_{it} + e_{i,t+1}, & H_0:\ \delta = -\tfrac{1}{2}
\end{aligned}
```

  $`\alpha_{s(i)}`$ is a three-digit SIC effect. The growth equation is run separately on the smaller and larger
  halves of the growth sample split at median log revenue. The within-firm R&D elasticity replaces $`\alpha_{s(i)}`$ with a
  company effect (within transformation). If $`\operatorname{sd}(g \mid S) \propto S^{\delta}`$, the third equation
  identifies $`\delta`$ because $`\ln\lvert\tilde{u}\rvert`$ is log scale plus a size-free term. A second estimate
  regresses log standard deviation on mean log revenue across 20 equal-count size bins, with a 500-draw bootstrap
  over companies (seed 1951), and a third uses IQR/1.349 in each bin.
- **Exit by size.** Death rate $`d_k = D_k/(F_k + D_k)`$, deaths over surviving firms plus deaths, by initial
  size class, age 0 excluded, pooled 2015–2019; cells with suppressed deaths dropped from both numerator and
  denominator (52 of 550). Size is the class's mean employment $`\bar{e}_k`$, total year-$`t`$ employment over firms
  in the initial-size table. The model's law is $`\ln d_k = n_k \ln p`$ with $`n_k \propto \bar{e}_k`$, so log death
  rates are linear in $`\bar{e}_k`$; I allow a free intercept, $`\ln d_k = a + b\,\bar{e}_k`$, which favors the model,
  calibrate it exactly on the two smallest classes and fit it by least squares on all classes with positive deaths,
  against $`\ln d_k = a + b\ln\bar{e}_k`$.
- **Age within size.** The same death rate by age within the five smallest initial-size classes.
- **Extension.** For each year and for all firms and manufacturing (NAICS 31–33), solve two equations in
  $`(\mu, \lambda)`$. With $`P(a)`$ the model's survival function (eq. 7) and a firm of BDS age $`a`$ treated as
  $`a + 0.5`$ years old,

```math
\begin{aligned}
P(a) &= \frac{(\mu - \lambda)\,e^{-(\mu - \lambda)a}}{\mu - \lambda e^{-(\mu - \lambda)a}},
\qquad d_1 = 1 - \frac{P(1.5)}{P(0.5)} \\
E &= \frac{\eta}{M} = \frac{\lambda}{\ln[\mu/(\mu - \lambda)]},
\qquad \eta = \mu - \lambda
\end{aligned}
```

  The second line is the steady state of eq. 15–18. The mass of firms is
  $`M = (\eta/\lambda)\ln(\mu/\eta)`$ per unit mass of product lines and entrants arrive at rate $`\eta`$, so the
  entry rate per firm is $`\eta/M`$. Bounds that need no steady state are $`\mu = -\ln(1 - d_1)`$ when
  $`\lambda = 0`$ and the $`\lambda \to \mu`$ limit of the first equation. Expected life of an entrant is
  $`\ln[\mu/(\mu-\lambda)]/\lambda`$ (p. 995).

## Full test statistics

R&D elasticity, across firms: 0.802 (0.013), 95% CI [0.776, 0.827], t against one = −15.3, 2,356 companies.
Revenue floors of $1M, $100M and $1B give 0.721, 0.866 and 0.970 (t against one −23.9, −7.2, −0.8). By industry
with the $10M floor, drugs and chemicals 0.651, machinery and computers 0.874, electronics 0.833, instruments
0.823, software 0.962 (t = −1.6). Within firms 0.555 (0.027), t = −16.7. Random walk slope −0.0009 (0.0014),
t = −0.6.

Growth on log revenue, smaller half +0.0036 (0.0022), 95% CI [−0.0008, 0.0080]; larger half −0.0093 (0.0014),
t against zero = −6.7. Volatility elasticity, firm level −0.1523 (0.0048), 95% CI [−0.162, −0.143]; untrimmed
−0.1830 (0.0052); binned −0.125, bootstrap s.e. 0.0043, 95% interval [−0.134, −0.117]; IQR version −0.171. The
t statistics against −0.5 exceed 60.

Exit by size: geometric law calibrated on 1–4 and 5–9 employees halves the death rate every 4.11 employees;
least-squares geometric fit RMSE 0.581 log points; power-law elasticity −0.479, RMSE 0.243, eight classes with
positive deaths. Death rate at age 1 over age 26+: 2.49 (1–4 employees), 3.74 (5–9), 4.21 (10–19), 4.50 (20–99),
7.18 (100–499).

Extension, 1980s to 2010s averages: all firms $`\mu`$ 0.324 to 0.239 (−26.2%), bounds −22.1% and −27.2%,
entrants' share 8.8% to 6.8%; manufacturing $`\mu`$ 0.247 to 0.194 (−21.6%), entrants' share 9.5% to 2.7%. The
BDS accounting gap (change in firms minus births plus deaths) is 1.4% and 1.2% of firms in 2022 and 2023, the
largest in the series.

## Reproducing the results

```bash
pip install -r requirements.txt
python src/firm_growth_and_rd.py      # SEC tests, about 10 seconds
python src/exit_and_destruction.py    # BDS tests and the extension, a few seconds
```

Both run offline from the committed data. To rebuild the SEC panel from the quarterly zips (downloads about
5.5 GB, 20 to 40 minutes), run `python src/build_sec_panel.py` first.

## Repository layout

| Path | What it is |
|---|---|
| `src/build_sec_panel.py` | Builds the SEC firm-year panel from the quarterly data sets |
| `src/firm_growth_and_rd.py` | R&D, Gibrat and volatility tests, named-company table, volatility figure |
| `src/exit_and_destruction.py` | Exit by size and age, creative-destruction extension, two figures |
| `data/raw/` | Committed SEC panel and BDS tables |
| `results/` | Every CSV and PNG cited in the README |

## References

- Akcigit, U. & Ates, S. T. (2023). What happened to US business dynamism? *Journal of Political Economy* 131(8).
- Akcigit, U. & Kerr, W. R. (2018). Growth through heterogeneous innovations. *Journal of Political Economy* 126(4).
- Cohen, W. M. & Klepper, S. (1996). A reprise of size and R&D. *Economic Journal* 106(437).
- Hymer, S. & Pashigian, P. (1962). Firm size and rate of growth. *Journal of Political Economy* 70(6).
- Klette, T. J. & Kortum, S. (2004). Innovating firms and aggregate innovation. *Journal of Political Economy*
  112(5).
- US Census Bureau. Business Dynamics Statistics, 2023 release.
- US Securities and Exchange Commission. Financial Statement Data Sets.
