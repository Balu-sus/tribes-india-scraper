import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os

SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY", "DEFAULT_FALLBACK_KEY")

# Replace with your actual ScraperAPI key
SCRAPERAPI_KEY = "66c1a5e522552969cd9fa1fc839fa0aa"

def fetch_via_scraperapi(target_url):
    payload = {
        'api_key': SCRAPERAPI_KEY,
        'url': target_url,
        'country_code': 'in'  # Route through India proxies for accurate Amazon.in / Flipkart data
    }
    try:
        response = requests.get('http://api.scraperapi.com', params=payload, timeout=40)
        print(f"ScraperAPI Status for {target_url[:35]}... -> {response.status_code}")
        if response.status_code == 200:
            return response.text
        else:
            print(f"API Error Response: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def scrape_amazon_flipkart():
    marketplace_products = []
    
    # 1. SCRAPE AMAZON
    amazon_url = "https://www.amazon.in/s?k=tribes+india"
    html_amazon = fetch_via_scraperapi(amazon_url)
    
    if html_amazon:
        soup = BeautifulSoup(html_amazon, "html.parser")
        # Universal container for Amazon search results
        items = soup.find_all("div", {"data-component-type": "s-search-result"})
        print(f"Found {len(items)} raw Amazon product cards.")
        
        for item in items:
            # Flexible selector for title
            title_elem = item.find("h2") or item.find("span", class_="a-size-medium")
            price_elem = item.find("span", class_="a-price-whole")
            link_elem = item.find("a", class_="a-link-normal", href=True)
            
            if title_elem:
                title = title_elem.get_text(strip=True)
                price = f"₹{price_elem.get_text(strip=True)}" if price_elem else "N/A"
                
                href = link_elem["href"] if link_elem else ""
                product_url = "https://www.amazon.in" + href if href.startswith("/") else href
                
                marketplace_products.append({
                    "platform": "Amazon",
                    "title": title,
                    "price_inr": price,
                    "product_url": product_url,
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                })

    # 2. SCRAPE FLIPKART
    flipkart_url = "https://www.flipkart.com/search?q=tribes+india"
    html_flipkart = fetch_via_scraperapi(flipkart_url)
    
    if html_flipkart:
        soup = BeautifulSoup(html_flipkart, "html.parser")
        # Flipkart product grid containers
        items = soup.find_all("div", class_="_1AtVbE") or soup.find_all("div", class_="_75Wf1D") or soup.find_all("div", class_="cPHRSc")
        print(f"Found {len(items)} raw Flipkart product cards.")
        
        for item in items:
            title_elem = item.find("a", class_="IRwbT7") or item.find("div", class_="KzA324") or item.find("a", class_="w2-f8f")
            price_elem = item.find("div", class_="_30jeq3") or item.find("div", class_="Nx9bqj")
            link_elem = item.find("a", href=True)
            
            if title_elem:
                title = title_elem.get_text(strip=True)
                price = price_elem.get_text(strip=True) if price_elem else "N/A"
                
                href = link_elem["href"] if link_elem else ""
                product_url = "https://www.flipkart.com" + href if href.startswith("/") else href
                
                marketplace_products.append({
                    "platform": "Flipkart",
                    "title": title,
                    "price_inr": price,
                    "product_url": product_url,
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                })

    print(f"Total marketplace items collected: {len(marketplace_products)}")
    return pd.DataFrame(marketplace_products)
