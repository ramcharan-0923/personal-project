from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
import schemas

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/products", response_model=schemas.ProductResponse)
def create_product(
    name: str,
    category: str,
    price: float,
    stock: int,
    db: Session = Depends(get_db)
):
    product = models.Product(
        name=name,
        category=category,
        price=price,
        stock=stock
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product

    
@app.get("/")
def home():
    return {"message": "General Store API is working"}

@app.get("/products", response_model=list[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.get("/restock-alert")
def restock_alert(db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(
        models.Product.stock <= 10
    ).all()

    return {
        "message": "Products that need restocking",
        "products": products
    }


@app.get("/products/search/{name}")
def search_product(name: str, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(
        models.Product.name.ilike(f"%{name}%")
    ).all()

    return products



@app.get("/products/category/{category}")
def get_products_by_category(category: str, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(
        models.Product.category == category
    ).all()

    return products




@app.get("/products/{product_id}") 
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if product is None:
        return {"message": "Product not found"}

    return product

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
def update_product(
    product_id: int,
    name: str,
    price: float,
    category: str,
    stock: int,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if product is None:
        return {"message": "Product not found"}

    product.name = name
    product.price = price
    product.category = category
    product.stock = stock

    db.commit()
    db.refresh(product)

    return product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if product is None:
        return {"message": "Product not found"}

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}



@app.get(
    "/products/low-stock/{limit}",
    response_model=list[schemas.ProductResponse]
)
def get_low_stock(limit: int, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(
        models.Product.stock < limit
    ).all()

    return products


@app.post("/customers")
def create_customer(
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db)
):
    new_customer = models.Customer(
        name=customer.name,
        phone=customer.phone
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer

@app.get("/customer")
def get_customers(db:Session = Depends(get_db)):
    return db.query(models.Customer).all()

@app.get("/customers/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if customer is None:
        return {"message": "Customer not found"}

    return customer

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

    db.commit()
    db.refresh(existing_customer)

    return existing_customer

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if customer is None:
        return {"message": "Customer not found"}

    db.delete(customer)
    db.commit()

    return {"message": "Customer deleted successfully"}


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

    
@app.post("/sale-items")
def create_sale_item(
    item: schemas.SaleItemCreate,
    db: Session = Depends(get_db)
):
    new_item = models.SaleItem(
        sale_id=item.sale_id,
        product_id=item.product_id,
        quantity=item.quantity,
        price=item.price
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item    

@app.post("/sale-items")
def create_sale_item(
    item: schemas.SaleItemCreate,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(
        models.Product.id == item.product_id
    ).first()
    sale = db.query(models.Sale).filter(
    models.Sale.id == item.sale_id
).first()

    if sale is None:
        return {"message": "Sale not found"}

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

@app.get("/sale-items")
def get_sale_items(db:Session = Depends(get_db)):
    return db.query(models.SaleItem).all()
@app.get("/sales/{sale_id}")
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(models.Sale).filter(
        models.Sale.id == sale_id
    ).first()

    if sale is None:
        return {"message": "Sale not found"}

    return sale

@app.get("/sales")
def get_sales(db: Session = Depends(get_db)):
    return db.query(models.Sale).all()

@app.get("/sales/{sale_id}/items")
def get_sale_items_by_sale(sale_id: int, db: Session = Depends(get_db)):
    items = db.query(models.SaleItem).filter(
        models.SaleItem.sale_id == sale_id
    ).all()

    return items



@app.get("/sales/{sale_id}/total")
def calculate_sale_total(sale_id: int, db: Session = Depends(get_db)):
    items = db.query(models.SaleItem).filter(
        models.SaleItem.sale_id == sale_id
    ).all()

    if not items:
        return {"message": "No items found for this sale"}

    total = sum(item.quantity * float(item.price) for item in items)

    return {
        "sale_id": sale_id,
        "total_amount": total
    }

@app.put("/sales/{sale_id}/update-total")
def update_sale_total(sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(models.Sale).filter(
        models.Sale.id == sale_id
    ).first()

    if sale is None:
        return {"message": "Sale not found"}

    items = db.query(models.SaleItem).filter(
        models.SaleItem.sale_id == sale_id
    ).all()

    total = sum(item.quantity * float(item.price) for item in items)

    sale.total_amount = total

    db.commit()
    db.refresh(sale)

    return sale

@app.get("/sales/{sale_id}/bill")
def get_bill(sale_id: int, db: Session = Depends(get_db)):
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

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if product is None:
        return {"message": "Product not found"}

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}


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

@app.get("/products/search/{name}")
def search_products(name: str, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(
        models.Product.name.ilike(f"%{name}%")
    ).all()

    return products

@app.get("/products/category/{category}")
def get_products_by_category(
    category: str,
    db: Session = Depends(get_db)
):
    products = db.query(models.Product).filter(
        models.Product.category.ilike(category)
    ).all()

    return products


@app.get("/customers/{customer_id}/sales")
def get_customer_sales(
    customer_id: int,
    db: Session = Depends(get_db)
):
    sales = db.query(models.Sale).filter(
        models.Sale.customer_id == customer_id
    ).all()

    return sales


@app.get("/customers/{customer_id}/total-spent")
def get_customer_total_spent(
    customer_id: int,
    db: Session = Depends(get_db)
):
    sales = db.query(models.Sale).filter(
        models.Sale.customer_id == customer_id
    ).all()

    if not sales:
        return {
            "customer_id": customer_id,
            "total_spent": 0
        }

    total = sum(float(sale.total_amount) for sale in sales)

    return {
        "customer_id": customer_id,
        "total_spent": total
    }    

@app.get("/total-revenue")
def get_total_revenue(db: Session = Depends(get_db)):
    sales = db.query(models.Sale).all()

    total_revenue = sum(
        float(sale.total_amount) for sale in sales
    )

    return {
        "total_revenue": total_revenue
    }
@app.get("/best-selling-products")
def get_best_selling_products(db: Session = Depends(get_db)):
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



@app.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    total_products = db.query(models.Product).count()
    total_customers = db.query(models.Customer).count()
    total_sales = db.query(models.Sale).count()

    sales = db.query(models.Sale).all()
    total_revenue = sum(float(sale.total_amount) for sale in sales)

    return {
        "total_products": total_products,
        "total_customers": total_customers,
        "total_sales": total_sales,
        "total_revenue": total_revenue
    }

