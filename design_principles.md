> **This document was produced with Cursor.** The pipeline description and the audit of coding practices were written from the current contents of the scripts named below, not from an idealised version of the project.

# Design principles for the Christchurch Airbnb–bond pipeline

This note describes the data pipeline that turns Inside Airbnb listings and Tenancy Services bond statistics into the answers in `airbnb_vs_rentals.Rmd`. It also records how the code currently sits against four lecture practices: relative paths, named constants, fail-loud checks, and one-row sanity checks.

The scripts, in order, are:

1. `clean_christchurch_panel.Rmd`
2. `bond_listing_clean.Rmd`
3. `get_area_codes.py`
4. `join_listings_bonds.Rmd`
5. `airbnb_vs_rentals.Rmd`

---

## 1. Inputs

The pipeline starts from two source tables, plus one derived lookup that is built mid-pipeline.

| Input | Source | Used by |
| --- | --- | --- |
| `Christchurch Oct2025 to Jun2026 (combined).csv` | Concatenated Inside Airbnb monthly `listings.csv` extracts for Christchurch, October 2025 – June 2026 | `clean_christchurch_panel.Rmd` |
| `Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv` | MBIE Tenancy Services detailed quarterly bond report | `bond_listing_clean.Rmd` |
| Koordinates Query API, layer `123515` (Stats NZ SA2 2026) | External geocoding service; key from `KOORDINATES_API_KEY` | `get_area_codes.py` |

`bond_listing_clean.Rmd` also reads the **cleaned listings** file, not as a second source of bond information, but to take `min(month_date)` and `max(month_date)` so the bond window is aligned to the panel rather than hardcoded as a list of quarters.

The later steps take files produced earlier in the same repo:

| Intermediate input | Produced by | Used by |
| --- | --- | --- |
| `Christchurch Oct2025 to Jun2026 (cleaned).csv` | `clean_christchurch_panel.Rmd` | `get_area_codes.py` (and the date-range read in `bond_listing_clean.Rmd`) |
| `Christchurch_with_area_codes.csv` | `get_area_codes.py` | `join_listings_bonds.Rmd` |
| `Bond_Data_Quarterly_(cleaned).csv` | intended output of `bond_listing_clean.Rmd` | `join_listings_bonds.Rmd` |
| `Christchurch_with_bonds.csv` | `join_listings_bonds.Rmd` | `airbnb_vs_rentals.Rmd` |

**Mismatch to flag:** `bond_listing_clean.Rmd` writes `Bond Data Quarterly (cleaned).csv` (spaces, no extra underscores). `join_listings_bonds.Rmd` reads `Bond_Data_Quarterly_(cleaned).csv`. The file currently in the repo matches the **join** name, not the **write** name in the cleaning notebook. Knitting `bond_listing_clean.Rmd` as written would not produce the filename the join step expects.

A second mismatch: `bond_listing_clean.Rmd` points `data_dir` at `/Users/nalikadesai/Desktop/DATA201`, which is **outside** this repository (`Group-3-DATA201-422-`). The detailed quarterly CSV now also sits in the repo root. The notebook as committed does not read that in-repo copy.

---

## 2. Outputs

### Intermediate tables

| File | What it is |
| --- | --- |
| `Christchurch Oct2025 to Jun2026 (cleaned).csv` | Panel of listing-months with types fixed, structural missingness handled, kNN-imputed prices, and panel flags |
| `Bond Data Quarterly (cleaned).csv` / `Bond_Data_Quarterly_(cleaned).csv` | Bond rows for the overlapping quarters, with missing bed counts imputed and `-99` / blank locations dropped |
| `Christchurch_with_area_codes.csv` | Cleaned listings plus `area_code` (SA2) from Koordinates |
| `Christchurch_with_bonds.csv` | Left-joined listing-months with area-level quarterly bond totals |

### Analysis output

`airbnb_vs_rentals.Rmd` does not write a new CSV. It knits to HTML and reports three results:

1. Median observed Airbnb price in Christchurch Central (SA2 `326600`): **$238 per night**.
2. Largest short-term vs long-term price gap among entire homes with bond data: **Heathcote Ward, location `332700`, $255 per night**.
3. Airbnbs per 100 active bonds in Apr–Jun 2026, among areas with bond data: **8**.

Those numbers live in the notebook as written results, not as a separate saved table.

