"""Klette and Kortum (2004) on the Census Business Dynamics Statistics: exit, age and the pace of
creative destruction among all US employer firms, 1978-2023.

Part 1 (the model's exit predictions). A firm with n product lines behaves like n independent
one-line firms, so the chance it disappears within a year is p^n, where p is the chance a one-line
firm disappears. Exit should therefore fall geometrically with size, and once size is known a
firm's age should not matter (the paper's footnote 9 concedes the data disagree on age). Both are
checked against firm deaths by initial employment size and by age, pooled over 2015-2019.

Part 2 (the extension). In the model the exit hazard of a brand-new firm equals mu, the rate at
which any product line is captured by a rival, and in steady state the entry rate of firms equals
lambda / ln(mu / (mu - lambda)), where lambda is incumbents' innovation rate. Reading the two
published BDS numbers (the death rate of one-year-old firms and the firm entry rate) through these
formulas gives mu and lambda for every year from 1978 to 2023, for all firms and for manufacturing.

Input (committed): data/raw/bds/bds2023.csv, bds2023_fa.csv, bds2023_fa_ifz.csv, bds2023_ifz.csv,
bds2023_sec_fa.csv, downloaded from www2.census.gov/programs-surveys/bds/tables/time-series/2023/
Writes:
    results/exit_by_size.csv             death rate by initial size, data vs the model's geometric law
    results/exit_by_size_and_age.csv     death rate by age within each size class
    results/exit_fit.csv                 fit statistics for the two exit-size laws and the age test
    results/creative_destruction.csv     mu, lambda, entrants' share, expected life, by year
    results/creative_destruction_by_decade.csv   the same, averaged by decade
    results/creative_destruction_change.csv      percent change, 1980s average to 2010s average
    results/bds_accounting_check.csv     change in firm count vs births minus deaths, by year
    results/exit_by_size.png, results/creative_destruction.png

Usage (from the repository root):
    python src/exit_and_destruction.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
BDS = ROOT / "data" / "raw" / "bds"
OUT = ROOT / "results"

POOL = range(2015, 2020)    # five pre-pandemic years for the cross-sectional exit tables
MISSING = ["X", "D", "S", "N"]   # BDS codes: not applicable, disclosure-suppressed, etc.
AGE_SHIFT = 0.5             # a firm of BDS age a has been alive a + 0.5 years on average in March
AGE_YEARS = {"b) 1": 1, "c) 2": 2, "d) 3": 3, "e) 4": 4, "f) 5": 5, "g) 6 to 10": 8,
             "h) 11 to 15": 13, "i) 16 to 20": 18, "j) 21 to 25": 23, "k) 26+": 30}
SMALL_CLASSES = ["a) 1 to 4", "b) 5 to 9"]   # the model's geometric law is calibrated on these
AGE_TEST_SIZES = ["a) 1 to 4", "b) 5 to 9", "c) 10 to 19", "d) 20 to 99", "e) 100 to 499"]
SERIES = {"All employer firms": None, "Manufacturing": "31-33"}


def read(name):
    d = pd.read_csv(BDS / name, na_values=MISSING, dtype={"sector": str})
    print(f"Loaded {name}: {len(d):,} rows, {d['year'].min()}-{d['year'].max()}")
    return d


def death_rate(g):
    """Share of last year's firms that died: deaths / (surviving firms + deaths)."""
    ok = g["firmdeath_firms"].notna() & g["firms"].notna()
    return g.loc[ok, "firmdeath_firms"].sum() / (g.loc[ok, "firms"].sum()
                                                 + g.loc[ok, "firmdeath_firms"].sum())


