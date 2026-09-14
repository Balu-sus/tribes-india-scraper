# 🛒 Tribes India Product Dataset

An automated research dataset that periodically scrapes product details from [Tribes India](https://tribesindia.com/). Updated automatically every week using GitHub Actions.

## 📊 Dataset Metadata
* **Location:** `data/tribes_india_products.csv`
* **Metadata Info:** `data/metadata.json`
* **Update Frequency:** Weekly (Every Sunday at 00:00 UTC)

## 📁 Data Fields
| Column | Description |
| :--- | :--- |
| `title` | Name of the tribal handicraft or natural product |
| `price_inr` | Cleaned numerical price in Indian Rupees (₹) |
| `description` | Product description and details |
| `product_url` | Direct link to the product page on Tribes India |

## ⚙️ How It Works
This repo runs an automated Python scraper using **BeautifulSoup4** and **GitHub Actions**. Every week, the action executes `scraper.py`, generates an updated CSV and metadata file, and commits the changes back to this repository.
