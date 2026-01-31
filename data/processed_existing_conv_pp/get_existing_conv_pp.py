import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

def get_existing_conv_pp(regions):
    url= "https://raw.githubusercontent.com/wri/global-power-plant-database/refs/heads/master/output_database/global_power_plant_database.csv"
    #datei konnte nicht aus tu hub ausgelesen werden da es keine dowload file war -> option 1 local einlesen, option2 aus git hub 
    conv_energy = pd.read_csv(url, low_memory=False)

    df = conv_energy.loc[conv_energy["country"] == "AUT"].copy()

    gdf = gpd.GeoDataFrame(
        df[["primary_fuel", "capacity_mw"]],  # keep only what you want
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326"
    )

    regions_3035 = regions.to_crs(3035)
    pp_3035 = gdf.to_crs(3035)

    regions_join = regions_3035[["geometry"]].copy()
    regions_join["region"] = regions_join.index

    pp_with_region = gpd.sjoin(
        pp_3035,
        regions_join[["region","geometry"]],
        how="left",
        predicate="within"
    ).dropna(subset=["region"])

    conv_cap = (
    pp_with_region
    .groupby(["region","primary_fuel"])["capacity_mw"]
    .sum()
    .loc[lambda s: s.index.get_level_values("primary_fuel").isin(["Gas","Hydro"])]
    )
    
    return conv_cap

