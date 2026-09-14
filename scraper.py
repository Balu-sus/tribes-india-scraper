import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def find_next_page_link(soup, base_url):
    next_btn = (
        soup.find("a", rel="next") or
        soup.find("a", class_=lambda c: c and "next" in c.lower() if c else False) or
        soup.find("a", string=lambda s: s and ("next" in s.lower() or ">" in s) if s else False)
    )
    if next_btn and next_btn.get("href"):
        next_url = next_btn["href"]
        if not next_url.startswith("http"):
            return base_url.rstrip("/") + ("/" + next_url.lstrip("/"))
        return next_url
    return None

# --- 1. DIRECT PLATFORMS (Tribes India, India Handmade) ---
def scrape_direct_stores():
    products = []
    
    # Tribes India
    current_url = "https://tribesindia.com/category/food-natural-products"
    base_url = "https://tribesindia.com"
    page = 1
    
    while current_url and page <= 5:
        try:
            res = requests.get(current_url, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                break
            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.find_all("div", class_="product-layout") or soup.find_all("div", class_="product-thumb")
            
            for item in items:
                title_elem = item.find("h4") or item.find("a", class_="product-title")
                title = title_elem.get_text(strip=True) if title_elem else "N/A"
                link_elem = item.find("a", href=True)
                url = link_elem["href"] if link_elem else "N/A"
                if url != "N/A" and not url.startswith("http"):
                    url = base_url.rstrip("/") + "/" + url.lstrip("/")
                price_elem = item.find("span", class_="price-new") or item.find("span", class_="price")
                price = price_elem.get_text(strip=True) if price_elem else "N/A"
                
                products.append({
                    "platform": "Tribes India Store",
                    "title": title,
                    "price_inr": price,
                    "product_url": url,
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                })
            current_url = find_next_page_link(soup, base_url)
            page += 1
            time.sleep(1)
        except Exception as e:
            print(f"Error scraping Tribes India: {e}")
            break

    return pd.DataFrame(products)


# --- 2. AMAZON & FLIPKART SCRAPER ---
def scrape_amazon_flipkart():

    API_KEY = "66c1a5e522552969cd9fa1fc839fa0aa"

def fetch_protected_url(target_url):
    payload = {'api_key': API_KEY, 'url': target_url}
    response = requests.get('http://api.scraperapi.com', params=payload, timeout=30)
    return response.text if response.status_code == 200 else None
    
    marketplace_products = []
    
    # Define targeted search terms for Tribes India on Flipkart & Amazon
    search_queries = [
        {"platform": "Flipkart", "url": "https://www.flipkart.com/search?q=tribes+india"},
        {"platform": "Amazon", "url": "https://www.amazon.in/s?k=tribes+india"}
    ]
    
    for search in search_queries:
        platform = search["platform"]
        url = search["url"]
        print(f"Scraping {platform} listings...")
        
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                
                if platform == "Flipkart":
                    items = soup.find_all("div", class_="_1AtVbE") or soup.find_all("div", class_="_1xHG2k")
                    for item in items[:15]:
                        title = item.find("a", class_="IRwbT7") or item.find("div", class_="_30jeq3")
                        price = item.find("div", class_="_30jeq3")
                        link = item.find("a", href=True)
                        if title:
                            p_url = "https://www.flipkart.com" + link["href"] if link else url
                            marketplace_products.append({
                                "platform": "Flipkart",
                                "title": title.get_text(strip=True),
                                "price_inr": price.get_text(strip=True) if price else "N/A",
                                "product_url": p_url,
                                "last_updated": datetime.now().strftime("%Y-%m-%d")
                            })

                elif platform == "Amazon":
                    items = soup.find_all("div", {"data-component-type": "s-search-result"})
                    for item in items[:15]:
                        title = item.find("h2")
                        price = item.find("span", class_="a-price-whole")
                        link = item.find("a", class_="a-link-normal", href=True)
                        if title:
                            p_url = "https://www.amazon.in" + link["href"] if link else url
                            marketplace_products.append({
                                "platform": "Amazon",
                                "title": title.get_text(strip=True),
                                "price_inr": f"₹{price.get_text(strip=True)}" if price else "N/A",
                                "product_url": p_url,
                                "last_updated": datetime.now().strftime("%Y-%m-%d")
                            })
            time.sleep(2)
        except Exception as e:
            print(f"Error fetching {platform}: {e}")

    return pd.DataFrame(marketplace_products)


def run_all_scrapers():
    df_direct = scrape_direct_stores()
    df_marketplaces = scrape_amazon_flipkart()
    return df_direct, df_marketplaces
