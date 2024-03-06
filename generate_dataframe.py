import pandas as pd
from geopy.geocoders import Nominatim
from tqdm import tqdm
import data_process as datap
from math import sin, cos, sqrt, atan2, radians

# read original data and produce df of resale and rent
def hdb_data():
    df90_99 = pd.read_csv("ResaleFlatPricesBasedonApprovalDate19901999.csv")
    df00_12 = pd.read_csv("ResaleFlatPricesBasedonApprovalDate2000Feb2012.csv")
    df12_14 = pd.read_csv("ResaleFlatPricesBasedonRegistrationDateFromMar2012toDec2014.csv")
    df15_16 = pd.read_csv("ResaleFlatPricesBasedonRegistrationDateFromJan2015toDec2016.csv")
    df17_24 = pd.read_csv("ResaleflatpricesbasedonregistrationdatefromJan2017onwards.csv")
    df_rent = pd.read_csv("RentingOutofFlats.csv")

    #fix month format
    df12_14['month'] = pd.to_datetime(df12_14['month'], format='%b-%y')
    
    #cancat all data of resale and drop 2024's data
    df90_24 = pd.concat([df90_99, df00_12, df12_14, df15_16, df17_24], ignore_index=True)
    df90_24['year'] = pd.to_datetime(df90_24['month']).dt.year
    df90_24['remaining_lease'] = (99 + df90_24['lease_commence_date']) - df90_24['year']
    df_resale=df90_24[df90_24['year']<=2023]
    df_rent['year'] = pd.to_datetime(df_rent['rent_approval_date']).dt.year
    #df_rent['month'] = pd.to_datetime(df_rent['rent_approval_date'], format='%b-%y')

    #add id
    df_resale['id'] = df_resale.reset_index().index
    df_rent['id'] = df_rent.reset_index().index

    #add price_per_sqm to resale data
    df_resale['price_per_sqm'] = df_resale['resale_price']/df_resale['floor_area_sqm']

    return df_resale,df_rent

def add_address(df):
    #a.add address from zipcode_mapper
    df_location = pd.read_csv("sg_zipcode_mapper_utf.csv")
    df_from_zipcode = pd.merge(df, df_location[['block', 'street_name', 'lat', 'lng']],
                          on=['block', 'street_name'], how='left')
    df_from_zipcode = df_from_zipcode.drop_duplicates(subset=['id'])
    
    for index, row in df_from_zipcode[df_from_zipcode['lat'].isnull()].iterrows():
        match = df_location[df_location['street_name'] == row['street_name']].head(1)
        if not match.empty:
            df_from_zipcode.at[index, 'lat'] = match['lat'].values[0]
            df_from_zipcode.at[index, 'lng'] = match['lng'].values[0]
    
    #b.find out data without lat&lng
    df_missing_coords = df_from_zipcode[(pd.isnull(df_from_zipcode['lat'])) | (pd.isnull(df_from_zipcode['lng']))]
    
    #c.add from geopy.geocoders
    address_cache = {}         
    def add_ll_from_address(row):
        #address = f"{row['town']}, Singapore"
        address = f"{row['street_name']}, {row['town']},Singapore"
        #address = f"{row['block']}, {row['street_name']}, {row['town']},Singapore"
        if address in address_cache:
            return address_cache[address]
        else:
            geolocator = Nominatim(user_agent="my_geocoder", timeout=10)
            location = geolocator.geocode(address)
            if location:
                address_cache[address] = (location.latitude, location.longitude)
                return location.latitude, location.longitude
            return row['lat'], row['lng']

    #for idx, row in tqdm(df_missing_coords.iterrows(), total=len(df_missing_coords), desc="Adding Coordinates"):
        #df_from_zipcode.loc[idx, ['lat', 'lng']] = add_ll_from_address(row)

    return df_from_zipcode

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
    mrt_locations = pd.read_csv("mrt_location.csv")
    df['nearest_mrt'] = ""
    df['mrt_dist'] = float('inf')
    total_rows = len(df)

    for idx, row in tqdm(df.iterrows(), total=total_rows, desc="Calculating distances"):
        if row['lat']:
            min_dist = float('inf')
            nearest_mrt = None
            hdb_location = (row['lat'],row['lng'])
            for mrt_idx, mrt_row in mrt_locations.iterrows():
                if mrt_row['service_year'] <= row["year"]:
                    mrt_location = (mrt_row['latitude'],mrt_row['longitude'])
                    dist=earth_distance(hdb_location,mrt_location)
                    if dist<min_dist:
                        min_dist = dist
                        nearest_mrt = mrt_row['query']
            df.at[idx,'nearest_mrt'] = nearest_mrt
            df.at[idx,'mrt_dist'] = min_dist
    return df

df_resale = pd.read_csv("hdb_for_resale_withmrt.csv")
df_resale = df_resale[df_resale['year'] >= 2000]
df_resale = add_distance(df_resale)
df_resale.to_csv('hdb_for_rent_month.csv', index=False)
#df = add_address(df_resale)
#df.to_csv('hdb_for_resale.csv', index=False)
#df = add_distance(df)
#df.to_csv('hdb_for_resale_withmrt.csv', index=False)

#test code
#df_resale,df_rent = hdb_data()
#df_resale_fulladdress = add_address(df_resale)
#df_rent_fulladdress = add_address(df_rent)

#print(df_resale_fulladdress)
#print(len(df_resale))
#print(len(df_resale_fulladdress))
#print(df_resale_fulladdress[['lat', 'lng']].isnull().sum())
#print(df_rent_fulladdress[['lat', 'lng']].isnull().sum())
#duplicate_rows = df_resale_fulladress.duplicated(subset=['id'],keep=False)
#print(df_resale_fulladress[duplicate_rows])
'''
df_resale,df_rent = hdb_data()
print(len(df_resale))
print(len(df_rent))

print(df_resale)
'''
#df_resale_fulladdress.to_csv('hdb_for_resale.csv', index=False)
#df_rent.to_csv('hdb_for_rent.csv', index=False)
  