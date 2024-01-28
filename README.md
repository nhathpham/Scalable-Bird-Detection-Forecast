# Optimal Birdwatching in Massachussetts
![GitHub last commit](https://img.shields.io/github/last-commit/nhathpham/Scalable-Bird-Detection-Forecast)
![contributors](https://img.shields.io/github/contributors/nhathpham/Scalable-Bird-Detection-Forecast) 
![codesize](https://img.shields.io/github/languages/code-size/nhathpham/Scalable-Bird-Detection-Forecast) 

## Project Overview

Our project aims to address the challenges faced by enthusiasts, conservationists, and researchers in planning effective bird-watching trips, particularly for beginners. 

We build accurate and scalable times series models to forecast weekly detection rates of 465 species in each of 14 MA counties. We also provide recommendations for optimal locations and times through descriptive analysis. The results are presented on an interactive Tableau dashboard for user-friendly trip planning.

Throughout the project, we actively engaged with birdwatchers and conservationists across Massachussetts to understand their needs, obtain knowledge on birding practices, and gather feedback for development iterations.

## Data
### Source & Acquisition
#### eBird
- A citizen science project from Cornell Lab of Ornithology (ebird.org/data) comprising global bird sightings by bird watchers
- We conducted a survey among Massachusetts (MA) birders (102 responses), revealing 83% prefer regular or nearby locations, guiding our exclusive focus on MA.
- Extracted 8.5GB of MA bird sighting data from eBird.org (2013-2022).
- Dataset comprises observation and checklist data:
  + *Observation data*: individual bird sightings, including species, location, date, time, and notes
  + *Checklist data*: aggregates observations for each specific birding trip, summarizing total species count, location, date, time, and participant count.
- Given the inadequacy of eBird's API for detailed analyses, we opted for website data download over API calls.

#### Others
- American Birding Association’s 2023 species checklist and Massachusetts Avian Records Committee’s birds-in-review list: for uncommon bird species, supporting the birding activity analysis
- NCEI: for temperature and precipitation data. Incorporation into the forecast model as environmental regressors yielded no improvement observed, hence not included in the final model.
  

### Data processing
- Use R's 'auk' package designed for eBird data. Only complete checklists were included, with refinement by restricting checklist duration, distances, speeds, and group sizes.
-  Group bird sightings by county and aggregated into weekly intervals.
- Assign null detection rates to weeks with fewer than 5 checklists to maintain time series continuity for uninterrupted data sequences.
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
**1. Algorithm selection:**
- *Initial testing*: evaluated several time series forecasting models on a sample of 50 species (700 models). Narrowed down options to Prophet and Silverkite for performance and scalability
- *Comparison Silverkite and Prophet*:
  + Both accept similar time series data and provide options for customizing seasonality, holidays, trend handling, and hyperparameter tuning. 
  + Prophet uses a Bayesian approach to fit a model
  + Silverkite uses more traditional models such as a ridge, elastic net, and boosted trees
  + Both can model linear growth. Only Silverkite can handle square root and quadratic growth, while only Prophet can model logistic growth.
- *Fine-tune both models* using parameter tuning via grid search, cross-validation, and parallel processing.
- *Final choice*: Prophet due to efficiency for broader forecasting.

**2. Final Prophet model:**
- Employ logistic growth for a saturating minimum, stabilizing values near limits
- Predict zero for forecasted values below zero for logical consistency.
  
**3. Optimization:**
- Focus on tuning the changepoint prior scale parameter.
- Implement grid search with RMSE minimization for each bird-county pair.
- Develop a function for testing parameters within a multiprocessing.Pool object for parallel processing and efficiency.

Please refer to Final Report - Phase 2.docx for hyperparameter tuning and parallel processing details.

**4. Evaluation:** Models' performance was evaluated using RMSE and MAE metrics.

### Result 
**1. Total runtime** (6510 models): 1 hr 30 min, 11.6 seconds/ species

**2. Satisfactory accuracy**

<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/989b45ef-74f1-42f5-bd85-00f2e07049e0" width="400">


**3. Model performance varies across counties**

<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/57f1377e-cc21-4d41-a087-a51bb13b1b55" width="550">


**4 Model performance varies across species**
- High predictive accuracy for migratory birds because of pronounced seasonal patterns

<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/2f03f4bb-0ba2-46f1-86cd-9f73eee91743" width="400">

- Lower predictive accuracy for resident birds due to variable detection patterns, underreporting, complex behaviors
<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/825272a9-c312-415b-8b96-cd9378637aaf" width="400">

- Captures seasonality and trends well, especially changes that occur gradually; struggles with abrupt fluctuations
<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/cacc31d8-2148-4c81-a5ba-b8dd1ad24cb2" width="400">

- Performs well with elusive, hard-to-detect species (falcons, owls)
<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/2710d9ba-ff8b-443f-8260-4f48da65fe5b" width="400">

## Tableau dashboard

Access the dashboard here: https://tabsoft.co/3uFSm5S

<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/eac47e0e-d595-4788-8626-d8c3013abbc4" width="600">

## Birding activity analysis

Voila - Binder link: https://mybinder.org/v2/gh/nhathpham/Bird-Watching-Recommendation-System/main?labpath=%2Fvoila%2Frender%2FactivityMaps_1129.ipynb
- Voilà turns Jupyter notebooks into standalone web applications. 
Jupyter notebook - Binder link: 
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/nhathpham/Bird-Watching-Recommendation-System/main?urlpath=voila%2Frender%2FactivityMaps_1129.ipynb)



## Pipeline for yearly data updates
1. Download new data from eBird [eBird data](https://ebird.org/data/download)
2. Run data_cleaning.R and data_finalpreprocessing.py to prepare new data
3. Run detection_forecast_model.py on the prepared data to retrain model and get new forecast results

