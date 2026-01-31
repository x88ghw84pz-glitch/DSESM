import xarray as xr
import atlite
import geopandas as gpd
from urllib.request import urlretrieve

from atlite.gis import ExclusionContainer


def get_pv_and_wind(regions, excluder_solar, excluder_wind, sens_analysis, density=3.0):
    """
    Returns:
        pv_cap  (xr.DataArray): installable PV capacity per region
        pv_cf   (xr.DataArray): PV capacity factor time series per region
        wind_cap(xr.DataArray): installable wind capacity per region
        wind_cf (xr.DataArray): wind capacity factor time series per region
        sens_analysis : float or int, default 1.0
        Scenario selector for the cutout year/file.
        - 1 (or 1.0): use 2019 ERA5 cutout
        - 2 (or 2.0): use 2025 ERA5 cutout
        Any other value raises ValueError.
        density : float, default 3.0
        Installation density (e.g., MW/km²) used when converting eligible area to installable capacity.
    """

    # 1. Step Cut out
    if sens_analysis in (1, 1.0):
        cutout_file = "era5_aut_2019.nc"
    elif sens_analysis in (2, 2.0):
        cutout_file = "era5_aut_2025.nc"
    else:
        raise ValueError(f"Unsupported sens_analysis={sens_analysis}. Use 1 or 2.")

    url = ("https://tubcloud.tu-berlin.de/s/pcwa634tRJMy2Xo/download?path=%2F&files=" + cutout_file)
    urlretrieve(url, cutout_file)
    cutout = atlite.Cutout(path=cutout_file)

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
    
    # 5. Turn into dataframes fpr pypsa model
    pv_cf_df   = pv_cf.to_pandas()
    wind_cf_df = wind_cf.to_pandas()
    pv_cap_s   = pv_cap.to_pandas()
    wind_cap_s = wind_cap.to_pandas()

    # Align Timeseries: Removes 2020 timestep to only have 2019 time series 
    weather_year = pv_cf_df.index[0].year  
    pv_cf_df   = pv_cf_df[pv_cf_df.index.year == weather_year]
    wind_cf_df = wind_cf_df[wind_cf_df.index.year == weather_year]

    return pv_cap, pv_cf, wind_cap, wind_cf