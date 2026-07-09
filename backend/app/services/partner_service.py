from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.sql import partners as partner_model
from app.models.sql import company as company_model
from app.schemas import partners as partner_schema
from app.core.config import settings
import re


class PartnerService:
    def __init__(self, db: Session):
        self.db = db

    def _validate_nit_dv(self, nit: str, dv: str) -> bool:
        """
        Validate Colombian NIT with verification digit (DV)
        Rules:
        - Personas Naturales: 6-10 dígitos (Cédula)
        - Personas Jurídicas: 9 dígitos
        """
        clean_nit = re.sub(r"[-\s]", "", nit)

        if not clean_nit.isdigit() or len(clean_nit) < 6:
            return False
        
        if len(clean_nit) > 10:
            return False

        if len(dv) != 1 or not (dv.isdigit() or dv.upper() == 'K'):
            return False

        dv = dv.upper()

        nit_int = int(clean_nit)
        if nit_int < 100000:
            return False

        total = 0
        weights = [71, 69, 67, 59, 53, 47, 43, 41, 37, 31, 29, 23, 19, 17, 13, 7, 5, 3, 2]

        # Aplicar pesos de izquierda a derecha (algoritmo colombiano Módulo 11)
        for i, digit in enumerate(clean_nit):
            if i >= len(weights):
                break
            total += int(digit) * weights[i]

        remainder = total % 11

        if remainder == 0:
            dv_expected = "0"
        elif remainder == 1:
            dv_expected = "K"
        else:
            dv_expected = str(11 - remainder)

        return dv_expected == dv

    def create_partner(
        self, partner: partner_schema.PartnerCreate, company_id: int
    ) -> partner_model.Partner:
        # Verify company exists
        db_company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not db_company:
            raise ValueError("Company not found")

        if partner.dv and not self._validate_nit_dv(partner.nit, partner.dv):
            raise ValueError("Invalid NIT or verification digit (DV)")

        db_partner = partner_model.Partner(
            **partner.model_dump(), company_id=company_id
        )
        self.db.add(db_partner)
        self.db.commit()
        self.db.refresh(db_partner)
        return db_partner

    def get_partners(
        self, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[partner_model.Partner]:
        return (
            self.db.query(partner_model.Partner)
            .filter(partner_model.Partner.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_partner_by_id(
        self, partner_id: int, company_id: int
    ) -> Optional[partner_model.Partner]:
        return (
            self.db.query(partner_model.Partner)
            .filter(
                partner_model.Partner.id == partner_id,
                partner_model.Partner.company_id == company_id,
            )
            .first()
        )

    def update_partner(
        self, partner_id: int, partner: partner_schema.PartnerCreate, company_id: int
    ) -> Optional[partner_model.Partner]:
        db_partner = self.get_partner_by_id(partner_id, company_id)
        if db_partner:
            # Validate NIT and DV if they are being updated
            if partner.dv and not self._validate_nit_dv(partner.nit, partner.dv):
                raise ValueError("Invalid NIT or verification digit (DV)")

            for key, value in partner.model_dump().items():
                setattr(db_partner, key, value)
            self.db.commit()
            self.db.refresh(db_partner)
        return db_partner

    def delete_partner(self, partner_id: int, company_id: int) -> bool:
        db_partner = self.get_partner_by_id(partner_id, company_id)
        if db_partner:
            self.db.delete(db_partner)
            self.db.commit()
            return True
        return False
