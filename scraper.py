import os
import json
import csv
import re
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Setup paths
DATA_DIR = "data"
IMAGE_DIR = "images"
CSV_FILE_PATH = os.path.join(DATA_DIR, "tribes_india_products.csv")
PRODUCTS_JSON = os.path.join(DATA_DIR, "tribes_art_products.json")
METADATA_JSON = "metadata.json"
DATASET_METADATA_JSON = "dataset-metadata.json"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# Target Category URLs (Arts, Crafts & Jewellery)
TARGET_CATEGORY_URLS = [
    "https://tribesindia.com/category/jewellery",
    "https://tribesindia.com/category/metal-crafts",
    "https://tribesindia.com/category/tribal-paintings",
    "https://tribesindia.com/category/pottery",
    "https://tribesindia.com/category/cane-bamboo-crafts"
]

FOOD_KEYWORDS = {
    "food", "rice", "tea", "coffee", "honey", "spice", "soap", "shampoo",
    "oil", "powder", "ragi", "poha", "natural", "edible", "flour", "ghee", "jam", "pickle"
}

def extract_price(card) -> str:
    """Robust price extractor searching multiple price selectors and currency patterns."""
    price_elem = (
        card.find(class_=lambda c: c and any(p in c.lower() for p in ["price", "amount", "cost"])) or
        card.find("ins") or 
        card.find("span", class_="woocommerce-Price-amount")
    )
    
    raw_text = price_elem.text.strip() if price_elem else card.text
    
    price_match = re.search(r'(?:₹|Rs\.?|INR)\s*[\d,]+(?:\.\d{2})?', raw_text, re.IGNORECASE)
    if price_match:
        return price_match.group(0).strip()
    
    num_match = re.search(r'\b\d{1,3}(?:,\d{3})+\b|\b\d{3,5}\b', raw_text)
    if num_match:
        return f"₹{num_match.group(0)}"
        
    return "N/A"

def is_valid_item(title: str) -> bool:
    text = title.lower().strip()
    if not text or any(food in text for food in FOOD_KEYWORDS):
        return False
    return True

def run_scraper():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    scraped_products = []

    for cat_url in TARGET_CATEGORY_URLS:
        print(f"Fetching: {cat_url}")
        try:
            res = requests.get(cat_url, headers=headers, timeout=15)
            if res.status_code != 200:
                continue
        except Exception as e:
            print(f"Connection error: {e}")
            continue

        soup = BeautifulSoup(res.content, "html.parser")
        
        product_cards = (
            soup.find_all("div", class_=lambda c: c and "product" in c.lower()) or
            soup.find_all("li", class_=lambda c: c and "product" in c.lower()) or
            soup.find_all("article")
        )

        for card in product_cards:
            title_elem = (
                card.find(["h1", "h2", "h3", "h4"]) or 
                card.find("a", class_=lambda c: c and "title" in c.lower())
            )
            
            if not title_elem:
                continue

            title = title_elem.text.strip()
            if not is_valid_item(title):
                continue

            price = extract_price(card)

            img_elem = card.find("img")
            image_url = None
            if img_elem:
                image_url = img_elem.get("src") or img_elem.get("data-src")
                if image_url:
                    image_url = urljoin(cat_url, image_url)

            local_image_path = None
            if image_url:
                clean_title = "".join(c for c in title if c.isalnum() or c in (" ", "_")).rstrip()
                filename = f"{clean_title.replace(' ', '_')[:25]}.jpg"
                local_image_path = os.path.join(IMAGE_DIR, filename)

                try:
                    img_bytes = requests.get(image_url, headers=headers, timeout=10).content
                    with open(local_image_path, "wb") as f:
                        f.write(img_bytes)
                except Exception:
                    local_image_path = None

            scraped_products.append({
                "title": title,
                "price": price,
                "category_url": cat_url,
                "original_image_url": image_url or "",
                "local_image_path": local_image_path or ""
            })

    if not scraped_products:
        print("No products found to save.")
        return

    # Write CSV dataset
    fieldnames = ["title", "price", "category_url", "original_image_url", "local_image_path"]
    with open(CSV_FILE_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scraped_products)

    # Write JSON dataset
    with open(PRODUCTS_JSON, "w", encoding="utf-8") as f:
        json.dump(scraped_products, f, indent=4)

    # Sync metadata.json
    metadata = {
        "title": "Tribes India Art & Crafts Dataset",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_records": len(scraped_products),
        "columns": fieldnames,
        "description": "Scraped catalog data from Tribes India focusing on arts, crafts, and jewelry.",
        "source_url": "https://tribesindia.com"
    }
    with open(METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    # Sync dataset-metadata.json
    dataset_metadata = {
        "title": "Tribes India Art & Crafts Dataset",
        "id": "rokiann/tribes-india-product-dataset",
        "licenses": [{"name": "CC0-1.0"}]
    }
    with open(DATASET_METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(dataset_metadata, f, indent=4)

    print(f"Successfully updated dataset with {len(scraped_products)} items.")

if __name__ == "__main__":
    run_scraper()
