import os
import re
import time
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
BASE_URL = "https://tribesindia.com"

def get_product_urls(category_url):
    """Fetches individual product links from a listing page."""
    product_urls = set()
    try:
        response = requests.get(category_url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/product/" in href or "/products/" in href or "/item/" in href:
                    full_url = href if href.startswith("http") else BASE_URL + href
                    product_urls.add(full_url)
    except Exception as e:
        print(f"Error fetching category {category_url}: {e}")
    return list(product_urls)

def get_product_details(product_url):
    """Extracts title, price, and description from a single product page."""
    try:
        response = requests.get(product_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, "html.parser")

        title_elem = soup.find("h1")
        title_text = title_elem.text.strip() if title_elem else None

        price_elem = soup.find(class_=re.compile(r"price|amount|current-price", re.I))
        price_val = None
        if price_elem:
            raw_price = re.sub(r"[^\d.]", "", price_elem.text.strip())
            try:
                price_val = float(raw_price)
            except ValueError:
                price_val = None

        desc_elem = soup.find("div", class_=re.compile(r"description|detail|summary", re.I)) or soup.find("section", id=re.compile(r"description", re.I))
        desc_text = desc_elem.text.strip() if desc_elem else None

        if title_text or price_val:
            return {
                "title": title_text,
                "price_inr": price_val,
                "description": desc_text,
                "product_url": product_url
            }
    except Exception as e:
        print(f"Error scraping product {product_url}: {e}")
    return None

def save_dataset_and_metadata(scraped_data):
    """Saves the scraped data to CSV and writes dataset statistics to metadata.json."""
    os.makedirs("data", exist_ok=True)
    
    if scraped_data:
        df = pd.DataFrame(scraped_data)
        
        # Save CSV file
        csv_path = os.path.join("data", "tribes_india_products.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8")
        
        # Save Metadata JSON file
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
            
        print(f"Success: Saved {len(df)} products to {csv_path} and metadata to {meta_path}")
    else:
        print("Warning: No scraped data collected. Skipping file writing.")

if __name__ == "__main__":
    # Define category URLs to scrape
    category_urls = [
        "https://tribesindia.com/shop",
    ]
    
    # 1. Initialize scraped_data list
    scraped_data = []

    print("Gathering product URLs...")
    all_product_urls = set()
    for cat_url in category_urls:
        urls = get_product_urls(cat_url)
        all_product_urls.update(urls)
        time.sleep(1)

    print(f"Found {len(all_product_urls)} products. Starting detail extraction...")

    # 2. Extract details into scraped_data
    for url in all_product_urls:
        details = get_product_details(url)
        if details:
            scraped_data.append(details)
        time.sleep(1)

    # 3. Pass populated scraped_data to save function
    save_dataset_and_metadata(scraped_data)
