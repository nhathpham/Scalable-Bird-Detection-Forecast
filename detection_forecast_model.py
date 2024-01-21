import pandas as pd
import numpy as np
import prophet as pr
from prophet.diagnostics import performance_metrics
from prophet.diagnostics import cross_validation
import os
from multiprocessing import Pool
from tqdm.auto import tqdm
import logging
import warnings
import itertools
import os
from functools import partial
import time
from datetime import date, datetime, timedelta
import detection_newdata
import subprocess

def week_year_to_dt(week: int, year: int):
    """
    Calculates the date from the given week number and year. The calculation is done by first
    create a for January 1 with the given year, and then adds as many weeks needed using the 
    given "week" integer. We also must subtract 1 from the week since we don't want to add 7
    to the first week (which starts on Jan 1).

    Parameters:
    - week (int): week number
    - year (int): the year

    Returns:
    - datetime: the starting date of the given week number and year
    """
    dt = datetime(year, 1, 1)
    start_of_week = dt + timedelta((week - 1) * 7)

    return start_of_week



def dt_to_week_number(dt: datetime):
    """
    Calculates the week number of the given datetime. The calculation is done by first
    subtracting the given date by January 1st of that date's year to get the number of days
    elapsed. Then we divde by 7 to get the number of weeks elapsed, and then add 1 to convert
    to 1 based indexing.

    Parameters:
    - dt (datetime): The date to calculate the week number for.

    Returns:
    - int: the week number of the given date
    """
    year = dt.year

    return int((dt - datetime(year, 1, 1)).days / 7) + 1



def preprocess_data(df):
    """
    Preprocess the input DataFrame based on specific operations.

    Parameters:
    - input_data (pd.DataFrame): The input DataFrame to be processed.

    Returns:
    - pd.DataFrame: The processed DataFrame.
    """
    # Rename column 'detection_rate' to 'y'    
    processed_data = df.rename(columns={'detection_rate': 'y'})

    # Create a new datetime column 'ds' by combining 'year' and 'week' since it is required by prophet for forecasting.
    processed_data['ds'] = processed_data.apply(lambda row: week_year_to_dt(row['week'], row['year']), axis=1)

    # Drop labels from the DataFrame
    processed_data = processed_data.drop(labels=['totalChecklist_byWeekLocation', 'numChecklist_withSpecies'], axis=1)

    # Exclude rows where 'week' is equal to 53
    processed_data = processed_data[(processed_data['week'] != 53) | (processed_data['week'] != "53")]

    # Add cap and floor for logistic saturation
    processed_data['cap'] = 1
    processed_data['floor'] = 0

    return processed_data



def best_prophet_model(best_params, county_df):
    """
    Generate the best Prophet model's forecast for a given county.

    Parameters:
    - best_params (dict): Dictionary of best parameters for the Prophet model.
    - county_df (pd.DataFrame): DataFrame containing the county's time series data.

    Returns:
    - pd.DataFrame: Forecast DataFrame with columns ['ds', 'y', 'yhat', 'yhat_lower', 'yhat_upper'].
    """
    # Fit the best Prophet model to the county's data
    best_model = pr.Prophet(growth='logistic', yearly_seasonality=True,
                         weekly_seasonality=False, daily_seasonality=False, 
                         **best_params).fit(county_df)

    # Create a DataFrame for future dates (52 weeks) with specified frequency
    future = best_model.make_future_dataframe(periods=110, freq='W')
    future['cap'] = 1
    future['floor'] = 0

    # Generate forecast using the trained model
    forecast = best_model.predict(future)
    forecast['yhat'] = forecast['yhat'].clip(lower=0)

    # Add actual values to dataframe
    # result_df = pd.merge(county_df, forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], on='ds', how='outer')
    result_df = pd.merge(county_df, forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], on='ds', how='outer')

    result_df = result_df[['ds', 'actual', 'yhat', 'yhat_lower', 'yhat_upper']]

    # Have to rename here since had originally saved a copy of the y column before exponential smoothing in the
    # "actual" column. Now that we have excluded new "y" column and included in the "actual", we can rename "actual"
    # to "y".
    result_df = result_df.rename(columns={"actual": "y"})

    return result_df



def initialize_prophet_model_cv(county_df, params):
    """
    Initialize and evaluate a Prophet model for hyperparameter tuning.

    Parameters:
    - county_df (pd.DataFrame): DataFrame containing the county's time series data.
    - params (dict): Dictionary of Prophet model parameters.

    Returns:
    - pd.DataFrame: Cross-validated DataFrame with columns ['ds', 'y', 'yhat', 'yhat_lower', 'yhat_upper'].
    """
    # Initialize Prophet model and perform cross-validation
    m = pr.Prophet(growth='logistic', yearly_seasonality=True,
                   weekly_seasonality=False, daily_seasonality=False, **params).fit(county_df)

    df_cv = cross_validation(m, horizon='110 W', disable_tqdm=True)
    df_cv['cap'] = 1
    df_cv['floor'] = 0
    df_cv['yhat'] = df_cv['yhat'].clip(lower=0)

    return df_cv



