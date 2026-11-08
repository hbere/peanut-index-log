# Peanut Index forecast log — methodology v1

This file is committed to by hash in entry 0 of the log (`entries/000000.json`, field
`methodology_sha256`), timestamped before any forecast exists. It is never edited. A change is a
new file (`METHODOLOGY_v2.md`, …) and a new `methodology` entry naming that file's hash; it applies
only to forecasts written after that entry and never to an earlier one. Every version stays here.

## 1. What is forecast

- **Report:** USDA NASS *Peanut Prices*, the weekly report of prices received by farmers for farmer
  stock peanuts, published on the USDA ESMIS archive (normally Fridays, 15:00 ET).
- **Series:** the average price for **all** peanuts and for **runner**-type peanuts, in US dollars
  per pound, to the three decimals NASS prints.
- **Target week:** the week after the newest week in the latest issue held at forecast time. On a
  Wednesday that is the week that ended the previous Saturday, which the coming Friday's issue
  first reports.
- **Graded on the first print.** Each issue restates the trailing five weeks, so a week's price can
  be revised up to four times. The value used for grading is the week's value in the
  earliest-released issue that contains it. Later revisions are never used for grading.

## 2. When

- One forecast per target week, issued **on the Wednesday before the release, before 12:00 ET**.
  The entry's `on_time` field records whether it was. Only on-time forecasts are graded.
- A forecast is refused (nothing is written) unless the archive capture ran cleanly within the
  previous 90 minutes, the newest issue held is at most 8 days old, and the target week has not
  already been printed.
- **Every week is accounted for.** Every week first printed after entry 0 gets exactly one entry:
  a `resolution` (an on-time forecast existed) or a `missed` entry (it did not, including when only
  a late forecast existed, which the entry lists). A forecast whose target week is never printed
  (a cancelled report) gets a `no_print` entry 35 days after the week ended. The record of misses
  is part of the record.

## 3. Model v0.1

The model is deliberately simple. The log is judged by its length and honesty, and later versions
are judged against this one.

- **Point (the median):** the newest printed value ("same as last week").
- **Range:** quantiles 2.5, 10, 25, 50, 75, 90 and 97.5 %, from the distribution of that point's
  past one-week errors, using:
  - errors from prior calendar years only (none from the target's own year);
  - only weeks within ±3 weeks of the target's week of the year;
  - all of them multiplied by the **square root** of recent volatility over seasonal volatility.
    Recent volatility is the median absolute error of the last 8 weeks already printed at forecast
    time; seasonal volatility is the same median over the seasonal window. The ratio is clipped
    to 0.5–3 before the root is taken.
- **How it was chosen:** a walk-forward backtest, run year by year over 2011–2026 on the NASS
  archive from October 2006. Each year was forecast using only earlier years. Four variants were
  tried, and all four are reported:
  1. a seasonal drift added to the point: beat "same as last week" in only 8 of 16 years (all
     peanuts) and 2 of 16 (runner), so it was rejected;
  2. no volatility scaling: the ranges were too narrow;
  3. full (proportional) scaling: too wide when recent volatility was high, and too narrow when it
     was low;
  4. **square-root scaling (adopted):** the lowest mean pinball loss. It beat no scaling in 13 of
     16 years for both series, and beat full scaling in 12 of 16 (all) and 10 of 16 (runner). Its
     coverage was about the same whether recent volatility was low or high.

  | series | weeks | mean abs. error | 50 % range held | 80 % held | 95 % held |
  |---|---|---|---|---|---|
  | all | 764 | 1.60 ¢/lb | 47 % | 76 % | 91 % |
  | runner | 720 | 1.40 ¢/lb | 42 % | 75 % | 92 % |

  The ranges are still somewhat narrow, and in individual years they can be well off nominal (the
  worst year's 80 % range held only 50–54 %). That is the baseline any later model has to beat.

## 4. Scores

Each resolution entry records, per series:
- `abs_error`: |first print − point|;
- `abs_error_naive`: the same for "same as last week";
- `pinball`: the mean pinball (quantile) loss over the seven quantiles;
- whether the first print fell inside the central 50, 80 and 95 % ranges.

A withheld value (NASS prints `(D)`) is not scored for that series. No other baseline is scored
unless a later methodology entry adds it.

## 5. What makes the record checkable

- **One entry per file, written once.** Each entry is a canonical JSON file in `entries/`, never
  edited.
- **Hash chain.** Each entry carries the sha256 of the entry before it, so removing, reordering or
  editing any entry breaks every later link.
- **Timestamps.** Each entry file has an OpenTimestamps proof (`.ots`) anchoring its hash in the
  Bitcoin blockchain. The push to this public repository is a second, weaker clock.
- **Inputs by hash.** Each forecast names the NASS file it used, by URL and sha256. Each resolution
  names the NASS file that settled it, by URL, sha256 and the server's `Last-Modified` header.
  These are public files that anyone can download and hash.
- **Code by hash.** Each entry carries the sha256 of the forecasting code (`code_sha256`). The code
  is not published here, but can be disclosed to an auditor, who can check it against the hash.
- **Corrections.** An error in an entry is never fixed in place. A correction is a new entry that
  references the one it corrects.

To check all of this yourself, see `README.md`.
