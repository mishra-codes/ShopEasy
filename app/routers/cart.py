from bson import ObjectId
from fastapi import APIRouter, Request, Form
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

def _get_or_create_cart(db, customer_id):
    cart = db.carts.find_one({"customer_id": customer_id})
    if cart:
        return cart

    cart = {"customer_id": customer_id, "items": []}
    result = db.carts.insert_one(cart)
    cart["_id"] = result.inserted_id
    return cart

def _cart_items(db, customer_id):
    cart = db.carts.find_one({"customer_id": customer_id})
    if not cart:
        return []

    items = []
    for item in cart.get("items", []):
        product = db.products.find_one({"_id": item["product_id"]})
        if not product:
            continue
        qty = item["qty"]
        items.append({
            "cart_item_id": str(item["item_id"]),
            "product_id": str(product["_id"]),
            "name": product["name"],
            "price": product["price"],
            "qty": qty,
            "line_total": product["price"] * qty,
        })
    return items

@router.post("/cart/add")
def add_to_cart(
    request: Request,
    product_id: str = Form(...),
    qty: int = Form(1),
):
    customer_id = _require_login(request)
    if not customer_id:
        return RedirectResponse("/login", status_code=303)

    db = get_db()
    product_oid = _oid(product_id)
    if not product_oid or qty < 1:
        return RedirectResponse("/products", status_code=303)

    product = db.products.find_one({"_id": product_oid})
    if not product or product.get("stock_qty", 0) < qty:
        return RedirectResponse("/products", status_code=303)

    cart = _get_or_create_cart(db, customer_id)
    items = cart.get("items", [])
    existing = next((x for x in items if x["product_id"] == product_oid), None)

    if existing:
        existing["qty"] += qty
    else:
        items.append({"item_id": ObjectId(), "product_id": product_oid, "qty": qty})

    db.carts.update_one({"_id": cart["_id"]}, {"$set": {"items": items}})
    return RedirectResponse("/cart", status_code=303)

@router.get("/cart")
def view_cart(request: Request):
    customer_id = _require_login(request)
    if not customer_id:
        return RedirectResponse("/login", status_code=303)

    db = get_db()
    items = _cart_items(db, customer_id)
    total = sum(item["line_total"] for item in items)

    return templates.TemplateResponse(
        request=request,
        name="cart.html",
        context={"items": items, "total": total, "error": None},
    )

@router.post("/cart/update")
def update_cart_item(
    request: Request,
    cart_item_id: str = Form(...),
    qty: int = Form(...),
):
    customer_id = _require_login(request)
    if not customer_id:
        return RedirectResponse("/login", status_code=303)

    db = get_db()
    item_oid = _oid(cart_item_id)
    if not item_oid:
        return RedirectResponse("/cart", status_code=303)

    update = {"$pull": {"items": {"item_id": item_oid}}} if qty <= 0 else {
        "$set": {"items.$[item].qty": qty}
    }
    if qty <= 0:
        db.carts.update_one({"customer_id": customer_id}, update)
    else:
        db.carts.update_one(
            {"customer_id": customer_id},
            update,
            array_filters=[{"item.item_id": item_oid}],
        )

    return RedirectResponse("/cart", status_code=303)

@router.post("/cart/remove")
def remove_cart_item(request: Request, cart_item_id: str = Form(...)):
    customer_id = _require_login(request)
    if not customer_id:
        return RedirectResponse("/login", status_code=303)

    db = get_db()
    item_oid = _oid(cart_item_id)
    if item_oid:
        db.carts.update_one(
            {"customer_id": customer_id},
            {"$pull": {"items": {"item_id": item_oid}}},
        )
    return RedirectResponse("/cart", status_code=303)
