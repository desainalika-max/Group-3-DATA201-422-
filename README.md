# Data Divas


## Team
- Sudheesh
- Nalika
- Dian Qiu
- Agar

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
| **latitude** / **longitude** | Geographic coordinates |
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

## Cleaning the Airbnb Listings

**Source:** Deliverable 3 concatenated panel, Inside Airbnb, Christchurch, Oct 2025 – Jun 2026
**Cleaning script:** `clean_christchurch_panel.Rmd`
**Output:** `Christchurch Oct2025 to Jun2026 (cleaned).csv`

### Column changes

| Column | Change | Reason |
| --- | --- | --- |
| `id`, `host_id` | Read as character, not numeric | The largest `id` is 17 digits. A double only holds ~15 significant digits reliably, so reading these as numbers would silently corrupt the last few. They're labels, never used in arithmetic. |
| `license` | Dropped | 100% missing across all 28,795 rows |
| `month_year` | Converted to an ordered factor | As plain text, months sort alphabetically (April, August, December...), which breaks every grouped summary and chart. An explicit factor order fixes this. |
| `month_date` | Added | A real `Date` column alongside `month_year`, so month arithmetic and time-series joins work correctly. `month_year` stays as the display-order version. |
| `last_review` | Parsed to `Date` | Was read in as text |
| `reviews_per_month` | Missing values set to 0 | All 2,627 missing values belong to listings with `number_of_reviews == 0`. This is a structural zero, not a data gap — a listing with no reviews genuinely has 0 reviews per month. Imputing a market average would invent activity that never happened. `last_review` is left as `NA` for these rows, since there's no correct date to put there. |
| `host_name` | Filled within host, then labelled "Unknown" | One row was missing a host name. The same `host_id` appears 9 times and is named in the other 8, so the value is recovered with certainty rather than guessed. Any remaining true unknowns are labelled `"Unknown"` rather than left blank. |
| `minimum_nights` | Carried forward within listing as `minimum_nights_filled`; original kept | 37 gaps, each with a value present in an adjacent month for the same listing. Minimum nights is a host-set rule, not a market outcome, and changes rarely. Carrying it forward is safer than imputing. The raw `minimum_nights` column is kept unchanged alongside the filled version. |
| `price` | Imputed via kNN as `price_imputed`; original kept | See below |
| `months_present`, `in_all_9_months` | Added | Only 2,338 of 4,117 listings appear in all nine monthly snapshots. Any month-over-month price comparison should either filter to `in_all_9_months` or explicitly note that it doesn't, otherwise real price movement gets mixed up with listings simply entering or leaving the panel. |
| `long_stay` | Added | Flags the 129 rows requiring 30+ nights minimum stay. A different market to nightly tourist rental, worth excluding from tourist-price analysis. |
| `name` | Whitespace trimmed | Minor cleanup, no rows affected structurally |

### Price: the one column that needed a real imputation decision

Two distinct missingness problems were found:

- **December 2025, January 2026 and February 2026 have no observed prices at all** the entire column is blank in those three months, not a sample of missing values. Confirmed against the raw Inside Airbnb monthly file for December, so this is a source limitation and not something introduced by the Deliverable 3 concatenation.
- **The other six months are 5–8% missing**, and this missingness is not random: among rows with a price, 0.5% have zero availability; among rows missing a price, 62% do. Airbnb seems to only calculate a price when a listing has open dates, so no availability means no price shown.

**Decision:** the team used **kNN imputation** (`VIM::kNN`, k = 10) to fill missing prices, matching each listing to its 10 nearest neighbours on room type, coordinates, minimum nights, host listing count, and month. Because December–February have no observed prices at all within those months, values for that stretch are drawn from listings in other months. 27 implausible prices (above $2,000/night) were also treated as missing before imputation.

The original `price` column is kept unchanged. `price_imputed` holds the filled version. `price_was_imputed` flags every row that differs from the original, so any analysis can filter to observed-only prices if preferred.

