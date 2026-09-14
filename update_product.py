import os
import pandas as pd
from datetime import datetime

# Import scraper modules
from scrapers.tribes_india import scrape_tribes_india
from scrapers.india_handmade import scrape_india_handmade

SOURCES = {
    "tribes_india": {"func": scrape_tribes_india, "file": "data/tribes_india_products.csv"},
    "india_handmade": {"func": scrape_india_handmade, "file": "data/india_handmade_products.csv"}
}

def update_source_dataset(source_name, scrape_func, csv_file):
    print(f"Starting update for {source_name}...")
    new_data = scrape_func()
    df_new = pd.DataFrame(new_data)
    
    if df_new.empty:
        print(f"Warning: No data scraped for {source_name}.")
        return None

    df_new["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(csv_file):
        df_old = pd.read_csv(csv_file)
        df_old.set_index("product_url", inplace=True)
        df_new.set_index("product_url", inplace=True)

        # Update changed prices/attributes & keep new additions
        df_old.update(df_new)
        df_final = df_old.combine_first(df_new).reset_index()
    else:
        df_final = df_new

    df_final.to_csv(csv_file, index=False)
    print(f"Saved {len(df_final)} records to {csv_file}")
    return df_final

def build_master_catalog(dataframes):
    valid_dfs = [df for df in dataframes if df is not None and not df.empty]
    if valid_dfs:
        master_df = pd.concat(valid_dfs, ignore_index=True)
        master_df.to_csv("data/master_catalog.csv", index=False)
        print(f"Master catalog generated with {len(master_df)} total items.")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    all_dfs = []
    
    for name, config in SOURCES.items():
        df_result = update_source_dataset(name, config["func"], config["file"])
        all_dfs.append(df_result)
        
    build_master_catalog(all_dfs)
