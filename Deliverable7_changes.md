# Deliverable 7: what we changed and why

For Deliverable 7 we automated our pipeline, using the Week 10 lecture on automation. New
months of Inside Airbnb data can now be added with one command. We used it to add July and
August 2026.

Our answers with July and August 2026:

- Median Airbnb price in Christchurch Central: **$244** a night (was $238)
- Biggest gap between Airbnb and long-term rent: still **$255** a night, in area 332700 (Heathcote)
- Airbnbs per 100 long-term rentals: still **8**

The last two have not changed because the bond data stops at June 2026, so July and August
cannot be compared with rents yet.


## How to run it

```
make
```

This runs every step in order and saves everything in `output/`. It takes 5 to 6 minutes.
`make` only reruns the steps whose input files changed, so running it again straight away
does nothing. `make clean` deletes everything in `output/` so you can start again.

Without make: open `run_all.R` in RStudio, choose Session > Set Working Directory > To Source
File Location, then click Source. This needs no setup, but always reruns every step.

On Windows: open the repo folder in File Explorer, type `powershell` in the address bar and
press Enter. Then paste this line (change the R version to yours), and type `make`. Use
PowerShell, not Git Bash:

```
$env:PATH = "C:\Program Files\R\R-4.5.1\bin;C:\rtools45\usr\bin;C:\Program Files\RStudio\resources\app\bin\quarto\bin\tools;" + $env:PATH
```


## How to add a new month

1. On Inside Airbnb, New Zealand, download `listings.csv` (not `listings.csv.gz`).
2. Save it in `data/listings/`, named by its scrape date, for example `2026-08-13.csv`.
3. Run `make`.

No code changes are needed. If the file is not named by its date, or two files are from the
same month, the code stops with a message saying so.


## Folders

- Top folder: `Makefile`, `run_all.R` and the team documents.
- `src/`: the code. The steps, in the order `make` runs them:
  1. `combine_months.Rmd`: combines the monthly files and keeps Christchurch
  2. `clean_christchurch_panel.Rmd`: cleans the listings
  3. `bond_listing_clean.Rmd`: cleans the bond data
  4. `join_listings_bonds.Rmd`: joins the listings to the bond data
  5. `airbnb_vs_rentals.Rmd`: answers the questions and makes the plots

  `get_area_codes.py` gets the area codes. It is run by hand, because it needs the API key.
- `data/`: the downloaded files, never edited by hand. The monthly Airbnb files are in
  `data/listings/`.
- `output/`: everything the code makes, the four CSVs and the five HTML reports.


## Where we used the Week 10 lecture

- **Automated pipeline:** everything is done by one command. The only manual step is
  downloading the new file.
- **Orchestration files:** `Makefile` and `run_all.R` run all the other files, and sit in
  the top folder. `run_all.R` follows the R example on slide 9: one line per step, run in
  order, with the report at the end.
- **Makefiles and the example pipeline:** our `Makefile` has the same layout as the example
  (`all`, one rule per step, `clean`), and our `src/`, `data/` and `output/` folders match its
  `src/`, `data/` and `out/`. Like the lecture says, `make` only reruns what changed.
- **Automated reports:** the answers in `airbnb_vs_rentals.Rmd` are now worked out by the
  code, so they update by themselves.
- **Fail fast and loudly:** `combine_months.Rmd` checks each file as it reads it and
  stops with a message if something is wrong. `make` stops at the first step that fails.
- **Handling errors:** new listings that have no area code yet are kept and counted, instead
  of stopping the whole run.
- **Barriers to automation:** `get_area_codes.py` needs an API key, so it stays a step run
  by hand. The join uses its saved output, so everything else runs on any computer.

Not used: a `config.yaml` file (our settings stay at the top of each Rmd, from Deliverable 6),
Quarto (we kept R Markdown), and continuous integration.

We also kept to our design principles from Deliverable 6 (`design_principles.md`): the same
file names, every step run from the project root, settings named at the top of each file,
and checks that stop the code. The one change is the folders (`src/`, `data/` and `output/`),
which is noted in that file.


## What we changed

### New files

