import pandas as pd
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

def create_base_df(energy, weather):
    '''Combines energy and weather data and returns dataframe used for modeling'''
    base_df = pd.concat([energy, weather.shift(3)], axis=1)
    # concatenation above incorporates three hour time lag
    # between weather and energy data (weather three indices behind energy)

    # drops rows with now energy data (first day of data)
    base_df.drop(base_df[:'2018-01-29'].index, axis=0, inplace=True)

    # returns combined dataframe
    return base_df

def impute_df(df):
    '''Imputes missing data in df and returns dataframe with imputed values'''
    imp = IterativeImputer(random_state=42)

    # impute data using IterativeImputer
    df_imputed = imp.fit_transform(df)

    # Store imputed data in new dataframe
    imp_df = pd.DataFrame(index=df.index, columns=df.columns, data=df_imputed)

    # Return imputed dataframe
    return imp_df
