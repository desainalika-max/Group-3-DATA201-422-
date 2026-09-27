> **AI used.** The first draft of this document was produced with **Cursor**, from the
> code as it was before the Deliverable 6 fixes. It was then updated with **Claude
> (Claude Opus 5.5, in Claude Code)** so that it matches the code after the fixes.
> Section 6 lists every place where the first draft and the code disagreed, and how
> each one was fixed.

# Design principles for the Christchurch Airbnb–bond pipeline

This document describes the pipeline that turns Inside Airbnb listings and Tenancy
Services bond data into the answers in `airbnb_vs_rentals.Rmd`. It covers the inputs,
the outputs, the main steps, and the coding practices from the Week 9 lectures that
the code follows.

The files run in this order:

1. `clean_christchurch_panel.Rmd`
2. `get_area_codes.py` (only when listing coordinates change, because it needs an API key)
3. `bond_listing_clean.Rmd`
4. `join_listings_bonds.Rmd`
5. `airbnb_vs_rentals.Rmd`

---

## 1. Inputs

| Input | Source | Used by |
| --- | --- | --- |
| `Christchurch Oct2025 to Jun2026 (combined).csv` | Nine Inside Airbnb monthly `listings.csv` files, Christchurch rows only, stacked in Deliverable 3 | `clean_christchurch_panel.Rmd` |
| `Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv` | MBIE Tenancy Services detailed quarterly bond report | `bond_listing_clean.Rmd`, and `join_listings_bonds.Rmd` for its checks |
| Koordinates Query API, layer `123515` (Stats NZ SA2 2026) | Online service. The key is kept in `.env`, not in git | `get_area_codes.py` |

The input files are never edited by hand. Every change is made by code.

## 2. Outputs

### Files made along the way

| File | Made by | What it is | Used by |
| --- | --- | --- | --- |
| `Christchurch Oct2025 to Jun2026 (cleaned).csv` | `clean_christchurch_panel.Rmd` | One row per listing per month, with fixed types, filled prices and flags | `get_area_codes.py`, `bond_listing_clean.Rmd` (for its date range), `join_listings_bonds.Rmd` |
| `Christchurch_with_area_codes.csv` | `get_area_codes.py` | The listings plus an `area_code` column | `join_listings_bonds.Rmd`, which takes only `area_code` |
| `Bond_Data_Quarterly_(cleaned).csv` | `bond_listing_clean.Rmd` | Bond rows for the three quarters that overlap the listings | `join_listings_bonds.Rmd` |
| `Christchurch_with_bonds.csv` | `join_listings_bonds.Rmd` | Each listing-month with its area's bond totals for that quarter | `airbnb_vs_rentals.Rmd` |

Each Rmd also knits to an HTML report with the same name.

### Final answers (`airbnb_vs_rentals.html`)

1. Median Airbnb price in Christchurch Central (SA2 `326600`): **$236 a night**, against
   $211 for all of Christchurch. Each listing is counted once.
2. Largest gap between an Airbnb whole home and long-term rent: **area `332700`,
   Heathcote Ward, $259 a night** ($347 Airbnb against $89 rent).
3. Airbnbs per 100 long-term rentals, June 2026: **7**. Christchurch Central has 283.

These numbers are printed by the code (inline R), not typed into the text.

## 3. Main steps

