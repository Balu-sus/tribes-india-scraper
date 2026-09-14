import os
import json
import pandas as pd
from datetime import datetime, timezone

def save_dataset_and_metadata(scraped_data):
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    if scraped_data:
        df = pd.DataFrame(scraped_data)
        
        # Save CSV file
        csv_path = os.path.join("data", "tribes_india_products.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8")
        
        # Save Metadata file
        metadata = {
            "title": "Tribes India Product Dataset",
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "total_records": len(df),
            "columns": list(df.columns),
            "description": "Scraped product catalog data from Tribes India for research.",
            "source_url": "https://tribesindia.com"
        }
        
        meta_path = os.path.join("data", "metadata.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
            
        print(f"Dataset successfully saved: {len(df)} rows.")
    else:
        print("Warning: No scraped data found. Skipping file write to protect existing data.")

if __name__ == "__main__":
    # Add your scraping logic here
    # scraped_data = run_your_scraper()
    
    # Save results directly to repo
    save_dataset_and_metadata(scraped_data)
