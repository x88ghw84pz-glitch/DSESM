# get_re_potential.py
import xarray as xr
import atlite

def get_pv_and_wind(cutout, regions, A_pv, A_w, density=3.0):
    # --- gemeinsame Zellfläche ---
    area_km2 = cutout.grid.to_crs(3035).area / 1e6
    area_km2 = xr.DataArray(area_km2.values, dims=("spatial",))

    # --- PV ---
    M_pv = A_pv.stack(spatial=["y", "x"]) * area_km2 * density
    pv_gen, pv_cap = cutout.pv(
        matrix=M_pv,
        index=regions.index,
        panel=atlite.solarpanels.CdTe,
        orientation="latitude_optimal",
        return_capacity=True,
    )
    pv_cf = pv_gen / pv_cap

    # --- Wind ---
    M_w = A_w.stack(spatial=["y", "x"]) * area_km2 * density
    wind_gen, wind_cap = cutout.wind(
        matrix=M_w,
        index=regions.index,
        turbine=atlite.windturbines.Vestas_V112_3MW,
        return_capacity=True,
    )
    wind_cf = wind_gen / wind_cap
    print(pv_cap)
    return pv_cap, pv_cf, wind_cap, wind_cf

