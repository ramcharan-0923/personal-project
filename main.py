from fastapi import FastAPI, Depends,Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware

import models
import schemas

from database import engine, SessionLocal, Base


app = FastAPI(title="General Store Management API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)


# Database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {"message": "General Store Management API"}


# =========================================================
# PRODUCTS
# =========================================================

# Create product
@app.post("/products", response_model=schemas.ProductResponse)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)
):
    new_product = models.Product(
        name=product.name,
        category=product.category,
        price=product.price,
        stock=product.stock
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# Get all products
@app.get("/products", response_model=list[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()


# Get product by ID
@app.get("/products/{product_id}", response_model=schemas.ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if product is None:
        return {"message": "Product not found"}

    return product


# Update product
@app.put("/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int,
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)
):
    existing_product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if existing_product is None:
        return {"message": "Product not found"}

    existing_product.name = product.name
    existing_product.category = product.category
    existing_product.price = product.price
    existing_product.stock = product.stock

    db.commit()
    db.refresh(existing_product)

    return existing_product


# Delete product
@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if product is None:
        return {"message": "Product not found"}

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}


# Low stock products
@app.get(
    "/products/low-stock/{limit}",
    response_model=list[schemas.ProductResponse]
)
def get_low_stock(
    limit: int,
    db: Session = Depends(get_db)
):
    return db.query(models.Product).filter(
        models.Product.stock < limit
    ).all()


# Restock product
@app.put("/products/{product_id}/restock")
def restock_product(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if product is None:
        return {"message": "Product not found"}

    if quantity <= 0:
        return {"message": "Quantity must be greater than 0"}

    product.stock += quantity

    db.commit()
    db.refresh(product)

    return product


# Search products
@app.get("/products/search/{name}")
def search_products(
    name: str,
    db: Session = Depends(get_db)
):
    return db.query(models.Product).filter(
        models.Product.name.ilike(f"%{name}%")
    ).all()


# Products by category
@app.get("/products/category/{category}")
def get_products_by_category(
    category: str,
    db: Session = Depends(get_db)
):
    return db.query(models.Product).filter(
        models.Product.category.ilike(category)
    ).all()


# =========================================================
# CUSTOMERS
# =========================================================

# Create customer
@app.post("/customers")
def create_customer(
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db)
):
    new_customer = models.Customer(
        name=customer.name,
        phone=customer.phone,
        email=customer.email,
        address=customer.address
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


# Get all customers
@app.get("/customers")
def get_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).all()


# Get customer by ID
@app.get("/customers/{customer_id}")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if customer is None:
        return {"message": "Customer not found"}

    return customer


# Update customer
@app.put("/customers/{customer_id}")
def update_customer(
    customer_id: int,
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db)
):
    existing_customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if existing_customer is None:
        return {"message": "Customer not found"}

    existing_customer.name = customer.name
    existing_customer.phone = customer.phone
    existing_customer.email = customer.email
    existing_customer.address = customer.address

    db.commit()
    db.refresh(existing_customer)

    return existing_customer


# Delete customer
@app.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if customer is None:
        return {"message": "Customer not found"}

    db.delete(customer)
    db.commit()

    return {"message": "Customer deleted successfully"}


# =========================================================
# SALES
# =========================================================

# Create sale
@app.post("/sales")
def create_sale(
    sale: schemas.SaleCreate,
    db: Session = Depends(get_db)
):
    new_sale = models.Sale(
        customer_id=sale.customer_id,
        total_amount=sale.total_amount
    )

    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)

    return new_sale


@app.get("/sales")
def get_sales(db: Session = Depends(get_db)):
    sales = db.query(models.Sale).all()

    result = []

    for sale in sales:
        total = db.query(
            func.sum(models.SaleItem.quantity * models.SaleItem.price)
        ).filter(
            models.SaleItem.sale_id == sale.id
        ).scalar()

        result.append({
            "id": sale.id,
            "total_amount": total or 0
        })

    return result


# Get sale by ID
@app.get("/sales/{sale_id}")
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db)
):
    sale = db.query(models.Sale).filter(
        models.Sale.id == sale_id
    ).first()

    if sale is None:
        return {"message": "Sale not found"}

    return sale


# =========================================================
# SALE ITEMS
# =========================================================

