import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Output JSON paths
IMAGE_DIR = "images"
PRODUCTS_JSON_FILE = "tribes_art_products.json"
CATEGORIES_JSON_FILE = "tribes_categories.json"

os.makedirs(IMAGE_DIR, exist_ok=True)

# Target categories (Art, Jewelry, Crafts)
CATEGORY_MAPPING = {
    "Jewellery": "https://tribesindia.com/category/jewellery",
    "Metal Crafts": "https://tribesindia.com/category/metal-crafts",
    "Tribal Paintings": "https://tribesindia.com/category/tribal-paintings",
    "Pottery": "https://tribesindia.com/category/pottery",
    "Cane & Bamboo Crafts": "https://tribesindia.com/category/cane-bamboo-crafts"
}

# Filters
FOOD_KEYWORDS = {
    "food", "rice", "tea", "coffee", "honey", "spice", "soap", "shampoo",
    "oil", "powder", "ragi", "poha", "natural", "edible", "flour", "ghee", "jam"
}

ART_TOY_KEYWORDS = {
    "necklace", "pendant", "earring", "ring", "craft", "metal", "statue",
    "painting", "pottery", "decor", "toy", "handicraft", "wood", "brass",
    "figurine", "bamboo", "jewellery", "bangle", "locket"
}

def is_art_item(title: str) -> bool:
    text = title.lower()
    if any(food_term in text for food_term in FOOD_KEYWORDS):
        return False
    if any(art_term in text for art_term in ART_TOY_KEYWORDS):
        return True
    return False

def run_scraper():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    all_products = []
    category_summary = {}

    for cat_name, cat_url in CATEGORY_MAPPING.items():
        print(f"Scraping category: {cat_name}")
        category_summary[cat_name] = []
        
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

            # Skip food items
            if not is_art_item(title):
                continue

            price = price_elem.text.strip() if price_elem else "N/A"
            image_url = urljoin(cat_url, img_elem["src"]) if img_elem and img_elem.get("src") else None
            local_image_path = None

            # Download image
            if image_url:
                clean_title = "".join(c for c in title if c.isalnum() or c in (" ", "_")).rstrip()
                filename = f"{clean_title.replace(' ', '_')[:25]}.jpg"
                local_image_path = os.path.join(IMAGE_DIR, filename)

                try:
                    img_bytes = requests.get(image_url, headers=headers).content
                    with open(local_image_path, "wb") as f:
                        f.write(img_bytes)
                except Exception as e:
                    print(f"Failed image download for {title}: {e}")

            record = {
                "title": title,
                "price": price,
                "category": cat_name,
                "original_image_url": image_url,
                "local_image_path": local_image_path
            }

            all_products.append(record)
            category_summary[cat_name].append(title)

    # File 1: Save main product records
    with open(PRODUCTS_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=4)

    # File 2: Save categorized summary
    with open(CATEGORIES_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(category_summary, f, indent=4)

    print(f"Updated both JSON files: {PRODUCTS_JSON_FILE} & {CATEGORIES_JSON_FILE}")

if __name__ == "__main__":
    run_scraper()
