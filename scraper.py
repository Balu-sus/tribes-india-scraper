import os
import json
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Output File Paths
IMAGE_DIR = "images"
PRODUCTS_JSON = "tribes_art_products.json"
METADATA_JSON = "metadata.json"
DATASET_METADATA_JSON = "dataset-metadata.json"

os.makedirs(IMAGE_DIR, exist_ok=True)

# Allowed Non-Food Target Categories
TARGET_CATEGORY_URLS = [
    "https://tribesindia.com/category/jewellery",
    "https://tribesindia.com/category/metal-crafts",
    "https://tribesindia.com/category/tribal-paintings",
    "https://tribesindia.com/category/pottery",
    "https://tribesindia.com/category/cane-bamboo-crafts"
]

# Exclusion / Inclusion Filters
FOOD_KEYWORDS = {
    "food", "rice", "tea", "coffee", "honey", "spice", "soap", "shampoo",
    "oil", "powder", "ragi", "poha", "natural", "edible", "flour", "ghee", "jam", "pickle"
}

ART_TOY_KEYWORDS = {
    "necklace", "pendant", "earring", "ring", "craft", "metal", "statue",
    "painting", "pottery", "decor", "toy", "handicraft", "wood", "brass",
    "figurine", "bamboo", "jewellery", "bangle", "locket"
}

def is_art_item(title: str) -> bool:
    text = title.lower()
    if any(food in text for food in FOOD_KEYWORDS):
        return False
    if any(art in text for art in ART_TOY_KEYWORDS):
        return True
    return False

def update_metadata_files(total_records: int):
    """Updates metadata.json and dataset-metadata.json automatically."""
    
    # 1. Update metadata.json
    metadata_content = {
        "title": "Tribes India Art & Crafts Dataset",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_records": total_records,
        "columns": [
            "title",
            "price",
            "category_url",
            "original_image_url",
            "local_image_path"
        ],
        "description": "Scraped arts, crafts, and jewelry catalog data from Tribes India (excluding food products).",
        "source_url": "https://tribesindia.com"
    }

    with open(METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(metadata_content, f, indent=4)

    # 2. Update dataset-metadata.json
    dataset_metadata_content = {
        "title": "Tribes India Art & Crafts Dataset",
        "id": "rokiann/tribes-india-product-dataset",
        "licenses": [
            {
                "name": "CC0-1.0"
            }
        ]
    }

    with open(DATASET_METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(dataset_metadata_content, f, indent=4)

    print(f"Successfully updated {METADATA_JSON} and {DATASET_METADATA_JSON}")

def run_scraper():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    scraped_products = []

    for cat_url in TARGET_CATEGORY_URLS:
        res = requests.get(cat_url, headers=headers)
        if res.status_code != 200:
            continue

        soup = BeautifulSoup(res.content, "html.parser")
        product_cards = soup.find_all("div", class_="product-card") or soup.find_all("li", class_="product")

        for card in product_cards:
            title_elem = card.find("h2") or card.find("h3") or card.find("a", class_="product-title")
            price_elem = card.find("span", class_="price")
            img_elem = card.find("img")

            if not title_elem:
                continue

            title = title_elem.text.strip()
            if not is_art_item(title):
                continue

            price = price_elem.text.strip() if price_elem else "N/A"
            image_url = urljoin(cat_url, img_elem["src"]) if img_elem and img_elem.get("src") else None
            local_image_path = None

            if image_url:
                clean_title = "".join(c for c in title if c.isalnum() or c in (" ", "_")).rstrip()
                filename = f"{clean_title.replace(' ', '_')[:25]}.jpg"
                local_image_path = os.path.join(IMAGE_DIR, filename)

                try:
                    img_bytes = requests.get(image_url, headers=headers).content
                    with open(local_image_path, "wb") as f:
                        f.write(img_bytes)
                except Exception as e:
                    print(f"Error downloading image for {title}: {e}")

            record = {
                "title": title,
                "price": price,
                "category_url": cat_url,
                "original_image_url": image_url,
                "local_image_path": local_image_path
            }
            scraped_products.append(record)

    # Output product dataset
    with open(PRODUCTS_JSON, "w", encoding="utf-8") as f:
        json.dump(scraped_products, f, indent=4)

    # Sync both metadata files with the new total_records count
    update_metadata_files(total_records=len(scraped_products))

if __name__ == "__main__":
    run_scraper()
