import os
import re
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
BASE_URL = "https://tribesindia.com"

def get_product_urls(category_url):
    """Fetches individual product links from a category listing page."""
    product_urls = set()
    try:
        response = requests.get(category_url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            # Finds product page links matching common e-commerce URL structures
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/product/" in href or "/products/" in href or "/item/" in href:
                    full_url = href if href.startswith("http") else BASE_URL + href
                    product_urls.add(full_url)
    except Exception as e:
        print(f"Error fetching category {category_url}: {e}")
    return list(product_urls)

def get_product_details(product_url):
    """Extracts title, price, and description from a product page."""
    try:
        response = requests.get(product_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, "html.parser")

        # 1. Product Title
        title_elem = soup.find("h1")
        title_text = title_elem.text.strip() if title_elem else None

        # 2. Product Price (cleans currency symbols like ₹ or commas)
        price_elem = soup.find(class_=re.compile(r"price|amount|current-price", re.I))
        price_val = None
        if price_elem:
            raw_price = re.sub(r"[^\d.]", "", price_elem.text.strip())
            try:
                price_val = float(raw_price)
            except ValueError:
                price_val = None

        # 3. Product Description
        desc_elem = soup.find("div", class_=re.compile(r"description|detail|summary", re.I)) or soup.find("section", id=re.compile(r"description", re.I))
        desc_text = desc_elem.text.strip() if desc_elem else None

        # Only return if we found at least a title or URL to avoid dead rows
        if title_text or price_val:
            return {
                "title": title_text,
                "price_inr": price_val,
                "description": desc_text,
                "product_url": product_url
            }
    except Exception as e:
        print(f"Error scraping {product_url}: {e}")
    return None

if __name__ == "__main__":
    # Categories to scrape (Add target category page URLs here)
    category_urls = [
        "https://tribesindia.com/shop", 
    ]
    
    scraped_data = []

    print("Gathering product URLs...")
    all_product_urls = set()
    for cat_url in category_urls:
        urls = get_product_urls(cat_url)
        all_product_urls.update(urls)
        time.sleep(1)

    print(f"Found {len(all_product_urls)} products. Starting detail extraction...")

    for url in all_product_urls:
        details = get_product_details(url)
        if details:
            scraped_data.append(details)
        time.sleep(1)  # Polite crawling delay

    # Save output for GitHub & Kaggle
    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(scraped_data)
    
    if not df.empty:
        df.to_csv("data/tribes_india_products.csv", index=False, encoding="utf-8")
        print(f"Success: Scraped {len(df)} products and saved to data/tribes_india_products.csv")
    else:
        print("Warning: No product data was scraped. Check your target URLs or HTML selectors.")
