import numpy as np
import pandas as pd
import string
import os


def energy_data():

    '''Initial formatting of energy dataframe

    This function stores energy production data into
    a dataframe and does initial formatting. The data files
    are located in the data/solar_output directory. The function
    reads in each file individually and stores them all into a 
    single dataframe. Aggregates the data into hourly time index 
    and adds two features used for modeling.

    Returns
        hourly: formatted energy datafrmae

    '''
    # collect all energy files from data/solar_output/ directory
    filelist = os.listdir('../../data/solar_output/')

    # add file path to each file
    fl = ['../../data/solar_output/' + str(f) for f in filelist]

    # store data from each file in a dataframe
    dfs = [pd.read_csv(f) for f in fl]

    # combine individual energy dataframes into one dataframe
    big_df = pd.concat(dfs)

    # change column names
    big_df.columns = ['time', 'nexus_meter', 'inverter']

    # drop irrelevant rows and columns
    big_df.drop([0,1], axis=0, inplace=True)
    big_df.drop('inverter', axis=1, inplace=True)

    # convert time column to datetime
    big_df['time'] = pd.to_datetime(big_df['time'])

    # order dataframe by time column and set as index
    big_df = big_df.sort_values('time')
    big_df.set_index('time', inplace=True)

    # convert datatypes to float
    big_df = big_df.astype(float)

    # aggregate to hourly time index
    hourly = big_df.resample('H').sum()

    hourly = hourly['2018-01-30':]

    # add week of year and hour of day columns
    hourly['week'] = hourly.index.week
    hourly['hour'] = hourly.index.hour

    # return formatted energy dataframe
    return hourly

def weather_data():

    '''Initial formatting of weather dataframe

    This function reads weather data into a dataframe and 
    does initial formatting and processing steps. The data
    file is located in the data/weather/ directory. The function
    subsets the dataframe to include relevant columns. Removes 
    extraneous letters from a few columns and converts symbols
    representing missing data to np.nan. Also drops rows not 
    relevant for analysis.

    Returns:
        weather_df: formatted weather dataframe

    '''

    # columns relevant for analysis
    weather_cols = ['HourlyAltimeterSetting', 'HourlyDewPointTemperature', 'HourlyDryBulbTemperature',
    'HourlyRelativeHumidity', 'HourlySkyConditions', 'HourlyStationPressure', 
    'HourlyVisibility', 'HourlyWindSpeed', 'HourlyWindDirection', 'HourlyPrecipitation']

    # store weather data as dataframe
    df = pd.read_csv('../../data/weather/weatherstation2.csv')

    # convert time column to datetime object and set as index
    df['DATE'] = pd.to_datetime(df['DATE'])
    df.set_index('DATE', inplace=True)

    # convert all occurences of 'T' to 0 in HourlyPrecipitation
    df['HourlyPrecipitation'] = ['0.00' if val == 'T' else val for val in df['HourlyPrecipitation']]

    # iterates over columns and removes extraneous letters present
    cols_with_letter = '123'
    while len(cols_with_letter) > 0:
        cols_with_letter = columns_with_letter(df[weather_cols])

        for col in cols_with_letter:
            letter = letter_in_column(df[col])
            df[col] = remove_letter_from_column(df, col, letter)

    # drops irrelevant rows
    to_drop = df[(df.index.hour == 23) & (df.index.minute == 59)].index
    df.drop(to_drop, axis=0, inplace=True)
    
    # converts all occurances of '*' to np.nan
    df['HourlyDewPointTemperature'].loc[df['HourlyDewPointTemperature'] == '*'] = np.nan
    df['HourlyDryBulbTemperature'].loc[df['HourlyDryBulbTemperature'] == '*'] = np.nan
    df['HourlyRelativeHumidity'].loc[df['HourlyRelativeHumidity'] == '*'] = np.nan
    df['HourlyVisibility'].loc[df['HourlyVisibility'] == '*'] = np.nan   

    # converts all occurences of ' ' to np.nan
    df['HourlyWindDirection'] = df['HourlyWindDirection'].replace('', np.nan) 

    # calculates cloud percentage from 'HourlySkyConditions
    df['cloud_coverage'] = cloud_coverage(df['HourlySkyConditions'])
    weather_cols.append('cloud_coverage')

    # returns formatted dataframe
    return df[weather_cols].drop('HourlySkyConditions', axis=1)


def columns_with_letter(df):

    '''Determines which columns have an extraneous letter

    Multiple columns have letters at the end of the numerical
    values. This prevents numerical manipulation. This function
    determines which columns have these letter so they can be
    removed.

    Args
        df: dataframe with columns to be checked
    
    Returns
        cols: set of columns with extraneous letters
    '''
    alph = string.ascii_lowercase
    cols = []
    for col in df.columns:
        for row in df[col].values:
            try:
                if row[-1].lower() in alph:
                    cols.append(col)
            except:
                pass
    return np.unique(cols)

def letter_in_column(col):

    '''Determines the specific letter in a given column

    Complement to columns_with_letter. This function
    searches through each value in a column and finds 
    what letter is present in the column. If no letters
    are found, function returns none.

    Args
        col: column to be searched for letter

    Returns
        val: letter in column. 
        
        returns None if no letter is found
    '''
    alph = string.ascii_lowercase
    val = None
    for row in col.values:
        try:
            if row[-1].lower() in alph:
                val = row[-1]
        except:
            pass
    return val

def remove_letter_from_column(df, col, letter):

    '''Removes letter from column

    Complement to letter_in_column. This function
    iterates through each value in the column, adds
    each value to the list, and removes an extraneous
    letter if present before adding to the list. It then
    returns the column as a list of its values with no
    letters present.

    Args
        df: dataframe containing column with extraneous letter
        col: column in df with extraneous letter
        letter: letter present in col

    Returns
        lst: all values from col with letter removed
    '''
    lst = []
    for val in df[col].values:
        if letter in str(val):
            lst.append(val.replace(letter, ''))
        else:
            lst.append(val)
    return lst

def cloud_coverage(sky_conditions):

    '''Calculates cloud coverage percentage from HourlySkyConditions

    This function uses the various cloud layers present in 
    the column HourlySkyConditions to compute the percent 
    cloud coverage at a given time. According to documentation,
    when multiple cloud layers are present I am to use the highest
    layer as an accurate representation of cloud cover. This function
    uses the measure of the highest cloud layer in oktas to compute
    percentage of cloud cover.

    Args:
        sky_conditions: data from NOAA giving cloud coverage information

    Returns
        cloud_percent: percent of sky covered by clouds for each observation
    '''
    clouds = []
    for val in sky_conditions.values:
        if type(val) == float:
            clouds.append(val)
        elif type(val) == str:
            v = val.split()
            if len(v) == 1:
                clouds.append(int(v[0][-1]))
            elif len(v) > 1:
                try:
                    clouds.append(int(v[-2][-1]))
                except:
                    clouds.append(int(v[-1][-1]))

    cloud_percent = [v if v==np.nan else ((v/10) * 100) for v in clouds]

    return cloud_percent