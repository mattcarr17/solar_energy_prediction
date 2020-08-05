import numpy as np
import pandas as pd
import string
import os







def energy_data():
    filelist = os.listdir('../../data/solar_output/')

    fl = ['../../data/solar_output/' + str(f) for f in filelist]

    dfs = [pd.read_csv(f) for f in fl]

    big_df = pd.concat(dfs)

    big_df.columns = ['time', 'nexus_meter', 'inverter']

    big_df.drop([0,1], axis=0, inplace=True)

    big_df['time'] = pd.to_datetime(big_df['time'])

    big_df = big_df.sort_values('time')
    big_df.set_index('time', inplace=True)

    big_df = big_df.astype(float)

    hourly = big_df.resample('H').sum()

    hourly = hourly['2018-01-30':]

    return hourly

def weather_data():
    weather_cols = ['HourlyAltimeterSetting', 'HourlyDewPointTemperature', 'HourlyDryBulbTemperature',
    'HourlyRelativeHumidity', 'HourlySeaLevelPressure', 'HourlySkyConditions', 'HourlyStationPressure', 
    'HourlyVisibility', 'HourlyWindSpeed', 'HourlyWindDirection', 'HourlyPrecipitation']
    df = pd.read_csv('../../data/weather/weatherstation2.csv')

    df['DATE'] = pd.to_datetime(df['DATE'])
    df.set_index('DATE', inplace=True)

    cols_with_letter = columns_with_letter(df[weather_cols])

    for col in cols_with_letter:
        letter = letter_in_column(df[col])
        df[col] = remove_letter_from_column(df, col, letter)

    df['cloud_coverage'] = cloud_coverage(df['HourlySkyConditions'])
    weather_cols.append('cloud_coverage')
    return df[weather_cols].drop('HourlySkyConditions', axis=1)


def columns_with_letter(df):
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
    lst = []
    for val in df[col].values:
        if letter in str(val):
            lst.append(val.replace(letter, ''))
        else:
            lst.append(val)
    return lst

def cloud_coverage(sky_conditions):
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