**Mismatch to flag:** `airbnb_vs_rentals.Rmd` contains the full document **twice**. The second copy adds a Banks Peninsula caveat and a note that bedrooms cannot be compared. A knit of the file as it stands would render two copies of the same analysis.

---

## 3. Main steps

```
combined listings CSV
        │
        ▼
clean_christchurch_panel.Rmd
  • read ids as character
  • drop empty license column
  • ordered month factor + month_date
  • structural zeros for reviews_per_month
  • fill host_name / minimum_nights within listing
  • kNN price (k = 10); keep original price
  • flags: months_present, in_all_9_months, long_stay
        │
        ├──────────────────────────────────► cleaned listings CSV
        │                                            │
        │                                            ▼
        │                                   get_area_codes.py
        │                                     unique lat/lng
        │                                     Koordinates SA2 lookup
        │                                     multiprocessing + checkpoints
        │                                            │
        │                                            ▼
        │                                   listings + area_code CSV
        │                                            │
quarterly bonds CSV                                  │
        │                                            │
        ▼                                            │
bond_listing_clean.Rmd                               │
  • overlap quarters with listings date range        │
  • drop NA and -99 Location Id                      │
  • kNN Number Of Beds (k = 5)                       │
        │                                            │
        ▼                                            │
cleaned bonds CSV ───────────────────────────────────┤
                                                     ▼
                                          join_listings_bonds.Rmd
                                            • map month → quarter
                                            • keep bond ALL/ALL totals
                                              (drop imputed ALL beds)
                                            • left join on area_code + quarter
                                                     │
                                                     ▼
                                          Christchurch_with_bonds.csv
                                                     │
                                                     ▼
                                          airbnb_vs_rentals.Rmd
                                            Q1 Central median price
                                            Q2 largest nightly gap
                                            Q3 Airbnbs vs active bonds
```

Design choices that matter for later steps:

- **Types as labels.** Listing `id`, `host_id`, and later `area_code` / `Location Id` are read as character so large integers are not rounded.
- **Do not overwrite raw price.** `price` stays as observed (including gaps and the 27 values above $2,000). Analysis that wants “real” prices filters `price_was_imputed == FALSE`.
- **Quarterly vs monthly.** Listings are assigned the first day of their quarter so they can join to bond `TimeFrame`.
- **Join grain.** Bond totals are the row where dwelling type and beds are both `"ALL"` and `beds_was_imputed` is false. The join is a **left** join so unmatched Airbnbs are kept and flagged with `has_bond_data`.
- **Units.** Bond rents are weekly; Airbnb prices are per night. The analysis divides weekly rent by 7 before subtracting.

---

## 4. Coding and software strategies (lecture practices vs this repo)

The lectures we are citing here are the ones that cover **relative vs absolute paths**, **named constants instead of magic numbers**, **self-documenting code and assertions over comments**, and **hand-checking one row before trusting the full run**. Each subsection states the practice, then what the code actually does.

### 4.1 Relative file paths vs absolute file paths

**Lecture practice:** never hardcode a personal machine path. Paths should be relative to the project root so the same script runs on every computer.

**Where the code follows it**

- `clean_christchurch_panel.Rmd` sets `data_dir <- "."` and builds `in_file` / `out_file` with `file.path`. The comment in that chunk is explicit that this is so the notebook works on every machine.
- `get_area_codes.py` uses `INPUT_FILE` and `OUTPUT_FILE` as filenames in the current working directory, not `/Users/...`.
- `join_listings_bonds.Rmd` and `airbnb_vs_rentals.Rmd` read and write CSV names in the working directory (the repo folder when knitted from there).

**Where the code does not follow it**

- `bond_listing_clean.Rmd` hardcodes Nalika’s machine:

  ```r
  data_dir <- "/Users/nalikadesai/Desktop/DATA201"
  ```

  That is exactly the pattern the lecture forbids. It also points **one folder above the repo**, not at the project root.

- The same notebook then **ignores** `in_file` and reads the CSV with a second absolute path:

  ```r
  bonds <- read_csv(
    "/Users/nalikadesai/Desktop/DATA201/Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv",
    ...
  )
  ```

  So even if `data_dir` were fixed, this `read_csv` would still be machine-specific.

- Relative paths here mean “current working directory”, not “directory of this file”. `get_area_codes.py` will fail if it is launched from another folder. That is weaker than resolving paths from the project root, but it is still portable if the team always runs from the repo.

