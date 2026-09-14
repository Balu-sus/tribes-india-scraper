import os
import pandas as pd
from datetime import datetime

CSV_FILE = "tribes_india_products.csv"

def fetch_latest_data():
    # Replace this block with your actual scraping logic
    # Example: return pd.read_csv("scraped_data_temp.csv")
    pass

def update_dataset():
    if not os.path.exists(CSV_FILE):
        print(f"File {CSV_FILE} not found. Creating a new one.")
        df_new = fetch_latest_data()
        df_new.to_csv(CSV_FILE, index=False)
        return

    # Load baseline dataset
    df_old = pd.read_csv(CSV_FILE)
    df_new = fetch_latest_data()

    # Index by unique product key
    df_old.set_index("product_url", inplace=True)
    df_new.set_index("product_url", inplace=True)

    # Update changed fields & append brand-new items
    df_old.update(df_new)
    df_final = df_old.combine_first(df_new).reset_index()

    # Save merged data
    df_final.to_csv(CSV_FILE, index=False)
    print(f"Successfully updated dataset on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    update_dataset()