def exit_by_size():
    fa = read("bds2023_fa_ifz.csv")
    size = read("bds2023_ifz.csv")
    fa = fa[fa["year"].isin(POOL) & (fa["fage"] != "a) 0")]     # entrants have no initial size
    sz = size[size["year"].isin(POOL)]
    dropped = fa["firmdeath_firms"].isna().sum()
    print(f"  exit by size, {POOL.start}-{POOL.stop - 1}: {len(fa):,} size-age-year cells, "
          f"{dropped:,} with suppressed deaths left out of both numerator and denominator")
    rows = []
    for cls, g in fa.groupby("ifsize"):
        s = sz[sz["ifsize"] == cls]
        ok = g["firmdeath_firms"].notna() & g["firms"].notna()
        at_risk = g.loc[ok, "firms"].sum() + g.loc[ok, "firmdeath_firms"].sum()
        rows.append(dict(size_class=cls[3:], mean_employment=s["emp"].sum() / s["firms"].sum(),
                         firms_at_risk_per_year=at_risk / len(POOL), deaths=g.loc[ok, "firmdeath_firms"].sum(),
                         death_rate=death_rate(g)))
    t = pd.DataFrame(rows)

    # The model: log P(exit) = n log p with n proportional to employment, so log death rates are
    # linear in employment. The fit allows a free intercept, which is more generous to the model
    # than a line through the origin. Calibrate on the two smallest classes, then predict the rest.
    a, b = t.iloc[0], t.iloc[1]
    slope = (np.log(b["death_rate"]) - np.log(a["death_rate"])) / (b["mean_employment"] - a["mean_employment"])
    t["kk_geometric"] = np.exp(np.log(a["death_rate"]) + slope * (t["mean_employment"] - a["mean_employment"]))
    pos = t[t["death_rate"] > 0]
    lin = np.polyfit(pos["mean_employment"], np.log(pos["death_rate"]), 1)
    pw = np.polyfit(np.log(pos["mean_employment"]), np.log(pos["death_rate"]), 1)
    t["kk_geometric_best_fit"] = np.exp(np.polyval(lin, t["mean_employment"]))
    t["power_law_fit"] = np.exp(np.polyval(pw, np.log(t["mean_employment"])))
    pos = t[t["death_rate"] > 0]     # again, now carrying the fitted columns

    def rmse(col):
        return np.sqrt(np.mean((np.log(pos[col]) - np.log(pos["death_rate"])) ** 2))
    fit = [dict(test="Geometric law (model), calibrated on 1-4 and 5-9 employee firms",
                statistic="employees per halving of the death rate", value=np.log(0.5) / slope),
           dict(test="Geometric law (model), least squares on all classes",
                statistic="rmse of log death rate", value=rmse("kk_geometric_best_fit")),
           dict(test="Power law, least squares on all classes",
                statistic="elasticity of death rate to employment", value=pw[0]),
           dict(test="Power law, least squares on all classes",
                statistic="rmse of log death rate", value=rmse("power_law_fit")),
           dict(test="Size classes with positive death rate", statistic="count", value=len(pos))]
    return t, fit


def exit_by_age(fit):
    fa = read("bds2023_fa_ifz.csv")
    fa = fa[fa["year"].isin(POOL) & fa["fage"].isin(AGE_YEARS) & fa["ifsize"].isin(AGE_TEST_SIZES)]
    rows = []
    for (cls, age), g in fa.groupby(["ifsize", "fage"]):
        rows.append(dict(size_class=cls[3:], age=age[3:], age_years=AGE_YEARS[age],
                         firms_per_year=g["firms"].sum() / len(POOL), death_rate=death_rate(g)))
    t = pd.DataFrame(rows).sort_values(["size_class", "age_years"])
    for cls, g in t.groupby("size_class", sort=False):
        young = g.loc[g["age"] == "1", "death_rate"].iloc[0]
        old = g.loc[g["age"] == "26+", "death_rate"].iloc[0]
        fit.append(dict(test=f"Age effect within size class {cls} employees",
                        statistic="death rate at age 1 / death rate at age 26+", value=young / old))
    return t


def survival(t, mu, lam):
    """Probability a one-line entrant is still alive at age t (eq. 7 of the paper)."""
    k = mu - lam
    return k * np.exp(-k * t) / (mu - lam * np.exp(-k * t))


