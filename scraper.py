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
    """Fetches product page links directly from a valid category listing."""
    product_urls = set()
    try:
        response = requests.get(category_url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if any(keyword in href for keyword in ["/product/"]):
                    full_url = href if href.startswith("http") else BASE_URL + href
                    product_urls.add(full_url)
    except Exception as e:
        print(f"Error fetching category {category_url}: {e}")
    return list(product_urls)

def get_product_details(product_url):
    """Extracts clean title, price, and description from a product page."""
    try:
        response = requests.get(product_url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, "html.parser")

        # 1. Clean Title Extraction (avoiding 'Add to wishlist' headers)
        title_text = None
        for h1 in soup.find_all("h1"):
            text = h1.text.strip()
            if text and "wishlist" not in text.lower():
                title_text = text
                break
        
        if not title_text:
            meta_title = soup.find("meta", property="og:title")
            if meta_title and meta_title.get("content"):
                title_text = meta_title["content"].replace("- Tribes India", "").strip()

        # 2. Extract Prices (Handles encoded currency symbols like â‚ą / ã‚¿ / ₹)
        raw_text = soup.get_text()
        prices = re.findall(r"(?:â‚ą|ã‚¿|₹|\$)\s*([\d\.,]+)", raw_text)
        
        cleaned_prices = []
        for p in prices:
            try:
                val = float(p.replace(",", ""))
                if val > 0:
                    cleaned_prices.append(val)
            except ValueError:
                continue

        discounted_price = cleaned_prices[0] if cleaned_prices else None
        original_price = cleaned_prices[1] if len(cleaned_prices) > 1 else discounted_price

        # 3. Clean Description Extraction
        desc_elem = soup.find("div", class_=re.compile(r"description|detail|summary", re.I)) or soup.find("section", id=re.compile(r"description", re.I))
        desc_text = desc_elem.text.strip() if desc_elem else None

        if title_text or discounted_price:
            return {
                "title": title_text,
                "price_inr": discounted_price,
                "original_price_inr": original_price,
                "description": desc_text,
                "product_url": product_url
            }
    except Exception as e:
        print(f"Error scraping product {product_url}: {e}")
    return None

def save_dataset_and_metadata(scraped_data):
    """Saves output files cleanly to the data/ directory."""
    os.makedirs("data", exist_ok=True)
    
    df = pd.DataFrame(scraped_data if scraped_data else [])
    
    # Save CSV
    csv_path = os.path.join("data", "tribes_india_products.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    
    # Save Metadata
    metadata = {
        "title": "Tribes India Product Dataset",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_records": len(df),
        "columns": list(df.columns) if not df.empty else ["title", "price_inr", "original_price_inr", "description", "product_url"],
        "description": "Scraped product catalog data from Tribes India for research.",
        "source_url": "https://tribesindia.com"
    }
    
    meta_path = os.path.join("data", "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
        
    print(f"Successfully generated {csv_path} with {len(df)} records.")

if __name__ == "__main__":
    category_urls = [
        "https://tribesindia.com/category/vandhan-naturals",
        "https://tribesindia.com/category/clothing-fabrics",
        "https://tribesindia.com/category/tribal-paintings"
    ]
    
    scraped_data = []

    print("Gathering product URLs...")
    all_product_urls = set()
    for cat_url in category_urls:
        urls = get_product_urls(cat_url)
        all_product_urls.update(urls)
        time.sleep(1)

    print(f"Found {len(all_product_urls)} products. Starting detail extraction...")

    for url in list(all_product_urls)[:30]:
        details = get_product_details(url)
        if details:
            scraped_data.append(details)
        time.sleep(1)

    save_dataset_and_metadata(scraped_data)
