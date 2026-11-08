# Peanut Index forecast log

A public, append-only record of weekly forecasts of the USDA NASS *Peanut Prices* report, made
before each release and graded on the first print. The rules are in [METHODOLOGY.md](METHODOLOGY.md),
committed to by hash in entry 0 before the first forecast.

## Layout

| path | what |
|---|---|
| `entries/NNNNNN.json` | one entry per file: `methodology`, `forecast`, `resolution`, `missed` or `no_print` |
| `entries/NNNNNN.json.ots` | the OpenTimestamps proof for that file |
| `log.jsonl` | every entry, one per line, for easy reading (derived from `entries/`) |
| `verify.py` | checks the chain and the methodology hash (Python 3 standard library only) |

## Check it yourself

```bash
python3 verify.py                     # the hash chain, the canonical form, the methodology hash
pip install opentimestamps-client
ots verify entries/000001.json.ots    # the timestamp, against Bitcoin (or use opentimestamps.org)
```

Then pick any forecast or resolution entry, download the NASS file at its `url`, and compare its
sha256 with the entry's `sha256`.

Public USDA data; the forecasts are the author's own and are not investment advice.
