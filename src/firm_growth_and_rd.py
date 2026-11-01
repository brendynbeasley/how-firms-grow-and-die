"""Klette and Kortum (2004) on US public companies: R&D, size and the volatility of growth.

The model treats a firm as a bundle of n product lines, each won by innovation and lost to a
rival's innovation, and it makes three sharp predictions about firms that this script checks on
every US company filing a 10-K with the SEC, fiscal 2011-2024:

  1. R&D spending is proportional to revenue (R = n c(lambda)), so the elasticity of R&D with
     respect to revenue is exactly 1 and log R&D follows a random walk.
  2. Expected growth does not depend on size (Gibrat's law), at least for larger firms.
  3. The variance of growth is inversely proportional to size, Var(G) = (lambda + mu) / n per
     unit of time, so the standard deviation of growth falls with size at an elasticity of -1/2.

Input (committed; built by src/build_sec_panel.py):
    data/raw/sec_firm_years.csv.gz, data/raw/sec_firms.csv
Writes:
    results/kk_predictions_sec.csv    each prediction, the model's value, the estimate, its CI
    results/rd_by_size.csv            R&D reporting and intensity by revenue class, fiscal 2024
    results/rd_elasticity_robustness.csv   the R&D elasticity by revenue floor and by industry
    results/growth_by_size.csv        mean and standard deviation of growth by size bin
    results/named_firms.csv           well-known companies: size, R&D intensity, volatility
    results/growth_volatility.png     the volatility-size relationship against the model's line

Usage (from the repository root):
    python src/firm_growth_and_rd.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results"

MIN_REVENUE = 10e6       # $10M; the model has no pre-revenue firms (same floor as the Bain repo)
FINANCE_SIC = (6000, 6999)   # banks, insurers, REITs: "revenue" is not sales of goods
N_BINS = 20              # size bins for the volatility plot
TRIM = 0.01              # drop the top and bottom 1% of growth rates (mergers, spin-offs)
N_BOOT = 500             # firm-level bootstrap draws for the binned slope
SEED = 1951
COMPARE_YEAR = 2014      # a decade before the last year, for the named-company table
KK_SLOPE = -0.5          # model: sd of growth proportional to size^(-1/2), eq. (12)
SIZE_CLASSES = [10e6, 100e6, 1e9, 10e9, 100e9, np.inf]
SIZE_LABELS = ["$10M-100M", "$100M-1B", "$1B-10B", "$10B-100B", "$100B+"]
RD_FLOORS = [1e6, 10e6, 100e6, 1e9]   # revenue floors for the R&D elasticity robustness check
RD_INDUSTRIES = {"Drugs and chemicals (SIC 28)": (2800, 2899),
                 "Machinery and computers (SIC 35)": (3500, 3599),
                 "Electronics and chips (SIC 36)": (3600, 3699),
                 "Instruments and medical devices (SIC 38)": (3800, 3899),
                 "Software and IT services (SIC 737)": (7370, 7379)}

# Well-known companies, by SEC central index key (CIK)
NAMED = {320193: "Apple", 1018724: "Amazon", 1652044: "Alphabet", 789019: "Microsoft",
         1326801: "Meta Platforms", 1045810: "Nvidia", 50863: "Intel", 200406: "Johnson & Johnson",
         310158: "Merck", 78003: "Pfizer", 37996: "Ford", 1467858: "General Motors",
         12927: "Boeing", 18230: "Caterpillar", 1318605: "Tesla", 1065280: "Netflix",
         1159167: "iRobot", 1166691: "Comcast", 104169: "Walmart", 66740: "3M"}


def load():
    panel = pd.read_csv(RAW / "sec_firm_years.csv.gz")
    firms = pd.read_csv(RAW / "sec_firms.csv")
    d = panel.merge(firms, on="cik", how="left")
    raw = d.copy()
    print(f"Loaded {len(d):,} firm-years with revenue ({d['cik'].nunique():,} filers), "
          f"fiscal {d['year'].min()}-{d['year'].max()}")
    steps = [("business address outside the US", lambda x: x["countryba"] != "US"),
             ("missing SIC code", lambda x: x["sic"].isna()),
             ("finance, insurance and real estate (SIC 6000-6999)",
              lambda x: x["sic"].between(*FINANCE_SIC)),
             (f"revenue below ${MIN_REVENUE / 1e6:.0f}M", lambda x: x["revenue"] < MIN_REVENUE)]
    for why, rule in steps:
        drop = rule(d)
        print(f"  dropped {int(drop.sum()):,} firm-years: {why}")
        d = d[~drop]
    d = d.copy()
    d["sic3"] = (d["sic"] // 10).astype(int)
    d["lrev"] = np.log(d["revenue"])
    print(f"  kept {len(d):,} firm-years from {d['cik'].nunique():,} companies")
    return d, raw


def rd_tests(d):
    """Prediction 1: R&D proportional to revenue; log R&D a random walk."""
    r = d[d["rd"] > 0].copy()
    r["lrd"] = np.log(r["rd"])
    print(f"\nR&D sample: {len(r):,} firm-years with positive R&D, {r['cik'].nunique():,} companies "
          f"({len(d) - len(r):,} firm-years report no R&D)")
    rows = []
    m = smf.ols("lrd ~ lrev + C(year) + C(sic3)", r).fit(cov_type="cluster",
                                                          cov_kwds={"groups": r["cik"]})
    rows.append(row("R&D elasticity to revenue, across firms (industry and year effects)",
                    1.0, m, "lrev", len(r), r["cik"].nunique()))

    # Within firms: demean by firm, keep year effects
    w = r.copy()
    yd = pd.get_dummies(w["year"], prefix="y", drop_first=True, dtype=float)
    w = pd.concat([w, yd], axis=1)
    cols = ["lrd", "lrev"] + list(yd.columns)
    w[cols] = w[cols] - w.groupby("cik")[cols].transform("mean")
    w = w[w.groupby("cik")["cik"].transform("size") > 1]
    m = smf.ols("lrd ~ lrev + " + " + ".join(yd.columns) + " - 1", w).fit(
        cov_type="cluster", cov_kwds={"groups": w["cik"]})
    rows.append(row("R&D elasticity to revenue, within firms over time (firm and year effects)",
                    1.0, m, "lrev", len(w), w["cik"].nunique()))

    # Random walk: change in log R&D on its lagged level
    r = r.sort_values(["cik", "year"])
    r["lag_lrd"] = r.groupby("cik")["lrd"].shift()
    r["lag_year"] = r.groupby("cik")["year"].shift()
    rw = r[r["lag_year"] == r["year"] - 1].copy()
    rw["dlrd"] = rw["lrd"] - rw["lag_lrd"]
    lo, hi = rw["dlrd"].quantile([TRIM, 1 - TRIM])
    rw = rw[rw["dlrd"].between(lo, hi)]
    m = smf.ols("dlrd ~ lag_lrd + C(year)", rw).fit(cov_type="cluster",
                                                    cov_kwds={"groups": rw["cik"]})
    rows.append(row("Change in log R&D on last year's log R&D (random walk)",
                    0.0, m, "lag_lrd", len(rw), rw["cik"].nunique()))
    return rows


def rd_robustness(panel):
    """R&D elasticity across firms for several revenue floors and for the main R&D industries."""
    p = panel[(panel["countryba"] == "US") & panel["sic"].notna()
              & ~panel["sic"].between(*FINANCE_SIC) & (panel["rd"] > 0) & (panel["revenue"] > 0)].copy()
    p["sic3"] = (p["sic"] // 10).astype(int)
    p["lrd"], p["lrev"] = np.log(p["rd"]), np.log(p["revenue"])
    cases = [(f"All industries, revenue at least ${f / 1e6:,.0f}M", p[p["revenue"] >= f])
             for f in RD_FLOORS]
    cases += [(name, p[(p["revenue"] >= MIN_REVENUE) & p["sic"].between(*rng)])
              for name, rng in RD_INDUSTRIES.items()]
    rows = []
    for name, r in cases:
        m = smf.ols("lrd ~ lrev + C(year) + C(sic3)", r).fit(cov_type="cluster",
                                                              cov_kwds={"groups": r["cik"]})
        rows.append(row(name, 1.0, m, "lrev", len(r), r["cik"].nunique()))
    return pd.DataFrame(rows).rename(columns={"prediction": "sample"})


def row(name, model_value, fit, var, n, firms):
    b, se = fit.params[var], fit.bse[var]
    return dict(prediction=name, model_value=model_value, estimate=b, std_error=se,
                ci_low=b - 1.96 * se, ci_high=b + 1.96 * se,
                t_vs_model=(b - model_value) / se, n_obs=n, n_firms=firms)


def rd_by_size(d, year=2024):
    y = d[d["year"] == year].copy()
    y["size_class"] = pd.cut(y["revenue"], SIZE_CLASSES, labels=SIZE_LABELS, right=False)
    out = []
    for lab, g in y.groupby("size_class", observed=True):
        rd = g[g["rd"] > 0]
        out.append(dict(size_class=lab, companies=len(g), share_reporting_rd=len(rd) / len(g),
                        median_rd_intensity=(rd["rd"] / rd["revenue"]).median(),
                        pooled_rd_intensity=rd["rd"].sum() / rd["revenue"].sum(),
                        total_rd_billion=rd["rd"].sum() / 1e9))
    out = pd.DataFrame(out)
    out.insert(0, "fiscal_year", year)
    return out


def growth_pairs(d, raw):
    """Revenue growth from each kept firm-year to the next fiscal year.

    The $10M floor applies to the starting year only. Next year's revenue is taken from the whole
    US non-financial panel, so a company that falls below $10M still counts; otherwise the
    sharpest declines of small companies would be dropped and their volatility understated.
    """
    nxt = raw[(raw["countryba"] == "US") & raw["sic"].notna() & ~raw["sic"].between(*FINANCE_SIC)
              & (raw["revenue"] > 0)][["cik", "year", "revenue"]]
    nxt = nxt.rename(columns={"revenue": "revenue_next"}).assign(year=lambda x: x["year"] - 1)
    g = d.merge(nxt, on=["cik", "year"], how="inner")
    g["growth"] = np.log(g["revenue_next"] / g["revenue"])
    n0 = len(g)
    print(f"\nGrowth sample: {n0:,} consecutive-year pairs ({len(d) - n0:,} kept firm-years have no "
          f"revenue the next fiscal year); {int((g['revenue_next'] < MIN_REVENUE).sum()):,} pairs end "
          f"below ${MIN_REVENUE / 1e6:.0f}M and are kept")
    g_all = g.copy()
    g_all["resid"] = g_all["growth"] - g_all.groupby("year")["growth"].transform("mean")
    lo, hi = g["growth"].quantile([TRIM, 1 - TRIM])
    g = g[g["growth"].between(lo, hi)].reset_index(drop=True)
    print(f"  dropped {n0 - len(g):,} with growth outside the 1st-99th percentile "
          f"({lo:.2f} to {hi:.2f} log points); kept {len(g):,}")
    g["resid"] = g["growth"] - g.groupby("year")["growth"].transform("mean")
    return g, g_all


def binned_slope(g, robust=False):
    bins = pd.qcut(g["lrev"], N_BINS, labels=False)
    t = g.groupby(bins).agg(lrev=("lrev", "mean"), resid=("resid", list))
    if robust:   # interquartile range / 1.349, a standard deviation that ignores the tails
        sd = t["resid"].apply(lambda x: np.subtract(*np.percentile(x, [75, 25])) / 1.349)
    else:
        sd = t["resid"].apply(np.std)
    return np.polyfit(t["lrev"], np.log(sd), 1)[0]


def scale_regression(g):
    """log |deviation from the year mean| on log revenue, clustered by company."""
    s = g[g["resid"] != 0].copy()
    s["labs"] = np.log(s["resid"].abs())
    return smf.ols("labs ~ lrev", s).fit(cov_type="cluster", cov_kwds={"groups": s["cik"]}), s


def growth_tests(g, g_all):
    rows = []
    med = g["lrev"].median()
    for name, sub, model_value in [
            ("Growth on log revenue, smaller half of firms (survivors)", g[g["lrev"] < med], None),
            ("Growth on log revenue, larger half of firms (Gibrat's law)", g[g["lrev"] >= med], 0.0)]:
        m = smf.ols("growth ~ lrev + C(year)", sub).fit(cov_type="cluster",
                                                        cov_kwds={"groups": sub["cik"]})
        mv = 0.0 if model_value is None else model_value
        r = row(name, mv, m, "lrev", len(sub), sub["cik"].nunique())
        if model_value is None:
            r["model_value"] = np.nan    # model says negative among survivors, no exact value
            r["t_vs_model"] = np.nan
        rows.append(r)

    # Firm-level scale regression: log |residual| on log size
    m, s = scale_regression(g)
    rows.append(row("Elasticity of growth volatility to size, firm level (log absolute deviation on log revenue)",
                    KK_SLOPE, m, "lrev", len(s), s["cik"].nunique()))
    m, s = scale_regression(g_all)
    rows.append(row("Same, growth not trimmed", KK_SLOPE, m, "lrev", len(s), s["cik"].nunique()))

    # Binned version with a firm bootstrap
    b = binned_slope(g)
    rng = np.random.default_rng(SEED)
    groups = {k: v.index.values for k, v in g.groupby("cik")}
    keys = np.array(list(groups))
    draws = []
    for _ in range(N_BOOT):
        pick = rng.choice(keys, len(keys), replace=True)
        draws.append(binned_slope(g.loc[np.concatenate([groups[k] for k in pick])]))
    se = np.std(draws)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    rows.append(dict(prediction=f"Elasticity of growth volatility to size, {N_BINS} size bins (bootstrap)",
                     model_value=KK_SLOPE, estimate=b, std_error=se, ci_low=lo, ci_high=hi,
                     t_vs_model=(b - KK_SLOPE) / se, n_obs=len(g), n_firms=g["cik"].nunique()))
    rb = binned_slope(g, robust=True)
    rows.append(dict(prediction=f"Same, with a tail-robust spread (IQR / 1.349)", model_value=KK_SLOPE,
                     estimate=rb, std_error=np.nan, ci_low=np.nan, ci_high=np.nan, t_vs_model=np.nan,
                     n_obs=len(g), n_firms=g["cik"].nunique()))
    return rows


def growth_table(g):
    bins = pd.qcut(g["lrev"], N_BINS, labels=False)
    t = g.groupby(bins).agg(firm_years=("growth", "size"), median_revenue=("revenue", "median"),
                            mean_log_revenue=("lrev", "mean"), mean_growth=("growth", "mean"),
                            sd_growth=("resid", "std"))
    t.index.name = "size_bin"
    return t.reset_index()


def named_table(d, g, fit_slope):
    gb = g.groupby("cik")["growth"]
    median_rev = g["revenue"].median()
    t = growth_table(g)
    anchor = np.exp(np.interp(np.log(median_rev), t["mean_log_revenue"], np.log(t["sd_growth"])))
    out = []
    for cik, name in NAMED.items():
        f = d[d["cik"] == cik]
        if f.empty or cik not in gb.groups:
            print(f"  {name}: not in the cleaned panel, skipped")
            continue
        last = f.sort_values("year").iloc[-1]
        early = f[f["year"] == COMPARE_YEAR]
        ratio = last["revenue"] / median_rev
        out.append(dict(company=name, cik=cik, fiscal_year=int(last["year"]),
                        revenue_billion=last["revenue"] / 1e9,
                        revenue_compare_year_billion=(early["revenue"].iloc[0] / 1e9) if len(early) else np.nan,
                        rd_billion=(last["rd"] / 1e9) if last["rd"] > 0 else np.nan,
                        rd_intensity=(last["rd"] / last["revenue"]) if last["rd"] > 0 else np.nan,
                        years_of_growth=int(gb.get_group(cik).size),
                        sd_growth_actual=gb.get_group(cik).std(),
                        sd_growth_kk=anchor * ratio ** KK_SLOPE,
                        sd_growth_fitted=anchor * ratio ** fit_slope,
                        revenue_vs_median_firm=ratio, median_firm_revenue_million=median_rev / 1e6,
                        sd_growth_median_firm=anchor))
    print(f"  median firm revenue ${median_rev / 1e6:,.0f}M; sd of growth there {anchor:.3f}")
    return pd.DataFrame(out).sort_values("revenue_billion", ascending=False), anchor, median_rev


def plot(t, slope, anchor, median_rev):
    fig, ax = plt.subplots(figsize=(7.5, 5))
    x = t["median_revenue"] / 1e6
    ax.scatter(x, t["sd_growth"], color="#1f4e79", zorder=3, label="US companies, 2011-2024")
    xs = np.geomspace(x.min(), x.max(), 100)
    ax.plot(xs, anchor * (xs * 1e6 / median_rev) ** slope, color="#1f4e79",
            label=f"Fitted slope {slope:.2f}")
    ax.plot(xs, anchor * (xs * 1e6 / median_rev) ** KK_SLOPE, color="#c55a11", ls="--",
            label="Klette-Kortum: slope -0.50")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Company revenue, $ millions (median of each of 20 size bins)")
    ax.set_ylabel("Standard deviation of annual revenue growth")
    ax.set_title("Big companies are steadier, but not as steady as the model says")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "growth_volatility.png", dpi=150)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    d, raw = load()
    rows = rd_tests(d)
    rob = rd_robustness(raw)
    rob.to_csv(OUT / "rd_elasticity_robustness.csv", index=False, float_format="%.4f")
    print("\nR&D elasticity robustness\n" + rob.round(3).to_string(index=False))
    size = rd_by_size(d)
    size.to_csv(OUT / "rd_by_size.csv", index=False, float_format="%.4f")
    print("\nR&D by revenue class, fiscal 2024\n" + size.to_string(index=False))

    g, g_all = growth_pairs(d, raw)
    rows += growth_tests(g, g_all)
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "kk_predictions_sec.csv", index=False, float_format="%.4f")
    print("\nPredictions against the data\n" + res.round(3).to_string(index=False))

    t = growth_table(g)
    t.to_csv(OUT / "growth_by_size.csv", index=False, float_format="%.4f")
    print("\nGrowth by size bin\n" + t.round(3).to_string(index=False))

    slope = res.loc[res["prediction"].str.contains("size bins"), "estimate"].iloc[0]
    named, anchor, median_rev = named_table(d, g, slope)
    named.to_csv(OUT / "named_firms.csv", index=False, float_format="%.4f")
    print("\nNamed companies\n" + named.round(3).to_string(index=False))
    plot(t, slope, anchor, median_rev)
    print("\nWrote results/kk_predictions_sec.csv, rd_by_size.csv, rd_elasticity_robustness.csv, growth_by_size.csv, "
          "named_firms.csv, growth_volatility.png")


if __name__ == "__main__":
    main()
