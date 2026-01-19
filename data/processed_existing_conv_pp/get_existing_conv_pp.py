import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

def get_existing_conv_pp():
    url= "https://raw.githubusercontent.com/wri/global-power-plant-database/refs/heads/master/output_database/global_power_plant_database.csv"
    #datei konnte nicht aus tu hub ausgelesen werden da es keine dowload file war -> option 1 local einlesen, option2 aus git hub 
    conv_energy = pd.read_csv(url, low_memory=False)

    df = conv_energy.loc[conv_energy["country"] == "AUT"].copy()

    gdf = gpd.GeoDataFrame(
        df[["primary_fuel", "capacity_mw"]],  # keep only what you want
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326"
    )
    return gdf

