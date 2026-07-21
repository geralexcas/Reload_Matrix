from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.models.sql.dian_billing import DianBillingRange
from app.schemas.dian_billing import DianBillingRangeCreate, DianBillingRangeResponse


class DianBillingRangeService:
    def __init__(self, db: Session):
        self.db = db

    def create_range(
        self, range_data: DianBillingRangeCreate, company_id: int, commit: bool = False
    ) -> DianBillingRange:
        dr = DianBillingRange(
            **range_data.model_dump(),
            company_id=company_id,
            next_number=range_data.from_number,
        )
        self.db.add(dr)
        self.db.flush()
        if commit:
            self.db.commit()
        self.db.refresh(dr)
        return dr

    def get_ranges(self, company_id: int) -> List[DianBillingRange]:
        return (
            self.db.query(DianBillingRange)
            .filter(DianBillingRange.company_id == company_id)
            .order_by(DianBillingRange.created_at.desc())
            .all()
        )

    def get_active_ranges(self, company_id: int) -> List[DianBillingRange]:
        return (
            self.db.query(DianBillingRange)
            .filter(
                DianBillingRange.company_id == company_id,
                DianBillingRange.is_active == True,
            )
            .order_by(DianBillingRange.created_at.desc())
            .all()
        )

    def get_next_number(self, company_id: int, prefix: str) -> Optional[int]:
        dr = (
            self.db.query(DianBillingRange)
            .filter(
                DianBillingRange.company_id == company_id,
                DianBillingRange.prefix == prefix,
                DianBillingRange.is_active == True,
                DianBillingRange.next_number <= DianBillingRange.to_number,
            )
            .first()
        )
        if not dr:
            return None
        return dr.next_number

    def consume_number(self, range_id: int, company_id: int, commit: bool = False) -> bool:
        dr = (
            self.db.query(DianBillingRange)
            .filter(
                DianBillingRange.id == range_id,
                DianBillingRange.company_id == company_id,
            )
            .first()
        )
        if not dr or dr.next_number > dr.to_number:
            return False
        dr.next_number += 1
        if dr.next_number > dr.to_number:
            dr.is_active = False
        if commit:
            self.db.commit()
        return True

    def validate_range_available(
        self, company_id: int, prefix: str, number: int
    ) -> bool:
        dr = (
            self.db.query(DianBillingRange)
            .filter(
                DianBillingRange.company_id == company_id,
                DianBillingRange.prefix == prefix,
                DianBillingRange.is_active == True,
                DianBillingRange.from_number <= number,
                DianBillingRange.to_number >= number,
            )
            .first()
        )
        return dr is not None

    def get_range_by_id(
        self, range_id: int, company_id: int
    ) -> Optional[DianBillingRange]:
        return (
            self.db.query(DianBillingRange)
            .filter(
                DianBillingRange.id == range_id,
                DianBillingRange.company_id == company_id,
            )
            .first()
        )

    def update_range(
        self, range_id: int, range_data: DianBillingRangeCreate, company_id: int, commit: bool = False
    ) -> Optional[DianBillingRange]:
        dr = self.get_range_by_id(range_id, company_id)
        if not dr:
            return None
        for key, value in range_data.model_dump().items():
            setattr(dr, key, value)
        self.db.flush()
        if commit:
            self.db.commit()
        self.db.refresh(dr)
        return dr

    def deactivate_range(self, range_id: int, company_id: int, commit: bool = False) -> bool:
        dr = self.get_range_by_id(range_id, company_id)
        if not dr:
            return False
        dr.is_active = False
        if commit:
            self.db.commit()
        return True
