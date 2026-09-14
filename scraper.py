import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def find_next_page_link(soup, base_url):
    """
    Looks for standard HTML elements used for 'Next' page buttons.
    """
    next_btn = (
        soup.find("a", rel="next") or
        soup.find("a", class_=lambda c: c and "next" in c.lower() if c else False) or
        soup.find("a", string=lambda s: s and ("next" in s.lower() or ">" in s) if s else False)
    )
    
    if next_btn and next_btn.get("href"):
        next_url = next_btn["href"]
        if not next_url.startswith("http"):
            # Construct full absolute URL
            if next_url.startswith("/"):
                return base_url.rstrip("/") + next_url
            return base_url.rstrip("/") + "/" + next_url
        return next_url
    return None


# --- 1. TRIBES INDIA (NEXT BUTTON) ---
def scrape_tribes_india():
    products = []
    current_url = "https://tribesindia.com/category/food-natural-products"
    base_url = "https://tribesindia.com"
    page = 1

    print("Scraping Tribes India via Next Button...")

    while current_url:
        print(f"Scraping Page {page}: {current_url}")
        try:
            res = requests.get(current_url, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                print(f"Failed to fetch page. Status code: {res.status_code}")
                break

            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.find_all("div", class_="product-layout") or soup.find_all("div", class_="product-thumb")

            if not items:
                print("No items found on this page.")
                break

            for item in items:
                title_elem = item.find("h4") or item.find("a", class_="product-title")
                title = title_elem.get_text(strip=True) if title_elem else "N/A"

                link_elem = item.find("a", href=True)
                product_url = link_elem["href"] if link_elem else "N/A"
                if product_url != "N/A" and not product_url.startswith("http"):
                    product_url = base_url.rstrip("/") + "/" + product_url.lstrip("/")

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

            # Find next page link using DOM inspection
            current_url = find_next_page_link(soup, base_url)
            page += 1
            time.sleep(1)

        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    return products


# --- 2. INDIA HANDMADE (NEXT BUTTON) ---
def scrape_india_handmade():
    products = []
    current_url = "https://indiahandmade.com/collections/handicrafts"
    base_url = "https://indiahandmade.com"
    page = 1

    print("Scraping India Handmade via Next Button...")

    while current_url:
        print(f"Scraping Page {page}: {current_url}")
        try:
            res = requests.get(current_url, headers=HEADERS, timeout=15)
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
                    product_url = base_url.rstrip("/") + "/" + product_url.lstrip("/")

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

            current_url = find_next_page_link(soup, base_url)
            page += 1
            time.sleep(1)

        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    return products


# --- MAIN RUNNER ---
def run_all_scrapers():
    all_data = []
    all_data.extend(scrape_tribes_india())
    all_data.extend(scrape_india_handmade())
    
    df_new = pd.DataFrame(all_data)
    return df_new

if __name__ == "__main__":
    df = run_all_scrapers()
    print(f"Extracted a total of {len(df)} products across platforms.")
