# Deliverable 6: what we changed and why

We went back over our code using the Week 9 lecture ideas: relative file paths, settings
at the top of each file, checks that stop the code, and sanity checking one row by hand.

Where to find each part of Deliverable 6:

| Task | Where |
| --- | --- |
| 1. Revisit the code | The Rmd files and `get_area_codes.py` |
| 2. Notes on what changed and why | This file |
| 3. Sanity check example | `README.md`, section "Sanity Check Example" |
| 4. Design principles document | `design_principles.md` |
| 5. Document vs code check | `design_principles.md`, section 6 |

## Answers before and after

| | Deliverable 5 | Deliverable 6 |
|---|---|---|
| Q1: median Airbnb price, Christchurch Central | $238 | **$236** |
| Q1: median Airbnb price, all of Christchurch | $205 | $211 |
| Q2: area with the largest gap | 332700 Heathcote, $255 | 332700 Heathcote, **$259** |
| Q3: Airbnbs per 100 long-term rentals | 8 | **7** |

The conclusions did not change. The numbers moved a little because of the fixes in
section 5.

## 1. Relative file paths

| What we changed | Why |
| --- | --- |
| `bond_listing_clean.Rmd` used `/Users/nalikadesai/Desktop/DATA201`. It now uses the repo folder. | The lecture says never use a path from your own computer. The file only ran on one laptop. |
| The bond Rmd now saves `Bond_Data_Quarterly_(cleaned).csv`, the name the join reads. | It saved a different name, so rerunning it never updated the file the join uses. |
| The bond CSV was rebuilt from the code. | The saved file came from an older version of the code and still had 94 rows with no area. |

## 2. Settings at the top of each file

| What we changed | Why |
| --- | --- |
| Each file now starts with one or two lines saying what it reads and writes. | The lecture's "file header": a reader knows what the file is for before reading the code. |
| Numbers that control the code are named once at the top, e.g. `price_max <- 2000`, `knn_k <- 10`, `long_stay_nights <- 30`, `days_per_week <- 7`, `N_PROCESSES = 20`. | The lecture says no "magic numbers". A named setting says what the number means and is easy to change. The full list is in `design_principles.md`, section 4.2. |

## 3. Checks that stop the code

| What we changed | Why |
| --- | --- |
| Checks written as a printed number with `# expect 0` are now `if (...) stop("...")`. | The lecture says to use assertions instead of comments. A printed number is easy to miss, but `stop()` ends the knit, so a bad join or a duplicate row cannot pass silently. |
| `get_area_codes.py` now stops with an error if any listing has no area code (after saving its file). | Before, a failed lookup quietly became a blank area code. |
| Bond `Location Id` is read as text. | Read as a number, area 200000 was saved as `2e+05`. Area codes are labels, the same lesson as the listing `id`. |

## 4. Sanity checks: one row worked out by hand

Nalika's sanity check example (in the README) checks the geocoding step with one known
Redcliffs listing. We built on it:

| What we changed | Why |
| --- | --- |
| The Redcliffs check now runs in `get_area_codes.py` at the start of every run. It stops if the answer is not `332100`. | Done by hand once, it only protected that one run. In code, it catches a swapped latitude and longitude every time. |
| `clean_christchurch_panel.Rmd` checks one listing's filled price by hand: real prices 450, 450, 490, 614, 615, 741, so the median is (490 + 614) / 2 = $552. | This is the lecture's "calculate and compare" for the price-filling step. |
| `join_listings_bonds.Rmd` checks that one Central listing in April 2026 has the same bond values as the raw bond report (42 active bonds, $537 rent). | This checks the join against the original data, not against our own cleaned file. |

## 5. Data fixes we found while checking

**Filled prices (`clean_christchurch_panel.Rmd`).** kNN filled missing prices by copying
from similar listings. It cannot tell apart listings from the same host at the same
address, so one host's 7 listings, from 2-bedroom flats to 4-bedroom townhouses, all got
$213 for December. This happened to 564 prices. Now a missing price is filled with the
listing's own median price first, and kNN is only used for listings that never show a
price.

**Medians count each listing once (`airbnb_vs_rentals.Rmd`).** Before, a listing seen in
six months counted six times. Now each listing gets one price (its own median) before we
take the median. This moved Central from $238 to $236. Leaving out the host with 7
listings does not change it.

**Question 3 counts Airbnbs in one month.** Active bonds count rentals at one point in
time, so we now count the Airbnbs listed in June 2026. Before, we counted every listing
seen in April, May or June. This moved 8 per 100 to 7.

**Bed counts in the bond data (`bond_listing_clean.Rmd`).** A blank bed count is its own
group: bonds where the bedrooms were not recorded. kNN gave them a bed count the area
already had, which made 779 duplicate rows. The Rmd said "No duplicate rows", but its
own check printed 779. They are now labelled "Not recorded", and a check stops the run
on any duplicate.

**Result numbers come from the code.** Numbers in the result text are now written with
inline R. The hand-typed table of why some rows have no bond data turned out to be wrong
(522 where it should be 61).

## 6. Fixing the merge

When Nalika's work was merged, `airbnb_vs_rentals.Rmd` ended up with the whole analysis
twice and would not knit ("Duplicate chunk label 'setup'"). We kept one copy, the
Deliverable 6 version, and added back the two notes from the second copy: the Banks
Peninsula caveat and "bedrooms cannot be compared".

## 7. Considered but not changed

- **Separate `data/`, `src/` and `out/` folders.** The lecture recommends this. Moving the
  files now would break teammates' file paths in the middle of the project, so we kept
  one folder.
- **File names with spaces**, such as `Christchurch Oct2025 to Jun2026 (cleaned).csv`.
  Renaming would also break other files. We will use plain names for new files.
- **Month names and quarter dates written out in full.** A loop would be shorter, but the
  team agreed on simple code that everyone can read.
- **Rent includes rooms.** Question 2 compares whole-home Airbnbs with rent for all
  dwelling types. House-only rents exist for most areas, so this is our next improvement.
