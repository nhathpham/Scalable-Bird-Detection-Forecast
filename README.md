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
- NCEI: for temperature and precipitation data. Incorporation into the forecast model as environmental regressors yielded no improvement observed, likely due to mismatched units (monthly temperature data vs. weekly detection rate data); not included in the final model.
- American Birding Association’s 2023 species checklist and Massachusetts Avian Records Committee’s birds-in-review list: for uncommon bird species, supporting the birding activity analysis
  

### Data processing
- Initial data cleaning and filtering used the 'auk' package in R, designed for eBird data. Only complete checklists were included, with refinement by restricting checklist duration, distances, speeds, and group sizes.
- Group bird sightings by county and aggregated into weekly intervals.
- Null detection rates were assigned to weeks with fewer than 5 checklists to maintain time series continuity for uninterrupted data sequences.
- Additional processing on location data uses KDTree algorithm and geodesic package for pairing user-input addresses with nearest predefined locations

## Forecast model
### Code structure for forecast model
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

### Model training
To predict weekly bird detection rates, we tested several statistical and machine learning time series forecasting models on a subset of data (50 species/ 700 models). After evaluating their performance and scalability, we narrowed our selection to Prophet and Greykite, with Greykite outperforming in overall efficacy.  Prophet is a specialized time series forecasting model that decomposes time series data into trend, seasonality, and other components and combines them in an additive model. Greykite uses a hybrid forecasting model that can incorporate a wide range of forecasting techniques to handle diverse time series data. 

We further fine-tuned both models using parameter tuning via grid search, cross-validation, and parallel processing. After evaluating their performance and processing speed, we selected Prophet as the more efficient method to extend our forecasts to all bird species. 

We employed logistic regression and specified a saturating mininum. This stabilized forecasted values as they approached the limits over time. When forecasted values fell below zero, we adjusted forecasts to zero to maintain logical consistency.

For model optimization, we focused on tuning changepoint prior scale parameter through cross-validation. We implemented grid search to identify the parameter setting that minimized RMSE, treating each bird and county independently. To efficiently execute this process, we developed a function that tests all potential parameters for a given bird-county pair. We leveraged Python’s `multiprocessing` library, specifically the `Pool` object, to facilitate parallel testing of these combinations, enhancing the speed and efficiency of our parameter tuning efforts.
Specific details on hyperparameter tuning and parallel processing are in the Final Report - Phase 2.docx document.

We evaluated our models' performance using RMSE and MAE metrics.

### Result 
**1/ Total runtime** (6510 models): 1 hr 30 min, 11.6 seconds/ species
**2/ Satisfactory accuracy**
<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/989b45ef-74f1-42f5-bd85-00f2e07049e0" width="400">

**3/ Model performance varies across counties**
![image](https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/57f1377e-cc21-4d41-a087-a51bb13b1b55)
<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/57f1377e-cc21-4d41-a087-a51bb13b1b55" width="700">

**4/ Model performance varies across species**
![image](https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/2f03f4bb-0ba2-46f1-86cd-9f73eee91743)
<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/2f03f4bb-0ba2-46f1-86cd-9f73eee91743" width="700">

![image](https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/825272a9-c312-415b-8b96-cd9378637aaf)
<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/825272a9-c312-415b-8b96-cd9378637aaf" width="700">

![image](https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/cacc31d8-2148-4c81-a5ba-b8dd1ad24cb2)
<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/cacc31d8-2148-4c81-a5ba-b8dd1ad24cb2" width="700">

![image](https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/2710d9ba-ff8b-443f-8260-4f48da65fe5b)
<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/2710d9ba-ff8b-443f-8260-4f48da65fe5b" width="700">



## Tableau dashboard

## Birding activity analysis
Voila - Binder link: https://mybinder.org/v2/gh/nhathpham/Bird-Watching-Recommendation-System/main?labpath=%2Fvoila%2Frender%2FactivityMaps_1129.ipynb
- Voilà turns Jupyter notebooks into standalone web applications. 
Jupyter notebook - Binder link: 
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/nhathpham/Bird-Watching-Recommendation-System/main?urlpath=voila%2Frender%2FactivityMaps_1129.ipynb)



## Pipeline for yearly data updates
1. Download new data from eBird [eBird data](https://ebird.org/data/download)
2. Run data_cleaning.R and data_finalpreprocessing.py to prepare new data
3. Run detection_forecast_model.py on the prepared data to retrain model and get new forecast results

# Packages Used
- Facebook's Prophet forecasting package
- Numpy
- Pandas

# How to run:
1. Clone this repo

