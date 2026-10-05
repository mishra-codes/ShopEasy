from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.mongo_uri)
db = client[settings.mongo_db]

products = [
    {"name": "Wireless Mouse", "category": "Electronics", "price": 799.00, "stock_qty": 25},
    {"name": "Mechanical Keyboard", "category": "Electronics", "price": 2499.00, "stock_qty": 15},
    {"name": "USB-C Hub", "category": "Electronics", "price": 1499.00, "stock_qty": 20},
    {"name": "Laptop Backpack", "category": "Accessories", "price": 1299.00, "stock_qty": 30},
    {"name": "Water Bottle", "category": "Lifestyle", "price": 499.00, "stock_qty": 40},
]

for product in products:
    db.products.update_one(
        {"name": product["name"]},
        {"$setOnInsert": product},
        upsert=True
    )
print(f"Inserted {len(products)} products into {settings.mongo_db}.products")
client.close()
