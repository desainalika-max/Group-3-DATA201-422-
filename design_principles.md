# Design principles for the Christchurch Airbnb–bond pipeline

**Cursor was used to produce this document.** The file was drafted in Cursor against the current source (`clean_christchurch_panel.Rmd`, `bond_listing_clean.Rmd`, `get_area_codes.py`, `join_listings_bonds.Rmd`, `airbnb_vs_rentals.Rmd`). Claims below were checked against that code, not inferred from the README alone.

The pipeline joins monthly Inside Airbnb listings for Christchurch with quarterly Tenancy Services bond data, then answers three comparison questions. Scripts are meant to be run from the **project root** (the repository folder).

---

## 1. Inputs

| File | Role | Consumed by |
| --- | --- | --- |
| `Christchurch Oct2025 to Jun2026 (combined).csv` | Concatenated monthly Inside Airbnb listings (Oct 2025 – Jun 2026) | `clean_christchurch_panel.Rmd` |
| `Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv` | Tenancy Services detailed quarterly bond report | `bond_listing_clean.Rmd`; also used as a **raw** lookup in the join sanity check |
| `Christchurch Oct2025 to Jun2026 (cleaned).csv` | Cleaned listings panel (intermediate) | `bond_listing_clean.Rmd` (date range only); `get_area_codes.py` |
| `Christchurch_with_area_codes.csv` | Listings plus Stats NZ SA2 codes | `join_listings_bonds.Rmd` |
| `Bond_Data_Quarterly_(cleaned).csv` | Cleaned bond table | `join_listings_bonds.Rmd` |
| `Christchurch_with_bonds.csv` | Joined listing–bond table | `airbnb_vs_rentals.Rmd` |
| `.env` with `KOORDINATES_API_KEY` | Koordinates vector-query key | `get_area_codes.py` |

External services: Koordinates vector query API, layer `123515` (SA2 2026 codes). That layer id is a named constant in Python (`LAYER_ID`), not a path.

Raw source files are expected to sit in the **same folder as the scripts**. There is no `data/` subdirectory.

*Deliverable 7 update:* the code is now in `src/`, the downloaded files in `data/` and everything the code makes in `output/`. The scripts keep their names and are still run from the project root (see `Deliverable7_changes.md`).

---

## 2. Outputs

| File | Produced by | Contents |
| --- | --- | --- |
| `Christchurch Oct2025 to Jun2026 (cleaned).csv` | `clean_christchurch_panel.Rmd` | Cleaned panel: character ids, ordered months, filled nights, `price_imputed` / `price_was_imputed`, panel flags |
| `Bond_Data_Quarterly_(cleaned).csv` | `bond_listing_clean.Rmd` | Bonds filtered to the listings window; national total dropped; missing bed counts imputed; `beds_was_imputed` |
| `Christchurch_with_area_codes.csv` | `get_area_codes.py` | Cleaned listings plus `area_code` (SA2). Written incrementally as a checkpoint, then again at the end |
| `Christchurch_with_bonds.csv` | `join_listings_bonds.Rmd` | Left-joined listing rows with area-level quarterly bond totals and `has_bond_data` |
| Knitted HTML | each `.Rmd` | Narrative, tables, and (in the analysis file) plots |

The analysis notebook does not write a new CSV. Its “outputs” are the three Deliverable 5 answers (median Central price, largest short- vs long-term gap, Airbnbs per 100 rentals) and two plots.

**Mismatch with the README (flagged, not papered over):** the README states that the saved bond CSV was produced by an **older** version of `bond_listing_clean.Rmd` and was **not re-run**, so `Bond_Data_Quarterly_(cleaned).csv` on disk may not match what the current notebook would write. The design of the pipeline is “knit this file → get that CSV”; the checked-in bond file is allowed to lag that design.

---

## 3. Main steps

Run in this order, from the project root.

```
combined listings CSV
        │
        ▼
clean_christchurch_panel.Rmd  ──►  cleaned listings CSV
        │                                    │
        │                                    ├──►  bond_listing_clean.Rmd  ──►  cleaned bonds CSV
        │                                    │              (uses listings only for min/max month_date)
        │                                    │
        │                                    └──►  get_area_codes.py  ──►  listings + SA2 codes
        │                                                                      │
        └──────────────────────────────────────────────────────────────────────┤
                    raw bond CSV (sanity check only)                           │
                                                                               ▼
                                                         join_listings_bonds.Rmd
                                                                               │
                                                                               ▼
                                                         Christchurch_with_bonds.csv
                                                                               │
                                                                               ▼
                                                         airbnb_vs_rentals.Rmd
```

1. **Clean the Airbnb panel** (`clean_christchurch_panel.Rmd`). Read ids as character. Drop the empty `license` column. Order months. Treat zero-review `reviews_per_month` as 0. Carry `host_name` and `minimum_nights` within id/host. Treat prices above `price_max` as missing and fill `price_imputed` with kNN (`k = knn_k`). Add `in_all_9_months` and `long_stay`.

