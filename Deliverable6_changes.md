# Deliverable 6: what we changed and why

We went back over the Deliverable 4 and 5 code (`clean_christchurch_panel.Rmd`,
`bond_listing_clean.Rmd`, `join_listings_bonds.Rmd`, `airbnb_vs_rentals.Rmd`) and checked it
against the Week 9 coding practices. Some changes fix the data or the method, so the answers
moved a little. The rest make the code easier to rerun and read, and do not change any result.

## Answers before and after

| | Deliverable 5 | Deliverable 6 |
|---|---|---|
| Q1: median Airbnb price, Christchurch Central (326600) | $238 | **$236** |
| Q1: median Airbnb price, all of Christchurch | $205 | $211 |
| Q2: area with the largest gap | 332700 Heathcote, $255 | 332700 Heathcote, **$259** |
| Q2: Christchurch median gap | $144 | $149 |
| Q3: Airbnbs per 100 long-term rentals | 8 | **7** |
| Q3: Christchurch Central (326600) per 100 rentals | 348 | 283 |

None of the conclusions changed. Central still costs more than Christchurch as a whole and
has by far the most Airbnbs per rental, and the largest gap is still in 332700 (Heathcote).

## 1. Changes to the data and the method

### 1.1 Filled prices come from the listing itself first (`clean_christchurch_panel.Rmd`)

**What:** a missing price is now filled with the listing's own median price from the months
it has a real price. kNN is only used for listings with no real price in any month (518 of
10,694 filled rows). A new column, `price_source`, says whether each price is `observed`,
`own median` or `kNN`.

**Why:** kNN picks neighbours on room type, location, minimum nights, host size and month.
Listings from the same host at the same address match on all of these, so kNN copied one
price to all of them. Host 482671075 has 7 listings at one Christchurch Central address,
from 2-bedroom flats to 4-bedroom townhouses, and kNN gave all 7 the same $213 for December.
The 4-bedroom townhouse charges $450 to $741 in the months with a real price. 564 filled
prices were copies like this. Now 32 are, all in the kNN rows. The citywide median of the
filled December prices moved from $167 to $209, so kNN had been making December look cheap.

### 1.2 Every listing counts once in a median (`airbnb_vs_rentals.Rmd`)

**What:** we first take each listing's own median price, then the median across listings.
Before, the median was taken over rows, one row per listing per month.

**Why:** listings were weighted by how many months they appear. In Central, 85 of the 150
listings have a real price in six months and count six times, while 4 appear once and
count once. The host with 7 listings at one address had 42 rows. Counting each listing once
moves Central from $238 to $236.

We also checked whether one host skews the answer. Once every listing counts once, leaving
out host 482671075 does not change the median ($236 either way). The three biggest hosts run
48% of Central listings and charge less than the rest. Without them the median would be
$254. We kept them, because each of their listings is a real place a guest can book, and we
report the check next to the answer.

### 1.3 Q3 counts Airbnbs in one month (`airbnb_vs_rentals.Rmd`)

**What:** Airbnbs are now the listings in June 2026. Before, they were every listing seen
at any time in April, May or June.

**Why:** active bonds count the rentals running at one point in time. In every area they
are far higher than the bonds lodged that quarter, so they are not new rentals. Counting
Airbnbs over three months counted a listing that closed in April and a new one that opened
in June as two, even though they were never listed at the same time. With one month on both
sides the comparison is like for like: 8 per 100 becomes 7.

### 1.4 Bond area codes are read as text (`bond_listing_clean.Rmd`)

**What:** `Location Id` is read as text instead of a number.

**Why:** read as a number, area 200000 was written out as `2e+05`. It is the same lesson as
the Airbnb `id` column in Deliverable 4: codes are labels, not numbers. Area 200000 is not
in Christchurch, so no answer changed.

### 1.5 The reasons for missing bond data are computed (`join_listings_bonds.Rmd`)

**What:** the table of why 6,849 listing rows have no bond data is now made by code.

**Why:** in Deliverable 5 the three counts were typed in by hand. Computing them showed the
third one was wrong: it should be 61, not 522. The other 461 of those rows belong under
"area has no bond rows that quarter".

## 2. Coding-practice changes (results unchanged)

| Change | Where | Why |
|---|---|---|
| Relative paths instead of `/Users/nalikadesai/Desktop/DATA201` | `bond_listing_clean.Rmd` | The file only ran on one laptop. Now it runs from the repo folder on anyone's computer, like the other Rmd files. |
| Output name fixed to `Bond_Data_Quarterly_(cleaned).csv` | `bond_listing_clean.Rmd` | The Rmd wrote `Bond Data Quarterly (cleaned).csv`, but the join reads the underscore name, so rerunning it never updated the file the join uses. |
| Saved bond CSV regenerated from the code | `Bond_Data_Quarterly_(cleaned).csv` | The saved file came from an older version of the code and still had 94 rows with no area, which the current code removes. The saved data should always be what the saved code makes. |
| Area codes joined on listing id and month | `join_listings_bonds.Rmd` | `get_area_codes.py` needs an API key. Its output was a full copy of the cleaned listings, so any cleaning fix went stale unless someone reran the API. Now only the `area_code` column is taken from it. |
| `stopifnot()` instead of printed checks marked `# expect 0` | cleaning and join Rmds | A printed number is easy to miss. A failed `stopifnot()` stops the knit, so a broken join or a missing file cannot pass silently. |
| Settings set once at the top | `airbnb_vs_rentals.Rmd` | The area code, the 20-listing minimum, the host id and the count month were typed where they were used. Now each is set once and has a comment. |
| Result numbers written with inline R | join and analysis Rmds | Typed numbers go out of date when the data changes, as the missing-bond table showed. Inline R always prints what the code just computed. |
| Run order in the README and at the top of the join Rmd | `README.md` | A new reader can rerun everything without asking which file comes first. |
| README price section updated | `README.md` | It still described the Deliverable 4 kNN-only method. |

## 3. Considered but not changed

- **File names with spaces and brackets**, such as `Christchurch Oct2025 to Jun2026 (cleaned).csv`.
  Good practice says to avoid them. Renaming now would break `get_area_codes.py`, the README
  and every teammate's local copy, so we kept the names and will use plain names for new files.
- **The nine-line month `case_when()` blocks.** A loop or a function would be shorter, but the
  team agreed to keep the code at a level every member can read and rerun. Each block is
  written out once and commented.
- **kNN for missing bond bed counts.** It fills some bed counts with `"ALL"` (44 rows after
  the rerun), which makes those rows look like area totals. The join already drops imputed rows, so no answer is affected.
  We left the method as it is, and the join Rmd explains why those rows are dropped.
- **Summer prices.** A listing's own median comes from its non-summer months, so filled
  December to February prices are probably a little low. This is listed as a known
  limitation. The Q1 and Q2 answers use real prices only, so they are not affected.
