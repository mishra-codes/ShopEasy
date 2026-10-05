from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.database import get_db
from app.templating import templates

router = APIRouter()

def _require_login(request: Request):
    return request.session.get("customer_id")

def _oid(value):
    try:
        return ObjectId(value)
    except Exception:
        return None

def calculate_discount(amount):
    if amount >= 5000:
        return round(amount * 0.10, 2)
    if amount >= 2000:
        return round(amount * 0.05, 2)
    return 0

@router.post("/checkout")
def checkout(request: Request):
    customer_id = _require_login(request)
    if not customer_id:
        return RedirectResponse("/login", status_code=303)

    db = get_db()
    cart = db.carts.find_one({"customer_id": customer_id})
    if not cart or not cart.get("items"):
        return RedirectResponse("/cart", status_code=303)

    order_items = []
    total = 0

    for cart_item in cart["items"]:
        product = db.products.find_one({"_id": cart_item["product_id"]})
        if not product:
            continue

        qty = cart_item["qty"]
        if product.get("stock_qty", 0) < qty:
            items = []
            for ci in cart["items"]:
                p = db.products.find_one({"_id": ci["product_id"]})
                if p:
                    items.append({
                        "cart_item_id": str(ci["item_id"]),
                        "product_id": str(p["_id"]),
                        "name": p["name"],
                        "price": p["price"],
                        "qty": ci["qty"],
                        "line_total": p["price"] * ci["qty"],
                    })
            total = sum(x["line_total"] for x in items)
            return templates.TemplateResponse(
                request=request,
                name="cart.html",
                context={
                    "items": items,
                    "total": total,
                    "error": f'Insufficient stock for "{product["name"]}". '
                              f'Available: {product.get("stock_qty", 0)}, Requested: {qty}',
                },
            )

        line_total = product["price"] * qty
        total += line_total
        order_items.append({
            "product_id": product["_id"],
            "name": product["name"],
            "qty": qty,
            "price_at_order": product["price"],
            "line_total": line_total,
        })

    if not order_items:
        return RedirectResponse("/cart", status_code=303)

    discount = calculate_discount(total)
    final_total = round(total - discount, 2)
    now = datetime.now(timezone.utc)

    order = {
        "customer_id": customer_id,
        "order_date": now,
        "status": "PLACED",
        "total_amount": final_total,
        "items": order_items,
        "discount": discount,
    }
    result = db.orders.insert_one(order)
    order_id = result.inserted_id

    # Decrease inventory after successful order creation.
    for item in order_items:
        db.products.update_one(
            {"_id": item["product_id"]},
            {"$inc": {"stock_qty": -item["qty"]}},
        )

    db.order_status_logs.insert_one({
        "order_id": order_id,
        "status": "PLACED",
        "changed_on": now,
    })

    # Empty the customer's cart.
    db.carts.update_one({"_id": cart["_id"]}, {"$set": {"items": []}})

    return RedirectResponse(f"/orders/{order_id}", status_code=303)

@router.get("/orders")
def list_orders(request: Request):
    customer_id = _require_login(request)
    if not customer_id:
        return RedirectResponse("/login", status_code=303)

    db = get_db()
    orders = []
    for o in db.orders.find({"customer_id": customer_id}).sort("order_date", -1):
        orders.append({
            "order_id": str(o["_id"]),
            "order_date": o["order_date"],
            "status": o["status"],
            "total_amount": o["total_amount"],
        })

    return templates.TemplateResponse(
        request=request, name="orders.html", context={"orders": orders}
    )

@router.get("/orders/{order_id}")
def order_detail(request: Request, order_id: str):
    customer_id = _require_login(request)
    if not customer_id:
        return RedirectResponse("/login", status_code=303)

    db = get_db()
    oid = _oid(order_id)
    if not oid:
        return RedirectResponse("/orders", status_code=303)

    order = db.orders.find_one({"_id": oid, "customer_id": customer_id})
    if not order:
        return RedirectResponse("/orders", status_code=303)

    order_view = {
        "order_id": str(order["_id"]),
        "order_date": order["order_date"],
        "status": order["status"],
        "total_amount": order["total_amount"],
    }

    items = [
        {
            "name": item["name"],
            "qty": item["qty"],
            "price_at_order": item["price_at_order"],
            "line_total": item["line_total"],
        }
        for item in order.get("items", [])
    ]

    payment = db.payments.find_one({"order_id": oid})
    if payment:
        payment = {
            "payment_id": str(payment["_id"]),
            "amount": payment["amount"],
            "method": payment["method"],
            "status": payment["status"],
            "payment_date": payment["payment_date"],
        }

    return templates.TemplateResponse(
        request=request,
        name="order_detail.html",
        context={"order": order_view, "items": items, "payment": payment},
    )
