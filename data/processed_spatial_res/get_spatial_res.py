import geopandas as gpd

def get_spatial_res():
    source = "https://tubcloud.tu-berlin.de/s/567ckizz2Y6RLQq/download?path=%2Fgadm&files=gadm_410-levels-ADM_1-AUT.gpkg" 

    regions = gpd.read_file(source) #reading in the source 
    regions = regions.set_index("GID_1")

    #adding attributes to the dataframe for aggregating the geometries to 5 regions therefore mapping the new Region names to the NAME_1 entries
    new_regions = {
        "Wien": "Wien",
        "Niederösterreich": "Niederösterreich/Burgenland",
        "Burgenland": "Niederösterreich/Burgenland",
        "Oberösterreich": "Oberösterreich/Salzburg",
        "Salzburg": "Oberösterreich/Salzburg",
        "Tirol": "Tirol/Vorarlberg",
        "Vorarlberg": "Tirol/Vorarlberg",
        "Kärnten": "Kärnten/Steiermark",
        "Steiermark": "Kärnten/Steiermark"
    }

    regions["region_5"] = regions["NAME_1"].map(new_regions)

    #now dissolving the geometries on "region_5" regions
    regions_5 = regions.dissolve(by="region_5")

    #adding representative points
    regions_5["REP_POINT"] = regions_5.representative_point()

    return regions_5



    