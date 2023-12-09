# Bird-Watching-Recommendation-System
This project’s objective is to recommend species of birds to a user based on a user's characteristics and observation history, and then predict the most accurate and optimal times and locations to sight these birds based on previous bird behavior and migratory patterns. 

This project used 465 bird species across 14 Massachusetts counties. The data consisted of sightings from 2013 to 2022 and aimed to forecast for the years 2023 and 2024. 

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