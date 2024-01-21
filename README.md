# Optimal Birdwatching in Massachussetts
![GitHub last commit](https://img.shields.io/github/last-commit/nhathpham/Scalable-Bird-Detection-Forecast)
![contributors](https://img.shields.io/github/contributors/nhathpham/Scalable-Bird-Detection-Forecast) 
![codesize](https://img.shields.io/github/languages/code-size/nhathpham/Scalable-Bird-Detection-Forecast) 

## Project Overview

Our bird-watching project aims to address the challenges faced by enthusiasts, conservationists, and researchers in planning effective bird-watching excursions, particularly for beginners. We build accurate and scalable times series models to forecast weekly detection rates of 465 species in 14 MA counties and provide recommendations for optimal bird-watching spots and times. The results are presented on an interactive Tableau dashboard for user-friendly trip planning.

Throughout the project, we actively engage with birdwatchers and conservationists across Massachussetts to understand their needs, obtain knowledge on birding practices, and gather feedback for development iterations.

## Data
### Source & Acquisition
#### eBird
- Utilize eBird dataset from Cornell Lab of Ornithology (ebird.org/data) comprising global bird sightings by professional and amateur bird watchers (Cornell, 2023).
- Conducted a survey among Massachusetts (MA) birders (102 responses), revealing 83% prefer regular or nearby locations (Appendix Figure A1), guiding our exclusive focus on MA.
- Extracted 8.5GB of MA bird sighting data from eBird.org (2013-2022).
- Dataset comprises observation and checklist data; observation rows detail individual bird sightings, including species, location, date, time, and notes. Checklist data aggregates observations for specific outings, summarizing total species count, location, date, time, and participant count.
- Given the inadequacy of eBird's API for detailed analyses, we opted for website data download over API calls.

#### Other
- National Centers for Environmental Information (NCEI): for temperature and precipitation data. Attempted incorporation into the forecast model as environmental regressors, but no improvement observed, likely due to mismatched units (monthly temperature data vs. weekly detection rate data); not included in the final model.
- American Birding Association’s 2023 species checklist and Massachusetts Avian Records Committee’s birds-in-review list: for uncommon bird species, supporting the birding activity analysis
  

### Data processing
- Initial data cleaning and filtering used the 'auk' package in R, designed for eBird data. Only complete checklists were included, with refinement by restricting checklist duration, distances, speeds, and group sizes.
- Group bird sightings by county and aggregated into weekly intervals.
- Null detection rates were assigned to weeks with fewer than 5 checklists to maintain time series continuity for uninterrupted data sequences.
- Additional processing on location data uses KDTree algorithm and geodesic package for pairing user-input addresses with nearest predefined locations

## Code structure for forecast model
```bash
├── cleaned data
│   ├── allbirds_detection.feather
├── data_cleaning.R
├── data_finalpreprocessing.py
├── detection_forecast_model.py
├── deliverables
│   ├── Final Presentation - Phase 1.pdf
│   ├── Final Presentation - Phase 2.pdf
│   ├── Final Report - Phase 1.docx
│   ├── Final Report - Phase 2.docx
```

## Result 

### Forecast model evaluation 

### Tableau dashboard

### Birding activity analysis

## Future work



# Demo:

Voila - Binder link: https://mybinder.org/v2/gh/nhathpham/Bird-Watching-Recommendation-System/main?labpath=%2Fvoila%2Frender%2FactivityMaps_1129.ipynb
- Voilà turns Jupyter notebooks into standalone web applications. 
Jupyter notebook - Binder link: 

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/nhathpham/Bird-Watching-Recommendation-System/main?urlpath=voila%2Frender%2FactivityMaps_1129.ipynb)


# Packages Used
- Facebook's Prophet forecasting package
- Numpy
- Pandas

# Data Source
We used the eBird dataset from the Cornell Lab of Ornithology. The dataset is organized into two primary components: observation data and checklist data. In the observation data, each row represents an individual bird species sighting, providing detailed information about the species observed, the specific location, date, time, and any additional notes. Checklist data, on the other hand, compiles these individual observations into structured records centered around specific bird-watching outings or events. 

# Design:
For preprocessing, we streamlined the dataset by removing unnecessary columns and renaming the date and target columns, along with adjusting the data types. We employed logistic regression and specified a saturating mininum. This stabilized forecasted values as they approached the limits over time. When forecasted values fell below zero, we adjusted forecasts to zero to maintain logical consistency.

For model optimization, we focused on tuning changepoint prior scale parameter through cross-validation. We implemented grid search to identify the parameter setting that minimized RMSE, treating each bird and county independently. To efficiently execute this process, we developed a function that tests all potential parameters for a given bird-county pair. We leveraged Python’s `multiprocessing` library, specifically the `Pool` object, to facilitate parallel testing of these combinations, enhancing the speed and efficiency of our parameter tuning efforts.

We evaluated our model's performance using RMSE and MAE metrics.

# How to run:
1. Clone this repo
2. Download the [eBird data](https://ebird.org/data/download)
3. Run `detection_newdata.py` to prepare the data
4. Run `cleaned_bird_model.py` on the prepared data to get forecast results
