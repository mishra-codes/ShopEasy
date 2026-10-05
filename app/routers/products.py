from fastapi import APIRouter, Request
from app.database import get_db
from app.templating import templates

router = APIRouter()

def product_view(doc):
    return {
        "product_id": str(doc["_id"]),
        "name": doc["name"],
        "category": doc.get("category", ""),
        "price": doc["price"],
        "stock_qty": doc.get("stock_qty", 0),
    }

@router.get("/")
@router.get("/products")
def list_products(request: Request):
    db = get_db()
    products = [
        product_view(p)
        for p in db.products.find().sort([("category", 1), ("name", 1)])
    ]
    return templates.TemplateResponse(
        request=request, name="products.html", context={"products": products}
    )
