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

The dataset is a **snapshot of Airbnb listings taken on 22 June 2026** — this is the scrape date.

To calculate how long ago a listing's last review was, we count backwards from the snapshot date:

### Why the snapshot date matters

- **Initial issue:** the snapshot date was first set to `13 June`, but the dataset actually contains reviews dated up to `22 June`. Any review after `13 June` (e.g. `16 June`) produced a **negative** result:

- This happened because we were measuring backwards from a date that hadn't occurred yet relative to some reviews.

- **Fix:** setting the snapshot date to `22 June` — the true scrape date — ensures every review falls on or before that date, so all `days_ago` values come out zero or positive.

- **Why 22 June is correct:** it matches the most recent review date found in the dataset, confirming it as the actual day the scrape occurred.
