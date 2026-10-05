# Runs the whole pipeline in order, for anyone without make: Rscript run_all.R
# (or open this file in RStudio and click Source). Run it from the repo folder.
# Each Rmd is knitted in a fresh environment, the same as clicking Knit,
# and its HTML report is saved in output/.
# src/get_area_codes.py needs the API key, so it is run by hand.

rmarkdown::render("src/combine_months.Rmd", output_dir = "output", envir = new.env())
rmarkdown::render("src/clean_christchurch_panel.Rmd", output_dir = "output", envir = new.env())
rmarkdown::render("src/bond_listing_clean.Rmd", output_dir = "output", envir = new.env())
rmarkdown::render("src/join_listings_bonds.Rmd", output_dir = "output", envir = new.env())
rmarkdown::render("src/airbnb_vs_rentals.Rmd", output_dir = "output", envir = new.env())
