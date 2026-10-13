# Deliverable 6: what we changed and why

For Deliverable 6 we went back through our code using the Week 9 lecture slides on best coding practices. This file covers tasks 1, 2 and 3. Tasks 4 and 5 (the design principles document) are done by Nalika.

None of these changes affect our answers. They are still the same as Deliverable 5:

- Median Airbnb price in Christchurch Central: $238 a night
- Biggest gap between Airbnb and long-term rent: area 332700 in Heathcote, $255 a night
- Airbnbs per 100 long-term rentals: 8

No data files were changed. Only the code, the HTML reports and the README.


## What we changed and why

### 1. Relative file paths

Lecture: "Always use relative file paths".

- `bond_listing_clean.Rmd` used a folder on Nalika's laptop (`/Users/nalikadesai/Desktop/DATA201`), so it only worked on her computer. It now uses the repo folder, so it works for everyone.
- It also saved its output under a different name (`Bond Data Quarterly (cleaned).csv`) from the one the join reads (`Bond_Data_Quarterly_(cleaned).csv`). The names now match.

### 2. Settings at the top of each file

Lecture: "Draw attention to parameters" and "no magic numbers".

- Numbers that control the code used to be hidden in the middle of it, like 2000, 10 and 30. They now have names at the top of each file, for example `price_max <- 2000` and `knn_k <- 10`.
- The name says what the number means, and there is only one place to change it.

### 3. File headers

Lecture: "File headers".

- Each file now starts with a line or two saying which file it reads and which file it saves. Reading the tops of the files is enough to see how they connect.

### 4. Checks that stop the code

Lecture: "Assertions as documentation".

- Some checks printed a number with a comment like `# expect 0`, and the code carried on even when the number was wrong. They now use `if (...) stop("...")`, so the code stops with a message when something is wrong.
- `get_area_codes.py` now stops with an error if a listing did not get an area code, instead of leaving it blank without saying anything.

### 5. Say what type each column is

Lecture: "If you have detailed expectations, record them in the code".

- The bond file now reads `Location Id` as text, because it is an area code, not a number. Read as a number, area 200000 was saved as `2e+05`.


## Every file we changed

`clean_christchurch_panel.Rmd`

- Added a line at the top saying what it reads and saves.
- Added settings at the top: `price_max` (2000), `knn_k` (10), `long_stay_nights` (30) and `random_seed` (2026). The code now uses these names instead of the numbers.
- The `9` in `in_all_9_months` is now worked out from the list of months.
- New checks that stop the code: the input file is missing, a price is still missing after kNN, or a listing appears twice in the same month.

`bond_listing_clean.Rmd`

- Added a line at the top saying what it reads and saves.
- Changed the laptop path to the repo folder, and made `read_csv` use it too.
- Changed the output name to `Bond_Data_Quarterly_(cleaned).csv`.
- Added settings at the top: `national_total_id` (-99), `knn_k` (5) and `random_seed` (2026).
- New checks that stop the code if an input file is missing.
- `Location Id` is now read as text.

`join_listings_bonds.Rmd`

- Added a line at the top saying what it reads and saves.
- The file names are now set once at the top.
- New checks that stop the code: a month did not get a quarter, an area has two bond totals in the same quarter, or the join changed the number of rows.
- New section 5, the sanity check example (see below).

`airbnb_vs_rentals.Rmd`

- Added a line at the top saying what it reads and which file to knit first.
- Added settings at the top: `central_area` ("326600"), `min_listings` (20), `latest_quarter` (April to June 2026) and `days_per_week` (7). The code now uses these names.
- New check that stops the code if a listing appears twice in the same month.

`get_area_codes.py`

- Added a comment at the top saying what it does, that it needs the API key, and to run it from the repo folder.
- Added settings at the top: `N_PROCESSES` (20), `TIMEOUT_SECONDS` (15) and `CHECKPOINT_EVERY` (500).
- It now stops with an error if any listing has no area code. It still saves its file first, so the API calls are not lost.

`README.md`

- Fixed the bond output file name.
- Added the "Deliverable 6" section with these notes and the sanity check example.

The HTML reports for the cleaning, join and analysis files were re-knitted, so they show the new code. The results in them are the same as before.


## Sanity check example (task 3)

Lecture: "Calculate the expected result by hand, for one or more rows. Compare with the computer output".

- Step checked: the join, which gives each Airbnb listing the bond numbers for its area and quarter.
- Why it needs checking: if the area code or the quarter is matched wrongly, a listing gets another area's rent. Nothing crashes, the numbers are just wrong.
- How we checked it: we took one Christchurch Central (326600) listing in April 2026. April is in the quarter that starts on 2026-04-01, so the listing should get the 326600 total for that quarter. We looked that row up ourselves in the raw bond report (`Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv`), not in our cleaned file, and compared the two.
- Result: both show 42 active bonds and a weekly rent of $537, so the join matched the right area and the right quarter.
- This check is now in section 5 of `join_listings_bonds.Rmd`. If the numbers ever stop matching, the knit stops with an error.


## Things we noticed but did not change

- The bond file says it has no duplicate rows, but its own check prints 779. They come from the kNN step that fills missing bed counts. Fixing this would change the data, so we left it for now. It does not affect our answers, because the join only uses area totals that kNN did not fill.
- The saved bond CSV was made by an older version of `bond_listing_clean.Rmd`, so it is not exactly what the code makes now. We did not re-run it, so the data stays the same as Deliverable 5.
- `get_area_codes.py` was not re-run, because it needs the API key. We checked that the Python file has no syntax errors.
- Separate folders for data, code and outputs. The lecture suggests this, but moving files now would break everyone's file paths. The structure we would use is in "Suggested folder structure" below.
- File names with spaces, like `Christchurch Oct2025 to Jun2026 (cleaned).csv`, for the same reason.


## Suggested folder structure

Lecture: "Clean separation of parts: Data, Code, Output" and "Do not edit Data".

Right now every file sits in one folder, so the raw data, the code and the files the code makes are all mixed together. Following the lecture's default project structure, the repo would look like this:

```
Group-3-DATA201-422-/
  README.md
  Deliverable6_changes.md
  teamrules
  .gitignore

  data/
    Christchurch Oct2025 to Jun2026 (combined).csv
    Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv

  src/
    1_clean_christchurch_panel.Rmd
    2_get_area_codes.py
    3_bond_listing_clean.Rmd
    4_join_listings_bonds.Rmd
    5_airbnb_vs_rentals.Rmd

  out/
    Christchurch Oct2025 to Jun2026 (cleaned).csv
    Christchurch_with_area_codes.csv
    Bond_Data_Quarterly_(cleaned).csv
    Christchurch_with_bonds.csv
    clean_christchurch_panel.html
    join_listings_bonds.html
    airbnb_vs_rentals.html
```

What each folder is for:

- `data/` holds the files we downloaded. We never edit them by hand. Every change is made by the code, so anyone can see exactly what was done to the original data.
- `src/` holds the code. The number at the start of each name is the order to run them in, so nobody has to guess which file comes first.
- `out/` holds everything the code makes: the cleaned files, the joined file and the HTML reports. All of it can be made again by running the code on the data (the lecture's "Data + Code -> Output").
- The lecture says outputs usually do not go in git. We would still keep `out/` in git, because teammates use these files without running the code, and `Christchurch_with_area_codes.csv` needs an API key to make again.

Why we have not moved the files yet:

- Every file path in the code would change (for example `data/Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv` instead of `Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv`), and every teammate's copy would need updating at the same time. We would do it as one change with the whole team, not in the middle of a deliverable.
