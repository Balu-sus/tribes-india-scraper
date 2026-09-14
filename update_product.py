import os
import pandas as pd
from scraper import run_all_scrapers

CSV_FILE = "tribes_india_products.csv"

def update_dataset():
    # Runs the Next Button multi-platform scrapers
    df_new = run_all_scrapers()
    
    if df_new.empty:
        print("No new data scraped.")
        return

    if os.path.exists(CSV_FILE):
        df_old = pd.read_csv(CSV_FILE)
        
        # Merge logic to update prices/details without losing items
        df_old.set_index("product_url", inplace=True)
        df_new.set_index("product_url", inplace=True)

        df_old.update(df_new)
        df_final = df_old.combine_first(df_new).reset_index()
    else:
        df_final = df_new

    df_final.to_csv(CSV_FILE, index=False)
    print(f"Dataset successfully updated with {len(df_final)} records.")

if __name__ == "__main__":
    update_dataset()
