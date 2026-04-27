import pytest
from app.services.partner_service import PartnerService
from app.schemas.partners import PartnerCreate


class TestNITValidation:
    def test_valid_nit_with_dv(self):
        service = PartnerService(None)
        assert service._validate_nit_dv("900123456", "7") is True

    def test_invalid_dv(self):
        service = PartnerService(None)
        assert service._validate_nit_dv("900123456", "9") is False

    def test_calculate_dv_known_value(self):
        service = PartnerService(None)
        assert service._validate_nit_dv("900123456", "7") is True

    def test_calculate_dv_another_known_value(self):
        service = PartnerService(None)
        assert service._validate_nit_dv("800123456", "1") is True

    def test_invalid_nit_characters(self):
        service = PartnerService(None)
        assert service._validate_nit_dv("ABC123", "1") is False

    def test_empty_nit(self):
        service = PartnerService(None)
        assert service._validate_nit_dv("", "0") is False


class TestPartnerService:
    def test_create_partner_valid(self, db_session, test_company):
        service = PartnerService(db_session)
        partner_data = PartnerCreate(
            nit="800123456",
            dv="1",
            name="Test Partner S.A.S",
            partner_type="CUSTOMER",
            responsibility_fiscal="RESPONSABLE IVA",
            email="partner@test.com",
            phone="3001234567",
            address="Calle 10 #20-30",
        )
        partner = service.create_partner(partner_data, test_company.id)
        assert partner.nit == "800123456"
        assert partner.company_id == test_company.id

    def test_create_partner_invalid_dv(self, db_session, test_company):
        service = PartnerService(db_session)
        partner_data = PartnerCreate(
            nit="900123456",
            dv="9",
            name="Test Partner",
            partner_type="CUSTOMER",
            responsibility_fiscal="RESPONSABLE IVA",
        )
        with pytest.raises(ValueError, match="DV"):
            service.create_partner(partner_data, test_company.id)
