import pandas as pd

def regional_load():
    
    # national GEGIS time series 
    
    url_gegis = "C:\Users\steli\DSESM\data\processed_load_profile\load.csv"
    
    df_gegis = pd.read_csv(url_gegis, index_col=0, parse_dates=True)

    # national load for Austria
    load_au = df_gegis["AU"]

    
    # Population by region 
    
    pop_regions = pd.Series(
        {
            "Kärnten/Steiermark": 1839780,               
            "Niederösterreich/Burgenland": 2025947,      
            "Oberösterreich/Salzburg": 2102099,          
            "Tirol/Vorarlberg": 1186033,                 
            "Wien": 2006134,                             
        }
    )

    # population shares
    pop_shares = pop_regions / pop_regions.sum()

    #Distributing national load to regions 
    load_regions = pd.DataFrame(
        {region: load_au * share for region, share in pop_shares.items()}
    )

    return load_regions