import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

CSV_FILE = "tribes_india_products.csv"
BASE_URL = "https://tribesindia.com"
# Main store category endpoint
CATEGORY_URL = "https://tribesindia.com/category/food-natural-products"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_all_pages():
    all_products = []
    page = 1

    print("Starting full catalog extraction...")

    while True:
        # Construct paginated URL
        url = f"{CATEGORY_URL}?page={page}"
        print(f"Scraping Page {page}: {url}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                print(f"Page {page} returned status code {response.status_code}. Ending loop.")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            
            # Select product card containers (adjust CSS class as needed based on target site layout)
            items = soup.find_all("div", class_="product-layout") or soup.find_all("div", class_="product-thumb")
            
            if not items:
                print(f"No products found on page {page}. Total pages scraped: {page - 1}.")
                break

            for item in items:
                title_elem = item.find("h4") or item.find("a", class_="product-title")
                title = title_elem.get_text(strip=True) if title_elem else "N/A"

                link_elem = item.find("a", href=True)
                product_url = link_elem["href"] if link_elem else "N/A"
                if product_url != "N/A" and not product_url.startswith("http"):
                    product_url = BASE_URL + product_url

                # Extract prices
                price_elem = item.find("span", class_="price-new") or item.find("span", class_="price")
                orig_price_elem = item.find("span", class_="price-old")

                price = price_elem.get_text(strip=True) if price_elem else None
                orig_price = orig_price_elem.get_text(strip=True) if orig_price_elem else price

                all_products.append({
                    "title": title,
                    "price_inr": price,
                    "original_price_inr": orig_price,
                    "product_url": product_url,
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                })

            page += 1
            time.sleep(1) # Polite crawling delay

        except Exception as e:
            print(f"Error scraping page {page}: {e}")
            break

    return pd.DataFrame(all_products)

def update_dataset():
    df_new = scrape_all_pages()
    
    if df_new.empty:
        print("No data extracted. Aborting dataset update.")
        return

    if os.path.exists(CSV_FILE):
        df_old = pd.read_csv(CSV_FILE)
        
        # Merge on primary key 'product_url'
        df_old.set_index("product_url", inplace=True)
        df_new.set_index("product_url", inplace=True)

        df_old.update(df_new)
        df_final = df_old.combine_first(df_new).reset_index()
    else:
        df_final = df_new.reset_index()

    df_final.to_csv(CSV_FILE, index=False)
    print(f"Dataset successfully updated. Total records in CSV: {len(df_final)}")

if __name__ == "__main__":
    update_dataset()
