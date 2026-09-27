

# Data Divas


## Team
- Sudheesh
- Nalika
- Dian Qiu
- Agar
- Jonah

## Dataset

**Source:** [Inside Airbnb](https://insideairbnb.com/get-the-data/) - **listings.csv**, New Zealand, June 2026

## Column Descriptions
| Column | Description |
| --- | --- |
| **id** | Unique identifier for the listing |
| **name** | Listing title |
| **host_id** | Unique identifier for the host |
| **host_name** | Host's first name |
| **neighbourhood_group** | Broader region grouping |
| **neighbourhood** | Suburb/area of the listing |
| **latitude**                        | Geographic coordinate (north-south position) |
| **longitude**                       | Geographic coordinate (east-west position)   |
| **room_type** | Entire home/apt, Private room, Shared room, or Hotel room|
| **price** | Nightly price (NZD) |
| **minimum_nights** | Minimum stay required |
| **number_of_reviews** | Total reviews received |
| **last_review** | Date of most recent review |
| **reviews_per_month** | Average review frequency |
| **calculated_host_listings_count** | Number of listings this host manages |
| **availability_365** | Days available for booking in the next year |
| **number_of_reviews_ltm** | Reviews received in the last 12 months |
| **license** | Registration/license number, if applicable |

## Snapshot Date & "Days Since Last Review"

The dataset is a **snapshot of Airbnb listings taken on 22 June 2026** this is the scrape date.

To calculate how long ago a listing's last review was, we count backwards from the snapshot date:

### Why the snapshot date matters

- **Initial issue:** the snapshot date was first set to `13 June`, but the dataset actually contains reviews dated up to `22 June`. Any review after `13 June` (e.g. `16 June`) produced a **negative** result:

- This happened because we were measuring backwards from a date that hadn't occurred yet relative to some reviews.

- **Fix:** setting the snapshot date to `22 June` (the true scrape date) ensures every review falls on or before that date, so all `days_ago` values come out zero or positive.

- **Why 22 June is correct:** it matches the most recent review date found in the dataset, confirming it as the actual day the scrape occurred.

## How to rerun everything

All files read and write in the repo folder, so open the repo folder (or knit in RStudio) and run them in this order:

1. `clean_christchurch_panel.Rmd`: cleans the Airbnb panel and writes `Christchurch Oct2025 to Jun2026 (cleaned).csv`
2. `bond_listing_clean.Rmd`: cleans the bond data and writes `Bond_Data_Quarterly_(cleaned).csv`
3. `join_listings_bonds.Rmd`: adds area codes and bond totals, writes `Christchurch_with_bonds.csv`
4. `airbnb_vs_rentals.Rmd`: answers the three questions

`get_area_codes.py` looks up the area code of every coordinate online and needs an API key in `.env`. It only needs to run again if listing coordinates change, because `join_listings_bonds.Rmd` takes just the `area_code` column from its output.

Each file stops with an error if one of its checks fails, so a knit that finishes has passed all of them.

What changed in Deliverable 6, and why, is in the section "Deliverable 6: what we changed and why" at the end of this README (also saved as `Deliverable6_changes.md`). How the pipeline is designed is in `design_principles.md`.

## Cleaning the Airbnb Listings

**Source:** Deliverable 3 concatenated panel, Inside Airbnb, Christchurch, Oct 2025 – Jun 2026
**Cleaning script:** `clean_christchurch_panel.Rmd`
**Output:** `Christchurch Oct2025 to Jun2026 (cleaned).csv`

### Column changes

| Column | Change | Reason |
| --- | --- | --- |
| `id`                                | Read as character, not numeric                                           | The largest `id` is 17 digits. A double only holds ~15 significant digits reliably, so reading these as numbers would silently corrupt the last few. It's a label, never used in arithmetic.             |
| `host_id`                           | Read as character, not numeric                                           | Same reasoning as `id`: some host IDs are large enough to risk precision loss if stored as a number, so it's kept as a label instead.                                                                     |
| `license` | Dropped | 100% missing across all 28,795 rows |
| `month_year` | Converted to an ordered factor | As plain text, months sort alphabetically (April, August, December...), which breaks every grouped summary and chart. An explicit factor order fixes this. |
| `month_date` | Added | A real `Date` column alongside `month_year`, so month arithmetic and time-series joins work correctly. `month_year` stays as the display-order version. |
| `last_review` | Parsed to `Date` | Was read in as text |
| `reviews_per_month` | Missing values set to 0 | All 2,627 missing values belong to listings with `number_of_reviews == 0`. This is a structural zero, not a data gap, a listing with no reviews genuinely has 0 reviews per month. Imputing a market average would invent activity that never happened. `last_review` is left as `NA` for these rows, since there's no correct date to put there. |
| `host_name` | Filled within host, then labelled "Unknown" | One row was missing a host name. The same `host_id` appears 9 times and is named in the other 8, so the value is recovered with certainty rather than guessed. Any remaining true unknowns are labelled `"Unknown"` rather than left blank. |
| `minimum_nights` | Carried forward within listing as `minimum_nights_filled`; original kept | 37 gaps, each with a value present in an adjacent month for the same listing. Minimum nights is a host-set rule, not a market outcome, and changes rarely. Carrying it forward is safer than imputing. The raw `minimum_nights` column is kept unchanged alongside the filled version. |
| `price` | Filled as `price_imputed`, original kept, new `price_source` column | See below |
| `months_present`   | Added | Count of how many of the nine monthly snapshots this listing appears in. |
| `in_all_9_months`  | Added | TRUE if the listing appears in all nine monthly snapshots. Any month-over-month price comparison should either filter to this or explicitly note that it doesn't, otherwise real price movement gets mixed up with listings simply entering or leaving the panel. |
| `long_stay` | Added | Flags the 129 rows requiring 30+ nights minimum stay. A different market to nightly tourist rental, worth excluding from tourist-price analysis. |
| `name` | Whitespace trimmed | Minor cleanup, no rows affected structurally |

### Price: the one column that needed a real imputation decision

Two distinct missingness problems were found:

- **December 2025, January 2026 and February 2026 have no observed prices at all** the entire column is blank in those three months, not a sample of missing values. Confirmed against the raw Inside Airbnb monthly file for December, so this is a source limitation and not something introduced by the Deliverable 3 concatenation.
- **The other six months are 5–8% missing**, and this missingness is not random: among rows with a price, 0.5% have zero availability; among rows missing a price, 62% do. Airbnb seems to only calculate a price when a listing has open dates, so no availability means no price shown.

**Decision (updated in Deliverable 6):** a missing price is filled with the listing's **own median price** from the months it does have a real price (10,176 rows). Only listings with no real price in any month fall back to **kNN imputation** (`VIM::kNN`, k = 10, 518 rows), matching each listing to its 10 nearest neighbours on room type, coordinates, minimum nights, host listing count, and month. 27 implausible prices (above $2,000/night) are treated as missing first.

**Why it changed:** in Deliverable 4 kNN filled every gap. kNN cannot tell apart listings with the same host at the same address, so it copied one price across them: host 482671075's 7 listings at one Christchurch Central address, from 2-bedroom flats to 4-bedroom townhouses, all got $213 for December. 564 filled prices were copies like this. With the listing's own median first, only 32 remain, all in the kNN rows.

The original `price` column is kept unchanged. `price_imputed` holds the filled version. `price_was_imputed` flags every row that differs from the original, so any analysis can filter to observed-only prices if preferred. `price_source` says where each price came from: `observed`, `own median` or `kNN`.

### Known limitations

1. December 2025 – February 2026 have no observed prices, so imputed values in that window are the least reliable in the dataset.
2. The 518 kNN rows belong to listings that never show a real price, so they still rely on neighbours. Filled December–February prices come from each listing's other months, so they miss the summer peak and are probably a little low.
3. Imputation uncertainty isn't carried through, so any standard errors computed on `price_imputed` will be slightly too small.
4. Only 2,338 of 4,117 listings appear in all nine months, unbalanced panel, see `in_all_9_months`.

### How to use the output

- **Observed prices only:** filter `price_was_imputed == FALSE`
- **Balanced month-over-month comparisons:** filter `in_all_9_months == TRUE`
- **Tourist-market pricing:** exclude `long_stay == TRUE`


## Cleaning the Bond Dataset

**Source:** [Tenancy Services | Rental bond data](https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/), Detailed quarterly report, Jan 2020 – Apr 2026
**License:** Creative Commons Attribution 3.0 NZ, credited to the Ministry of Business, Innovation and Employment
**Cleaning script:** `bond_listing_clean.Rmd`
**Output:** `Bond_Data_Quarterly_(cleaned).csv`

Data comes from Tenancy Services' bond database, covering private-sector bonds lodged each month, listed by tenancy start date, using SA2-2019 area definitions from Statistics NZ. Fixed random rounding to base 3 and suppression of results under 5 bonds is applied by MBIE before release. Recent quarters are provisional due to an ongoing bond-system migration and may not be directly comparable with earlier periods.

### Column Descriptions

| Column | Description |
| --- | --- |
| **TimeFrame** | Quarter start date, based on tenancy start date |
| **Location Id** | SA2-2019 area code (Statistics NZ) |
| **Dwelling Type** | House / Apartment / Flat / Room / Boarding House / ALL |
| **Number Of Beds** | 0–9, "5+", "ALL" (rollup), or "Not recorded" |
| **Total Bonds** | Bonds lodged in the group |
| **Active Bonds** | Still ongoing |
| **Closed Bonds** | Ended |
| **Median Rent** | Weekly rent, median |
| **Geometric Mean Rent** | Median substitute. Avoids the plateauing effect of rents clustering at round numbers |
| **Upper Quartile Rent**                           | Synthetic 75th percentile, assumes log-normal distribution                           |
| **Lower Quartile Rent**                           | Synthetic 25th percentile, assumes log-normal distribution                           |
| **Log Std Dev Weekly Rent** | Spread of the log-rent distribution |

### Cleaning decisions

- **Timeframe:** matched dynamically against the cleaned listings file's actual date range, rather than hardcoded, so the filter stays correct if the listings panel is later edited. Three quarters overlap: 2025-10-01 (Oct–Dec 2025), 2026-01-01 (Jan–Mar 2026), 2026-04-01 (Apr–Jun 2026). No 2026-07-01 quarter exists yet, since bond data publishes a couple of months behind.
- **Columns:** every column is kept. `Total Bonds`, `Active Bonds`, `Closed Bonds` are the stock-side variables the merge needs; `Median Rent` and the other rent statistics are the price-side variables. Nothing was dropped, since next week's comparison needs both sides.
- **Location Id:** rows with a blank `Location Id`, or `Location Id == -99`, were dropped entirely. Blank rows also had no rent statistics, carrying no usable information. `-99` represents an "All of New Zealand" rollup rather than a real SA2 area, cannot be matched in a location-based merge, and would distort a location-level dataset if kept.
- **Number Of Beds (changed in Deliverable 6):** a blank bed count is its own group, bonds where the number of bedrooms was not recorded. 856 of the 858 blank rows sit next to their own "ALL" total row and have their own bond counts. They are now labelled `"Not recorded"`. In Deliverable 4 they were filled by kNN, which gave them bed counts the area already had and created 779 duplicate rows.

### Known limitations

1. `Location Id` is an SA2 area code, not a name. The listings get their SA2 area codes from `get_area_codes.py`, and the two are joined in `join_listings_bonds.Rmd`.
2. Bond data is quarterly while listings are monthly, so any merge will compare a single quarterly figure against up to three monthly listings figures.

### How to use the output

- **Area totals:** keep rows where `Dwelling Type` and `Number Of Beds` are both `"ALL"`. There is exactly one per area and quarter.
- **Joining to the Airbnb panel:** join on `Location Id` = the listings' `area_code`, and `TimeFrame` = the listing's quarter (see `join_listings_bonds.Rmd`).


### Sanity Check Example

**Step checked**: Geocoding the Airbnb listings to Stats NZ SA2 area codes via
the Koordinates Query API.

**Why this step needs checking**: The Koordinates API takes coordinates as
`x=longitude, y=latitude`. This is an easy pair to swap by mistake. A swapped
coordinate still returns a real, valid-looking area code with no error
thrown, so a bug here would not crash the script; it would just silently
tag every listing with the wrong area.

**Check performed**: Before running the geocoding script across the full
dataset, we tested a single known coordinate for a listing in Redcliffs
and confirmed the API returned area code `332100` (Redcliffs) which is a real,
correctly-located Christchurch suburb, before trusting the script to run
across all ~4,000 unique listing coordinates.

**Result**: Confirmed correct, catching a potential coordinate-order error before it could silently corrupt the entire
geocoded dataset.


## Deliverable 6: what we changed and why

Nalika's design principles document (`design_principles.md`, made with Cursor) checks our code against four practices from the Week 9 lectures: relative file paths (her section 4.1), avoiding magic numbers (4.2), checks that stop the code instead of comments (4.3), and sanity checking one row by hand (4.4). Her section 6 lists every place where the code did not match. For task 1 we fixed those places in the code. These notes follow the same order as her document, so each change can be matched to the problem she found.

Where to find each part of Deliverable 6:

- Task 1 (revisit the code): the Rmd files and `get_area_codes.py`
- Task 2 (notes on what we changed): this section (also saved as `Deliverable6_changes.md`)
- Task 3 (sanity check example): Nalika's "Sanity Check Example" section in the README
- Task 4 (design principles document): Nalika's `design_principles.md`
- Task 5 (does the document match the code): Nalika's section 6 lists the mismatches, and the fixes are in the parts below

### How the answers changed

- The median Airbnb price in Christchurch Central went from $238 to $236 a night.
- The median Airbnb price for all of Christchurch went from $205 to $211 a night.
- The area with the largest gap is still 332700 in Heathcote, but the gap went from $255 to $259 a night.
- Airbnbs per 100 long-term rentals went from 8 to 7.
- None of our conclusions changed. The numbers moved a little because of the data fixes in part 5.
- We updated these figures in sections 2 and 4.4 of Nalika's document so it shows the new answers. Everything else in her document is as she wrote it.

### 1. Relative file paths (Nalika's section 4.1)

- Her document found that `bond_listing_clean.Rmd` used a folder on Nalika's laptop, `/Users/nalikadesai/Desktop/DATA201`, in two places, so it only ran on her computer. We changed both to the repo folder so it runs for anyone.
- She also found that the file saved `Bond Data Quarterly (cleaned).csv` while the join reads `Bond_Data_Quarterly_(cleaned).csv`, so rerunning it never updated the file the join used. We made the names match.
- The saved bond CSV had been made by an older version of the code and still had 94 rows with no area. We rebuilt it from the current code, so the saved data is what the code actually makes.
- She noted that `get_area_codes.py` only works when it is run from the repo folder. We kept that, and added a line at the top of the script saying so.

### 2. Magic numbers (Nalika's section 4.2)

Her table lists the numbers that were typed straight into the code. Each one is now named once at the top of its file, so the name says what it means and there is only one place to change it:

- `clean_christchurch_panel.Rmd`: `k = 10` is now `knn_k`, `2000` is now `price_max`, `30` is now `long_stay_nights`, and the `9` in `in_all_9_months` is now worked out from the list of months.
- `bond_listing_clean.Rmd`: `-99` is now `national_total_id`. The `k = 5` is gone, because this file no longer uses kNN (see part 5).
- `get_area_codes.py`: `processes=20`, `timeout=15` and the `500` checkpoint are now `N_PROCESSES`, `TIMEOUT_SECONDS` and `CHECKPOINT_EVERY`.
- `airbnb_vs_rentals.Rmd`: `7` is now `days_per_week`, `20` is now `min_listings`, `"326600"` is now `central_area`, and `"2026-04-01"` is now `count_month` (now June 2026, see part 5).
- Each file also starts with a line or two saying what it reads and what it writes, like the file headers in the lecture.

### 3. Checks that stop the code (Nalika's section 4.3)

- Her document showed that checks like `sum(duplicated(...))   # expect 0` only print a number and carry on. We changed all of them to `if (...) stop("...")`, the same pattern as the lecture's assertions slide. This covers every check she listed: duplicate listing-months, months without a quarter, duplicate bond totals, the join adding rows, and missing input files.
- She found that `get_area_codes.py` turns a failed lookup into a blank area code without saying anything. It now saves its file and then stops with an error if any listing has no area code.
- She pointed out that `bond_listing_clean.Rmd` only claimed "no duplicate rows" in its text. When we turned that claim into a real check, it failed: there were 779 duplicate rows. Part 5 explains the fix.
- The bond `Location Id` is now read as text. When it was read as a number, area 200000 was saved as `2e+05`, the same problem her document describes for the listing ids.

### 4. Sanity checks on one row (Nalika's section 4.4 and her sanity check example)

- Her Redcliffs check was written in the README but not in the code, so a later edit to the geocoder could break it without anyone noticing. It now runs inside `get_area_codes.py` at the start of every run, and the script stops if Redcliffs does not come back as 332100.
- She found there was no one-row check for the filled prices. `clean_christchurch_panel.Rmd` now checks one townhouse by hand: its real prices are 450, 450, 490, 614, 615 and 741, so its median is (490 + 614) / 2 = $552, and the code has to give exactly that.
- She found there was no one-row check for the join, and suggested a listing in 326600 in April 2026. `join_listings_bonds.Rmd` now does exactly that. The listing shows 42 active bonds and a weekly rent of $537, the same as the raw bond report.

### 5. Other problems we found while fixing these

- Filled prices. kNN filled missing prices by copying from similar listings, but it cannot tell apart listings from the same host at the same address. One host's 7 listings, from 2 bedroom flats to a 4 bedroom townhouse, all got $213 for December. This happened to 564 prices. Now a missing price is filled with that listing's own median price first, and kNN is only used for listings that never show a price.
- Counting each listing once. A listing seen in six months used to count six times in the median. Now each listing gets one price, its own median, before we take the median across listings. Central went from $238 to $236, and leaving out the host with 7 listings does not change it.
- Question 3. Active bonds count the rentals at one point in time, so we now count the Airbnbs listed in June 2026, instead of every Airbnb seen at any point from April to June. This moved the answer from 8 to 7 per 100 rentals.
- Bed counts in the bond data. A blank bed count means the number of bedrooms was not recorded. kNN gave these rows bed counts the area already had, which made the 779 duplicate rows from part 3. They are now labelled "Not recorded", and the check stops the run if a duplicate ever appears. Nalika's sections 3 and 5 still describe the old kNN step and the `beds_was_imputed` column, because her document was written before this change.
- Typed numbers. Numbers in the result text are now printed by the code instead of typed by hand. This showed that one hand-typed count, in the table of why some listings have no bond data, was wrong (522 instead of 61).

### 6. The doubled analysis file (last row of Nalika's section 6)

- Her document found that `airbnb_vs_rentals.Rmd` had the whole analysis in it twice. It also would not knit. We kept one copy and added back the two notes that were only in the second copy: the Banks Peninsula caveat and the note that bedrooms cannot be compared.

### 7. Things we considered but did not change

- Separate data, src and out folders. The lecture recommends this, but moving files halfway through the project would break everyone's file paths.
- File names with spaces, like `Christchurch Oct2025 to Jun2026 (cleaned).csv`. Renaming them would break other files too, so we will use simple names for new files instead.
- Month names and quarter dates written out in full. A loop would be shorter, but the team agreed to keep the code simple enough for everyone to read.
- Rent includes rooms. Question 2 compares whole-home Airbnbs with rent for every kind of rental, including rooms. House-only rents exist for most areas, so this is the next thing we would improve.
