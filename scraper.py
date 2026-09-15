import os
import json
import csv
import requests
from datetime import datetime, timezone

DATA_DIR = "data"
IMAGE_DIR = "images"
CSV_FILE_PATH = os.path.join(DATA_DIR, "tribes_india_products.csv")
PRODUCTS_JSON = os.path.join(DATA_DIR, "tribes_art_products.json")
METADATA_JSON = "metadata.json"
DATASET_METADATA_JSON = "dataset-metadata.json"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# Direct JSON/API catalog endpoints bypassing dynamic JS loading
API_CATEGORY_URLS = [
    "https://tribesindia.com/wp-json/wc/v3/products?category=jewellery&per_page=50",
    "https://tribesindia.com/wp-json/wc/v3/products?category=metal-crafts&per_page=50",
    "https://tribesindia.com/wp-json/wc/v3/products?category=paintings&per_page=50",
    "https://tribesindia.com/wp-json/wc/v3/products?category=pottery&per_page=50",
    "https://tribesindia.com/wp-json/wc/v3/products?category=cane-bamboo&per_page=50"
]

FOOD_KEYWORDS = {
    "food", "rice", "tea", "coffee", "honey", "spice", "soap", "shampoo",
    "oil", "powder", "ragi", "poha", "natural", "edible", "flour", "ghee", "jam", "pickle"
}

def run_scraper():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    scraped_products = []

    for api_url in API_CATEGORY_URLS:
        print(f"Querying API endpoint: {api_url}")
        try:
            res = requests.get(api_url, headers=headers, timeout=15)
            if res.status_code != 200:
                print(f"API endpoint returned status {res.status_code}, skipping...")
                continue
            
            items = res.json()
            if not isinstance(items, list):
                items = items.get("products", [])

        except Exception as e:
            print(f"Failed fetching from API {api_url}: {e}")
            continue

        for item in items:
            title = item.get("name", "").strip()
            
            # Filter food/grocery items
            if not title or any(food in title.lower() for food in FOOD_KEYWORDS):
                continue

            # Extract price from JSON structure
            price = item.get("price") or item.get("regular_price") or "N/A"
            if price != "N/A" and not str(price).startswith("₹"):
                price = f"₹{price}"

            # Extract primary image URL from images array
            images = item.get("images", [])
            image_url = images[0].get("src") if images and isinstance(images, list) else None

            # Enforce strictly complete items (must have price and image)
            if price == "N/A" or not image_url:
                continue

            # Download local image
            clean_title = "".join(c for c in title if c.isalnum() or c in (" ", "_")).rstrip()
            filename = f"{clean_title.replace(' ', '_')[:25]}.jpg"
            local_image_path = os.path.join(IMAGE_DIR, filename)

            try:
                img_bytes = requests.get(image_url, headers=headers, timeout=10).content
                with open(local_image_path, "wb") as f:
                    f.write(img_bytes)
            except Exception:
                local_image_path = ""

            scraped_products.append({
                "title": title,
                "price": price,
                "category_url": api_url,
                "original_image_url": image_url,
                "local_image_path": local_image_path
            })

    if not scraped_products:
        print("No dynamic items fetched from API.")
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
        "description": "API-scraped catalog data containing complete items with price and images.",
        "source_url": "https://tribesindia.com"
    }
    with open(METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    print(f"Successfully populated {len(scraped_products)} items.")

if __name__ == "__main__":
    run_scraper()
