from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.sql import company as company_model
from app.models.sql import user as user_model
from app.models.sql.repair import (
    RepairOrder as ro_model,
    RepairItem as ri_model,
    Technician as tech_model,
)
from app.schemas import repair as rep_schema
from app.schemas.payment import POSPayment
from app.services import repair_service
from app.core.database import get_db
from app.api.v1.deps import verify_company_membership, require_permission

router = APIRouter()


# Repair Order endpoints
@router.post(
    "/",
    response_model=rep_schema.RepairOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_repair_order(
    repair_order: rep_schema.RepairOrderCreate,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "create")),
):
    """
    Create a new repair order.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    return service.create_repair_order(repair_order, company_id)


@router.post(
    "/simple",
    response_model=rep_schema.RepairOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/simple/",
    response_model=rep_schema.RepairOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_repair_order_simple(
    repair_order: rep_schema.RepairOrderSimpleCreate,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "create")),
):
    """
    Create a new repair order (simplified form).
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    return service.create_repair_order_simple(repair_order, company_id)


@router.post(
    "/with-items/",
    response_model=rep_schema.RepairOrderWithItemsResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_repair_order_with_items(
    repair_order_with_items: rep_schema.RepairOrderWithItemsCreate,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "create")),
):
    """
    Create a new repair order with items.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    return service.create_repair_order_with_items(repair_order_with_items, company_id)


@router.get("/", response_model=List[rep_schema.RepairOrderResponse])
def read_repair_orders(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "read")),
):
    """
    Retrieve repair orders for a company.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    return service.get_repair_orders(company_id, skip=skip, limit=limit)


@router.get(
    "/{repair_order_id}", response_model=rep_schema.RepairOrderWithItemsResponse
)
def read_repair_order(
    repair_order_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "read")),
):
    """
    Retrieve a specific repair order with its items.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    db_repair_order = service.get_repair_order_with_items(repair_order_id, company_id)
    if db_repair_order is None:
        raise HTTPException(status_code=404, detail="Repair order not found")
    return db_repair_order


@router.put("/{repair_order_id}", response_model=rep_schema.RepairOrderResponse)
def update_repair_order(
    repair_order_id: int,
    repair_order: rep_schema.RepairOrderUpdate,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "update")),
):
    """
    Update a repair order.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    db_repair_order = service.update_repair_order(
        repair_order_id, repair_order, company_id
    )
    if db_repair_order is None:
        raise HTTPException(status_code=404, detail="Repair order not found")
    return db_repair_order


@router.post("/{repair_order_id}/items/", response_model=rep_schema.RepairItemResponse)
def create_repair_item(
    repair_order_id: int,
    item: rep_schema.RepairItemCreate,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "create")),
):
    """
    Add an item (service or product) to a repair order.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    db_item = service.create_repair_item(item, repair_order_id, company_id)
    return db_item


@router.delete(
    "/{repair_order_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_repair_item(
    repair_order_id: int,
    item_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "delete")),
):
    """
    Delete a repair item.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    success = service.delete_repair_item(item_id, repair_order_id, company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Repair item not found")


@router.delete("/{repair_order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_repair_order(
    repair_order_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "delete")),
):
    """
    Delete a repair order.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    success = service.delete_repair_order(repair_order_id, company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Repair order not found")
    return None


@router.post("/{repair_order_id}/cancel", response_model=rep_schema.RepairOrderResponse)
def cancel_repair_order(
    repair_order_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "delete")),
):
    """
    Cancel a repair order and its associated invoice if it exists.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    try:
        return service.cancel_repair_order(repair_order_id, company_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error cancelling repair order: {str(e)}"
        )


# Warranty endpoints
@router.post(
    "/{repair_order_id}/apply-warranty/",
    response_model=rep_schema.RepairOrderResponse,
)
def apply_warranty_to_repair_order(
    repair_order_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "update")),
):
    """
    Apply warranty to a repair order.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    db_repair_order = service.apply_warranty(repair_order_id, company_id)
    if db_repair_order is None:
        raise HTTPException(status_code=404, detail="Repair order not found")
    return db_repair_order


@router.post(
    "/warranties/",
    response_model=rep_schema.WarrantyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_warranty(
    warranty: rep_schema.WarrantyCreate,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "create")),
):
    """
    Create a new warranty for a repair order or repair item.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    try:
        return service.create_warranty(warranty, company_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/warranties/", response_model=List[rep_schema.WarrantyResponse])
def read_warranties(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "read")),
):
    """
    Retrieve warranties for a company, optionally filtered by status.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    return service.get_warranties(
        company_id, skip=skip, limit=limit, status_filter=status_filter
    )


@router.get("/warranties/{warranty_id}", response_model=rep_schema.WarrantyResponse)
def read_warranty(
    warranty_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "read")),
):
    """
    Retrieve a specific warranty.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    db_warranty = service.get_warranty_by_id(warranty_id, company_id)
    if db_warranty is None:
        raise HTTPException(status_code=404, detail="Warranty not found")
    return db_warranty


