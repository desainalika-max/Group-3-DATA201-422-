.PHONY: all clean

all: output/airbnb_vs_rentals.html

# every monthly listings file; the folder is listed too, because its date changes when
# a month is added or removed, even if the new file has an old date (Windows keeps it)
LISTINGS = $(wildcard data/listings/*.csv)

# combine the monthly files and keep Christchurch
output/Christchurch_combined.csv: src/combine_months.Rmd data/listings $(LISTINGS)
	Rscript -e "rmarkdown::render('src/combine_months.Rmd', output_dir = 'output')"

# clean the listings
output/Christchurch_cleaned.csv: src/clean_christchurch_panel.Rmd output/Christchurch_combined.csv
	Rscript -e "rmarkdown::render('src/clean_christchurch_panel.Rmd', output_dir = 'output')"

# src/get_area_codes.py needs the API key, so it is run by hand, not by make.
# Its output, data/Christchurch_with_area_codes.csv, is used by the join.

# clean the bond data
output/Bond_Data_Quarterly_(cleaned).csv: src/bond_listing_clean.Rmd data/Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv output/Christchurch_cleaned.csv
	Rscript -e "rmarkdown::render('src/bond_listing_clean.Rmd', output_dir = 'output')"

# join the listings to the bond data
output/Christchurch_with_bonds.csv: src/join_listings_bonds.Rmd output/Christchurch_cleaned.csv data/Christchurch_with_area_codes.csv output/Bond_Data_Quarterly_(cleaned).csv
	Rscript -e "rmarkdown::render('src/join_listings_bonds.Rmd', output_dir = 'output')"

# answer the questions and make the plots
output/airbnb_vs_rentals.html: src/airbnb_vs_rentals.Rmd output/Christchurch_with_bonds.csv
	Rscript -e "rmarkdown::render('src/airbnb_vs_rentals.Rmd', output_dir = 'output')"

# removes everything in output/ that the code makes (data/ is never touched)
clean:
	rm -f output/Christchurch_combined.csv \
	      output/Christchurch_cleaned.csv \
	      "output/Bond_Data_Quarterly_(cleaned).csv" \
	      output/Christchurch_with_bonds.csv \
	      output/combine_months.html \
	      output/clean_christchurch_panel.html \
	      output/bond_listing_clean.html \
	      output/join_listings_bonds.html \
	      output/airbnb_vs_rentals.html
