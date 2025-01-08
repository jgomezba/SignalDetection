import os
import json
import pathlib
import sys
from itertools import combinations, product

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN, OPTICS
from sklearn.preprocessing import StandardScaler

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print(sys.path)

from constants import CSV_HEADERS_ES
from Packages.geo_utils.geodesic_point import GeodesicPoint

def convert_angle(angle):
    if angle > 180:
        return angle - 180
    else:
        return angle

def read_initial_data(json_file_name:str):
    with open(json_file_name, 'r') as file:
        config = json.load(file)
    return config

def get_csv_simulation(csv_location:str):
    current_path = os.getcwd()
    data = pd.read_csv(pathlib.Path(current_path, csv_location), names=CSV_HEADERS_ES.split(","))
    return data

def clean_transform_data(data:pd.DataFrame):
    receptors_df = data[["ordinal sensora", "latitud sensora", "longitud sensora"]]
    receptors_df.drop_duplicates(inplace=True)

    data_for_model_df = data[["latitud sensora", "longitud sensora", "ángulo llegada respecto a norte"]]
    data_for_model_df.loc[:, 'converted_angles'] = data_for_model_df['ángulo llegada respecto a norte'].apply(convert_angle)
    
    real_emitter = data[["LatitudEmisorActivo","LongitudEmisorActivo"]]
    real_emitter.drop_duplicates(inplace=True)
    
    return data_for_model_df, receptors_df, real_emitter

def calculate_intersection_points(data_for_model_df:pd.DataFrame, number_of_receptors:int, plot_intersections:bool = True):
    points_list = []
    for i in range(0, len(data_for_model_df), number_of_receptors):
        current_points = []
        
        for j in range(0, number_of_receptors):
            lat = data_for_model_df["latitud sensora"][i+j]
            lon = data_for_model_df["longitud sensora"][i+j]
            az = data_for_model_df["converted_angles"][i+j]
            current_points.append(GeodesicPoint(lat, lon, az))
            
        points_list.append(current_points)

    intersections = []
    for point_group in points_list:
        for p1, p2 in combinations(point_group, 2):
            intersect = GeodesicPoint.compute_intersection(p1, p2)
            if not intersect[0] is None and not intersect[1] is None:
                intersections.append(intersect)

    if plot_intersections:
        latitudes, longitudes = zip(*intersections)
        plt.figure(figsize=(12, 8))


        plt.subplot(1, 2, 1)  
        plt.scatter(longitudes, latitudes, color='blue', marker='o', s=5)
        plt.grid(True)
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.title("Default View")

        plt.subplot(1, 2, 2)  
        plt.scatter(longitudes, latitudes, color='blue', marker='o', s=5)
        plt.grid(True)
        plt.xlim(axis_x)  # Apply x-axis limit
        plt.ylim(axis_y)  # Apply y-axis limit
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.title("With Axis Limits")

        # Adjust layout and display
        plt.tight_layout()
        plt.show()

    #Create dataframe with intersection points:
    df_intersections = pd.DataFrame(intersections, columns=["latitude", "longitude"])
    df_intersections_filtered = df_intersections[
        (df_intersections['latitude'] >= axis_y[0]) & (df_intersections['latitude'] <= axis_y[1]) &
        (df_intersections['longitude'] >= axis_x[0]) & (df_intersections['longitude'] <= axis_x[1])
    ]

    return df_intersections, df_intersections_filtered

def execute_DBSCAN_model(dataframe:pd.DataFrame, epsilon:float, minimum_samples:int, plot:bool=True):
    coordinates = dataframe[['latitude', 'longitude']].values
    coordinates_scaled = StandardScaler().fit_transform(coordinates)

    db = DBSCAN(eps=epsilon, min_samples=minimum_samples, metric='euclidean') 
    dataframe['cluster'] = db.fit_predict(coordinates_scaled)

    centroids_DBSCAN = (
        dataframe[dataframe['cluster'] != -1] 
        .groupby('cluster')      
        [['latitude', 'longitude']]  
        .mean()                  
    )

    if plot:
        plt.figure(figsize=(10, 6))
        plt.scatter(dataframe['longitude'], dataframe['latitude'], c=dataframe['cluster'], cmap='inferno', s=5)
        plt.title('DBSCAN Clustering on Latitudes and Longitudes')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.colorbar(label='Cluster ID')
        plt.show()
        
    return centroids_DBSCAN

