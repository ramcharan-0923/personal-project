from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    category: str
    price: float
    stock: int


class ProductResponse(ProductCreate):
    id: int

    class Config:
        from_attributes = True


class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: str | None = None
    address: str | None = None


class SaleCreate(BaseModel):
    customer_id: int
    total_amount: float


class SaleItemCreate(BaseModel):
    sale_id: int
    product_id: int
    quantity: int
    price: float

