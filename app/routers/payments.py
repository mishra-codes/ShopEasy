from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from app.database import get_db

router = APIRouter()

@router.post("/orders/{order_id}/pay")
def pay_order(
    request: Request,
    order_id: str,
    amount: float = Form(...),
    method: str = Form(...),
):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return RedirectResponse("/login", status_code=303)

    try:
        oid = ObjectId(order_id)
    except Exception:
        return RedirectResponse("/orders", status_code=303)

    db = get_db()
    order = db.orders.find_one({"_id": oid, "customer_id": customer_id})
    if not order:
        return RedirectResponse("/orders", status_code=303)

    if db.payments.find_one({"order_id": oid}):
        return RedirectResponse(f"/orders/{order_id}", status_code=303)

    if round(amount, 2) != round(order["total_amount"], 2):
        return RedirectResponse(f"/orders/{order_id}", status_code=303)

    payment = {
        "order_id": oid,
        "amount": round(amount, 2),
        "method": method,
        "status": "SUCCESS",
        "payment_date": datetime.now(timezone.utc),
    }
    db.payments.insert_one(payment)

    db.orders.update_one(
        {"_id": oid},
        {"$set": {"status": "SHIPPED"}},
    )
    db.order_status_logs.insert_one({
        "order_id": oid,
        "status": "SHIPPED",
        "changed_on": datetime.now(timezone.utc),
    })

    return RedirectResponse(f"/orders/{order_id}", status_code=303)