### Known limitations

1. December 2025 – February 2026 have no observed prices, so imputed values in that window are the least reliable in the dataset.
2. kNN was chosen as a first approach; other imputation methods haven't been tested and may give different results.
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
**Output:** `Bond Data Quarterly (cleaned).csv`

Data comes from Tenancy Services' bond database, covering private-sector bonds lodged each month, listed by tenancy start date, using SA2-2019 area definitions from Statistics NZ. Fixed random rounding to base 3 and suppression of results under 5 bonds is applied by MBIE before release. Recent quarters are provisional due to an ongoing bond-system migration and may not be directly comparable with earlier periods.

### Column Descriptions

| Column | Description |
| --- | --- |
| **TimeFrame** | Quarter start date, based on tenancy start date |
| **Location Id** | SA2-2019 area code (Statistics NZ) |
| **Dwelling Type** | House / Apartment / Flat / Room / Boarding House / ALL |
| **Number Of Beds** | 0–9, "5+", or "ALL" (rollup) |
| **Total Bonds** | Bonds lodged in the group |
| **Active Bonds** | Still ongoing |
| **Closed Bonds** | Ended |
| **Median Rent** | Weekly rent, median |
| **Geometric Mean Rent** | Median substitute. Avoids the plateauing effect of rents clustering at round numbers |
| **Upper Quartile Rent** / **Lower Quartile Rent** | Synthetic 75th/25th percentile, assumes log-normal distribution |
| **Log Std Dev Weekly Rent** | Spread of the log-rent distribution |
| **beds_was_imputed** | **Added.** TRUE where `Number Of Beds` was filled by kNN rather than reported |

### Cleaning decisions

- **Timeframe:** matched dynamically against the cleaned listings file's actual date range, rather than hardcoded, so the filter stays correct if the listings panel is later edited. Three quarters overlap: 2025-10-01 (Oct–Dec 2025), 2026-01-01 (Jan–Mar 2026), 2026-04-01 (Apr–Jun 2026). No 2026-07-01 quarter exists yet, since bond data publishes a couple of months behind.
- **Columns:** every column is kept. `Total Bonds`, `Active Bonds`, `Closed Bonds` are the stock-side variables the merge needs; `Median Rent` and the other rent statistics are the price-side variables. Nothing was dropped, since next week's comparison needs both sides.
- **Location Id:** rows with a blank `Location Id`, or `Location Id == -99`, were dropped entirely. Blank rows also had no rent statistics, carrying no usable information. `-99` represents an "All of New Zealand" rollup rather than a real SA2 area, cannot be matched in a location-based merge, and would distort a location-level dataset if kept.
- **Number Of Beds:** missing values (distinct from the legitimate "ALL" aggregate level, and spread thinly across dwelling types rather than concentrated in one) were imputed via kNN (k = 5), matching each row to its nearest neighbours on dwelling type, location, bond counts, and rent statistics. `beds_was_imputed` flags every filled row. Unlike the listings price column, there was no unimputed copy kept alongside, since after imputation zero missing values remain.

### Known limitations

1. `Location Id` is an SA2 area code, not a name or coordinate. No location-name lookup exists in this file, so it can't yet be filtered to Christchurch-only or joined to the listings data by name, a separate SA2-to-district lookup (e.g. from Stats NZ) is needed before next week's merge.
2. The kNN distance calculation treats `Location Id` as categorical (same area vs. different), not as spatial distance. Different SA2 codes aren't numerically "close" to each other, so cross-location neighbour matching leans more on dwelling type and bond/rent figures than true geographic proximity.
3. Bond data is quarterly while listings are monthly, so any merge will compare a single quarterly figure against up to three monthly listings figures.

### How to use the output

- **Reliable bed counts:** filter `beds_was_imputed == FALSE`
- **Joining to the Airbnb panel:** requires the SA2-to-Christchurch lookup mentioned above before `Location Id` can be matched to listing coordinates.
