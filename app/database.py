from pymongo import MongoClient, ASCENDING
from app.config import settings

client: MongoClient | None = None
db = None

def init_db():
    global client, db
    client = MongoClient(settings.mongo_uri)
    client.admin.command("ping")
    db = client[settings.mongo_db]

    # Indexes replace several relational UNIQUE/lookup constraints.
    db.customers.create_index("email", unique=True)
    db.carts.create_index("customer_id", unique=True)
    db.orders.create_index([("customer_id", ASCENDING), ("order_date", -1)])
    db.payments.create_index("order_id", unique=True)
    db.order_status_logs.create_index([("order_id", ASCENDING), ("changed_on", ASCENDING)])

def close_db():
    global client, db
    if client:
        client.close()
    client = None
    db = None

def get_db():
    if db is None:
        raise RuntimeError("MongoDB is not initialized")
    return db