```
combined listings CSV
        │
        ▼
clean_christchurch_panel.Rmd
  • read ids as text
  • drop the empty license column
  • months as an ordered factor, plus a real date
  • 0 reviews a month for listings with no reviews
  • fill host_name and minimum_nights from the same listing
  • price: the real price, else the listing's own median price,
    else kNN (only for listings that never show a price)
  • flags: price_was_imputed, price_source, in_all_9_months, long_stay
  • check by hand: one townhouse's filled price is its own median ($552)
        │
        ▼
cleaned listings CSV ─────────────────────────┐
        │                                     │
        ▼                                     │
get_area_codes.py                             │
  • check first: Redcliffs must be 332100     │
  • look up each unique coordinate            │
  • save progress every 500 coordinates       │
  • stop if any listing has no area code      │
        │                                     │
        ▼                                     │
listings + area_code CSV                      │
                                              │
quarterly bonds CSV                           │
        │                                     │
        ▼                                     │
bond_listing_clean.Rmd                        │
  • keep the quarters that overlap the listings
  • drop blank and -99 (all of NZ) Location Ids
  • blank bed counts become "Not recorded"    │
  • stop if two rows share the same key       │
        │                                     │
        ▼                                     ▼
cleaned bonds CSV ──────────►  join_listings_bonds.Rmd
                                 • attach area_code by listing id and month
                                 • give each month its quarter
                                 • keep the one "ALL"/"ALL" total per area and quarter
                                 • left join on area_code + quarter
                                 • check by hand: one Central listing's bond row
                                   matches the raw bond report
                                              │
                                              ▼
                                 Christchurch_with_bonds.csv
                                              │
                                              ▼
                                 airbnb_vs_rentals.Rmd
                                   one price per listing, then:
                                   Q1 Central median price
                                   Q2 largest nightly gap
                                   Q3 Airbnbs per 100 rentals
```

Design choices that later steps rely on:

- **IDs are text.** Listing `id`, `host_id`, `area_code` and `Location Id` are read as
  text, so long numbers are not rounded and area 200000 is not saved as `2e+05`.
- **Keep the original, flag the guess.** `price` is never overwritten. The filled value
  goes in `price_imputed`, and `price_was_imputed` and `price_source` say how it was filled.
  The answers use real prices only.
- **Monthly to quarterly.** Each listing month gets the first day of its quarter, so it can
  join to the bond `TimeFrame`.
- **Left join.** Every Airbnb row is kept. Rows with no bond data are flagged with
  `has_bond_data`, and section 6 of the join Rmd counts why.
- **Units.** Rents are weekly and prices are per night, so rent is divided by
  `days_per_week` (7) before comparing.
- **One listing, one vote.** Medians first take each listing's own median, so a listing
  seen in six months does not count six times.

---

## 4. Coding practices from the lectures

### 4.1 Relative file paths

**Lecture:** never use a path from your own computer. Use paths relative to the project
folder, so the code runs on anyone's computer.

**The code:** every file reads and writes in the repo folder (`data_dir <- "."` in the
cleaning Rmds, plain file names elsewhere). There is no `/Users/...` path anywhere. The
bond Rmd writes `Bond_Data_Quarterly_(cleaned).csv`, the same name the join reads.

### 4.2 No magic numbers: settings at the top

**Lecture:** give numbers that control the code a name, and set them at the top of the
file.

**The code:** each file starts with a short description, then a `settings` block:

| File | Settings |
| --- | --- |
| `clean_christchurch_panel.Rmd` | `price_max` (2000), `knn_k` (10), `long_stay_nights` (30), `random_seed` (2026) |
| `bond_listing_clean.Rmd` | `national_total_id` (-99) |
| `get_area_codes.py` | `LAYER_ID`, `N_PROCESSES` (20), `TIMEOUT_SECONDS` (15), `CHECKPOINT_EVERY` (500), and the Redcliffs check point |
| `airbnb_vs_rentals.Rmd` | `central_area` ("326600"), `big_host`, `min_listings` (20), `count_month` ("June 2026"), `days_per_week` (7) |

The nine month names and the three quarter dates are still written out in full. We kept
them that way on purpose, because the team agreed to write simple code that every member
can read.

### 4.3 Checks that stop the code, not comments

**Lecture:** instead of a comment such as "must not have duplicates", write a check that
stops the code with an error.

**The code:** every check that used to be a printed number with `# expect 0` is now an
`if (...) stop("...")`, for example:

```r
if (anyDuplicated(airbnb[, c("id", "month_year")]) > 0) {
  stop("A listing appears twice in the same month")
}
```

Checks like this cover: the input file exists, every row has a price after filling, one
row per listing per month, one bond row per key, one bond total per area and quarter,
every listing gets an area code and a quarter, and the join does not add rows.

`get_area_codes.py` also stops with an error if any listing has no area code. It saves
its file first, so the API calls already made are not lost.

### 4.4 Sanity check one row by hand

**Lecture:** work out the answer for one row by hand and compare it with what the code
gives.