**Verdict:** four of five scripts are portable; `bond_listing_clean.Rmd` currently is not. This document does not claim the whole pipeline is path-safe.

### 4.2 Avoiding magic numbers

**Lecture practice:** parameters such as `k` in kNN, or the number of parallel processes, should be named. Visible constants belong near the top of the file, not as unexplained numbers in the middle of a call.

**Where the code follows it**

- `get_area_codes.py` names `LAYER_ID = 123515` at the top. The layer is still an opaque Stats NZ identifier, but it is not buried inside the request URL.
- `API_KEY` is loaded from the environment, not pasted into the script.
- `month_levels` in `clean_christchurch_panel.Rmd` names the nine panel months in one place (though the `case_when` that builds `month_date` still repeats the same strings).

**Where the code does not follow it**

These values are used in place, with no named constant at the top of the file:

| Value | Where | What it controls |
| --- | --- | --- |
| `k = 10` | `clean_christchurch_panel.Rmd` | kNN neighbours for price |
| `k = 5` | `bond_listing_clean.Rmd` | kNN neighbours for beds |
| `processes=20` | `get_area_codes.py` | parallel API workers |
| `timeout=15` | `get_area_codes.py` | HTTP timeout (seconds) |
| `i % 500` | `get_area_codes.py` | checkpoint frequency |
| `2000` | listings clean + analysis | price treated as error |
| `9` | `in_all_9_months` | complete panel length |
| `30` | `long_stay` | nights that count as long-stay |
| `-99` | bond clean | national rollup location |
| `7` | `airbnb_vs_rentals.Rmd` | days in a week for rent conversion |
| `20` | `airbnb_vs_rentals.Rmd` | minimum listings to rank an SA2 |
| `"326600"` | `airbnb_vs_rentals.Rmd` | Christchurch Central |
| `"2026-04-01"` | `airbnb_vs_rentals.Rmd` | “latest” quarter |

Some of these are explained in nearby prose (`$2,000`, 30 nights, `-99`). That is better than a silent `k = 10`, but it is still not the lecture pattern of a named constant at the top (`knn_k <- 10`, `n_processes = 20`).

The two kNN calls also use **different** `k` without a shared, named reason in code. The notebooks say the team chose kNN; they do not say why 10 vs 5.

**Verdict:** the Python script is the closest to the lecture (named layer and files at the top). The R notebooks still bury the parameters the lecture uses as the example (`k`, process count).

### 4.3 Self-documenting code and assertions over comments

**Lecture practice:** prefer code that fails loudly (`stop()` / `raise`) over comments that describe an expectation without enforcing it.

**Where the code follows it**

- `get_area_codes.py` does `API_KEY = os.environ["KOORDINATES_API_KEY"]`. If the key is missing, Python raises `KeyError` immediately. That is the lecture’s “fail loudly” pattern.
- `area_code` is created as `dtype="object"` so later string codes cannot silently fail a numeric column. The comment next to that line explains a real constraint; the `dtype` is what enforces it.
- Several operations are named so the intent is in the data, not only in markdown: `price_was_imputed`, `beds_was_imputed`, `has_bond_data`, `minimum_nights_filled`, `in_all_9_months`.

**Where the code does not follow it**

Checks are printed, or described in comments, and the script continues either way:

```r
# clean_christchurch_panel.Rmd
sum(duplicated(airbnb[, c("id", "month_year")]))   # expect 0

# join_listings_bonds.Rmd
sum(is.na(listings$quarter))   # expect 0
sum(duplicated(bond_totals[, c("area_code", "quarter")]))   # expect 0
nrow(joined) == nrow(listings)   # expect TRUE, the join adds no rows
```

None of these use `stopifnot()` / `stop()`. A duplicate listing-month or a many-to-many join would still be written to CSV.

`file.exists(in_file)` in the cleaning notebooks is displayed, not asserted. A missing file then fails later inside `read_csv`, which is loud, but the existence check itself does not abort.

`get_area_codes.py` **swallows** request failures:

```python
except Exception as e:
    print(f"Failed for {lat}, {lng}: {e}")
    return None
```

A bad key, a wrong layer, or a swapped lat/lng can produce `None` area codes and a finished CSV. That is the opposite of failing loudly. The print at the end (`Missing area codes: n out of N`) is a diagnostic, not a halt.

`bond_listing_clean.Rmd` comments that there are “no duplicate rows” and “no missing values remain”. Those are narrative claims after `sum(duplicated(...))` and `colSums(is.na(bonds))`. They are not assertions.

