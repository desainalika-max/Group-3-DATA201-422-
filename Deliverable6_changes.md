# Deliverable 6: what we changed and why

Nalika's design principles document (`design_principles.md`, made with Cursor) checks our code against four practices from the Week 9 lectures: relative file paths (her section 4.1), avoiding magic numbers (4.2), checks that stop the code instead of comments (4.3), and sanity checking one row by hand (4.4). Her section 6 lists every place where the code did not match. For task 1 we fixed those places in the code. These notes follow the same order as her document, so each change can be matched to the problem she found.

Where to find each part of Deliverable 6:

- Task 1 (revisit the code): the Rmd files and `get_area_codes.py`
- Task 2 (notes on what we changed): this file (the same notes are also at the end of the README)
- Task 3 (sanity check example): Nalika's "Sanity Check Example" section in the README
- Task 4 (design principles document): Nalika's `design_principles.md`
- Task 5 (does the document match the code): Nalika's section 6 lists the mismatches, and the fixes are in the parts below

## How the answers changed

- The median Airbnb price in Christchurch Central went from $238 to $236 a night.
- The median Airbnb price for all of Christchurch went from $205 to $211 a night.
- The area with the largest gap is still 332700 in Heathcote, but the gap went from $255 to $259 a night.
- Airbnbs per 100 long-term rentals went from 8 to 7.
- None of our conclusions changed. The numbers moved a little because of the data fixes in part 5.
- We updated these figures in sections 2 and 4.4 of Nalika's document so it shows the new answers. Everything else in her document is as she wrote it.

## 1. Relative file paths (Nalika's section 4.1)

- Her document found that `bond_listing_clean.Rmd` used a folder on Nalika's laptop, `/Users/nalikadesai/Desktop/DATA201`, in two places, so it only ran on her computer. We changed both to the repo folder so it runs for anyone.
- She also found that the file saved `Bond Data Quarterly (cleaned).csv` while the join reads `Bond_Data_Quarterly_(cleaned).csv`, so rerunning it never updated the file the join used. We made the names match.
- The saved bond CSV had been made by an older version of the code and still had 94 rows with no area. We rebuilt it from the current code, so the saved data is what the code actually makes.
- She noted that `get_area_codes.py` only works when it is run from the repo folder. We kept that, and added a line at the top of the script saying so.

## 2. Magic numbers (Nalika's section 4.2)

Her table lists the numbers that were typed straight into the code. Each one is now named once at the top of its file, so the name says what it means and there is only one place to change it:

- `clean_christchurch_panel.Rmd`: `k = 10` is now `knn_k`, `2000` is now `price_max`, `30` is now `long_stay_nights`, and the `9` in `in_all_9_months` is now worked out from the list of months.
- `bond_listing_clean.Rmd`: `-99` is now `national_total_id`. The `k = 5` is gone, because this file no longer uses kNN (see part 5).
- `get_area_codes.py`: `processes=20`, `timeout=15` and the `500` checkpoint are now `N_PROCESSES`, `TIMEOUT_SECONDS` and `CHECKPOINT_EVERY`.
- `airbnb_vs_rentals.Rmd`: `7` is now `days_per_week`, `20` is now `min_listings`, `"326600"` is now `central_area`, and `"2026-04-01"` is now `count_month` (now June 2026, see part 5).
- Each file also starts with a line or two saying what it reads and what it writes, like the file headers in the lecture.

## 3. Checks that stop the code (Nalika's section 4.3)

- Her document showed that checks like `sum(duplicated(...))   # expect 0` only print a number and carry on. We changed all of them to `if (...) stop("...")`, the same pattern as the lecture's assertions slide. This covers every check she listed: duplicate listing-months, months without a quarter, duplicate bond totals, the join adding rows, and missing input files.
- She found that `get_area_codes.py` turns a failed lookup into a blank area code without saying anything. It now saves its file and then stops with an error if any listing has no area code.
- She pointed out that `bond_listing_clean.Rmd` only claimed "no duplicate rows" in its text. When we turned that claim into a real check, it failed: there were 779 duplicate rows. Part 5 explains the fix.
- The bond `Location Id` is now read as text. When it was read as a number, area 200000 was saved as `2e+05`, the same problem her document describes for the listing ids.

## 4. Sanity checks on one row (Nalika's section 4.4 and her sanity check example)

- Her Redcliffs check was written in the README but not in the code, so a later edit to the geocoder could break it without anyone noticing. It now runs inside `get_area_codes.py` at the start of every run, and the script stops if Redcliffs does not come back as 332100.
- She found there was no one-row check for the filled prices. `clean_christchurch_panel.Rmd` now checks one townhouse by hand: its real prices are 450, 450, 490, 614, 615 and 741, so its median is (490 + 614) / 2 = $552, and the code has to give exactly that.
- She found there was no one-row check for the join, and suggested a listing in 326600 in April 2026. `join_listings_bonds.Rmd` now does exactly that. The listing shows 42 active bonds and a weekly rent of $537, the same as the raw bond report.

## 5. Other problems we found while fixing these

- Filled prices. kNN filled missing prices by copying from similar listings, but it cannot tell apart listings from the same host at the same address. One host's 7 listings, from 2 bedroom flats to a 4 bedroom townhouse, all got $213 for December. This happened to 564 prices. Now a missing price is filled with that listing's own median price first, and kNN is only used for listings that never show a price.
- Counting each listing once. A listing seen in six months used to count six times in the median. Now each listing gets one price, its own median, before we take the median across listings. Central went from $238 to $236, and leaving out the host with 7 listings does not change it.
- Question 3. Active bonds count the rentals at one point in time, so we now count the Airbnbs listed in June 2026, instead of every Airbnb seen at any point from April to June. This moved the answer from 8 to 7 per 100 rentals.
- Bed counts in the bond data. A blank bed count means the number of bedrooms was not recorded. kNN gave these rows bed counts the area already had, which made the 779 duplicate rows from part 3. They are now labelled "Not recorded", and the check stops the run if a duplicate ever appears. Nalika's sections 3 and 5 still describe the old kNN step and the `beds_was_imputed` column, because her document was written before this change.
- Typed numbers. Numbers in the result text are now printed by the code instead of typed by hand. This showed that one hand-typed count, in the table of why some listings have no bond data, was wrong (522 instead of 61).

## 6. The doubled analysis file (last row of Nalika's section 6)

- Her document found that `airbnb_vs_rentals.Rmd` had the whole analysis in it twice. It also would not knit. We kept one copy and added back the two notes that were only in the second copy: the Banks Peninsula caveat and the note that bedrooms cannot be compared.

## 7. Things we considered but did not change

- Separate data, src and out folders. The lecture recommends this, but moving files halfway through the project would break everyone's file paths.
- File names with spaces, like `Christchurch Oct2025 to Jun2026 (cleaned).csv`. Renaming them would break other files too, so we will use simple names for new files instead.
- Month names and quarter dates written out in full. A loop would be shorter, but the team agreed to keep the code simple enough for everyone to read.
- Rent includes rooms. Question 2 compares whole-home Airbnbs with rent for every kind of rental, including rooms. House-only rents exist for most areas, so this is the next thing we would improve.
