# 🛒 ShopEasy — Online Shopping & Inventory Management System

ShopEasy is a web-based **Online Shopping and Inventory Management System** developed as an ADP project.

The application provides a simple shopping platform where customers can register, browse products, manage their cart, place orders, make payments, and track their orders.

The project uses **FastAPI** for the backend, **MongoDB** for database management, and **Jinja2/HTML/CSS** for the frontend.

---

## ✨ Features

### 👤 Customer Management
- Customer registration
- Customer login
- Session-based authentication
- Customer-specific cart
- Customer order history

### 🛍️ Product Management
- View available products
- Product categories
- Product prices
- Real-time stock availability
- Stock quantity validation

### 🛒 Shopping Cart
- Add products to cart
- Update cart quantities
- Remove products from cart
- Automatic stock validation
- Cart total calculation

### 📦 Order Management
- Place orders
- Generate order details
- Store ordered items
- Calculate order totals
- Track order status
- View previous orders

### 💳 Payment Management
- Payment processing interface
- Payment records stored in MongoDB
- Payment status tracking

### 📊 Inventory Management
- Centralized product inventory
- Stock is shared across all customers
- Stock decreases when an order is successfully placed
- Prevents customers from ordering unavailable quantities

---

## 🧰 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core programming language |
| FastAPI | Backend web framework |
| MongoDB | Database |
| PyMongo | MongoDB integration |
| Jinja2 | Server-side HTML templates |
| HTML5 | Frontend structure |
| CSS3 | Frontend styling |
| Uvicorn | ASGI server |
| Python-dotenv | Environment configuration |

---

## 🏗️ Project Architecture

```text
                    ┌─────────────────────┐
                    │      Customer       │
                    │      Browser        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │      Backend        │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
       Authentication      Products          Orders
             │                 │                 │
             └─────────────────┼─────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      MongoDB        │
                    │      Database       │
                    └─────────────────────┘

## Project Structure

```text
ShopEasy/
├── app/
│   ├── routers/
│   ├── templates/
│   ├── static/
│   ├── config.py
│   ├── database.py
│   └── main.py
├── scripts/
│   └── seed.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/ShopEasy-MongoDB.git
cd ShopEasy-MongoDB
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:

```env
MONGO_URI=mongodb://127.0.0.1:27017
MONGO_DB=shopeasy
SESSION_SECRET=your-secret-key
```

Seed the database:

```bash
python -m scripts.seed
```

Run the application:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Future Updates

- Admin dashboard
- Add/Edit/Delete products
- Inventory management
- Sales and order analytics
- Low-stock alerts

## Developer

**Ayush Mishra**  
BSc Information Technology  
KES Shroff College

> Academic project developed for educational purposes.