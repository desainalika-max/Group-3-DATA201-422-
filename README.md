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

## Deliverable 4

### Datasets

#### 1. Christchurch Airbnb Listings
**Source:** Inside Airbnb, concatenated across Oct 2025 – Jun 2026 (Deliverable 3)
**File:** `Deliverable 4/data/raw/chch_listings_raw.csv` (not tracked in git — see Setup below)
**Cleaning script:** `Deliverable 4/clean_listings.Rmd`

**Known limitation:** `price` is 100% missing for Dec 2025, Jan 2026, and Feb 2026 in the source file — confirmed against the raw Inside Airbnb monthly file, not introduced by our Deliverable 3 concatenation. This affects 10,667 of 28,795 rows (37%). We flag these rows with `price_missing` rather than dropping them, since dropping would remove an entire quarter's supply data.

**Columns kept / added**
| Column | Description |
| --- | --- |
| **id** | Unique identifier for the listing |
| **host_id** | Unique identifier for the host |
| **neighbourhood** | Christchurch City ward |
| **latitude** / **longitude** | Geographic coordinates, used for SA2 spatial join in Deliverable 5 |
| **room_type** | Entire home/apt, Private room, Shared room, or Hotel room |
| **price** | Nightly price (NZD); 37% missing, see limitation above |
| **minimum_nights** | Minimum stay required |
| **number_of_reviews_ltm** | Reviews received in the last 12 months |
| **reviews_per_month** | Average review frequency |
| **last_review** | Date of most recent review |
| **calculated_host_listings_count** | Number of listings this host manages |
| **availability_365** | Days available for booking in the next year |
| **month_year** | Scrape month, parsed from source (day-first) |
| **month_label** | `YYYY-MM` |
| **quarter** | `YYYYQ#`, matches bond dataset `TimeFrame` format |
| **price_missing** | TRUE where `price` is NA |
| **bedrooms_est** | Bedroom count extracted from `name` where mentioned (~12% coverage); indicative only |

**Columns dropped**
| Column | Reason |
| --- | --- |
| **license** | 100% missing |
| **neighbourhood_group** | Single constant value ("Christchurch City") |
| **host_name** | Personal data, no analytical use |
| **name** | Free text, mined for `bedrooms_est` then dropped |

---

#### 2. Tenancy Services Rental Bond Data
**Source:** [Tenancy Services — Rental bond data](https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/), Detailed quarterly report, Jan 2020 – Apr 2026
**File:** `Deliverable 4/data/raw/bond_raw.csv` (not tracked in git — each team member downloads their own copy)
**License:** Creative Commons Attribution 3.0 NZ, credited to the Ministry of Business, Innovation and Employment
**Cleaning script:** `Deliverable 4/clean_bonds.Rmd`

Data comes from Tenancy Services' bond database, covering private-sector bonds lodged each month, listed by tenancy start date, using SA2-2019 area definitions from Statistics NZ. Fixed random rounding to base 3 and suppression of results under 5 bonds is applied by MBIE before release. Recent quarters are provisional due to an ongoing bond-system migration and may not be directly comparable with earlier periods.

**Column Descriptions**
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
| **Geometric Mean Rent** | Median substitute — avoids the plateauing effect of rents clustering at round numbers |
| **Upper Quartile Rent** / **Lower Quartile Rent** | Synthetic 75th/25th percentile, assumes log-normal distribution |
| **Log Std Dev Weekly Rent** | Spread of the log-rent distribution |
| **rent_suppressed** | **Added.** TRUE where rent measures are NA due to MBIE's <5-bond suppression rule |

**Cleaning decisions**
- **Location filter:** restricted to Christchurch City SA2 codes, using the Stats NZ SA2-2019-to-Territorial-Authority concordance. This removes the dataset's non-geographic rollup rows (`Location Id` = -99 or blank) as a side effect.
- **Dwelling Type:** collapsed to `"ALL"` only. Bond `Dwelling Type` describes building type, which has no consistent counterpart in the Airbnb `room_type` field, so keeping the breakdown would not support a valid comparison next week.
- **Number Of Beds:** kept at the specific level (1, 2, 3, 4, 5+), since it aligns directly with `bedrooms_est` in the Airbnb dataset.
- **Missing rent:** flagged with `rent_suppressed` rather than dropped. Only 9 rows within Christchurch are genuinely suppressed; they still carry valid `Total Bonds` counts.
- **Timeframe filter:** restricted to `2025-10-01`, `2026-01-01`, `2026-04-01`, matching the Airbnb coverage of Oct 2025 – Jun 2026 exactly.

---

### Setup — reproducing this on another machine

Raw data files are excluded from git (see `.gitignore`) to keep the repository small. To rerun the pipeline:

1. Clone the repo
2. Place the Deliverable 3 concatenated CSV at `Deliverable 4/data/raw/chch_listings_raw.csv`
3. Download the Tenancy Services "Detailed quarterly report" CSV from the link above and place it at `Deliverable 4/data/raw/bond_raw.csv`
4. Open `Deliverable 4/Deliverable 4.Rproj` in RStudio
5. Knit `clean_listings.Rmd`, then `clean_bonds.Rmd`
6. Cleaned outputs are written to `Deliverable 4/data/clean/`