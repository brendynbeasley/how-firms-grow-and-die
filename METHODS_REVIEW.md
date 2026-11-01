# Methods review: Klette and Kortum (2004)

- **Paper.** Klette, Tor Jakob, and Samuel Kortum. 2004. "Innovating Firms and Aggregate Innovation." *Journal of
  Political Economy* 112(5): 986–1018.
- **Statistical focus.** The firm-level predictions that carry the paper's claim to "confront firm-level evidence":
  R&D intensity independent of firm size (R(n) = n c(λ), p. 993), and the growth-variance result
  Var[G | n0] proportional to 1/n0 (eq. 12, p. 997), together with the exit law p0(t;1)^n (p. 995).
- **Review standard.** Internal consistency of the formal results, explicitness of assumptions, and testability of
  predictions; for the empirical regularities the paper relies on, standard reporting of sources, magnitudes and
  uncertainty.
- **What was read.** The full published text, pp. 986–1018, including Appendices A to D and the references, from
  the PDF of the journal version posted on Samuel Kortum's Yale faculty website. No data or code accompany the paper, and
  none of the empirical studies it cites were re-read for this review except as quoted in the paper itself.

## Methods summary

The paper is a theory paper. It lists ten "stylized facts" drawn from published firm-level studies (Section II,
with sources in Appendix A) and builds a continuous-time model of multiproduct firms to reproduce them. A firm is
a count n of product lines; it adds lines at Poisson rate I = G(R, n), with G homogeneous of degree one, and loses
each line at rate μ to rivals' innovations. The Bellman equation (eq. 3) has the linear solution V(n) = vn, I(n) =
λn (eq. 4), so innovation and R&D are proportional to size. Firm size follows a linear birth-death process (eqs.
5–6) solved by a probability-generating function (Appendix C), giving survival, size, age and growth moments (eqs.
7–12). Entry closes the industry model and yields a logarithmic steady-state size distribution (eq. 17). A
quality-ladder general equilibrium (Section IIIE) determines μ and the growth rate g = μ ln q̄. Section IV
interprets the stylized facts through the model. There is no estimation, calibration to data, or simulation.

## Statistics extraction table

| Statistic | Value and unit | Source location | What it measures | What it does not establish |
|---|---|---|---|---|
| Innovation intensity | λ = I(n)/n, a rate per year, independent of n | Eq. 4, p. 993 | Optimal arrivals of new lines per existing line | That real firms' innovation rates are size-free; derived from assumed homogeneity of G |
| R&D intensity | R(n)/n = c(λ), share of revenue, independent of n | p. 993 | Research spending as a share of revenue | Any magnitude; c(·) is never parameterized |
| Expected growth | E[G_t \| n0] = exp(−(μ−λ)t) − 1, independent of n0 | Eq. 11, p. 996 | Gibrat's law in expectation, including exits | Conditional-on-survival growth, which falls with size (p. 997) |
| Growth variance | Var[G_t \| n0] = (λ+μ) e^{−(μ−λ)t}[1 − e^{−(μ−λ)t}] / (n0(μ−λ)); limit (λ+μ)/n0 per unit time | Eq. 12 and note 10, p. 997 | Dispersion of growth as a function of initial size | That variance falls as 1/n in data; note 11 says it does not |
| Exit probability | p0(t;1)^n for a firm of size n within t | p. 995 | Survival as n independent one-line units | Any age effect at given size; note 9 concedes data show one |
| Exit hazard by age | μ(μ−λ)/(μ − λe^{−(μ−λ)a}); starts at μ, tends to μ−λ | Eq. 8, pp. 995–996 | Declining hazard with age through size | Hazard levels; no parameter values given |
| Expected life of an entrant | ln[μ/(μ−λ)]/λ, years | p. 995 | Mean age at exit | Any number |
| Size distribution | Logarithmic, P_n ∝ [1/(1+θ)]^n / n, θ = η/λ | Eq. 17 and p. 1001 | Steady-state share of firms with n lines | Fit to observed size distributions; not compared with data |
| Growth rate | g = μ ln q̄ | p. 1005 | Aggregate growth from innovation rate and step size | Magnitudes; note 15 concedes the Jones (1995) scale-effect critique applies |
| Patent elasticity (cited) | 0.3 to 0.6; preferred 0.5 | Appendix A, pp. 1010–1011, quoting Griliches (1990) and Blundell, Griffith and Windmeijer (2002) | Elasticity of patents with respect to R&D | Anything about the model's patent prediction, which is stated qualitatively |
| Persistence (cited) | About 50% of business-unit R&D intensity variance from firm effects | Appendix A, p. 1011, quoting Scott (1984) | Persistence of R&D intensity | Source, sample or uncertainty, none reported here |
| Random-walk error variance (cited) | About 1.5% relative to between-firm variance | Appendix A, p. 1011, quoting Hall et al. (1986) | Within-firm variability of log R&D | Its confidence interval or sample |