def solve(d1, entry):
    """mu and lambda that reproduce the age-1 death rate and the steady-state entry rate."""
    def mu_of(x):                 # entry = lambda / ln(mu/(mu-lambda)), with x = lambda/mu
        return entry * np.log(1 / (1 - x)) / x

    def gap(x):
        mu = mu_of(x)
        return 1 - survival(1 + AGE_SHIFT, mu, x * mu) / survival(AGE_SHIFT, mu, x * mu) - d1
    lo, hi = 1e-6, 1 - 1e-9
    if gap(lo) * gap(hi) > 0:
        return np.nan, np.nan
    x = brentq(gap, lo, hi)
    return mu_of(x), x * mu_of(x)


def creative_destruction():
    allf = read("bds2023_fa.csv").assign(sector="All")
    sec = read("bds2023_sec_fa.csv")
    rows = []
    for label, code in SERIES.items():
        d = allf if code is None else sec[sec["sector"] == code]
        for yr, g in d.groupby("year"):
            g = g.set_index("fage")
            if "b) 1" not in g.index or pd.isna(g.loc["b) 1", "firmdeath_firms"]):
                continue
            d1 = g.loc["b) 1", "firmdeath_firms"] / (g.loc["b) 1", "firms"] + g.loc["b) 1", "firmdeath_firms"])
            entry = g.loc["a) 0", "firms"] / g["firms"].sum()
            mu, lam = solve(d1, entry)
            # Bounds on mu that need no steady-state assumption: lambda = 0 gives
            # d1 = 1 - exp(-mu); lambda = mu gives d1 = mu / (1 + (1 + AGE_SHIFT) * mu) at a = 1.
            mu_lo = -np.log(1 - d1)
            mu_hi = brentq(lambda m: 1 - survival(1 + AGE_SHIFT, m, m * (1 - 1e-9))
                           / survival(AGE_SHIFT, m, m * (1 - 1e-9)) - d1, 1e-6, 10)
            rows.append(dict(series=label, year=yr, death_rate_age1=d1, entry_rate=entry, mu=mu,
                             lam=lam, entrant_share=(mu - lam) / mu,
                             expected_life=np.log(mu / (mu - lam)) / lam,
                             products_per_firm=1 / ((mu - lam) / lam * np.log(mu / (mu - lam))),
                             mu_if_lambda_zero=mu_lo, mu_if_no_entry=mu_hi))
    t = pd.DataFrame(rows)
    bad = t["mu"].isna().sum()
    print(f"  creative destruction: {len(t):,} series-years, {bad} without a solution")
    return t


def by_decade(t):
    t = t.copy()
    t["period"] = (t["year"] // 10 * 10).astype(str) + "s"
    t.loc[t["year"] >= 2020, "period"] = "2020-23"
    cols = ["death_rate_age1", "entry_rate", "mu", "lam", "entrant_share", "expected_life",
            "mu_if_lambda_zero", "mu_if_no_entry"]
    out = t.groupby(["series", "period"], sort=False)[cols].mean()
    out.insert(0, "years", t.groupby(["series", "period"], sort=False)["year"].size())
    return out.reset_index()


def accounting_check():
    """Change in the firm count against births minus deaths; a large gap flags a measurement shift."""
    n = read("bds2023.csv").set_index("year")
    fa = read("bds2023_fa.csv")
    births = fa[fa["fage"] == "a) 0"].set_index("year")["firms"]
    t = pd.DataFrame({"firms": n["firms"], "change_in_firms": n["firms"].diff(), "births": births,
                      "deaths": n["firmdeath_firms"]})
    t["births_minus_deaths"] = t["births"] - t["deaths"]
    t["gap"] = t["change_in_firms"] - t["births_minus_deaths"]
    t["gap_share_of_firms"] = t["gap"] / t["firms"]
    return t.dropna().reset_index()


def plot_exit(t):
    fig, ax = plt.subplots(figsize=(7.5, 5))
    pos = t[t["death_rate"] > 0]
    ax.scatter(pos["mean_employment"], pos["death_rate"] * 100, color="#1f4e79", zorder=3,
               label="US employer firms, 2015-2019")
    xs = np.geomspace(t["mean_employment"].min(), t["mean_employment"].max(), 200)
    a = t.iloc[0]
    slope = (np.log(t.iloc[1]["death_rate"]) - np.log(a["death_rate"])) / (t.iloc[1]["mean_employment"] - a["mean_employment"])
    kk = np.exp(np.log(a["death_rate"]) + slope * (xs - a["mean_employment"])) * 100
    keep = kk > pos["death_rate"].min() * 100 / 20
    ax.plot(xs[keep], kk[keep], color="#c55a11", ls="--", label="Klette-Kortum: exit = p^n")
    pw = np.polyfit(np.log(pos["mean_employment"]), np.log(pos["death_rate"]), 1)
    ax.plot(xs, np.exp(np.polyval(pw, np.log(xs))) * 100, color="#1f4e79",
            label=f"Power law, elasticity {pw[0]:.2f}")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Employees last year (mean of each BDS size class)")
    ax.set_ylabel("Share of firms that closed within the year, %")
    ax.set_title("Exit falls with size far more slowly than the model says")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "exit_by_size.png", dpi=150)
    plt.close(fig)


