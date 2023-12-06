# Install packages if not already installed
install_if_missing <- function(packages) {
  new_packages <- packages[!(packages %in% installed.packages()[,"Package"])]
  if (length(new_packages) > 0) {
    install.packages(new_packages, dependencies=TRUE, repos='http://cran.us.r-project.org')
  }
}

# List of required packages
required_packages <- c("auk", "dplyr", "lubridate", "readr", "feather")

# Install missing packages
install_if_missing(required_packages)
library(auk)
library(dplyr)
library(lubridate)
library(readr)
library(feather)


# This script takes new raw EBD data from eBird and clean it using auk R package. 
# The result (a feather file) will be further processed in Python to get data ready for the forecast model

# 1. Load new data
newebd_path <- "ebd_US-MA_202301_202303_smp_relOct-2023.txt"
raw_newdata <- read_ebd(newebd_path)


# 2. Data cleaning
new_ebd <- raw_newdata %>%
  filter(all_species_reported,
         protocol_type %in% c("Stationary", "Traveling"))


# Function to convert time observation to hours since midnight
time_to_decimal <- function(x) {
  x <- hms(x, quiet = TRUE)
  hour(x) + minute(x) / 60 + second(x) / 3600
}

new_ebd <- new_ebd %>%
  mutate(
    # convert count to integer and X to NA. IGNORE the warning "NAs introduced by coercion"
    observation_count = as.integer(observation_count),
    # effort_distance_km to 0 for stationary counts
    effort_distance_km = if_else(protocol_type == "Stationary",
                                 0, effort_distance_km),
    # convert duration to hours
    effort_hours = duration_minutes / 60,
    # speed km/h
    effort_speed_kmph = effort_distance_km / effort_hours,
    # convert time to decimal hours since midnight
    hours_of_day = time_to_decimal(time_observations_started),
    # split date into year and day of year
    year = year(observation_date)
  )

new_ebd <- new_ebd %>%
  filter(effort_hours <= 6,
         effort_distance_km <= 10,
         effort_speed_kmph <= 100,
         number_observers <= 10)
new_ebd <- select(new_ebd, checklist_id, common_name, county, observation_date,
                  locality, locality_id, locality_type, latitude, longitude,
                  hours_of_day, year)

# 3. Export to a .feather file
write_feather(new_ebd, "new_ebd.feather")