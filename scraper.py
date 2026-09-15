import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Local file configuration
IMAGE_DIR = "images"
DATA_FILE = "tribes_art_products.json"
os.makedirs(IMAGE_DIR, exist_ok=True)

# Target ONLY Art/Craft/Jewellery categories from Tribes India
TARGET_CATEGORY_URLS = [
    "https://tribesindia.com/category/jewellery",
    "https://tribesindia.com/category/metal-crafts",
    "https://tribesindia.com/category/tribal-paintings",
    "https://tribesindia.com/category/pottery",
    "https://tribesindia.com/category/cane-bamboo-crafts"
]

# Exclusion keywords (Food, Grocery, Natural Products)
FOOD_KEYWORDS = {
    "food", "rice", "tea", "coffee", "honey", "spice", "soap", "shampoo",
    "oil", "powder", "ragi", "poha", "natural", "edible", "flour", "ghee", "jam"
}

# Inclusion keywords (Art, Crafts, Toys, Jewellery)
ART_TOY_KEYWORDS = {
    "necklace", "pendant", "earring", "ring", "craft", "metal", "statue",
    "painting", "pottery", "decor", "toy", "handicraft", "wood", "brass",
    "figurine", "bamboo", "jewellery", "bangle", "locket"
}

def is_art_item(title: str, category_url: str) -> bool:
    """Filters out food items and checks for valid art/craft terms."""
    combined_text = f"{title} {category_url}".lower()
    
    # Drop if any food/grocery term matches
    if any(food_term in combined_text for food_term in FOOD_KEYWORDS):
        return False
        
    # Accept if art/craft term matches
    if any(art_term in combined_text for art_term in ART_TOY_KEYWORDS):
        return True
        
    return False

def scrape_and_save():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    scraped_products = []

    for cat_url in TARGET_CATEGORY_URLS:
        print(f"Scraping category: {cat_url}")
        res = requests.get(cat_url, headers=headers)
        if res.status_code != 200:
            continue

        soup = BeautifulSoup(res.content, "html.parser")
        
        # Extract product elements (adjust selector based on page DOM)
        product_cards = soup.find_all("div", class_="product-card") or soup.find_all("li", class_="product")

        for card in product_cards:
            title_elem = card.find("h2") or card.find("h3") or card.find("a", class_="product-title")
            price_elem = card.find("span", class_="price")
            img_elem = card.find("img")

            if not title_elem:
                continue

            title = title_elem.text.strip()

            # Filter out non-art/food products
            if not is_art_item(title, cat_url):
                print(f"Skipped (Food/Grocery): {title}")
                continue

            price = price_elem.text.strip() if price_elem else "N/A"
            image_url = urljoin(cat_url, img_elem["src"]) if img_elem and img_elem.get("src") else None
            local_image_path = None

            # Download raw image binary at the same time as metadata
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

            product_record = {
                "title": title,
                "price": price,
                "category_url": cat_url,
                "original_image_url": image_url,
                "local_image_path": local_image_path
            }

            scraped_products.append(product_record)
            print(f"Saved product + image: {title}")

    # Output dataset directly inside the repo
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(scraped_products, f, indent=4)

if __name__ == "__main__":
    scrape_and_save()
