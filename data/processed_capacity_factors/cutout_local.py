import xarray as xr
import atlite
import geopandas as gpd



def get_regions():
    source = "https://tubcloud.tu-berlin.de/s/567ckizz2Y6RLQq/download?path=%2Fgadm&files=gadm_410-levels-ADM_1-AUT.gpkg"
    regions = gpd.read_file(source).set_index("GID_1")

    mapping = {
        "Wien": "Wien",
        "Niederösterreich": "Niederösterreich/Burgenland",
        "Burgenland": "Niederösterreich/Burgenland",
        "Oberösterreich": "Oberösterreich/Salzburg",
        "Salzburg": "Oberösterreich/Salzburg",
        "Tirol": "Tirol/Vorarlberg",
        "Vorarlberg": "Tirol/Vorarlberg",
        "Kärnten": "Kärnten/Steiermark",
        "Steiermark": "Kärnten/Steiermark",
    }

    regions["region_5"] = regions["NAME_1"].map(mapping)
    regions_5 = regions.dissolve(by="region_5")
    regions_5["REP_POINT"] = regions_5.representative_point()

    return regions_5



def get_cutout():
    cutout = atlite.Cutout(
        "/Users/simon/Documents/01_Uni/02_Master/S3/05 DSESM/4group assign/era5_aut_2019.nc"
    )
    return cutout



def get_availability(cutout, regions, excluder_solar, excluder_wind):
    A_pv = cutout.availabilitymatrix(regions.geometry, excluder_solar)
    A_w  = cutout.availabilitymatrix(regions.geometry, excluder_wind)
    return A_pv, A_w



def get_pv_and_wind(cutout, regions, A_pv, A_w, density=3.0):
    # Zellflächen (km²)
    area_km2 = cutout.grid.to_crs(3035).area / 1e6
    area_km2 = xr.DataArray(area_km2.values, dims=("spatial",))

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

    return pv_cap, pv_cf, wind_cap, wind_cf

def get_excluders():
    shape_url = "https://tubcloud.tu-berlin.de/s/567ckizz2Y6RLQq/download?path=%2F&files=country_shapes.geojson"
    protected_areas_url = "https://tubcloud.tu-berlin.de/s/567ckizz2Y6RLQq/download?path=%2Fwdpa&files=WDPA_Oct2022_Public_shp-AUT.tif"
    copernicus_url = "https://tubcloud.tu-berlin.de/s/567ckizz2Y6RLQq/download?path=%2Fcopernicus-glc&files=PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326-AT.tif"
    elevation_url = "GEBCO_2014_2D-AT.nc"
    airports_url = "https://tubcloud.tu-berlin.de/s/567ckizz2Y6RLQq/download?path=%2F&files=ne_10m_airports.gpkg"
    roads_url = "https://tubcloud.tu-berlin.de/s/567ckizz2Y6RLQq/download?path=%2F&files=ne_10m_roads.gpkg"

    excluder_wind = ExclusionContainer(crs=3035, res=100)

    excluder_wind.add_geometry(roads_url, buffer=300)
    excluder_wind.add_geometry(airports_url, buffer=5100)
    excluder_wind.add_raster(protected_areas_url, crs=3035)

    codes_urban = [50]
    codes_water_glacier = [70, 80, 90]
    codes_woods = [111, 114, 115, 116, 121, 124, 125, 126]

    excluder_wind.add_raster(
        copernicus_url,
        codes=codes_urban + codes_water_glacier + codes_woods,
        buffer=1000,
        invert=True,
    )

    excluder_solar = ExclusionContainer(crs=3035, res=100)
    excluder_solar.add_raster(protected_areas_url, crs=3035)

    return excluder_solar, excluder_wind