## Research design

Formal model with comparative statics and closed-form stochastic results. The design choice that carries every
firm-level prediction is assumption (iv) on p. 991, homogeneity of degree one of G in R and n, combined with
independence of line losses across a firm's products. Both are stated explicitly.

## Sampling strategy

Not applicable. The paper collects no data. The stylized facts are selected from surveys (Griliches, Cohen,
Sutton, Caves) using a stated rule: findings are included only if "robust and economically significant" (p. 988).
How robustness was judged is not documented.

## Sample size

Not applicable for the paper. The cited studies' sample sizes are not reported in the paper.

## Inclusion and exclusion criteria

The selection rule for stylized facts is qualitative (p. 988). Cohen and Klepper's caveat that the probability of
reporting R&D rises with size is discussed and set aside as a data artifact (p. 1011), a judgment the reader can
see but not check from the paper.

## Independent and dependent variables

In the model, initial size n0 (product lines, equal to revenue under the normalization) is the state variable;
outcomes are R&D, innovation counts, growth, exit and age. The mapping from n to observable revenue is exact by
construction (each line earns one unit), which is why size can be read as revenue in tests.

## Statistical methods

Probability-generating functions for a linear birth-death process (Appendix C); steady-state solution of the
industry flow equations (Appendix D). The derivations shown are internally consistent with the stated
assumptions. For example, eq. 12's small-t limit (λ+μ)/n0 follows from summing n0 independent unit processes.

## Reported effect sizes

The only effect sizes are exact model implications: an R&D-size elasticity of one, a variance-size elasticity of
minus one, and a zero growth-size slope in expectation. Cited empirical magnitudes appear in Appendix A
(table above).

## Confidence intervals

None reported, as is normal for a theory paper. Cited magnitudes are reported without intervals.

## P-values, if applicable

Not applicable.

## Missing data treatment

Not applicable. The paper does discuss one measurement issue relevant to its facts, that small firms may do
informal R&D they do not report (p. 1010, quoting Griliches 1990).

## Stated limitations

The paper is unusually candid. Note 9 (p. 996) concedes an age effect on exit at given size that the model cannot
produce. Note 11 (p. 997) concedes that growth variance falls less steeply than 1/n, citing Hymer and Pashigian
(1962). Note 15 (p. 1006) concedes the Jones (1995) critique and welfare sensitivity to log preferences. Section
IVA describes its treatment of heterogeneous research intensity as "somewhat tentative and ad hoc" (p. 1007). Section
IVB notes that strategic interaction and aggregate shocks are excluded.

## Interpretation notes

- The model's predictions are exact, so any departure in data is a rejection in principle; the paper's own
  footnotes identify two such departures. These are stated limitations, not errors.
- The paper's evidence base is a set of secondary summaries. It reports no new estimates, so the strength of each
  stylized fact rests on the cited surveys, not on the paper.
- Reporting gap, not an analytical error: the stylized facts are stated without magnitudes, except the few quoted
  in Appendix A, so a reader cannot tell how closely the model is meant to match them.
- R&D intensity independent of size is an assumption-driven result (homogeneity of G). Its empirical support, as
  the paper notes, holds among R&D performers and may not hold across all firms.
- The modern rerun in this repository is not a reproduction. It applies the model's predictions to SEC filings for
  2011–2024 and Census Business Dynamics Statistics for 1978–2023, and finds the R&D prediction holds among large
  firms, while the variance, exit and age predictions depart from the data in the directions the paper's own notes
  anticipate.

## Unanswered questions

- How sensitive are the firm-level predictions to correlated losses across a firm's lines, which would slow the
  fall of variance and exit with size?
- What parameter values (λ, μ, η, c(·)) would the model need to match US magnitudes for entry, exit and growth?
- Does the logarithmic size distribution fit observed firm size distributions, whose upper tail is often described
  as Pareto?
- How should n be measured empirically (product lines, revenue, patents), and does the choice change the tests?

## Items requiring expert verification

- Whether the cited magnitudes in Appendix A (0.3 to 0.6, 50%, 1.5%) are quoted accurately from Griliches (1990),
  Scott (1984) and Hall et al. (1986); the original studies were not re-read here.
- Whether later structural estimates of this class of model, such as Lentz and Mortensen (2008), resolve the
  variance and age departures within the model's framework.