# Create sale item and reduce stock
@app.post("/sale-items")
def create_sale_item(
    item: schemas.SaleItemCreate,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(
        models.Product.id == item.product_id
    ).first()

    if product is None:
        return {"message": "Product not found"}

    sale = db.query(models.Sale).filter(
        models.Sale.id == item.sale_id
    ).first()

    if sale is None:
        return {"message": "Sale not found"}

    if item.quantity <= 0:
        return {"message": "Quantity must be greater than 0"}

    if product.stock < item.quantity:
        return {"message": "Not enough stock"}

    new_item = models.SaleItem(
        sale_id=item.sale_id,
        product_id=item.product_id,
        quantity=item.quantity,
        price=item.price
    )

    product.stock -= item.quantity

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


# Get all sale items
@app.get("/sale-items")
def get_sale_items(db: Session = Depends(get_db)):
    return db.query(models.SaleItem).all()


# Get sale items by sale ID
@app.get("/sales/{sale_id}/items")
def get_sale_items_by_sale(
    sale_id: int,
    db: Session = Depends(get_db)
):
    return db.query(models.SaleItem).filter(
        models.SaleItem.sale_id == sale_id
    ).all()


# =========================================================
# BILLING
# =========================================================

# Calculate sale total
@app.get("/sales/{sale_id}/total")
def calculate_sale_total(
    sale_id: int,
    db: Session = Depends(get_db)
):
    items = db.query(models.SaleItem).filter(
        models.SaleItem.sale_id == sale_id
    ).all()

    if not items:
        return {"message": "No items found for this sale"}

    total = sum(
        item.quantity * float(item.price)
        for item in items
    )

    return {
        "sale_id": sale_id,
        "total_amount": total
    }


# Update sale total
@app.put("/sales/{sale_id}/update-total")
def update_sale_total(
    sale_id: int,
    db: Session = Depends(get_db)
):
    sale = db.query(models.Sale).filter(
        models.Sale.id == sale_id
    ).first()

    if sale is None:
        return {"message": "Sale not found"}

    items = db.query(models.SaleItem).filter(
        models.SaleItem.sale_id == sale_id
    ).all()

    total = sum(
        item.quantity * float(item.price)
        for item in items
    )

    sale.total_amount = total

    db.commit()
    db.refresh(sale)

    return sale


# Generate bill
@app.get("/sales/{sale_id}/bill")
def get_bill(
    sale_id: int,
    db: Session = Depends(get_db)
):
    sale = db.query(models.Sale).filter(
        models.Sale.id == sale_id
    ).first()

    if sale is None:
        return {"message": "Sale not found"}

    customer = db.query(models.Customer).filter(
        models.Customer.id == sale.customer_id
    ).first()

    items = db.query(models.SaleItem).filter(
        models.SaleItem.sale_id == sale_id
    ).all()

    return {
        "bill_id": sale.id,
        "customer": customer,
        "items": items,
        "total_amount": sale.total_amount
    }


# =========================================================
# CUSTOMER SALES
# =========================================================

# Customer sales
@app.get("/customers/{customer_id}/sales")
def get_customer_sales(
    customer_id: int,
    db: Session = Depends(get_db)
):
    return db.query(models.Sale).filter(
        models.Sale.customer_id == customer_id
    ).all()


# Customer total spent
@app.get("/customers/{customer_id}/total-spent")
def get_customer_total_spent(
    customer_id: int,
    db: Session = Depends(get_db)
):
    sales = db.query(models.Sale).filter(
        models.Sale.customer_id == customer_id
    ).all()

    total = sum(
        float(sale.total_amount)
        for sale in sales
    )

    return {
        "customer_id": customer_id,
        "total_spent": total
    }


# =========================================================
# REPORTS
# =========================================================

# Total revenue
@app.get("/total-revenue")
def get_total_revenue(
    db: Session = Depends(get_db)
):
    sales = db.query(models.Sale).all()

    total_revenue = sum(
        float(sale.total_amount)
        for sale in sales
    )

    return {
        "total_revenue": total_revenue
    }


# Best selling products
@app.get("/best-selling-products")
def get_best_selling_products(
    db: Session = Depends(get_db)
):
    items = db.query(models.SaleItem).all()

    product_sales = {}

    for item in items:
        if item.product_id not in product_sales:
            product_sales[item.product_id] = 0

        product_sales[item.product_id] += item.quantity

    result = []

    for product_id, quantity_sold in product_sales.items():
        result.append({
            "product_id": product_id,
            "quantity_sold": quantity_sold
        })

    result.sort(
        key=lambda x: x["quantity_sold"],
        reverse=True
    )

    return result


# Dashboard
@app.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db)
):
    total_products = db.query(models.Product).count()
    total_customers = db.query(models.Customer).count()
    total_sales = db.query(models.Sale).count()

    sales = db.query(models.Sale).all()

    total_revenue = sum(
        float(sale.total_amount)
        for sale in sales
    )

    return {
        "total_products": total_products,
        "total_customers": total_customers,
        "total_sales": total_sales,
        "total_revenue": total_revenue
    }


@app.post("/sale-items")
def create_sale_item(
    sale_id: int,
    product_id: int,
    quantity: int,
    price: float,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if not product:
        return {"message": "Product not found"}

    if product.stock < quantity:
        return {"message": "Not enough stock"}

    sale_item = models.SaleItem(
        sale_id=sale_id,
        product_id=product_id,
        quantity=quantity,
        price=price
    )

    product.stock -= quantity

    db.add(sale_item)
    db.commit()
    db.refresh(sale_item)

    return sale_item

@app.post("/feedback")
def create_feedback(
    customer_id: int,
    message: str,
    rating: int = Query(...,ge=1,le=5),
    db: Session = Depends(get_db)
):
    feedback = models.Feedback(
        customer_id=customer_id,
        message=message,
        rating=rating
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback

@app.get("/feedback")
def get_feedback(db: Session = Depends(get_db)):
    return db.query(models.Feedback).all()