2. **Clean the bond table** (`bond_listing_clean.Rmd`). Keep quarters whose three-month span overlaps the cleaned listings dates (not a hardcoded quarter list). Drop missing `Location Id` and the national rollup (`national_total_id`). Impute missing `Number Of Beds` with kNN (`k = knn_k`).

3. **Attach SA2 codes** (`get_area_codes.py`). Query unique coordinates in parallel (`N_PROCESSES`), checkpoint every `CHECKPOINT_EVERY` lookups, map codes back onto all listing rows.

4. **Join** (`join_listings_bonds.Rmd`). Map each listing month to a quarter start date. Keep bond rows that are genuine area totals (`Dwelling Type` and `Number Of Beds` both `"ALL"`, and `beds_was_imputed == FALSE`). Left-join listings to those totals on `area_code` and `quarter`. Check one Central listing against the **raw** bond file.

5. **Analyse** (`airbnb_vs_rentals.Rmd`). Median observed price in area `central_area`; gap between entire-home Airbnb price and weekly rent / `days_per_week`, ranked with `min_listings`; Airbnb counts vs `bond_active` in `latest_quarter`.

---

## 4. Coding and software strategies

These match the Week 9 lecture points we were asked to apply: **project-relative paths**, **named parameters instead of magic numbers**, **assertions that fail loudly**, and **code that can be run from the project root on another machine**. Each subsection states the intended rule, then what the code actually does.

### 4.1 Relative paths, not personal machine paths

**Lecture:** never hardcode a path tied to one computer; use paths relative to the project root so the pipeline runs unchanged on another machine.

**What the code does (follows this):**

- No script currently contains a `/Users/...` (or other absolute) path.
- `clean_christchurch_panel.Rmd` and `bond_listing_clean.Rmd` set `data_dir <- "."` and build paths with `file.path(...)`. Comments state that `.` is the repo folder.
- `get_area_codes.py` uses `"Christchurch Oct2025 to Jun2026 (cleaned).csv"` and `"Christchurch_with_area_codes.csv"` as relative names, and the header says to run it from the repo folder.
- `join_listings_bonds.Rmd` and `airbnb_vs_rentals.Rmd` use bare relative filenames (`"Christchurch_with_bonds.csv"`, and so on).

**Where it is incomplete or inconsistent:**

- The first two Rmds use `data_dir` + `file.path`; the join and analysis notebooks do not. All of those strings are still relative, so this is a **style inconsistency**, not a return to machine-specific paths.
- Relative paths only work if the working directory **is** the project root. That is true when you Open Folder / knit from the repo. It is not encoded as something like `here::here()` or a path relative to the script file. If someone knits an Rmd or runs the Python script from another working directory, the same relative names will fail.
- File names contain spaces (`Christchurch Oct2025 to Jun2026 (cleaned).csv`). That is awkward but portable; the README notes the team chose not to rename them mid-project.

**Honest summary:** the pipeline **does** follow the lecture on this point in the way that mattered (the old Nalika-laptop absolute path in `bond_listing_clean.Rmd` is gone). It does **not** use a robust project-root helper, and path construction is not the same in every file.

### 4.2 Avoiding magic numbers

**Lecture:** parameters such as *k* in kNN, or the number of parallel processes, should be named. Visible constants belong near the top of the file, not unexplained numbers in the middle of a call.

**What the code does (follows this in the places the lecture named):**

| File | Named constants at the top |
| --- | --- |
| `clean_christchurch_panel.Rmd` | `price_max`, `knn_k`, `long_stay_nights`, `random_seed` |
| `bond_listing_clean.Rmd` | `national_total_id`, `knn_k`, `random_seed` |
| `get_area_codes.py` | `LAYER_ID`, `N_PROCESSES`, `TIMEOUT_SECONDS`, `CHECKPOINT_EVERY` |
| `airbnb_vs_rentals.Rmd` | `central_area`, `min_listings`, `latest_quarter`, `days_per_week` |

kNN calls use `k = knn_k`. The process pool uses `processes=N_PROCESSES`. Those are the examples the lecture called out, and they are named.

**Where magic numbers remain (flagged):**

- **Quarter length** in `bond_listing_clean.Rmd`: `TimeFrame %m+% months(3) - days(1)`. The `3` is the length of a quarter and is not a named constant.
- **Month → quarter map** in `join_listings_bonds.Rmd`: dates `"2025-10-01"`, `"2026-01-01"`, `"2026-04-01"` and the month-name groups sit in a `case_when` in the body, not in the settings chunk. `bond_listing_clean.Rmd` derives quarters from the listings date range; the join **hardcodes** the same calendar. If the panel window changed, the bond filter would move and the join map would not.
- **Sanity-check identifiers** in `join_listings_bonds.Rmd`: `"326600"` and `"April 2026"` are literals. The analysis file names the same area as `central_area`; the join does not reuse that name.
- **`LAYER_ID = 123515`** is named (good) but not explained in a comment (which Stats NZ layer / vintage).
- **Plot chrome** in `airbnb_vs_rentals.Rmd`: `par(mar = c(5, 11, 2, 1))` and `head(5)` are unexplained numbers. They do not change the three numeric answers, but they are still magic numbers by the lecture definition.
- **`in_all_9_months`** is computed as `months_present == length(month_levels)` (the `9` is not used in the comparison — good), but the **column name** still hardcodes nine months.

