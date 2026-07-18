from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.sql import partners as partner_model
from app.models.sql import company as company_model
from app.schemas import partners as partner_schema
import re


class PartnerService:
    def __init__(self, db: Session):
        self.db = db

    def _validate_nit_dv(self, nit: str, dv: str) -> bool:
        """
        Validate Colombian NIT with verification digit (DV).

        Algoritmo DIAN Modulo 11, longitud variable:
        - Pesos (secuencia extendida de la Orden Administrativa 4 de 1989):
          [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3]
        - Aplicados de DERECHA a IZQUIERDA (digito menos significativo
          recibe el primer peso).  Si el NIT es mas largo que la lista,
          los pesos se ciclan desde el inicio.
        - Regla DV: remainder == 0 -> "0", remainder == 1 -> "K",
          resto -> str(11 - remainder).

        Esta implementacion debe coincidir con el frontend
        (frontend/src/utils/validators.js::calculateDV) para no aceptar
        en backend lo que el cliente rechaza en UI, ni viceversa.
        """
        clean_nit = re.sub(r"[-\s.]", "", nit or "")

        if not clean_nit.isdigit() or len(clean_nit) < 5:
            return False

        if dv is None or len(dv) != 1 or not (dv.isdigit() or dv.upper() == 'K'):
            return False

        dv = dv.upper()

        weights = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3]
        reversed_digits = clean_nit[::-1]
        total = 0
        for i, digit in enumerate(reversed_digits):
            total += int(digit) * weights[i % len(weights)]

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

        if partner.dv and not partner.force_dv and not self._validate_nit_dv(partner.nit, partner.dv):
            raise ValueError("Invalid NIT or verification digit (DV)")

        # Remove force_dv from model dump as it's not in the SQL model
        partner_data = partner.model_dump()
        partner_data.pop('force_dv', None)

        db_partner = partner_model.Partner(
            **partner_data, company_id=company_id
        )
        self.db.add(db_partner)
        
        try:
            self.db.commit()
            self.db.refresh(db_partner)
            
            # Verify the partner was actually saved by querying it back
            verified_partner = (
                self.db.query(partner_model.Partner)
                .filter(partner_model.Partner.id == db_partner.id)
                .first()
            )
            
            if not verified_partner:
                # If verification fails, rollback and raise an error
                self.db.rollback()
                raise ValueError("Partner creation failed: record not persisted in database")
                
            return db_partner
            
        except Exception as e:
            # Ensure we rollback on any error
            self.db.rollback()
            raise ValueError(f"Database error during partner creation: {str(e)}")

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
            if partner.dv and not partner.force_dv and not self._validate_nit_dv(partner.nit, partner.dv):
                raise ValueError("Invalid NIT or verification digit (DV)")

            partner_data = partner.model_dump()
            partner_data.pop('force_dv', None)

            for key, value in partner_data.items():
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