def execute_OPTICS_model(dataframe:pd.DataFrame, minimum_samples:int, plot:bool=True):
    coordinates = dataframe[['latitude', 'longitude']].values
    coordinates_scaled = StandardScaler().fit_transform(coordinates)

    optics = OPTICS(min_samples=minimum_samples, metric='euclidean')
    dataframe['cluster'] = optics.fit_predict(coordinates_scaled)

    centroids_OPTICS = (
        dataframe[dataframe['cluster'] != -1] 
        .groupby('cluster')                        
        [['latitude', 'longitude']]                
        .mean()                                    
    )

    if plot:
        plt.figure(figsize=(10, 6))
        plt.scatter(dataframe['longitude'], dataframe['latitude'], c=dataframe['cluster'], cmap='inferno', s=5)
        plt.title('OPTICS Clustering on Latitudes and Longitudes')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.colorbar(label='Cluster ID')
        plt.show()
    
    return centroids_OPTICS

def get_min_distances_df(df_emmiters, centroids_df):
    combinations = list(product(df_emmiters.itertuples(index=False), centroids_df.itertuples()))

    result_df = pd.DataFrame([
        {
            'LatitudEmisorActivo': comb[0].LatitudEmisorActivo,
            'LongitudEmisorActivo': comb[0].LongitudEmisorActivo,
            'Cluster_Latitude': comb[1].latitude,
            'Cluster_Longitude': comb[1].longitude
        }
        for idx, comb in enumerate(combinations)
    ])
    
    result_df['distance'] = result_df.apply(
    lambda row: GeodesicPoint.haversine_distance(
        GeodesicPoint(row['LatitudEmisorActivo'], row['LongitudEmisorActivo']),
        GeodesicPoint(row['Cluster_Latitude'], row['Cluster_Longitude']),km=True
    ),
    axis=1
    )
    min_distance_rows = result_df.loc[result_df.groupby(['Cluster_Latitude', 'Cluster_Longitude'])['distance'].idxmin()]

    return min_distance_rows

if __name__ == "__main__":
    #Read config parameters
    config = read_initial_data('Code/Modeling/config.json')
    csv_location = config["csv_location"]
    number_of_receptors = config["number_of_receptors"]
    axis_x = tuple(config["axis_x"]) 
    axis_y = tuple(config["axis_y"])  
    plot_intersections = config["plot_intersections"]
    
    #Read data
    df = get_csv_simulation(csv_location)
    
    #Clean and transform data
    df_model, df_receptors, df_emmiters = clean_transform_data(df)
    
    #Calculate intersection points
    df_intersections, df_intersections_filtered = calculate_intersection_points(df_model, number_of_receptors, plot_intersections)
    
    #Apply DBSCAN
    centroids_model_1 = execute_DBSCAN_model(df_intersections_filtered, 0.1, 100)
    
    #Apply OPTICS
    centroids_model_2 = execute_OPTICS_model(df_intersections_filtered, 100)
    
    #Get minimum distances
    DBSCAN_distances_df = get_min_distances_df(df_emmiters, centroids_model_1)
    OPTICS_distances_df = get_min_distances_df(df_emmiters, centroids_model_2)
    
    print(f"DBSCAN: error {DBSCAN_distances_df["distance"].mean()} km")
    print(DBSCAN_distances_df)
    print()
    print(f"OPTICS: error {OPTICS_distances_df["distance"].mean()} km")
    print(OPTICS_distances_df)
    
   