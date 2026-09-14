import pandas as pd
from datetime import datetime

# 1. Load existing dataset
df_existing = pd.read_csv("tribes_india_products.csv")

# 2. Fetch/Scrape new data (replace with your actual web scraping logic)
# new_data = scrape_tribes_india()
df_new = pd.DataFrame(new_data)

# 3. Merge existing and new data on product_url
# We update existing rows with new values and keep track of updated_at timestamps
df_existing.set_index("product_url", inplace=True)
df_new.set_index("product_url", inplace=True)

# Identify changed or new records
df_existing.update(df_new)  # Overwrites changed values in existing records
df_combined = df_existing.combine_first(df_new)  # Appends brand new products

df_combined.reset_index(inplace=True)

# 4. Save updated dataset
df_combined.to_csv("tribes_india_products.csv", index=False)
print(f"Dataset successfully updated on {datetime.now().strftime('%Y-%m-%d')}")