def plot_cd(t):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    for (label, g), color in zip(t.groupby("series", sort=False), ["#1f4e79", "#c55a11"]):
        axes[0].fill_between(g["year"], g["mu_if_lambda_zero"] * 100, g["mu_if_no_entry"] * 100,
                             color=color, alpha=0.15, lw=0)
        axes[0].plot(g["year"], g["mu"] * 100, color=color, label=label)
        axes[1].plot(g["year"], g["entrant_share"] * 100, color=color, label=label)
    axes[0].set_title("Creative destruction rate \u03bc, % of lines a year\n(band: bounds without the steady state)")
    axes[1].set_title("Entrants' share of innovation, (\u03bc - \u03bb) / \u03bc, %")
    for ax in axes:
        ax.set_xlabel("Year")
        ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "creative_destruction.png", dpi=150)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    size, fit = exit_by_size()
    size.to_csv(OUT / "exit_by_size.csv", index=False, float_format="%.5f")
    print("\nExit by initial size\n" + size.round(4).to_string(index=False))
    age = exit_by_age(fit)
    age.to_csv(OUT / "exit_by_size_and_age.csv", index=False, float_format="%.5f")
    print("\nExit by age within size\n" + age.pivot(index="age_years", columns="size_class",
                                                     values="death_rate").round(3).to_string())
    fit = pd.DataFrame(fit)
    fit.to_csv(OUT / "exit_fit.csv", index=False, float_format="%.4f")
    print("\nExit tests\n" + fit.round(3).to_string(index=False))
    cd = creative_destruction()
    cd.to_csv(OUT / "creative_destruction.csv", index=False, float_format="%.4f")
    dec = by_decade(cd)
    dec.to_csv(OUT / "creative_destruction_by_decade.csv", index=False, float_format="%.4f")
    a, b = dec[dec["period"] == "1980s"].set_index("series"), dec[dec["period"] == "2010s"].set_index("series")
    cols = ["death_rate_age1", "entry_rate", "mu", "mu_if_lambda_zero", "mu_if_no_entry", "lam",
            "entrant_share", "expected_life"]
    chg = ((b[cols] - a[cols]) / a[cols]).stack().rename("pct_change_1980s_to_2010s").reset_index()
    chg.columns = ["series", "measure", "pct_change_1980s_to_2010s"]
    chg.to_csv(OUT / "creative_destruction_change.csv", index=False, float_format="%.4f")
    print("\nChange from the 1980s to the 2010s\n" + chg.round(3).to_string(index=False))
    print("\nCreative destruction by decade\n" + dec.round(3).to_string(index=False))
    acc = accounting_check()
    acc.to_csv(OUT / "bds_accounting_check.csv", index=False, float_format="%.4f")
    print("\nFirm-count accounting, last ten years\n" + acc.tail(10).round(4).to_string(index=False))
    plot_exit(size)
    plot_cd(cd)
    print("\nWrote results/exit_by_size.csv, exit_by_size_and_age.csv, exit_fit.csv, "
          "creative_destruction.csv, creative_destruction_by_decade.csv, creative_destruction_change.csv, bds_accounting_check.csv, exit_by_size.png, creative_destruction.png")


if __name__ == "__main__":
    main()
