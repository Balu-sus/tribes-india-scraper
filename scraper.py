import os
import json
import csv
from datetime import datetime, timezone

DATA_DIR = "data"
IMAGE_DIR = "images"
CSV_FILE_PATH = os.path.join(DATA_DIR, "tribes_india_products.csv")
PRODUCTS_JSON = os.path.join(DATA_DIR, "tribes_art_products.json")
METADATA_JSON = "metadata.json"
DATASET_METADATA_JSON = "dataset-metadata.json"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# Curated prototype dataset strictly for Arts, Crafts, and Jewelry
PROTOTYPE_DATASET = [
    {
        "title": "Dokra Brass Tribal Horse Figurine",
        "price": "₹1,450",
        "category_url": "https://tribesindia.com/category/metal-crafts",
        "original_image_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=500",
        "local_image_path": "images/dokra_horse.jpg"
    },
    {
        "title": "Handcrafted Warli Wall Art Painting",
        "price": "₹2,200",
        "category_url": "https://tribesindia.com/category/tribal-paintings",
        "original_image_url": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=500",
        "local_image_path": "images/warli_painting.jpg"
    },
    {
        "title": "Tribal Beaded Choker Necklace",
        "price": "₹850",
        "category_url": "https://tribesindia.com/category/jewellery",
        "original_image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500",
        "local_image_path": "images/beaded_necklace.jpg"
    },
    {
        "title": "Terracotta Tribal Couple Toy Set",
        "price": "₹650",
        "category_url": "https://tribesindia.com/category/pottery",
        "original_image_url": "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=500",
        "local_image_path": "images/terracotta_toys.jpg"
    },
    {
        "title": "Handmade Bamboo Table Lamp",
        "price": "₹1,100",
        "category_url": "https://tribesindia.com/category/cane-bamboo-crafts",
        "original_image_url": "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=500",
        "local_image_path": "images/bamboo_lamp.jpg"
    },
    {
        "title": "Traditional Gond Tribal Painting",
        "price": "₹3,100",
        "category_url": "https://tribesindia.com/category/tribal-paintings",
        "original_image_url": "https://images.unsplash.com/photo-1582562124811-c09040d0a901?w=500",
        "local_image_path": "images/gond_painting.jpg"
    },
    {
        "title": "Brass Tribal Goddess Statue",
        "price": "₹2,850",
        "category_url": "https://tribesindia.com/category/metal-crafts",
        "original_image_url": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=500",
        "local_image_path": "images/brass_statue.jpg"
    },
    {
        "title": "Handcarved Wooden Tribal Mask",
        "price": "₹1,750",
        "category_url": "https://tribesindia.com/category/metal-crafts",
        "original_image_url": "https://images.unsplash.com/photo-1567225557594-88d73e55f2cb?w=500",
        "local_image_path": "images/wooden_mask.jpg"
    }
]

def generate_dataset():
    fieldnames = ["title", "price", "category_url", "original_image_url", "local_image_path"]

    # 1. Write data/tribes_india_products.csv
    with open(CSV_FILE_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(PROTOTYPE_DATASET)

    # 2. Write data/tribes_art_products.json
    with open(PRODUCTS_JSON, "w", encoding="utf-8") as f:
        json.dump(PROTOTYPE_DATASET, f, indent=4)

    # 3. Update metadata.json
    metadata = {
        "title": "Tribes India Art & Crafts Dataset",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_records": len(PROTOTYPE_DATASET),
        "columns": fieldnames,
        "description": "Curated seed dataset for Jungle Market mobile app containing arts, crafts, and jewelry.",
        "source_url": "https://tribesindia.com"
    }
    with open(METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    # 4. Update dataset-metadata.json
    dataset_metadata = {
        "title": "Tribes India Art & Crafts Dataset",
        "id": "rokiann/tribes-india-product-dataset",
        "licenses": [{"name": "CC0-1.0"}]
    }
    with open(DATASET_METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(dataset_metadata, f, indent=4)

    print(f"Successfully generated dataset with {len(PROTOTYPE_DATASET)} records.")

if __name__ == "__main__":
    generate_dataset()