@router.get(
    "/repair-orders/{repair_order_id}/warranties/",
    response_model=List[rep_schema.WarrantyResponse],
)
def read_warranties_by_repair_order(
    repair_order_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "read")),
):
    """
    Retrieve all warranties for a specific repair order.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    return service.get_warranties_by_repair_order(repair_order_id, company_id)


@router.put(
    "/warranties/{warranty_id}/status/",
    response_model=rep_schema.WarrantyResponse,
)
def update_warranty_status(
    warranty_id: int,
    new_status: str,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "update")),
):
    """
    Update warranty status (ACTIVE, EXPIRED, VOID, CLAIMED).
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    try:
        db_warranty = service.update_warranty_status(
            warranty_id, company_id, new_status
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if db_warranty is None:
        raise HTTPException(status_code=404, detail="Warranty not found")
    return db_warranty


@router.post(
    "/warranties/{warranty_id}/claim/",
    response_model=rep_schema.WarrantyResponse,
)
def file_warranty_claim(
    warranty_id: int,
    claim: rep_schema.WarrantyClaim,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "update")),
):
    """
    File a warranty claim for an active warranty.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    try:
        return service.file_warranty_claim(warranty_id, company_id, claim)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/warranties/check-expired/",
    response_model=List[rep_schema.WarrantyResponse],
)
def check_expired_warranties(
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "read")),
):
    """
    Check and mark expired warranties automatically.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    return service.check_expired_warranties(company_id)


@router.delete("/warranties/{warranty_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_warranty(
    warranty_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "delete")),
):
    """
    Delete a warranty.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    success = service.delete_warranty(warranty_id, company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Warranty not found")
    return None


# Invoice generation endpoints
@router.post(
    "/{repair_order_id}/generate-invoice/",
    response_model=rep_schema.RepairOrderWithItemsResponse,
)
def generate_invoice_from_repair_order(
    repair_order_id: int,
    company_id: int,
    payment_data: Optional[POSPayment] = None,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "create")),
):
    """
    Generate an invoice from a completed repair order.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    try:
        db_invoice = service.create_invoice_from_repair(repair_order_id, company_id, payment_data)
        # Return the repair order with updated invoice link
        db_repair_order = service.get_repair_order_with_items(
            repair_order_id, company_id
        )
        return db_repair_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Technician endpoints
@router.post(
    "/technicians/",
    response_model=rep_schema.TechnicianResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_technician(
    technician: rep_schema.TechnicianCreate,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "create")),
):
    """
    Create a new technician.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    return service.create_technician(technician, company_id)


@router.get("/technicians/", response_model=List[rep_schema.TechnicianResponse])
def read_technicians(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "read")),
):
    """
    Retrieve technicians for a company.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    return service.get_technicians(company_id, skip=skip, limit=limit)


@router.get(
    "/technicians/{technician_id}", response_model=rep_schema.TechnicianResponse
)
def read_technician(
    technician_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "read")),
):
    """
    Retrieve a specific technician.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    db_technician = service.get_technician_by_id(technician_id, company_id)
    if db_technician is None:
        raise HTTPException(status_code=404, detail="Technician not found")
    return db_technician


@router.put(
    "/technicians/{technician_id}", response_model=rep_schema.TechnicianResponse
)
def update_technician(
    technician_id: int,
    technician: rep_schema.TechnicianCreate,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "update")),
):
    """
    Update a technician.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    db_technician = service.update_technician(technician_id, technician, company_id)
    if db_technician is None:
        raise HTTPException(status_code=404, detail="Technician not found")
    return db_technician


@router.delete("/technicians/{technician_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_technician(
    technician_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("repair", "delete")),
):
    """
    Delete a technician.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = repair_service.RepairService(db)
    success = service.delete_technician(technician_id, company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Technician not found")
    return None