**Verdict:** the API key lookup is a genuine assertion. Most pipeline “expect 0 / expect TRUE” lines are comments plus printed numbers, which is what the lecture asks us not to treat as validation.

### 4.4 Sanity-check one row by hand before trusting the pipeline at scale

**Lecture practice:** pick one row (or one known case), compute the expected result by hand, and compare it to the code’s output before running the full dataset.

**Where the code / project follows it**

The README records a one-location geocoding check: a known Redcliffs listing should return SA2 `332100`. That is the lecture pattern applied to the step that is easiest to get silently wrong (`x=longitude`, `y=latitude`). It is documented as a pre-run check, not as an automated test in `get_area_codes.py`.

`airbnb_vs_rentals.Rmd` does **robustness checks** on Q1 (observed vs imputed medians; listing-months vs one row per listing) and reports that $238, $236, and $237 sit close together. That is related, but it is a sensitivity check on an aggregate, not a hand calculation of a single listing’s price.

`join_listings_bonds.Rmd` decomposes unmatched rows into three counted reasons (boundary splits, unpublished quiet areas, missing total row). That is a reconciliation of join coverage, not a one-row expected-join check.

`clean_christchurch_panel.Rmd` inspects latitude/longitude ranges and states they fall inside Christchurch including Banks Peninsula. Again, a global range check, not one known address.

**Where it does not follow it**

There is no scripted check of the form: “listing `id` X in October 2025 should have `price_imputed` = … because its ten neighbours were …”. kNN is trusted from `VIM::kNN` plus grouped median tables.

There is no one-row check that a known listing in SA2 `326600` in April 2026 picks up the bond `ALL`/`ALL` row for `2026-04-01`.

The Redcliffs check lives in `README.md`, not in `get_area_codes.py`, so a later edit to `LAYER_ID` or to `x`/`y` would not fail a test; someone would have to repeat the check by hand.

**Verdict:** the geocoding step has a documented one-case check, which matches the lecture. Imputation and the join do not. This document does not claim the whole pipeline was hand-verified row-by-row.

---

## 5. Other strategies the project actually uses

These are not the four lecture items, but they are consistent choices in the code:

- **Keep raw columns.** Observed `price` and (for listings) unfilled `minimum_nights` stay in the file so later work can opt out of imputation.
- **Flag what was filled.** `price_was_imputed` and `beds_was_imputed` are used downstream (the join drops imputed `"ALL"` bed rows so they cannot pass as area totals).
- **Character IDs.** Same rule from listings through to `area_code`, to avoid the KNIME-style type mismatch the listings notebook describes.
- **Secrets out of git.** The Koordinates key is an environment variable via `.dotenv`.
- **Checkpointed geocoding.** Partial CSVs are written every 500 unique coordinates so an API drop does not waste a full run.
- **Narrative notebooks.** Cleaning decisions are written as markdown next to the code (why 0 reviews/month, why `-99` is dropped, why a left join). That is documentation for the course write-up; it is not a substitute for the assertions in section 4.3.

---

## 6. Honest summary of mismatches

| Claim one might want to make | What is actually true |
| --- | --- |
| “The pipeline uses relative paths throughout.” | False. `bond_listing_clean.Rmd` hardcodes `/Users/nalikadesai/Desktop/DATA201` twice. |
| “Bond cleaning writes the file the join reads.” | Filenames disagree (`Bond Data Quarterly (cleaned).csv` vs `Bond_Data_Quarterly_(cleaned).csv`). |
| “kNN parameters are named constants at the top of each file.” | False. `k = 10` and `k = 5` are inline. `Pool(processes=20)` is inline. |
| “Validation fails the knit if a check fails.” | Mostly false. Duplicate keys and join row-counts are printed with “expect 0/TRUE”. |
| “API failures stop the geocoder.” | False. They become `None` area codes. Missing API **key** does raise. |
| “We hand-checked one case before scaling.” | True for Redcliffs → `332100` (README). Not implemented as code, and not done for kNN or the join. |
| “The analysis notebook is a single knit.” | The source currently duplicates the whole document. |

The pipeline’s **data** design (character IDs, keep raw price, left join, weekly/nightly unit conversion, `has_bond_data`) is coherent. The **software** design matches the lecture on paths and assertions only in parts; the bond-cleaning notebook is the largest gap.
