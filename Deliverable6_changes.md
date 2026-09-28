# Deliverable 6: what we changed and why

For Deliverable 6 we went back through our code using the ideas from the Week 9 lectures: relative file paths, putting settings at the top of each file, checks that stop the code, and sanity checking one row by hand. Below is what we changed and why.

Where to find each part of Deliverable 6:

- Task 1 (revisit the code): the Rmd files and `get_area_codes.py`
- Task 2 (notes on what we changed): this file (the same notes are also at the end of the README)
- Task 3 (sanity check example): the "Sanity Check Example" section of the README
- Task 4 (design principles document): `design_principles.md`
- Task 5 (checking the document against the code): section 6 of `design_principles.md`

## How the answers changed

- The median Airbnb price in Christchurch Central went from $238 to $236 a night.
- The median Airbnb price for all of Christchurch went from $205 to $211 a night.
- The area with the largest gap is still 332700 in Heathcote, but the gap went from $255 to $259 a night.
- Airbnbs per 100 long-term rentals went from 8 to 7.
- None of our conclusions changed. The numbers moved a little because of the data fixes in part 5.

## 1. Relative file paths

- `bond_listing_clean.Rmd` used a folder on Nalika's laptop (`/Users/nalikadesai/Desktop/DATA201`), so it only ran on her computer. We changed it to the repo folder so it runs for anyone. This is the lecture's rule about never using absolute paths.
- The same file saved its output as `Bond Data Quarterly (cleaned).csv`, but the join reads `Bond_Data_Quarterly_(cleaned).csv`. Rerunning it never updated the file the join used, so we made the names match.

## 2. Settings at the top of each file

- Each file now starts with a line or two saying what it reads and what it writes, like the file headers in the lecture.
- Numbers that control the code are now named once at the top, instead of being typed in the middle of the code. For example `price_max <- 2000`, `knn_k <- 10`, `long_stay_nights <- 30`, `days_per_week <- 7` and `N_PROCESSES = 20`. The lecture calls these magic numbers. A name says what the number means, and if we want to change it there is only one place to do it.

## 3. Checks that stop the code

- Many checks used to print a number with a comment like `# expect 0` and then carry on, even when the number was wrong. We changed them to `if (...) stop("...")`, the same pattern as the lecture's assertions slide. Now the knit stops with a clear message if a file is missing, a listing appears twice, or a join adds rows.
- `get_area_codes.py` used to turn a failed lookup into a blank area code without saying anything. It now saves its file and then stops with an error if any listing has no area code.
- The bond `Location Id` is now read as text. When it was read as a number, area 200000 was saved as `2e+05`. Area codes are labels, not numbers, which is the same lesson as the listing `id` in Deliverable 4.

## 4. Sanity checks on one row

Nalika's sanity check example tests the geocoding step with one known Redcliffs listing. We built on that idea:

- The Redcliffs check now runs inside `get_area_codes.py` every time. If Redcliffs does not come back as 332100 the script stops, so a swapped latitude and longitude cannot slip through.
- `clean_christchurch_panel.Rmd` checks one filled price by hand. One townhouse has real prices of 450, 450, 490, 614, 615 and 741, so its median is (490 + 614) / 2 = $552, and the code has to give exactly that.
- `join_listings_bonds.Rmd` checks one Central listing from April 2026 against the raw bond report. Both should show 42 active bonds and a weekly rent of $537.

## 5. Data problems we found while checking

- Filled prices. kNN filled missing prices by copying from similar listings, but it cannot tell apart listings from the same host at the same address. One host's 7 listings, from 2 bedroom flats to a 4 bedroom townhouse, all got $213 for December. This happened to 564 prices. Now a missing price is filled with that listing's own median price first, and kNN is only used for listings that never show a price.
- Counting each listing once. A listing seen in six months used to count six times in the median. Now each listing gets one price, its own median, before we take the median across listings. Central went from $238 to $236, and leaving out the host with 7 listings does not change it.
- Question 3. Active bonds count the rentals at one point in time, so we now count the Airbnbs listed in June 2026, instead of every Airbnb seen at any point from April to June. This moved the answer from 8 to 7 per 100 rentals.
- Bed counts in the bond data. A blank bed count means the number of bedrooms was not recorded. kNN gave these rows bed counts the area already had, which made 779 duplicate rows, even though the notebook said there were no duplicates. They are now labelled "Not recorded", and a check stops the run if a duplicate ever appears.
- Typed numbers. Numbers in the result text are now printed by the code instead of typed by hand. This showed that one hand-typed count, in the table of why some listings have no bond data, was wrong (522 instead of 61).