- `combine_months.Rmd` replaces `Filter CHC.R` and `Combine CHC.R` from
  Deliverable 3. Those had one copied block per month. Now one block runs in a loop, once
  per monthly file:

  ```r
  for (f in files) {
    month <- read.csv(f, na.strings = c("", "NA"),
                      colClasses = c(id = "character", host_id = "character"))
    month <- subset(month, neighbourhood_group == "Christchurch City")
    # the month comes from the scrape date at the start of the file name
    scrape_date <- as.Date(substr(basename(f), 1, 10), format = "%Y-%m-%d")
    month$month_year <- format(scrape_date, "%B %Y")
    month$month_date <- as.Date(format(scrape_date, "%Y-%m-01"))
    chch <- rbind(chch, month)
  }
  ```

- `Makefile` and `run_all.R` run all the steps in order.
- `data/listings/`: the 11 monthly Inside Airbnb files, October 2025 to August 2026.

### Changed

- `clean_christchurch_panel.Rmd`: the 9 months were typed into the code, so a new month would
  have been dropped. That list is now one line that reads the months from the data:

  ```r
  # before: month_levels <- c("October 2025", "November 2025", ..., "June 2026")
  #         plus a case_when giving each of the 9 months its date
  month_levels <- format(sort(unique(airbnb$month_date)), "%B %Y")
  ```

  The column `in_all_9_months` is renamed `in_all_months`, because there are now 11 months.
- `join_listings_bonds.Rmd`:
  - It used to read the API output file as its listings, so new months could not get in
    without the API key. It now reads the cleaned listings and only takes each coordinate's
    area code from that file.
  - The coordinates are rounded to 7 decimal places before matching, because Python changed
    the last digit of a few of them when it saved the file.
  - The typed-in list of months for each quarter is replaced by `floor_date(month_date, "quarter")`.
- `airbnb_vs_rentals.Rmd`:
  - The Question 1 numbers are now inline R code instead of typed in.
  - A line in Question 2 says only months with bond data are used.
  - A new section 4 plots the median price by month, so the new months can be seen. Every
    month in the data gets its own label, the title gives the first and last month, and
    the newest month's prices are written on the plot. All of these come from the data, so
    a new month shows up on the plot by itself.
- `bond_listing_clean.Rmd` and `get_area_codes.py`: file paths only.
- Every Rmd: one new setup line, `knitr::opts_knit$set(root.dir = "..")`. The code is now in
  `src/`, and this line makes it run from the repo folder, so the `data/` and `output/` paths
  did not need changing.
- `.gitignore`: ignores HTML files made by clicking Knit (they appear in `src/`).

### Renamed and moved

- `Christchurch Oct2025 to Jun2026 (combined).csv` and `(cleaned).csv` are now
  `Christchurch_combined.csv` and `Christchurch_cleaned.csv`. The old names said "to
  Jun2026", and `make` cannot handle spaces in file names.
- The code moved into `src/` (same names), the downloaded files into `data/`, and everything
  the code makes into `output/`. We used `git mv`, so the files keep their history.

### Not changed

The cleaning methods (including kNN), the checks from Deliverable 6, and the written answers
to Questions 2 and 3.


## What we checked

- **October 2025 to June 2026 is unchanged.** All 28,795 rows have the same prices, area codes
  and bond numbers as in Deliverable 5, and Question 1 on those months is still $238.
- **Adding a month works.** We added the real September 2026 file and ran `make`. Every step
  reran with no code changes, and the report covered 12 months. We then took it out again,
  and the results came back exactly the same.
- **Wrong files stop the code**, with a message, and change nothing.
- **`run_all.R` gives exactly the same results as `make`.**


## Things to know

- 224 July and August rows (mostly new listings) have no area code yet, so they are left out
  of the area results. Someone with the API key can run `python src/get_area_codes.py`,
  then `make`.
- When Tenancy Services publishes the next bond quarter, save it over
  `data/Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv` and run `make`. Then update by hand:
  `latest_quarter` at the top of `airbnb_vs_rentals.Rmd` (it is typed in as April to June
  2026), and the written answers to Questions 2 and 3.
- The numbers written in the text of the cleaning and join Rmds are from October 2025 to
  June 2026. The tables printed by the code are always up to date.
- The 779 duplicate bond rows from Deliverable 6 are still there. The join leaves them out,
  so they do not affect the answers.
