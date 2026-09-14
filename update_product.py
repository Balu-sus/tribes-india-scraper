import os
import pandas as pd
from scraper import run_all_scrapers

FILE_DIRECT = "tribes_india_products.csv"
FILE_MARKETPLACES = "amazon_flipkart_products.csv"

def save_or_update(df_new, file_path):
    if df_new.empty:
        print(f"No new data scraped for {file_path}.")
        return

    if os.path.exists(file_path):
        df_old = pd.read_csv(file_path)
        # Deduplicate based on product URL
        df_combined = pd.concat([df_old, df_new]).drop_duplicates(subset=["product_url"], keep="last")
    else:
        df_combined = df_new

    df_combined.to_csv(file_path, index=False)
    print(f"Saved {len(df_combined)} items to {file_path}")

def update_dataset():
    df_direct, df_marketplaces = run_all_scrapers()
    
    # Write to two distinct CSV files
    save_or_update(df_direct, FILE_DIRECT)
    save_or_update(df_marketplaces, FILE_MARKETPLACES)

if __name__ == "__main__":
    update_dataset()
