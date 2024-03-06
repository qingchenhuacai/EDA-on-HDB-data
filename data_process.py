import pandas as pd
import numpy as np
from math import sin, cos, sqrt, atan2, radians

#method of reading data
def get_hdb_resale_df():
    return pd.read_csv("data/hdb_for_resale_withmrt.csv")
def get_hdb_rent_df():
    return pd.read_csv("data/hdb_for_rent_month.csv")
def get_mrt_location():
    return pd.read_csv("data/mrt_location.csv")
def get_hdb_resale_mrt_df():
    return pd.read_csv("data/hdb_for_resale_mrt.csv")

#method of data subsample: randomly choose at most 100 data for each town
def data_subsample(df, size=100):
    sampled_df = pd.DataFrame(columns=df.columns)
    towns = df['town'].unique()
    for town in towns:
        town_data = df[df['town'] == town]
        if len(town_data) > size:
            sampled_data = town_data.sample(n=size)  
            # sampled_data = town_data.sample(n=size, random_state=42)
        else:
            sampled_data = town_data
        sampled_df = pd.concat([sampled_df, sampled_data])
    
    return sampled_df

#some statical computation
def max_min_avg_price(df, x_col, y_col):
    avg_price_data = df.groupby(x_col)[y_col].mean()
    max_label = avg_price_data.idxmax()
    min_label = avg_price_data.idxmin()

    max_value = avg_price_data.max()
    min_value = avg_price_data.min()

    return max_label, min_label, max_value, min_value


#method of culculate earth_distance
def earth_distance(x, y):

  R = 6373.0

  lat1, lng1 = radians(x[0]), radians(x[1])
  lat2, lng2 = radians(y[0]), radians(y[1])

  dlon = lng2 - lng1
  dlat = lat2 - lat1

  a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
  c = 2 * atan2(sqrt(a), sqrt(1 - a))

  return R * c

def add_distance(df):
    mrt_locations = pd.read_csv("mrt_data.csv")
    df['nearest_mrt'] = ""
    df['mrt_dist'] = float('inf')
    for idx, row in df.iterrows():
        min_dist = float('inf')
        nearest_mrt = None
        if not row['lat']:
            hdb_location = (row['lat'],row['lng'])
            for mrt_idx, mrt_row in mrt_locations.iterrows():
                mrt_location = (mrt_row['lat'],mrt_row['lng'])
                dist=earth_distance(hdb_location,mrt_location)
                if dist<min_dist:
                    min_dist = dist
                    nearest_mrt = mrt_row['station_name']
            df.at[idx,'nearest_mrt'] = nearest_mrt
            df.at[idx,'mrt_dist'] = min_dist
    return df