"""Build a firm-year panel of revenue and R&D spending for every SEC 10-K filer, fiscal 2011-2024.

Source: the SEC's Financial Statement Data Sets (FSDS), one zip per calendar quarter of filing
dates, each holding every number tagged in every XBRL filing made that quarter. The 58 quarters
from 2012q1 to 2026q2 are read. A 10-K reports the current fiscal year and the one before it, so
these filings cover fiscal 2011 to 2024. Fiscal 2025 is left out because companies whose year
ends in the first half of 2026 had not all filed by the end of 2026q2.

Rules, fixed before looking at any result:
  - 10-K filings only; amendments (10-K/A) and quarterly reports are ignored.
  - Consolidated, full-year (four-quarter), US-dollar values of standard us-gaap tags only.
  - Fiscal years follow the SEC's own "frames" convention: a year ending July-December belongs
    to that calendar year, a year ending January-June to the calendar year before.
  - Revenue is the largest of five revenue tags in a filing; R&D the largest of three R&D tags.
  - When a fiscal year appears in two filings, the filing in which it is the current year wins
    (the number as first reported); otherwise the comparison column of the next 10-K is used.
  - Name, SIC industry code and business-address country come from each filer's latest 10-K.

The zips live in data/raw/sec/ (ignored by git, about 5.5 GB). A missing zip is downloaded from
www.sec.gov; if SEC refuses the request (it blocks busy shared addresses), the script falls back
to the Internet Archive's capture of the same sec.gov address, a copy of the same file.

Writes (committed, so the analysis runs offline):
    data/raw/sec_firm_years.csv.gz   cik, fiscal year, revenue, R&D (US dollars)
    data/raw/sec_firms.csv           cik, SIC code, name, country of business address

Usage (from the repository root, takes 20-40 minutes):
    python src/build_sec_panel.py
"""

import time
import zipfile
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SEC_DIR = RAW / "sec"

YEARS = list(range(2011, 2025))
QUARTERS = [f"{y}q{q}" for y in range(2012, 2027) for q in (1, 2, 3, 4)][:-2]   # 2012q1-2026q2
FSDS = "https://www.sec.gov/files/dera/data/financial-statement-data-sets/{q}.zip"
HEADERS = {"User-Agent": "Brendyn Beasley research 83249437+brendynbeasley@users.noreply.github.com",
           "Accept-Encoding": "gzip, deflate"}
PAUSE = 0.5   # seconds between SEC requests; the shared limit is well above this
REVENUE_TAGS = ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet",
                "SalesRevenueGoodsNet"]
RD_TAGS = ["ResearchAndDevelopmentExpense",
           "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
           "ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost"]
GROUP = {t: "revenue" for t in REVENUE_TAGS} | {t: "rd" for t in RD_TAGS}


def fetch(q):
    """Return the local path of one FSDS zip, downloading it first if it is missing."""
    path = SEC_DIR / f"fsds_{q}.zip"
    if path.exists():
        return path
    SEC_DIR.mkdir(parents=True, exist_ok=True)
    url = FSDS.format(q=q)
    time.sleep(PAUSE)
    r = requests.get(url, headers=HEADERS, timeout=1800)
    if r.status_code != 200 or not r.content.startswith(b"PK"):
        cdx = requests.get("https://web.archive.org/cdx/search/cdx",
                           params={"url": url, "output": "json",
                                   "filter": ["statuscode:200", "mimetype:application/octet-stream"]},
                           timeout=120).json()
        if len(cdx) < 2:
            raise SystemExit(f"{q}: not available from sec.gov ({r.status_code}) or the Internet Archive")
        r = requests.get(f"https://web.archive.org/web/{cdx[-1][1]}id_/{url}", timeout=1800)
        if r.status_code != 200 or not r.content.startswith(b"PK"):
            raise SystemExit(f"{q}: archive copy failed ({r.status_code})")
    tmp = path.with_suffix(".part")
    tmp.write_bytes(r.content)
    tmp.rename(path)
    return path


def read_quarter(q):
    """Revenue and R&D values from the 10-K filings in one quarterly zip."""
    with zipfile.ZipFile(fetch(q)) as z:
        sub = pd.read_csv(z.open("sub.txt"), sep="\t", dtype=str,
                          usecols=["adsh", "cik", "name", "sic", "countryba", "form", "period", "filed"])
        sub = sub[sub["form"] == "10-K"]
        keep = set(sub["adsh"])
        header = z.open("num.txt").readline().decode().strip().split("\t")
        cols = ["adsh", "tag", "version", "ddate", "qtrs", "uom", "coreg", "value"]
        if "segments" in header:
            cols.append("segments")
        parts = []
        for chunk in pd.read_csv(z.open("num.txt"), sep="\t", dtype=str, usecols=cols,
                                 chunksize=2_000_000, quoting=3, on_bad_lines="skip"):
            c = chunk[chunk["tag"].isin(GROUP) & (chunk["qtrs"] == "4") & (chunk["uom"] == "USD")
                      & chunk["coreg"].isna() & chunk["version"].str.startswith("us-gaap")]
            if "segments" in c:
                c = c[c["segments"].isna()]
            parts.append(c[c["adsh"].isin(keep)][["adsh", "tag", "ddate", "value"]])
    num = pd.concat(parts).merge(sub, on="adsh")
    print(f"  {q}: {len(sub):,} 10-K filings, {len(num):,} revenue and R&D values kept")
    return num


def main():
    d = pd.concat([read_quarter(q) for q in QUARTERS], ignore_index=True)
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d = d.dropna(subset=["value"])
    d["cik"] = d["cik"].astype(int)
    end = pd.to_datetime(d["ddate"], format="%Y%m%d", errors="coerce")
    period = pd.to_datetime(d["period"], format="%Y%m%d", errors="coerce")
    d["fy"] = end.dt.year - (end.dt.month <= 6).astype(int)
    d["current"] = ((end - period).abs().dt.days <= 31).astype(int)
    d["group"] = d["tag"].map(GROUP)

    # Largest tag within a filing, then the preferred filing for each firm, year and measure
    per_filing = (d.groupby(["cik", "fy", "group", "adsh", "current", "filed", "ddate"])["value"]
                  .max().reset_index())
    per_filing = per_filing.sort_values(["current", "ddate", "filed"])
    best = per_filing.drop_duplicates(["cik", "fy", "group"], keep="last")
    panel = best.pivot_table(index=["cik", "fy"], columns="group", values="value").reset_index()
    panel = panel.rename(columns={"fy": "year"})
    n0 = len(panel)
    panel = panel[panel["year"].isin(YEARS) & panel["revenue"].notna()]
    print(f"Firm-years with revenue: kept {len(panel):,} in fiscal {YEARS[0]}-{YEARS[-1]}, "
          f"dropped {n0 - len(panel):,} outside the window or without revenue")
    panel[["cik", "year", "revenue", "rd"]].to_csv(RAW / "sec_firm_years.csv.gz", index=False,
                                                   compression="gzip", float_format="%.0f")

    firms = (d.sort_values("filed").drop_duplicates("cik", keep="last")
             [["cik", "sic", "name", "countryba"]])
    firms = firms[firms["cik"].isin(panel["cik"])]
    firms.to_csv(RAW / "sec_firms.csv", index=False)
    print(f"Wrote data/raw/sec_firm_years.csv.gz ({len(panel):,} rows, {panel['cik'].nunique():,} "
          f"filers) and data/raw/sec_firms.csv ({len(firms):,} filers)")
    print(panel.groupby("year").agg(filers=("cik", "size"), with_rd=("rd", "count")).to_string())


if __name__ == "__main__":
    main()