**Honest summary:** the parameters that used to be buried (`2000`, `10`, `30`, `5`, `20` processes, `7` days) **are** now named at the top. The pipeline is **not** free of unexplained numbers, especially dates and plot/table cuts.

### 4.3 Self-documenting code and assertions over comments

**Lecture:** prefer code that fails loudly (`stop()` / `raise`) over comments that describe an expectation without enforcing it.

**What the code does (follows this in several high-risk places):**

- Missing inputs: `clean_christchurch_panel.Rmd` and `bond_listing_clean.Rmd` call `stop(...)` if `in_file` / `listings_file` is absent.
- kNN leftover NAs: listings cleaning `stop`s if `price_imputed` still has `NA`.
- Panel key: listings cleaning and the analysis `stop` if `(id, month_year)` is duplicated.
- Join integrity: `stop` if any month has no quarter; `stop` if bond totals are duplicated on `(area_code, quarter)`; `stop` if the left join changes the row count; `stop` if the hand-checked Central row disagrees with the raw bond report.
- Area codes: after the API loop, `get_area_codes.py` `raise`s `ValueError` if any listing still has no code. `KOORDINATES_API_KEY` is read with `os.environ[...]`, which fails immediately if the key is missing.

Those are real assertions: a bad knit or run **stops**, it does not print `# expect 0` and continue.

**Where comments still outrun the code (flagged):**

- **`bond_listing_clean.Rmd` validation does not `stop`.** It prints `sum(duplicated(...))` and `colSums(is.na(...))`. The prose under that chunk says there are no duplicate rows on the natural key and no missing values remain. The README for Deliverable 6 says the duplicate check **prints 779** because kNN can fill bed counts as `"ALL"` and collide with real totals. That is exactly the lecture anti-pattern: a comment/narrative claims “none”, the number is not zero, and the knit still succeeds. The join later **does** drop imputed `"ALL"` rows, so the three analysis answers are protected; the bond-cleaning notebook itself is not.
- **No `stop` after bond kNN** if `Number Of Beds` is still `NA` (listings cleaning has the equivalent stop for price).
- **`join_listings_bonds.Rmd` and `airbnb_vs_rentals.Rmd` do not check `file.exists`.** A missing CSV fails inside `read_csv` with a generic error, not the explicit “Cannot find the input file” used in the first two notebooks.
- **Coordinate bounds** in listings cleaning are printed (`range(latitude)`, `range(longitude)`) and described in prose as Christchurch. They are **not** asserted with `stop`.
- **`get_area_codes.py` swallows per-coordinate failures** (`except Exception: ... return None`) and only fails after the full run. That is deliberate (checkpoint and retry), but a single failed lookup does not fail loudly at the moment it happens.
- R Markdown files are full of explanatory comments. That is appropriate for a marked report. The lecture point is not “no comments”; it is “do not substitute a comment for a check”. The bond duplicate paragraph is the place that still does that.

**Honest summary:** assertions were added where a silent failure would corrupt the join or the answers. They are **not** applied uniformly. The largest gap is `bond_listing_clean.Rmd`, whose own narrative over-claims what the checks enforce.

### 4.4 Runnable from the project root on another machine

This is the same lecture idea as 4.1, applied to the whole pipeline.

**What works without editing code:**

- Clone the repo, put the two raw CSVs in the project root (or keep them if they are already there), add `.env` with `KOORDINATES_API_KEY`, install the R packages and `pandas` / `requests` / `python-dotenv`, knit/run in order from that folder.

**What still ties a run to extra setup (not a hidden path, but not “zero modification” either):**

- The Koordinates key is machine-specific by necessity; it is correctly kept out of the repo via `.env`.
- `get_area_codes.py` hits a live API. Re-running it is slow and not deterministic if the service fails; the checkpoint file is the recovery mechanism.
- Knitting assumes the previous step’s CSV is already in the root. There is no Makefile or driver script; order is documented in notebook subtitles and this file.

---

## 5. Cross-check: this document vs the code

| Claim | Matches the code? |
| --- | --- |
| Inputs and outputs listed in sections 1–2 | Yes, for the five scripts named in the brief |
| Run order in section 3 | Yes |
| No personal absolute paths | Yes, in the current source |
| Named kNN *k*, process count, price cap, long-stay threshold, days per week | Yes |
| Every numeric parameter named at the top | **No** — quarter length, join dates, sanity-check area, `head(5)`, plot margins |
| Every expectation enforced with `stop`/`raise` | **No** — bond duplicate/NA checks print only; join/analysis skip `file.exists`; lat/long not asserted |
| Bond CSV on disk equals current `bond_listing_clean.Rmd` | **Not guaranteed** — README says it was not re-run after code edits |
| Bond cleaning has no duplicate keys | **No** — README reports 779 duplicates; join filters them out of the analysis |

If a later edit reintroduces an absolute `/Users/...` path, or removes a `stop()`, this file would be out of date. Re-check the five sources rather than assuming the strategies still hold.
