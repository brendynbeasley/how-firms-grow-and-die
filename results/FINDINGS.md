# Klette and Kortum (2004) on modern US data: findings

## In plain English

Klette and Kortum modeled a company as a bundle of product lines, each won by research and each lost when a rival
does better. The model makes exact predictions about company size, research spending, growth and exit. This study
checks them against every US public company filing with the SEC from 2011 to 2024 and every US employer firm in the
Census Business Dynamics Statistics from 1978 to 2023.

- **Research does scale with sales among big companies.** For companies with at least $1 billion of revenue, a 1%
  larger company spends 0.97% more on R&D, statistically the same as the model's 1%. Smaller companies, especially
  drug and biotech firms, spend proportionally more. Among the giants the research share still varies widely: Meta
  27%, Merck 28%, Alphabet 14%, Microsoft 12%, Apple 8%.
- **Big companies are steadier, but far less steady than the model says.** The model treats a large company as many
  independent small ones, so the standard deviation of Apple's annual revenue growth should be below 0.01. It was 0.13,
  Nvidia's 0.29 and Pfizer's 0.27. Volatility falls with size at an elasticity of about −0.15, not −0.5.
- **Small firms die more often, but not as fast as the model says, and age matters.** Firms with 1 to 4 employees
  close at 10.2% a year and firms with 20 to 99 at 3.4%, where the model predicts almost zero. At every size,
  one-year-old firms close 2.5 to 7 times as often as firms 26 or more years old.
- **Read through the model, creative destruction slowed by about a quarter.** The rate at which product lines change
  hands fell from 0.32 a year in the 1980s to 0.24 in the 2010s across all firms, and the share of innovation done by
  new manufacturing firms fell from 9.5% to 2.7%.

A narrative version with more examples is in the [README](../README.md); methods and the full list of test
statistics are in [TECHNICAL.md](../TECHNICAL.md).

**Key to the labels below.** *model_value* is the model's prediction for the coefficient. *t_vs_model* is
(estimate − model_value) / std_error. *Revenue* is annual revenue in US dollars from 10-K filings. *Growth* is the
log change in revenue between consecutive fiscal years; *sd_growth* is its standard deviation after removing year
means. *sd_growth_kk* is the median firm's volatility scaled by (revenue / median revenue)^(−1/2), the model's
rule; *sd_growth_fitted* uses the estimated slope instead. *death_rate* is firm deaths / (surviving firms + deaths)
in the Census data. *mu* is the model's rate at which a product line is captured by a rival, per year; *lam* is
incumbents' innovation rate per line; *entrant_share* is (mu − lam) / mu; *mu_if_lambda_zero* and *mu_if_no_entry*
bound mu without the steady-state assumption; *expected_life* is the model's expected life of a new firm in years.

## Tables

### The model's predictions on SEC data (kk_predictions_sec.csv)

