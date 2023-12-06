import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


######## NOTE: The structure of this script is for yearly updates (new data that has full 12 months) ################
def update_feather(all_birds_file, new_ebd_file):
    # 1. Load data
    # Load current training data (final data used for modeling)
    current_df = pd.read_feather(all_birds_file)  

    # Load new clean ebd data
    new_ebd = pd.read_feather(new_ebd_file)


    # 2. Filter to columns needed for forecast model
    cols_keep = ['checklist_id', 'common_name', 'county', 'observation_date']
    ebd = new_ebd[cols_keep]
    ebd = ebd.drop_duplicates(subset=['checklist_id', 'common_name'], keep='first').reset_index(drop=True)

    # Calculate the year and week from date
    ebd['observation_date'] = pd.to_datetime(ebd['observation_date'])
    ebd['week'] = ebd['observation_date'].dt.isocalendar().week
    ebd['year'] = ebd['observation_date'].dt.isocalendar().year

    # Filter out rows in new_df that have a year_week combination already present in the unique set of current_df
    current_df['year_week'] = current_df['year'].astype(str) + "-" + current_df['week'].astype(str)
    ebd['year_week'] = ebd['year'].astype(str) + "-" + ebd['week'].astype(str)
    unique_year_week_current = set(current_df['year_week'].unique())
    ebd = ebd[~ebd['year_week'].isin(unique_year_week_current)]
    current_df.drop(columns='year_week', inplace=True)

    # 3. Calculate weekly detection rate
    # a. Calculate the total number of observations of each species in each county on each week
    species_cl = ebd.groupby(['common_name', 'county', 'year', 'week']).size().reset_index(name='numChecklist_withSpecies')
    weekly_cl = ebd.groupby(['county', 'year', 'week'])['checklist_id'].nunique().reset_index(name='totalChecklist_byWeekLocation')
    new_df =  pd.merge(species_cl, weekly_cl, on=['county', 'year', 'week'], how='left')

    # b. Calculate detection rate
    new_df['detection_rate'] = new_df['numChecklist_withSpecies'] / new_df['totalChecklist_byWeekLocation']
    new_df = new_df.sort_values(by=['year','week'])

    # 4. Create a df with all weeks (52 or 53) for each year in each county, with total checklists (for that week and county)
    # DataFrame with combinations for years with 52 weeks
    standard_combinations = pd.MultiIndex.from_product([
        weekly_cl['county'].unique(),
        weekly_cl['year'].unique(),
        range(1, 53)  # Standard 52 weeks
    ], names=['county', 'year', 'week']).to_frame(index=False)

    # Find years with a maximum week number of 53
    max_week_by_year = weekly_cl.groupby('year')['week'].max()
    # List of years with 53 weeks
    years_53_weeks = max_week_by_year[max_week_by_year == 53].index.tolist()
    # DataFrame with combinations for years with 53 weeks
    extra_week_combinations = pd.MultiIndex.from_product([
        weekly_cl['county'].unique(),
        years_53_weeks,
        [53]
    ], names=['county', 'year', 'week']).to_frame(index=False)

    all_combinations = pd.concat([standard_combinations, extra_week_combinations], ignore_index=True)
    weekly_cl_complete = pd.merge(all_combinations, weekly_cl, on=['county', 'year', 'week'], how='left')

    # 5. Get weekly detection rate for each bird species observed in each county in all weeks of each year 
    counties = new_df['county'].unique().tolist()
    years = new_df['year'].unique().tolist()
    # we need 465 birds
    birds = current_df['common_name'].unique().tolist()
    weeks_per_year = {year: 53 if year in years_53_weeks else 52 for year in years}

    new_df_allWeeks = pd.DataFrame()
    for bird in birds:
        bird_df = new_df[new_df['common_name'] == bird].drop('totalChecklist_byWeekLocation', axis=1)
        for county in counties:
            # Create a full index DataFrame for each county
            all_weeks = [list(range(1, weeks_per_year[year] + 1)) for year in years]
            all_weeks = [item for sublist in all_weeks for item in sublist]  # Flatten the list
            repeated_years = [[year]*weeks_per_year[year] for year in years]
            repeated_years = [item for sublist in repeated_years for item in sublist]  # Flatten the list
            
            full_index = pd.MultiIndex.from_arrays([repeated_years, all_weeks], names=['year', 'week'])
            full_county = pd.DataFrame(index=full_index).reset_index()
            full_county ['county'] = county
            
            # Merge totalChecklist_byWeekLocation from weekly_cl_complete
            full_county = pd.merge(full_county, weekly_cl_complete, on=['county', 'year', 'week'], how='left')
            
            # Merge this DataFrame with the bird-specific data
            merged_df = pd.merge(full_county, bird_df[bird_df['county'] == county], on=['county', 'year', 'week'], how='left')
            # Fill the bird name (for Nan rows)
            merged_df['common_name'] = bird
            
            # Append the results to the final DataFrame
            new_df_allWeeks = pd.concat([new_df_allWeeks, merged_df], ignore_index=True)
            
    new_df_allWeeks.reset_index(drop=True, inplace=True)
    # 6. Add threshold for detection
    #  Set detection_rate to 0 where totalChecklist_byWeekLocation is not null and numChecklist_withSpecies is null
    condition1 = (new_df_allWeeks['totalChecklist_byWeekLocation'].notnull()) & (new_df_allWeeks['numChecklist_withSpecies'].isnull())
    new_df_allWeeks.loc[condition1, 'detection_rate'] = 0

    # Set detection_rate to NaN where totalChecklist_byWeekLocation is less than 5
    condition2 = new_df_allWeeks['totalChecklist_byWeekLocation'] <= 5
    new_df_allWeeks.loc[condition2, 'detection_rate'] = np.nan

    ####################### ONLY RUN THIS BECAUSE OUR TESTING NEW DATA THAT IS LESS THAN 1 YEAR #############################
    max_newWeek = new_df.week.max()
    new_df_final = new_df_allWeeks[new_df_allWeeks.week <=max_newWeek]


    # 7. Append new data to current data
    updated_df = pd.concat([current_df, new_df_final], ignore_index=True)
    updated_df= updated_df.reset_index(drop=True)

    ######################### SINCE WE ARE TESTING NEW DATA LESS THAN 1 YEAR, DO NOT RUN THIS #########################
    # 8. Remove the first year to remain 10-year rolling data
    # min_year_to_keep = updated_df.year.max() - 9  # Keeping 10 years, so subtract 9
    # allbirds_detection = allbirds_detection[allbirds_detection.year >= min_year_to_keep] 

    updated_df['year'] = updated_df['year'].astype(int)
    # 9. FINAL UPDATED DATA, READY FOR FORECAST MODEL
    updated_df.to_feather("allbirds_detection.feather")
    print("finished feather update")