def disable_loggers():
    """
    Disables all loggers and warning messages.

    Returns:
    - None
    """
    # Disable unnecessary logging and warnings
    logging.getLogger('prophet').disabled = True
    logging.getLogger('prophet.models').disabled = True
    logging.getLogger('cmdstanpy').disabled = True
    pd.options.mode.chained_assignment = None
    warnings.filterwarnings('ignore')

    logger = logging.getLogger('cmdstanpy')
    logger.addHandler(logging.NullHandler())
    logger.propagate = False
    logger.setLevel(logging.CRITICAL)



def prophet_worker(bird_county, processed_data, all_params):
    """
    Perform Prophet modeling for a specific bird and county.

    Parameters:
    - bird_county (tuple): Tuple containing bird and county names.
    - processed_data (pd.DataFrame): DataFrame containing the processed data.
    - all_params (list): List of dictionaries containing different Prophet model parameters.

    Returns:
    - Tuple: Two DataFrames - forecast results and testing results.
    """
    disable_loggers()

    bird, county = bird_county

    # Extract data for the specific bird and county
    bird_df = processed_data[processed_data["common_name"] == bird]
    test_results = pd.DataFrame(columns=['county', 'bird_name', 'RMSE', 'MAE'])
    county_df = bird_df[bird_df["county"] == county]
    
    # Apply exponential weighted moving average to 'y' column. We first have to keep a copy of the "y" column
    # in the "actual" column so we can merge it in the "best_prophet_model" function.
    county_df['actual'] = county_df['y']
    county_df['y'] = county_df['y'].ewm(span=4).mean()

    # Use cross-validation to evaluate parameters
    rmses = []
    maes = []
    for params in all_params:
        m = initialize_prophet_model_cv(county_df, params)
        df_p = performance_metrics(m, metrics=['rmse', 'mae'])
        rmses.append(df_p['rmse'].values[0])
        maes.append(df_p['mae'].values[0])

    # Find the best parameters
    best_rmse_idx = np.argmin(rmses)
    best_params_rmse = all_params[best_rmse_idx]
    best_rmse = np.min(rmses)

    mae = maes[best_rmse_idx]

    # Append testing results
    test_results.loc[-1] = [county, bird, best_rmse, mae]

    # Generate forecast using the best params
    result_df = best_prophet_model(best_params_rmse,  county_df)

    # Add additional columns to the forecast results
    result_df['county'] = county
    result_df['common_name'] = bird

    # Calculate week number by applying function
    result_df['week'] = result_df.apply(lambda row: dt_to_week_number(row['ds']), axis=1)
    result_df['year'] = result_df['ds'].dt.year

    # Exclude rows that have a week of 52 but also are NA for the "y" and are in 2022
    result_df = result_df[~((result_df['week'] == 52) & (result_df['y'].isna()) & (result_df['year'] == 2022))]

    # Include only the rows that have a week below 52
    result_df = result_df[(result_df['week'] <= 52) & (result_df['year'] <= 2024)]

    return result_df, test_results


def main():
    disable_loggers()
    # Run R script
    result = subprocess.run(["Rscript", "datacleaning_ebd.R"], capture_output=True, text=True)
    # Print standard output and error
    print("Standard Output:", result.stdout)
    print("Standard Error:", result.stderr)

    # Check if the R script ran successfully
    if result.returncode == 0:
        print("R script executed successfully.")
        detection_newdata.update_feather("allbirds_detection.feather", "new_ebd.feather")
    else:
        print("Error: R script failed to execute.")

    df = pd.read_feather("allbirds_detection.feather")
    processed_data = preprocess_data(df)
    
    birds = processed_data["common_name"].unique()
    counties = processed_data["county"].unique()
    param_grid = {'changepoint_prior_scale': [0.1, 0.5, 1, 5]}
    all_params = [dict(zip(param_grid.keys(), v)) for v in itertools.product(*param_grid.values())]
    bird_county_pairs = [(bird, county) for bird in birds for county in counties]
    partial_prophet_worker = partial(prophet_worker, processed_data=processed_data, all_params=all_params)

    start_time = time.time()
    with Pool(processes=os.cpu_count()) as p:
        pool_results = list(tqdm(p.imap_unordered(partial_prophet_worker, bird_county_pairs), total=len(bird_county_pairs)))
        p.close()
        p.join()
    end_time = time.time()
    elapsed_time_seconds = end_time - start_time
    elapsed_time = timedelta(seconds=elapsed_time_seconds)
    print(f"--- {elapsed_time} --- hours:minutes:seconds")

    # Gather results
    result_dfs, test_results = zip(*pool_results)
    all_forecasts = pd.concat(result_dfs, ignore_index=True)

    # Rename columns for tableau
    all_forecasts = all_forecasts.rename(columns={'ds': 'ts', 'y': 'actual', 'yhat': 'forecast', 
                                          'yhat_lower': 'forecast_lower', 'yhat_upper': 'forecast_upper'})
    test_results = pd.concat(test_results, ignore_index=True)

    # Save the concatenated dataframe to a CSV file
    print("Number of 53 weeks:", len(all_forecasts[(all_forecasts["week"] == 53) | (all_forecasts["week"] == "53")]))
    all_forecasts.to_csv('110_allbirds_forecasts.csv', index=False)
    test_results.to_csv('110_allbirds_test_results.csv', index=False)

if __name__ == '__main__':
    main()