| prediction | model_value | estimate | std_error | ci_low | ci_high | t_vs_model | n_obs | n_firms |
|---|---|---|---|---|---|---|---|---|
| R&D elasticity to revenue, across firms (industry and year effects) | 1.00 | 0.8015 | 0.0130 | 0.7760 | 0.8270 | -15.3 | 15,707 | 2,356 |
| R&D elasticity to revenue, within firms over time (firm and year effects) | 1.00 | 0.5555 | 0.0266 | 0.5033 | 0.6076 | -16.7 | 15,457 | 2,106 |
| Change in log R&D on last year's log R&D (random walk) | 0.00 | -0.0009 | 0.0014 | -0.0037 | 0.0020 | -0.6 | 12,854 | 2,055 |
| Growth on log revenue, smaller half of firms (survivors) |  | 0.0036 | 0.0022 | -0.0008 | 0.0080 |  | 17,610 | 3,404 |
| Growth on log revenue, larger half of firms (Gibrat's law) | 0.00 | -0.0093 | 0.0014 | -0.0120 | -0.0066 | -6.7 | 17,611 | 2,368 |
| Elasticity of growth volatility to size, firm level (log absolute deviation on log revenue) | -0.50 | -0.1523 | 0.0048 | -0.1617 | -0.1428 | 71.9 | 35,221 | 5,092 |
| Same, growth not trimmed | -0.50 | -0.1830 | 0.0052 | -0.1932 | -0.1728 | 60.9 | 35,941 | 5,174 |
| Elasticity of growth volatility to size, 20 size bins (bootstrap) | -0.50 | -0.1251 | 0.0043 | -0.1336 | -0.1173 | 87.6 | 35,221 | 5,092 |
| Same, with a tail-robust spread (IQR / 1.349) | -0.50 | -0.1708 |  |  |  |  | 35,221 | 5,092 |

### R&D elasticity by revenue floor and industry (rd_elasticity_robustness.csv)

| sample | model_value | estimate | std_error | ci_low | ci_high | t_vs_model | n_obs | n_firms |
|---|---|---|---|---|---|---|---|---|
| All industries, revenue at least $1M | 1.00 | 0.7207 | 0.0117 | 0.6977 | 0.7436 | -23.9 | 18,632 | 2,831 |
| All industries, revenue at least $10M | 1.00 | 0.8015 | 0.0130 | 0.7760 | 0.8270 | -15.3 | 15,707 | 2,356 |
| All industries, revenue at least $100M | 1.00 | 0.8658 | 0.0187 | 0.8292 | 0.9025 | -7.2 | 10,480 | 1,532 |
| All industries, revenue at least $1,000M | 1.00 | 0.9697 | 0.0372 | 0.8969 | 1.0425 | -0.8 | 4,294 | 585 |
| Drugs and chemicals (SIC 28) | 1.00 | 0.6512 | 0.0306 | 0.5912 | 0.7112 | -11.4 | 3,339 | 616 |
| Machinery and computers (SIC 35) | 1.00 | 0.8739 | 0.0272 | 0.8205 | 0.9272 | -4.6 | 1,353 | 165 |
| Electronics and chips (SIC 36) | 1.00 | 0.8330 | 0.0439 | 0.7471 | 0.9190 | -3.8 | 2,407 | 325 |
| Instruments and medical devices (SIC 38) | 1.00 | 0.8228 | 0.0242 | 0.7753 | 0.8703 | -7.3 | 2,505 | 330 |
| Software and IT services (SIC 737) | 1.00 | 0.9622 | 0.0238 | 0.9155 | 1.0089 | -1.6 | 3,279 | 474 |

### R&D by revenue class, fiscal 2024 (rd_by_size.csv)

Intensities are among companies reporting positive R&D. The reporting share is affected by tagging: several large companies disclose R&D in forms these files do not capture.

| fiscal_year | size_class | companies | share_reporting_rd | median_rd_intensity | pooled_rd_intensity | total_rd_billion |
|---|---|---|---|---|---|---|
| 2024 | $10M-100M | 533 | 0.606 | 0.244 | 0.925 | 12.7 |
| 2024 | $100M-1B | 848 | 0.489 | 0.162 | 0.222 | 40.9 |
| 2024 | $1B-10B | 954 | 0.288 | 0.079 | 0.123 | 112.6 |
| 2024 | $10B-100B | 320 | 0.247 | 0.065 | 0.104 | 261.4 |
| 2024 | $100B+ | 26 | 0.192 | 0.115 | 0.129 | 170.0 |

### Growth by size bin (growth_by_size.csv)

median_revenue is shown in millions of dollars; the CSV holds dollars.

| size_bin | firm_years | median_revenue_million | mean_log_revenue | mean_growth | sd_growth |
|---|---|---|---|---|---|
| 0.000 | 1,762.000 | 15 | 16.50 | 0.061 | 0.384 |
| 1.000 | 1,761.000 | 28 | 17.13 | 0.068 | 0.345 |
| 2.000 | 1,761.000 | 47 | 17.67 | 0.083 | 0.346 |
| 3.000 | 1,761.000 | 78 | 18.16 | 0.086 | 0.309 |
| 4.000 | 1,761.000 | 119 | 18.60 | 0.097 | 0.292 |
| 5.000 | 1,761.000 | 180 | 19.00 | 0.101 | 0.262 |
| 6.000 | 1,761.000 | 260 | 19.37 | 0.097 | 0.251 |
| 7.000 | 1,761.000 | 357 | 19.69 | 0.080 | 0.230 |
| 8.000 | 1,761.000 | 474 | 19.98 | 0.077 | 0.212 |
| 9.000 | 1,761.000 | 630 | 20.26 | 0.069 | 0.212 |
| 10.000 | 1,761.000 | 836 | 20.54 | 0.065 | 0.199 |
| 11.000 | 1,761.000 | 1,088 | 20.80 | 0.057 | 0.196 |
| 12.000 | 1,761.000 | 1,417 | 21.07 | 0.052 | 0.202 |
| 13.000 | 1,761.000 | 1,845 | 21.34 | 0.035 | 0.197 |
| 14.000 | 1,761.000 | 2,455 | 21.62 | 0.048 | 0.166 |
| 15.000 | 1,761.000 | 3,321 | 21.93 | 0.035 | 0.180 |
| 16.000 | 1,761.000 | 4,734 | 22.29 | 0.036 | 0.171 |
| 17.000 | 1,761.000 | 7,304 | 22.72 | 0.030 | 0.167 |
| 18.000 | 1,762.000 | 12,940 | 23.30 | 0.031 | 0.166 |
| 19.000 | 1,760.000 | 37,732 | 24.52 | 0.019 | 0.161 |

### Named companies (named_firms.csv)

Median firm revenue $729 million; volatility at the median 0.205. Revenue and R&D are for the latest fiscal year; revenue_compare_year_billion is fiscal 2014. Blank R&D means no R&D under the three tags read.

| company | cik | fiscal_year | revenue_billion | revenue_compare_year_billion | rd_billion | rd_intensity | years_of_growth | sd_growth_actual | sd_growth_kk | sd_growth_fitted | revenue_vs_median_firm |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Walmart | 104169 | 2024 | 681.0 | 485.7 |  |  | 13 | 0.023 | 0.0067 | 0.087 | 934.5 |
| Amazon | 1018724 | 2024 | 638.0 | 89.0 |  |  | 13 | 0.069 | 0.0069 | 0.088 | 875.4 |
| Apple | 320193 | 2024 | 391.0 | 182.8 | 31.37 | 0.080 | 13 | 0.131 | 0.0089 | 0.094 | 536.6 |
| Alphabet | 1652044 | 2024 | 350.0 | 66.0 | 49.33 | 0.141 | 11 | 0.073 | 0.0094 | 0.095 | 480.3 |
| Microsoft | 789019 | 2024 | 281.7 | 93.6 | 32.49 | 0.115 | 13 | 0.075 | 0.0105 | 0.098 | 386.6 |
| General Motors | 1467858 | 2024 | 187.4 | 155.9 |  |  | 13 | 0.092 | 0.0128 | 0.103 | 257.2 |
| Ford | 37996 | 2024 | 185.0 | 144.1 |  |  | 13 | 0.086 | 0.0129 | 0.103 | 253.9 |
| Meta Platforms | 1326801 | 2024 | 164.5 | 12.5 | 43.87 | 0.267 | 13 | 0.135 | 0.0137 | 0.104 | 225.7 |
| Nvidia | 1045810 | 2024 | 130.5 | 4.7 | 12.91 | 0.099 | 13 | 0.289 | 0.0154 | 0.107 | 179.1 |
| Comcast | 1166691 | 2024 | 123.7 | 68.8 |  |  | 13 | 0.054 | 0.0158 | 0.108 | 169.8 |
| Tesla | 1318605 | 2024 | 97.7 | 3.2 | 4.54 | 0.046 | 12 | 0.216 | 0.0177 | 0.111 | 134.1 |
| Johnson & Johnson | 200406 | 2024 | 88.8 | 74.3 | 17.23 | 0.194 | 13 | 0.058 | 0.0186 | 0.113 | 121.9 |
| Boeing | 12927 | 2024 | 66.5 | 90.8 | 3.81 | 0.057 | 13 | 0.146 | 0.0215 | 0.117 | 91.3 |
| Caterpillar | 18230 | 2024 | 64.8 | 55.2 | 2.11 | 0.033 | 13 | 0.160 | 0.0218 | 0.117 | 88.9 |
| Merck | 310158 | 2024 | 64.2 | 42.2 | 17.94 | 0.280 | 13 | 0.072 | 0.0219 | 0.117 | 88.1 |
| Pfizer | 78003 | 2024 | 63.6 | 49.6 | 10.82 | 0.170 | 13 | 0.274 | 0.0220 | 0.117 | 87.3 |
| Intel | 50863 | 2024 | 53.1 | 55.9 | 16.55 | 0.312 | 13 | 0.095 | 0.0241 | 0.120 | 72.9 |
| Netflix | 1065280 | 2024 | 39.0 | 5.5 | 2.93 | 0.075 | 13 | 0.077 | 0.0281 | 0.125 | 53.5 |
| 3M | 66740 | 2024 | 24.6 | 31.8 |  |  | 13 | 0.091 | 0.0354 | 0.132 | 33.7 |
| iRobot | 1159167 | 2024 | 0.7 | 0.6 | 0.09 | 0.137 | 13 | 0.192 | 0.2124 | 0.207 | 0.9 |

### Exit by initial size, 2015-2019 (exit_by_size.csv)

firms_at_risk_per_year is surviving firms plus deaths, ages 1 and up, per year, in cells whose deaths are not suppressed. At 5,000 employees and above, deaths are zero or suppressed in every year.

| size_class | mean_employment | firms_at_risk_per_year | deaths | death_rate | kk_geometric | kk_geometric_best_fit | power_law_fit |
|---|---|---|---|---|---|---|---|
| 1 to 4 | 2.3 | 2,924,069 | 1,486,008 | 0.1016 | 0.10164 | 0.0366 | 0.1062 |
| 5 to 9 | 6.7 | 1,007,051 | 241,914 | 0.0480 | 0.04804 | 0.0364 | 0.0631 |
| 10 to 19 | 13.6 | 625,616 | 130,016 | 0.0416 | 0.01501 | 0.0362 | 0.0449 |
| 20 to 99 | 39.7 | 533,503 | 91,144 | 0.0342 | 0.00018 | 0.0352 | 0.0269 |
| 100 to 499 | 197.0 | 91,320 | 8,990 | 0.0197 | 0.00000 | 0.0299 | 0.0125 |
| 500 to 999 | 662.6 | 10,334 | 403 | 0.0078 | 0.00000 | 0.0185 | 0.0070 |
| 1000 to 2499 | 1,447.4 | 5,963 | 131 | 0.0044 | 0.00000 | 0.0082 | 0.0048 |
| 2500 to 4999 | 3,117.6 | 1,335 | 16 | 0.0024 | 0.00000 | 0.0015 | 0.0033 |
| 5000 to 9999 | 5,737.9 | 677 | 0 | 0.0000 | 0.00000 | 0.0001 | 0.0025 |
| 10000+ | 26,199.4 | 1,027 | 0 | 0.0000 | 0.00000 | 0.0000 | 0.0012 |

### Exit by age within initial size, 2015-2019 (exit_by_size_and_age.csv)

Death rate; rows are firm age in years, columns initial employment.

| age | 1 to 4 | 5 to 9 | 10 to 19 | 20 to 99 | 100 to 499 |
|---|---|---|---|---|---|
| 1 | 0.190 | 0.119 | 0.108 | 0.090 | 0.087 |
| 2 | 0.139 | 0.086 | 0.080 | 0.073 | 0.058 |
| 3 | 0.122 | 0.076 | 0.073 | 0.064 | 0.051 |
| 4 | 0.112 | 0.066 | 0.065 | 0.058 | 0.043 |
| 5 | 0.105 | 0.062 | 0.059 | 0.058 | 0.043 |
| 6 to 10 | 0.090 | 0.050 | 0.046 | 0.043 | 0.031 |
| 11 to 15 | 0.077 | 0.038 | 0.035 | 0.033 | 0.025 |
| 16 to 20 | 0.073 | 0.033 | 0.029 | 0.027 | 0.020 |
| 21 to 25 | 0.073 | 0.032 | 0.028 | 0.024 | 0.017 |
| 26+ | 0.076 | 0.032 | 0.026 | 0.020 | 0.012 |

### Exit tests (exit_fit.csv)

| test | statistic | value |
|---|---|---|
| Geometric law (model), calibrated on 1-4 and 5-9 employee firms | employees per halving of the death rate | 4.110 |
| Geometric law (model), least squares on all classes | rmse of log death rate | 0.581 |
| Power law, least squares on all classes | elasticity of death rate to employment | -0.479 |
| Power law, least squares on all classes | rmse of log death rate | 0.243 |
| Size classes with positive death rate | count | 8 |
| Age effect within size class 1 to 4 employees | death rate at age 1 / death rate at age 26+ | 2.494 |
| Age effect within size class 10 to 19 employees | death rate at age 1 / death rate at age 26+ | 4.207 |
| Age effect within size class 100 to 499 employees | death rate at age 1 / death rate at age 26+ | 7.178 |
| Age effect within size class 20 to 99 employees | death rate at age 1 / death rate at age 26+ | 4.500 |
| Age effect within size class 5 to 9 employees | death rate at age 1 / death rate at age 26+ | 3.737 |

### Creative destruction by decade (creative_destruction_by_decade.csv)

The 1970s row covers 1978-1979 only; 2020-23 covers four years.

| series | period | years | death_rate_age1 | entry_rate | mu | lam | entrant_share | expected_life | mu_if_lambda_zero | mu_if_no_entry |
|---|---|---|---|---|---|---|---|---|---|---|
| All employer firms | 1970s | 2 | 0.216 | 0.133 | 0.306 | 0.264 | 0.137 | 7.5 | 0.244 | 0.321 |
| All employer firms | 1980s | 10 | 0.222 | 0.120 | 0.324 | 0.296 | 0.088 | 8.4 | 0.252 | 0.334 |
| All employer firms | 1990s | 10 | 0.203 | 0.102 | 0.286 | 0.264 | 0.078 | 9.8 | 0.227 | 0.293 |
| All employer firms | 2000s | 10 | 0.197 | 0.093 | 0.274 | 0.256 | 0.068 | 10.8 | 0.219 | 0.280 |
| All employer firms | 2010s | 10 | 0.178 | 0.082 | 0.239 | 0.223 | 0.068 | 12.3 | 0.196 | 0.243 |
| All employer firms | 2020-23 | 4 | 0.192 | 0.090 | 0.266 | 0.248 | 0.069 | 11.1 | 0.213 | 0.271 |
| Manufacturing | 1970s | 2 | 0.198 | 0.099 | 0.274 | 0.253 | 0.079 | 10.1 | 0.220 | 0.281 |
| Manufacturing | 1980s | 10 | 0.183 | 0.093 | 0.247 | 0.225 | 0.095 | 10.8 | 0.203 | 0.253 |
| Manufacturing | 1990s | 10 | 0.182 | 0.076 | 0.248 | 0.236 | 0.047 | 13.3 | 0.201 | 0.251 |
| Manufacturing | 2000s | 10 | 0.173 | 0.056 | 0.233 | 0.229 | 0.019 | 18.0 | 0.190 | 0.234 |
| Manufacturing | 2010s | 10 | 0.150 | 0.050 | 0.194 | 0.189 | 0.027 | 19.9 | 0.163 | 0.195 |
| Manufacturing | 2020-23 | 4 | 0.155 | 0.053 | 0.202 | 0.197 | 0.025 | 19.1 | 0.169 | 0.203 |

### Change from the 1980s to the 2010s (creative_destruction_change.csv)

| series | measure | pct_change_1980s_to_2010s |
|---|---|---|
| All employer firms | death_rate_age1 | -20.0% |
| All employer firms | entry_rate | -32.0% |
| All employer firms | mu | -26.2% |
| All employer firms | mu_if_lambda_zero | -22.1% |
| All employer firms | mu_if_no_entry | -27.2% |
| All employer firms | lam | -24.6% |
| All employer firms | entrant_share | -22.5% |
| All employer firms | expected_life | +46.8% |
| Manufacturing | death_rate_age1 | -18.0% |
| Manufacturing | entry_rate | -45.8% |
| Manufacturing | mu | -21.6% |
| Manufacturing | mu_if_lambda_zero | -19.5% |
| Manufacturing | mu_if_no_entry | -23.1% |
| Manufacturing | lam | -16.0% |
| Manufacturing | entrant_share | -71.0% |
| Manufacturing | expected_life | +85.0% |

### Creative destruction by year (creative_destruction.csv, main columns)

The CSV also holds expected_life and products_per_firm, the steady-state mean number of lines per firm.

| series | year | death_rate_age1 | entry_rate | mu | lam | entrant_share | mu_if_lambda_zero | mu_if_no_entry |
|---|---|---|---|---|---|---|---|---|
| All employer firms | 1978 | 0.217 | 0.137 | 0.305 | 0.259 | 0.151 | 0.244 | 0.321 |
| All employer firms | 1979 | 0.216 | 0.128 | 0.307 | 0.269 | 0.123 | 0.243 | 0.320 |
| All employer firms | 1980 | 0.231 | 0.118 | 0.344 | 0.322 | 0.065 | 0.262 | 0.353 |
| All employer firms | 1981 | 0.229 | 0.114 | 0.342 | 0.321 | 0.060 | 0.261 | 0.350 |
| All employer firms | 1982 | 0.239 | 0.112 | 0.367 | 0.351 | 0.043 | 0.274 | 0.374 |
| All employer firms | 1983 | 0.211 | 0.119 | 0.298 | 0.266 | 0.108 | 0.237 | 0.308 |
| All employer firms | 1984 | 0.215 | 0.132 | 0.302 | 0.260 | 0.140 | 0.242 | 0.317 |
| All employer firms | 1985 | 0.221 | 0.126 | 0.319 | 0.286 | 0.103 | 0.250 | 0.331 |
| All employer firms | 1986 | 0.218 | 0.124 | 0.311 | 0.278 | 0.107 | 0.245 | 0.323 |
| All employer firms | 1987 | 0.222 | 0.122 | 0.322 | 0.293 | 0.090 | 0.251 | 0.333 |
| All employer firms | 1988 | 0.221 | 0.118 | 0.322 | 0.296 | 0.081 | 0.250 | 0.331 |
| All employer firms | 1989 | 0.216 | 0.115 | 0.310 | 0.284 | 0.084 | 0.243 | 0.319 |
| All employer firms | 1990 | 0.218 | 0.111 | 0.315 | 0.293 | 0.071 | 0.245 | 0.323 |
| All employer firms | 1991 | 0.223 | 0.102 | 0.328 | 0.313 | 0.047 | 0.252 | 0.334 |
| All employer firms | 1992 | 0.210 | 0.099 | 0.300 | 0.283 | 0.058 | 0.236 | 0.306 |
| All employer firms | 1993 | 0.198 | 0.103 | 0.273 | 0.249 | 0.088 | 0.220 | 0.281 |
| All employer firms | 1994 | 0.206 | 0.104 | 0.290 | 0.269 | 0.076 | 0.230 | 0.298 |
| All employer firms | 1995 | 0.197 | 0.106 | 0.272 | 0.245 | 0.099 | 0.220 | 0.280 |
| All employer firms | 1996 | 0.200 | 0.104 | 0.278 | 0.254 | 0.088 | 0.223 | 0.286 |
| All employer firms | 1997 | 0.204 | 0.103 | 0.287 | 0.265 | 0.077 | 0.229 | 0.295 |
| All employer firms | 1998 | 0.187 | 0.098 | 0.253 | 0.228 | 0.098 | 0.207 | 0.260 |
| All employer firms | 1999 | 0.189 | 0.092 | 0.258 | 0.239 | 0.076 | 0.209 | 0.264 |
| All employer firms | 2000 | 0.191 | 0.091 | 0.262 | 0.244 | 0.069 | 0.211 | 0.267 |
| All employer firms | 2001 | 0.194 | 0.089 | 0.270 | 0.254 | 0.057 | 0.216 | 0.275 |
| All employer firms | 2002 | 0.195 | 0.092 | 0.270 | 0.253 | 0.065 | 0.217 | 0.275 |
| All employer firms | 2003 | 0.190 | 0.094 | 0.260 | 0.240 | 0.077 | 0.211 | 0.266 |
| All employer firms | 2004 | 0.190 | 0.099 | 0.258 | 0.233 | 0.096 | 0.210 | 0.265 |
| All employer firms | 2005 | 0.189 | 0.100 | 0.256 | 0.230 | 0.101 | 0.209 | 0.263 |
| All employer firms | 2006 | 0.194 | 0.103 | 0.266 | 0.240 | 0.098 | 0.215 | 0.273 |
| All employer firms | 2007 | 0.202 | 0.096 | 0.284 | 0.266 | 0.063 | 0.225 | 0.289 |
| All employer firms | 2008 | 0.209 | 0.090 | 0.300 | 0.288 | 0.041 | 0.235 | 0.305 |
| All employer firms | 2009 | 0.216 | 0.078 | 0.319 | 0.313 | 0.018 | 0.244 | 0.321 |
| All employer firms | 2010 | 0.196 | 0.076 | 0.275 | 0.267 | 0.029 | 0.218 | 0.278 |
| All employer firms | 2011 | 0.195 | 0.079 | 0.273 | 0.263 | 0.036 | 0.217 | 0.276 |
| All employer firms | 2012 | 0.179 | 0.081 | 0.240 | 0.225 | 0.062 | 0.197 | 0.244 |
| All employer firms | 2013 | 0.178 | 0.080 | 0.239 | 0.225 | 0.060 | 0.196 | 0.243 |
| All employer firms | 2014 | 0.177 | 0.081 | 0.237 | 0.222 | 0.064 | 0.195 | 0.241 |
| All employer firms | 2015 | 0.170 | 0.082 | 0.224 | 0.206 | 0.080 | 0.187 | 0.229 |
| All employer firms | 2016 | 0.172 | 0.085 | 0.227 | 0.207 | 0.087 | 0.189 | 0.232 |
| All employer firms | 2017 | 0.172 | 0.084 | 0.228 | 0.209 | 0.083 | 0.189 | 0.232 |
| All employer firms | 2018 | 0.169 | 0.084 | 0.222 | 0.202 | 0.089 | 0.185 | 0.227 |
| All employer firms | 2019 | 0.171 | 0.085 | 0.224 | 0.204 | 0.091 | 0.187 | 0.229 |
| All employer firms | 2020 | 0.173 | 0.085 | 0.229 | 0.209 | 0.087 | 0.190 | 0.234 |
| All employer firms | 2021 | 0.173 | 0.090 | 0.227 | 0.203 | 0.104 | 0.190 | 0.233 |
| All employer firms | 2022 | 0.212 | 0.094 | 0.305 | 0.292 | 0.045 | 0.238 | 0.310 |
| All employer firms | 2023 | 0.210 | 0.091 | 0.302 | 0.290 | 0.041 | 0.236 | 0.306 |
| Manufacturing | 1978 | 0.197 | 0.104 | 0.271 | 0.245 | 0.096 | 0.219 | 0.279 |
| Manufacturing | 1979 | 0.199 | 0.093 | 0.277 | 0.260 | 0.061 | 0.221 | 0.283 |
| Manufacturing | 1980 | 0.185 | 0.096 | 0.249 | 0.225 | 0.096 | 0.204 | 0.255 |
| Manufacturing | 1981 | 0.180 | 0.095 | 0.240 | 0.215 | 0.105 | 0.199 | 0.247 |
| Manufacturing | 1982 | 0.188 | 0.089 | 0.258 | 0.241 | 0.066 | 0.209 | 0.263 |
| Manufacturing | 1983 | 0.192 | 0.085 | 0.266 | 0.252 | 0.052 | 0.213 | 0.270 |
| Manufacturing | 1984 | 0.186 | 0.096 | 0.251 | 0.228 | 0.093 | 0.205 | 0.258 |
| Manufacturing | 1985 | 0.155 | 0.096 | 0.194 | 0.156 | 0.198 | 0.169 | 0.202 |
| Manufacturing | 1986 | 0.183 | 0.094 | 0.247 | 0.224 | 0.091 | 0.203 | 0.253 |
| Manufacturing | 1987 | 0.187 | 0.094 | 0.254 | 0.233 | 0.084 | 0.207 | 0.260 |
| Manufacturing | 1988 | 0.198 | 0.093 | 0.276 | 0.258 | 0.062 | 0.220 | 0.281 |
| Manufacturing | 1989 | 0.178 | 0.092 | 0.237 | 0.214 | 0.098 | 0.196 | 0.243 |
| Manufacturing | 1990 | 0.176 | 0.088 | 0.233 | 0.212 | 0.089 | 0.193 | 0.238 |
| Manufacturing | 1991 | 0.196 | 0.077 | 0.275 | 0.267 | 0.031 | 0.218 | 0.278 |
| Manufacturing | 1992 | 0.198 | 0.074 | 0.280 | 0.273 | 0.025 | 0.221 | 0.282 |
| Manufacturing | 1993 | 0.183 | 0.079 | 0.249 | 0.236 | 0.051 | 0.202 | 0.252 |
| Manufacturing | 1994 | 0.188 | 0.079 | 0.258 | 0.246 | 0.044 | 0.208 | 0.261 |
| Manufacturing | 1995 | 0.177 | 0.079 | 0.238 | 0.224 | 0.060 | 0.195 | 0.241 |
| Manufacturing | 1996 | 0.184 | 0.075 | 0.251 | 0.241 | 0.040 | 0.203 | 0.254 |
| Manufacturing | 1997 | 0.186 | 0.075 | 0.256 | 0.246 | 0.037 | 0.206 | 0.259 |
| Manufacturing | 1998 | 0.160 | 0.071 | 0.207 | 0.193 | 0.067 | 0.174 | 0.210 |
| Manufacturing | 1999 | 0.172 | 0.061 | 0.231 | 0.225 | 0.025 | 0.189 | 0.233 |
| Manufacturing | 2000 | 0.172 | 0.060 | 0.231 | 0.226 | 0.024 | 0.189 | 0.233 |
| Manufacturing | 2001 | 0.175 | 0.059 | 0.236 | 0.231 | 0.020 | 0.192 | 0.237 |
| Manufacturing | 2002 | 0.186 | 0.058 | 0.258 | 0.254 | 0.013 | 0.206 | 0.259 |
| Manufacturing | 2003 | 0.177 | 0.054 | 0.241 | 0.238 | 0.012 | 0.195 | 0.242 |
| Manufacturing | 2004 | 0.171 | 0.057 | 0.228 | 0.224 | 0.019 | 0.187 | 0.229 |
| Manufacturing | 2005 | 0.167 | 0.055 | 0.221 | 0.217 | 0.020 | 0.182 | 0.222 |
| Manufacturing | 2006 | 0.161 | 0.059 | 0.211 | 0.204 | 0.032 | 0.176 | 0.213 |
| Manufacturing | 2007 | 0.158 | 0.057 | 0.205 | 0.199 | 0.030 | 0.172 | 0.207 |
| Manufacturing | 2008 | 0.169 | 0.053 | 0.226 | 0.222 | 0.015 | 0.185 | 0.227 |
| Manufacturing | 2009 | 0.195 | 0.045 | 0.275 | 0.275 | 0.002 | 0.217 | 0.276 |
| Manufacturing | 2010 | 0.184 | 0.043 | 0.253 | 0.252 | 0.003 | 0.203 | 0.253 |
| Manufacturing | 2011 | 0.162 | 0.049 | 0.213 | 0.210 | 0.013 | 0.176 | 0.214 |
| Manufacturing | 2012 | 0.145 | 0.051 | 0.185 | 0.179 | 0.029 | 0.157 | 0.186 |
| Manufacturing | 2013 | 0.150 | 0.049 | 0.194 | 0.190 | 0.020 | 0.163 | 0.194 |
| Manufacturing | 2014 | 0.152 | 0.051 | 0.196 | 0.191 | 0.023 | 0.165 | 0.197 |
| Manufacturing | 2015 | 0.143 | 0.053 | 0.180 | 0.174 | 0.038 | 0.154 | 0.182 |
| Manufacturing | 2016 | 0.141 | 0.054 | 0.177 | 0.170 | 0.042 | 0.152 | 0.178 |
| Manufacturing | 2017 | 0.146 | 0.053 | 0.186 | 0.179 | 0.034 | 0.158 | 0.187 |
| Manufacturing | 2018 | 0.141 | 0.051 | 0.178 | 0.172 | 0.035 | 0.152 | 0.179 |
| Manufacturing | 2019 | 0.139 | 0.051 | 0.175 | 0.169 | 0.036 | 0.150 | 0.176 |
| Manufacturing | 2020 | 0.143 | 0.050 | 0.181 | 0.176 | 0.029 | 0.154 | 0.182 |
| Manufacturing | 2021 | 0.142 | 0.051 | 0.180 | 0.174 | 0.033 | 0.154 | 0.181 |
| Manufacturing | 2022 | 0.165 | 0.057 | 0.217 | 0.212 | 0.025 | 0.180 | 0.218 |
| Manufacturing | 2023 | 0.170 | 0.052 | 0.228 | 0.225 | 0.013 | 0.187 | 0.229 |

### Census firm-count accounting (bds_accounting_check.csv)

gap = change_in_firms minus births_minus_deaths.

| year | firms | change_in_firms | births | deaths | births_minus_deaths | gap | gap_share_of_firms |
|---|---|---|---|---|---|---|---|
| 1979 | 3,692,635 | 132,317 | 473,471 | 330,913 | 142,558 | -10,241 | -0.0028 |
| 1980 | 3,739,767 | 47,132 | 439,667 | 369,565 | 70,102 | -22,970 | -0.0061 |
| 1981 | 3,768,498 | 28,731 | 430,100 | 377,392 | 52,708 | -23,977 | -0.0064 |
| 1982 | 3,741,859 | -26,639 | 418,627 | 406,493 | 12,134 | -38,773 | -0.0104 |
| 1983 | 3,830,757 | 88,898 | 456,610 | 363,000 | 93,610 | -4,712 | -0.0012 |
| 1984 | 4,001,390 | 170,633 | 529,584 | 364,750 | 164,834 | 5,799 | 0.0014 |
| 1985 | 4,073,155 | 71,765 | 512,439 | 431,677 | 80,762 | -8,997 | -0.0022 |
| 1986 | 4,158,219 | 85,064 | 517,516 | 414,722 | 102,794 | -17,730 | -0.0043 |
| 1987 | 4,223,952 | 65,733 | 513,574 | 436,466 | 77,108 | -11,375 | -0.0027 |
| 1988 | 4,308,236 | 84,284 | 507,091 | 425,403 | 81,688 | 2,596 | 0.0006 |
| 1989 | 4,382,013 | 73,777 | 502,558 | 429,504 | 73,054 | 723 | 0.0002 |
| 1990 | 4,445,528 | 63,515 | 493,080 | 433,898 | 59,182 | 4,333 | 0.0010 |
| 1991 | 4,412,581 | -32,947 | 450,750 | 453,798 | -3,048 | -29,899 | -0.0068 |
| 1992 | 4,413,841 | 1,260 | 438,701 | 415,356 | 23,345 | -22,085 | -0.0050 |
| 1993 | 4,495,611 | 81,770 | 461,135 | 386,357 | 74,778 | 6,992 | 0.0016 |
| 1994 | 4,575,281 | 79,670 | 475,989 | 398,875 | 77,114 | 2,556 | 0.0006 |
| 1995 | 4,674,006 | 98,725 | 495,030 | 398,645 | 96,385 | 2,340 | 0.0005 |
| 1996 | 4,721,540 | 47,534 | 493,289 | 416,575 | 76,714 | -29,180 | -0.0062 |
| 1997 | 4,776,424 | 54,884 | 494,483 | 434,203 | 60,280 | -5,396 | -0.0011 |
| 1998 | 4,853,548 | 77,124 | 477,206 | 400,489 | 76,717 | 407 | 0.0001 |
| 1999 | 4,883,018 | 29,470 | 451,218 | 408,681 | 42,537 | -13,067 | -0.0027 |
| 2000 | 4,902,719 | 19,701 | 446,204 | 405,016 | 41,188 | -21,487 | -0.0044 |
| 2001 | 4,912,908 | 10,189 | 436,993 | 408,243 | 28,750 | -18,561 | -0.0038 |
| 2002 | 4,929,332 | 16,424 | 455,162 | 424,299 | 30,863 | -14,439 | -0.0029 |
| 2003 | 4,991,927 | 62,595 | 467,532 | 416,561 | 50,971 | 11,624 | 0.0023 |
| 2004 | 5,084,924 | 92,997 | 505,056 | 414,338 | 90,718 | 2,279 | 0.0004 |
| 2005 | 5,166,062 | 81,138 | 518,727 | 430,425 | 88,302 | -7,164 | -0.0014 |
| 2006 | 5,254,916 | 88,854 | 541,317 | 460,485 | 80,832 | 8,022 | 0.0015 |
| 2007 | 5,291,526 | 36,610 | 509,517 | 467,189 | 42,328 | -5,718 | -0.0011 |
| 2008 | 5,230,315 | -61,211 | 471,285 | 495,527 | -24,242 | -36,969 | -0.0071 |
| 2009 | 5,088,072 | -142,243 | 395,235 | 511,115 | -115,880 | -26,363 | -0.0052 |
| 2010 | 5,016,353 | -71,719 | 379,145 | 440,076 | -60,931 | -10,788 | -0.0022 |
| 2011 | 4,993,099 | -23,254 | 395,680 | 420,190 | -24,510 | 1,256 | 0.0003 |
| 2012 | 5,039,673 | 46,574 | 408,546 | 379,599 | 28,947 | 17,627 | 0.0035 |
| 2013 | 5,064,208 | 24,535 | 405,350 | 384,319 | 21,031 | 3,504 | 0.0007 |
| 2014 | 5,100,719 | 36,511 | 411,948 | 381,685 | 30,263 | 6,248 | 0.0012 |
| 2015 | 5,146,908 | 46,189 | 421,155 | 382,811 | 38,344 | 7,845 | 0.0015 |
| 2016 | 5,212,130 | 65,222 | 442,414 | 384,550 | 57,864 | 7,358 | 0.0014 |
| 2017 | 5,246,978 | 34,848 | 439,859 | 392,222 | 47,637 | -12,789 | -0.0024 |
| 2018 | 5,281,916 | 34,938 | 442,078 | 394,215 | 47,863 | -12,925 | -0.0024 |
| 2019 | 5,330,349 | 48,433 | 453,027 | 404,886 | 48,141 | 292 | 0.0001 |
| 2020 | 5,335,214 | 4,865 | 455,725 | 416,962 | 38,763 | -33,898 | -0.0064 |
| 2021 | 5,391,471 | 56,257 | 485,256 | 421,453 | 63,803 | -7,546 | -0.0014 |
| 2022 | 5,541,603 | 150,132 | 521,312 | 450,039 | 71,273 | 78,859 | 0.0142 |
| 2023 | 5,593,727 | 52,124 | 508,777 | 523,958 | -15,181 | 67,305 | 0.0120 |
