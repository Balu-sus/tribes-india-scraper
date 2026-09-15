import os
import json
import csv
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin

DATA_DIR = "data"
IMAGE_DIR = "images"
CSV_FILE_PATH = os.path.join(DATA_DIR, "tribes_india_products.csv")
PRODUCTS_JSON = os.path.join(DATA_DIR, "tribes_art_products.json")
METADATA_JSON = "metadata.json"
DATASET_METADATA_JSON = "dataset-metadata.json"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

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

def is_valid_item(title: str) -> bool:
    """Rejects known food items; accepts everything else in art categories."""
    text = title.lower().strip()
    if not text:
        return False
    # If it contains explicit food terms, reject it
    if any(food in text for food in FOOD_KEYWORDS):
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
                print(f"Failed to load {cat_url} (Status: {res.status_code})")
                continue
        except Exception as e:
            print(f"Connection error on {cat_url}: {e}")
            continue

        soup = BeautifulSoup(res.content, "html.parser")
        
        # Broad selector query to match various e-commerce templates
        product_cards = (
            soup.find_all("div", class_=lambda c: c and "product" in c.lower()) or
            soup.find_all("li", class_=lambda c: c and "product" in c.lower()) or
            soup.find_all("article")
        )

        print(f"Found {len(product_cards)} candidate elements on {cat_url}")

        for card in product_cards:
            # Flexible title searching
            title_elem = (
                card.find(["h1", "h2", "h3", "h4"]) or 
                card.find("a", class_=lambda c: c and "title" in c.lower())
            )
            price_elem = card.find(class_=lambda c: c and "price" in c.lower())
            img_elem = card.find("img")

            if not title_elem:
                continue

            title = title_elem.text.strip()

            if not is_valid_item(title):
                print(f"Filtered out (Food/Grocery): {title}")
                continue

            price = price_elem.text.strip() if price_elem else "N/A"
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

    print(f"Total valid products scraped: {len(scraped_products)}")

    # Safety check: Don't write blank files if scraping returned zero records
    if len(scraped_products) == 0:
        print("Warning: No products found! Skipping file overwrite to prevent blank CSV.")
        return

    # Write CSV
    fieldnames = ["title", "price", "category_url", "original_image_url", "local_image_path"]
    with open(CSV_FILE_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scraped_products)

    # Write JSON
    with open(PRODUCTS_JSON, "w", encoding="utf-8") as f:
        json.dump(scraped_products, f, indent=4)

    # Update metadata
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

if __name__ == "__main__":
    run_scraper()
