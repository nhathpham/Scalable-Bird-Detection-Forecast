# Optimal Birdwatching in Massachussetts
![GitHub last commit](https://img.shields.io/github/last-commit/nhathpham/Scalable-Bird-Detection-Forecast)
![contributors](https://img.shields.io/github/contributors/nhathpham/Scalable-Bird-Detection-Forecast) 
![codesize](https://img.shields.io/github/languages/code-size/nhathpham/Scalable-Bird-Detection-Forecast) 

## Project Overview

This project aims to create a tool to help bird enthusiasts, conservationists, and researchers in planning effective bird-watching trips, particularly for beginners. 

We built accurate and scalable times series models to forecast weekly detection rates of 465 species in each of 14 Massachussetts (MA) counties. We also provided recommendations for optimal locations and times through descriptive analysis. Results are presented on an interactive Tableau dashboard.

Throughout the project, we actively engaged with birdwatchers and conservationists across MA to understand their needs, obtain knowledge on birding practices, and gather feedback for development iterations.

## Data
### 1. Source & Acquisition
#### eBird
- A citizen science project from Cornell Lab of Ornithology comprising global bird sightings by bird watchers
- Our survey with 102 MA birders showed an 83% preference for local locations, leading to our exclusive focus on the state. We extracted 8.5GB of bird sighting data from eBird.org (2013-2022).
- *Observation data*: individual bird sightings, including species, location, date, time, and notes
- *Checklist data*: aggregates observations for each specific birding trip, summarizing total species count, location, date, time, and participant count.
- Given the inadequacy of eBird's API for detailed analyses, we opted for website data download over API calls.

#### Others
- American Birding Association’s 2023 and Massachusetts Avian Records Committee’s species list
- NCEI: for temperature and precipitation data. Incorporation into the forecast model as environmental regressors yielded no improvement observed, hence not included in the final model.
  

### 2. Data processing
- Use R's 'auk' package designed for eBird data. Only complete checklists were included, with refinement by restricting checklist duration, distances, speeds, and group sizes.
- Group bird sightings by county and aggregated into weekly intervals.
- Assign null detection rates to weeks with fewer than 5 checklists to maintain time series continuity for uninterrupted data sequences.
- Additional processing on location data uses KDTree algorithm and geodesic package for pairing user-input addresses with nearest predefined locations

## Forecast model
### 1. Code structure for forecast model
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

### 2. Model training
**2.1 Algorithm selection:**
- *Initial testing*: evaluated several time series forecasting models on a sample of 50 species (700 models). Narrowed down options to Prophet and Silverkite for performance and scalability
- *Comparison Silverkite and Prophet*:
  + Both provide options for customizing seasonality, holidays, trend handling, and hyperparameter tuning. 
  + Prophet uses a Bayesian approach to fit models. Silverkite uses more traditional models such as a ridge, elastic net, and boosted trees
  + Both can model linear growth. Only Silverkite can handle square root and quadratic growth, while only Prophet can model logistic growth.
- *Fine-tune both models* using parameter tuning via grid search, cross-validation, and parallel processing.
- *Final choice*: Prophet due to efficiency for broader forecasting.

**2.2 Final Prophet model:**
- Employ logistic growth for a saturating minimum, stabilizing values near limits
- Predict zero for forecasted values below zero for logical consistency.
  
**2.3 Optimization:**
- Focus on tuning the changepoint prior scale parameter.
- Implement grid search with RMSE minimization for each bird-county pair.
- Develop a function for testing parameters within a multiprocessing.Pool object for parallel processing and efficiency.

Please refer to Final Report - Phase 2.docx for hyperparameter tuning and parallel processing details.

**2.4 Evaluation:** Models' performance was evaluated using RMSE and MAE metrics.

### 2. Result 
**2.1 Total runtime** (6510 models): 1 hr 30 min, 11.6 seconds/ species

**2.2 Satisfactory accuracy**

<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/989b45ef-74f1-42f5-bd85-00f2e07049e0" width="400">


**2.3 Model performance varies across counties**

<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/57f1377e-cc21-4d41-a087-a51bb13b1b55" width="550">


**2.4 Model performance varies across species**
- High predictive accuracy for migratory birds because of pronounced seasonal patterns

<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/2f03f4bb-0ba2-46f1-86cd-9f73eee91743" width="400">

- Lower predictive accuracy for resident birds due to variable detection patterns, underreporting, complex behaviors
<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/825272a9-c312-415b-8b96-cd9378637aaf" width="400">

- Captures seasonality and trends well, especially changes that occur gradually; struggles with abrupt fluctuations
<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/cacc31d8-2148-4c81-a5ba-b8dd1ad24cb2" width="400">

- Performs well with elusive, hard-to-detect species (falcons, owls)
<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/2710d9ba-ff8b-443f-8260-4f48da65fe5b" width="400">

## Tableau dashboard

- Access the dashboard [**here**](https://tabsoft.co/3uFSm5S)
- [Demo Video](https://www.youtube.com/watch?v=tr-RAk1-CeE)
<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/eac47e0e-d595-4788-8626-d8c3013abbc4" width="600">

## Birding activity analysis

This analysis aims to find less-known and heavily frequented birding spots, helping birders discover new locations and balance environmental impact. Using 2022 eBird records, we divided the state into 8x8km grid cells and assessed popularity and diversity with key metrics. 

We created interactive maps to visualize the findings, currently hosted on Binder, with plans to improve speed and explore alternative hosting solutions.

Explore Maps:
- [Demo Video](https://www.youtube.com/watch?v=tGmr9RT5qmY)
- [Interactive Maps](https://mybinder.org/v2/gh/nhathpham/Scalable-Bird-Detection-Forecast/main?labpath=voila%2Frender%2Factivity_maps.ipynb) (performance issues; we're exploring alternative hosting options)

## User Feedback & Future Work
- Some feedback from users on the dashboard:
<img src="https://github.com/nhathpham/Scalable-Bird-Detection-Forecast/assets/87089936/5bcd2bcf-5f7a-40f9-9204-d8403bfabaf0" width="400">

- Explore model scaling through species clustering and hierarchical modeling
- Integrate habitat and weather data to improve forecast models
- Upgrade infrastructure using cloud solutions and develop a Flask app for centralized tool access

## Pipeline for yearly data updates
1. Download new data from eBird [eBird data](https://ebird.org/data/download)
2. Run data_cleaning.R and data_finalpreprocessing.py to prepare new data
3. Run detection_forecast_model.py on the prepared data to retrain model and get new forecast results

