from app.models.sql import company as company_model
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.sql.partners import Partner
from app.models.sql.inventory import Product
from app.models.sql.invoicing import Invoice
from app.models.sql.repair import RepairOrder
from app.models.sql.user import User
from app.schemas.dashboard import DashboardStats
from app.core.database import get_db
from app.api.v1.deps import get_current_active_user, verify_company_membership

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get dashboard statistics for a specific company.
    """
    partners_count = db.query(Partner).filter(Partner.company_id == company_id).count()
    products_count = db.query(Product).filter(Product.company_id == company_id).count()
    invoices_count = db.query(Invoice).filter(Invoice.company_id == company_id).count()
    repairs_count = db.query(RepairOrder).filter(RepairOrder.company_id == company_id).count()

    return DashboardStats(
        partners=partners_count,
        products=products_count,
        invoices=invoices_count,
        repairs=repairs_count
    )
