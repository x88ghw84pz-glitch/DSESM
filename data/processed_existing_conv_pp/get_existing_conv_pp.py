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
        df[["primary_fuel", "capacity_mw"]],  # keep whats neccessary
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326"
    )
    return gdf

def assign_points_to_regions(gdf_regions, gdf_plants, region_name_col="region_5"):
    # kopien erzeugen
    regions = gdf_regions[[region_name_col, "geometry"]].copy()
    plants = gdf_plants.copy()

    # Spatial join: Punkt-in-Polygon
    joined = (
        gpd.sjoin(
            plants,
            regions,
            how="left",
            predicate="within"   # alternativ: "intersects" bei Grenzfällen
        )
        .drop(columns=["index_right"], errors="ignore")
    )

    out = (
    joined
    .dropna(subset=[region_name_col])
    .groupby([region_name_col, "primary_fuel"], as_index=False)["capacity_mw"]
    .sum()
    .rename(columns={
        region_name_col: "Region",
        "primary_fuel": "Technology",
        "capacity_mw": "Capacity [MW]"
    })
    .sort_values(["Region", "Technology"])
    )

    return out