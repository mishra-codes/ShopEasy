import bcrypt as _bcrypt
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from pymongo.errors import DuplicateKeyError

from app.database import get_db
from app.templating import templates

router = APIRouter()

@router.get("/register")
def register_form(request: Request):
    return templates.TemplateResponse(
        request=request, name="register.html", context={"error": None}
    )

@router.post("/register")
def register_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    address: str = Form(...),
):
    db = get_db()
    password_hash = _bcrypt.hashpw(password[:72].encode(), _bcrypt.gensalt()).decode()

    try:
        result = db.customers.insert_one({
            "name": name,
            "email": email.lower().strip(),
            "phone": phone,
            "password_hash": password_hash,
            "address": address,
        })
    except DuplicateKeyError:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Email is already registered"},
        )

    return RedirectResponse("/login", status_code=303)

@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html", context={"error": None}
    )

@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    db = get_db()
    customer = db.customers.find_one({"email": email.lower().strip()})

    if not customer or not _bcrypt.checkpw(
        password[:72].encode(), customer["password_hash"].encode()
    ):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Invalid email or password"},
        )

    request.session["customer_id"] = str(customer["_id"])
    request.session["customer_name"] = customer["name"]
    return RedirectResponse("/products", status_code=303)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
