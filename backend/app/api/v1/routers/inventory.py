from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.sql import company as company_model
from app.models.sql import user as user_model
from app.models.sql.inventory import Product as prod_model
from app.schemas import inventory as inv_schema
from app.services import inventory_service
from app.core.database import get_db
from app.api.v1.deps import get_current_user

router = APIRouter()


# Product endpoints
@router.post(
    "", response_model=inv_schema.ProductResponse, status_code=status.HTTP_201_CREATED
)
@router.post(
    "/", response_model=inv_schema.ProductResponse, status_code=status.HTTP_201_CREATED
)
@router.post(
    "/products", response_model=inv_schema.ProductResponse, status_code=status.HTTP_201_CREATED
)
def create_product(
    product: inv_schema.ProductCreate,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Create a new product.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = inventory_service.InventoryService(db)
    return service.create_product(product, company_id)


@router.post("/bulk", response_model=List[inv_schema.ProductResponse])
def bulk_create_products(
    bulk_data: inv_schema.ProductBulkCreate,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Create multiple products (serialized).
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = inventory_service.InventoryService(db)
    try:
        return service.bulk_create_products(bulk_data, company_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[inv_schema.ProductResponse])
def read_products(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Retrieve products for a company.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = inventory_service.InventoryService(db)
    return service.get_products(company_id, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=inv_schema.ProductResponse)
def read_product(
    product_id: int,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Retrieve a specific product.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = inventory_service.InventoryService(db)
    db_product = service.get_product_by_id(product_id, company_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.put("/{product_id}", response_model=inv_schema.ProductResponse)
def update_product(
    product_id: int,
    product: inv_schema.ProductCreate,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Update a product.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = inventory_service.InventoryService(db)
    db_product = service.update_product(product_id, product, company_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Delete a product.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = inventory_service.InventoryService(db)
    try:
        success = service.delete_product(product_id, company_id)
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return None


# Additional endpoints for barcode scanning and stock management
@router.get("/barcode/{barcode}", response_model=inv_schema.ProductResponse)
def get_product_by_barcode(
    barcode: str,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Get product by barcode for scanning functionality.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = inventory_service.InventoryService(db)
    db_product = service.get_product_by_barcode(barcode, company_id)
    if db_product is None:
        raise HTTPException(
            status_code=404, detail="Product not found with this barcode"
        )
    return db_product


@router.get("/low-stock/", response_model=List[inv_schema.ProductResponse])
def get_low_stock_products(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Get products with stock at or below minimum level.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = inventory_service.InventoryService(db)
    return service.get_low_stock_products(company_id, skip=skip, limit=limit)


@router.patch("/{product_id}/stock", response_model=inv_schema.ProductResponse)
def adjust_stock_level(
    product_id: int,
    adjustment: int,  # Can be positive or negative
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Adjust stock level by a specified amount.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = inventory_service.InventoryService(db)
    db_product = service.adjust_stock_level(product_id, adjustment, company_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.post("/{product_id}/deduct-stock", response_model=inv_schema.ProductResponse)
def deduct_stock(
    product_id: int,
    quantity: float,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Deduct stock for a product. Used when parts are consumed in repairs or sales.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = inventory_service.InventoryService(db)
    try:
        db_product = service.deduct_stock(product_id, quantity, company_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.get("/{product_id}/check-stock")
def check_stock_availability(
    product_id: int,
    quantity: float,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Check if there is enough stock for a product.
    Returns: {"available": true/false, "current_stock": number, "requested": number}
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = inventory_service.InventoryService(db)
    db_product = service.get_product_by_id(product_id, company_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    available = service.check_stock_availability(product_id, quantity, company_id)
    return {
        "available": available,
        "current_stock": db_product.stock_level,
        "requested": quantity,
        "product_name": db_product.name,
    }
