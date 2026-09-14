import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- 1. TRIBES INDIA SCRAPER ---
def scrape_tribes_india():
    products = []
    page = 1
    base_url = "https://tribesindia.com"
    
    print("Scraping Tribes India...")
    while True:
        url = f"https://tribesindia.com/category/food-natural-products?page={page}"
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                break
            
            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.find_all("div", class_="product-layout") or soup.find_all("div", class_="product-thumb")
            
            if not items:
                break
                
            for item in items:
                title_elem = item.find("h4") or item.find("a", class_="product-title")
                title = title_elem.get_text(strip=True) if title_elem else "N/A"
                
                link_elem = item.find("a", href=True)
                product_url = link_elem["href"] if link_elem else "N/A"
                if product_url != "N/A" and not product_url.startswith("http"):
                    product_url = base_url + product_url

                price_elem = item.find("span", class_="price-new") or item.find("span", class_="price")
                orig_price_elem = item.find("span", class_="price-old")

                price = price_elem.get_text(strip=True) if price_elem else None
                orig_price = orig_price_elem.get_text(strip=True) if orig_price_elem else price

                products.append({
                    "platform": "Tribes India",
                    "title": title,
                    "price_inr": price,
                    "original_price_inr": orig_price,
                    "product_url": product_url,
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                })
            page += 1
            time.sleep(1)
        except Exception as e:
            print(f"Error scraping Tribes India page {page}: {e}")
            break
            
    return products

# --- 2. INDIA HANDMADE SCRAPER ---
def scrape_india_handmade():
    products = []
    page = 1
    base_url = "https://indiahandmade.com"
    
    print("Scraping India Handmade...")
    while True:
        url = f"https://indiahandmade.com/collections/handicrafts?page={page}"
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                break
                
            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.find_all("div", class_="product-card") or soup.find_all("li", class_="grid__item")
            
            if not items:
                break
                
            for item in items:
                title_elem = item.find("a", class_="full-unstyled-link") or item.find("h3")
                title = title_elem.get_text(strip=True) if title_elem else "N/A"
                
                link_elem = item.find("a", href=True)
                product_url = link_elem["href"] if link_elem else "N/A"
                if product_url != "N/A" and not product_url.startswith("http"):
                    product_url = base_url + product_url

                price_elem = item.find("span", class_="price-item--sale") or item.find("span", class_="price-item--regular")
                price = price_elem.get_text(strip=True) if price_elem else None

                products.append({
                    "platform": "India Handmade",
                    "title": title,
                    "price_inr": price,
                    "original_price_inr": price,
                    "product_url": product_url,
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                })
            page += 1
            time.sleep(1)
        except Exception as e:
            print(f"Error scraping India Handmade page {page}: {e}")
            break
            
    return products

# --- 3. MAIN RUNNER ---
def run_all_scrapers():
    all_data = []
    all_data.extend(scrape_tribes_india())
    all_data.extend(scrape_india_handmade())
    
    df_new = pd.DataFrame(all_data)
    return df_new

if __name__ == "__main__":
    df = run_all_scrapers()
    print(f"Scraped total {len(df)} products across platforms.")
