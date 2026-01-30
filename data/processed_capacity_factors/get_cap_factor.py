import xarray as xr
import atlite
import geopandas as gpd
from atlite.gis import ExclusionContainer


def get_pv_and_wind(regions, excluder_solar, excluder_wind, density=3.0):
    """
    Returns:
        pv_cap  (xr.DataArray): installable PV capacity per region
        pv_cf   (xr.DataArray): PV capacity factor time series per region
        wind_cap(xr.DataArray): installable wind capacity per region
        wind_cf (xr.DataArray): wind capacity factor time series per region
    """

    # --- Austria bbox + 0.25° buffer ---
    lon_min = 9.5  - 0.25   # west
    lon_max = 17.5 + 0.25   # east

    lat_max = 49.0 + 0.25   # north
    lat_min = 46.2 - 0.25   # south

    # 1. Step Cut out
    cutout = atlite.Cutout(
    path="cutouts/at_era5_test.nc",          # where it will be saved
    module="era5",                           # tells atlite to use ERA5 via CDS
    x=slice(lon_min, lon_max),                       # lon range (west..east) -> alter to Aust + (add a buffer of 0.25 degrees).
    y=slice(lat_min,lat_max ),                     # lat range (north..south) -> alter to Aust + (add a buffer of 0.25 degrees).
    time=slice("2024-01-01", "2025-01-02"),  # time range
    )

    cutout.prepare(compression=None)  

    # 2. Ermittlung availability
    A_pv = cutout.availabilitymatrix(regions.geometry, excluder_solar)
    A_w  = cutout.availabilitymatrix(regions.geometry, excluder_wind)
    
    # 3. Berechnung Zellflächen (km²)
    area_km2 = cutout.grid.to_crs(3035).area / 1e6
    area_km2 = xr.DataArray(area_km2.values, dims=("spatial",))

    # 4. Berechnung capacity factors
    M_pv = A_pv.stack(spatial=["y", "x"]) * area_km2 * density
    pv_gen, pv_cap = cutout.pv(
        matrix=M_pv,
        index=regions.index,
        panel=atlite.solarpanels.CdTe,
        orientation="latitude_optimal",
        return_capacity=True,
    )
    pv_cf = pv_gen / pv_cap

    M_w = A_w.stack(spatial=["y", "x"]) * area_km2 * density
    wind_gen, wind_cap = cutout.wind(
        matrix=M_w,
        index=regions.index,
        turbine=atlite.windturbines.Vestas_V112_3MW,
        return_capacity=True,
    )
    wind_cf = wind_gen / wind_cap

    # Align Timeseries: Removes 2020 timestep to only have 2019 time series 
    weather_year = pv_cf_df.index[0].year  
    pv_cf_df   = pv_cf_df[pv_cf_df.index.year == weather_year]
    wind_cf_df = wind_cf_df[wind_cf_df.index.year == weather_year]

    return pv_cap, pv_cf, wind_cap, wind_cf