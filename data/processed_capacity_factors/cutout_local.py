import xarray as xr
import atlite
import geopandas as gpd


# -------------------------------------------------
# 1) Regionen laden (5 Regionen)
# -------------------------------------------------
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


# -------------------------------------------------
# 2) Cutout laden
# -------------------------------------------------
def get_cutout():
    cutout = atlite.Cutout(
        "/Users/simon/Documents/01_Uni/02_Master/S3/05 DSESM/4group assign/era5_aut_2019.nc"
    )
    return cutout


# -------------------------------------------------
# 3) Availability-Matrizen
# -------------------------------------------------
def get_availability(cutout, regions, excluder_solar, excluder_wind):
    A_pv = cutout.availabilitymatrix(regions.geometry, excluder_solar)
    A_w  = cutout.availabilitymatrix(regions.geometry, excluder_wind)
    return A_pv, A_w


# -------------------------------------------------
# 4) PV & Wind Potenziale + CFs
# -------------------------------------------------
def get_pv_and_wind(cutout, regions, A_pv, A_w, density=3.0):
    # Zellflächen (km²)
    area_km2 = cutout.grid.to_crs(3035).area / 1e6
    area_km2 = xr.DataArray(area_km2.values, dims=("spatial",))

    # ---------- PV ----------
    M_pv = A_pv.stack(spatial=["y", "x"]) * area_km2 * density
    pv_gen, pv_cap = cutout.pv(
        matrix=M_pv,
        index=regions.index,
        panel=atlite.solarpanels.CdTe,
        orientation="latitude_optimal",
        return_capacity=True,
    )
    pv_cf = pv_gen / pv_cap

    # ---------- Wind ----------
    M_w = A_w.stack(spatial=["y", "x"]) * area_km2 * density
    wind_gen, wind_cap = cutout.wind(
        matrix=M_w,
        index=regions.index,
        turbine=atlite.windturbines.Vestas_V112_3MW,
        return_capacity=True,
    )
    wind_cf = wind_gen / wind_cap

    return pv_cap, pv_cf, wind_cap, wind_cf