**The code:** there are three one-row checks, and each one stops the run if it fails.

| Step | Row checked | Worked out by hand |
| --- | --- | --- |
| Area codes (`get_area_codes.py`) | The "Relaxing Redcliffs" listing | Must be area `332100`, Redcliffs. A swapped latitude and longitude gives a different answer. Also described in the README. |
| Price filling (`clean_christchurch_panel.Rmd`) | The 4-bedroom townhouse, December 2025 | Real prices 450, 450, 490, 614, 615, 741, so the median is (490 + 614) / 2 = $552 |
| Join (`join_listings_bonds.Rmd`) | One Central (326600) listing, April 2026 | Its bond values must equal the raw report's "ALL"/"ALL" row for 326600 in the 2026-04-01 quarter (42 active bonds, $537 weekly rent) |

### 4.5 File headers

**Lecture:** start each file with a line or two about what it does, then its settings,
packages and inputs.

**The code:** every file starts with one or two lines naming its input and output files,
followed by its settings block and its packages.

---

## 5. Other choices the project makes

- **Secrets stay out of git.** The API key is read from `.env`, which is in `.gitignore`.
- **Checkpointed geocoding.** Progress is saved every 500 coordinates.
- **Narrative notebooks.** The Rmds explain why each cleaning decision was made (why 0
  reviews a month, why -99 is dropped, why a left join). The explanations sit next to the
  code, and the checks in section 4.3 back them up.

---

## 6. Mismatches found and fixed (Deliverable 6)

We compared the first draft of this document with the code and with what we meant the
code to do. Every mismatch below has been fixed.

| What we wanted | What the code actually did | Fix |
| --- | --- | --- |
| Relative paths throughout | `bond_listing_clean.Rmd` used `/Users/nalikadesai/Desktop/DATA201`, twice | Paths are relative to the repo folder |
| The bond Rmd writes the file the join reads | It wrote `Bond Data Quarterly (cleaned).csv`; the join reads `Bond_Data_Quarterly_(cleaned).csv` | The file names now match |
| Numbers named at the top | `k = 10`, `k = 5`, `2000`, `30`, `-99`, `7`, `processes=20`, `timeout=15`, `500` sat inside the code | Named in a settings block at the top of each file |
| Checks stop the run | Checks printed a number with `# expect 0` and carried on | `if (...) stop("...")` |
| A failed area-code lookup is noticed | It quietly became a blank area code | The script stops with an error, after saving |
| The Redcliffs check protects the geocoder | It was done once by hand and only written in the README | It runs in code at the start of every run |
| The analysis notebook is one document | After a merge it held the whole analysis twice and did not knit ("Duplicate chunk label 'setup'") | One copy, keeping the Banks Peninsula caveat and the bedrooms note from the second copy |
| One bond row per area, quarter, dwelling type and bed count (the Rmd said "No duplicate rows") | kNN gave blank bed counts a value the area already had: 779 duplicate rows, and 44 areas with two "ALL" totals | Blank bed counts are labelled "Not recorded", and a check stops the run on any duplicate |
| Filled prices look like each listing's real prices | kNN copied one price to all of a host's listings at one address (7 listings from 2 to 4 bedrooms all got $213): 564 copied prices | Each listing's own median price first; kNN only for listings that never show a price. 32 copies are left, all in the kNN rows |
| "Median Airbnb price" counts each Airbnb once | Medians counted listing-months, so a listing seen in six months counted six times | Each listing's own median first, then the median across listings |

### Known gaps we have not fixed

- **Rent includes rooms.** The bond "ALL" totals include rooms and boarding houses, while
  question 2 uses whole-home Airbnbs, so the gap is probably a little larger than a
  whole-home-to-whole-home comparison would give. The bond file does have house-only
  rents for 110 of the 114 Christchurch areas in April to June 2026, so this can be
  improved. We kept the all-dwelling total for now so the answer stays comparable with
  Deliverable 5, and list it as the next improvement.
- **Folder structure.** The lecture suggests separate `data/`, `src/` and `out/` folders.
  The repo keeps everything in one folder, so that teammates' file paths do not break
  in the middle of the project.
