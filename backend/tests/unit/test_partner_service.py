import pytest
from app.services.partner_service import PartnerService
from app.schemas.partners import PartnerCreate


class TestNITValidation:
    """Anclas del algoritmo DIAN Modulo 11 (longitud variable).

    Los pares NIT/DV a continuacion se calcularon con el mismo algoritmo
    unificado que el frontend (frontend/src/utils/validators.js::calculateDV),
    de modo que backend y UI no puedan discrepar.  Cubren los tres casos
    especiales de remainder: 0 (DV="0"), 1 (DV="K") y 2..10 (DV=11-r).
    """

    def test_dv_regular_small(self):
        service = PartnerService(None)
        assert service._validate_nit_dv("100000", "1") is True

    def test_dv_zero(self):
        # remainder == 0 -> DV "0"
        service = PartnerService(None)
        assert service._validate_nit_dv("100009", "0") is True

    def test_dv_k_case(self):
        # remainder == 1 -> DV "K" (regla DIAN)
        service = PartnerService(None)
        assert service._validate_nit_dv("100007", "K") is True

    def test_dv_k_case_9_digits(self):
        # Caso K con NIT de 9 digitos (formato juridica)
        service = PartnerService(None)
        assert service._validate_nit_dv("362950628", "K") is True

    def test_dv_zero_9_digits(self):
        service = PartnerService(None)
        assert service._validate_nit_dv("786579303", "0") is True

    def test_dv_regular_9_digits(self):
        service = PartnerService(None)
        assert service._validate_nit_dv("219540831", "6") is True

    def test_invalid_dv_rejects(self):
        # DV correcto seria 8; probamos 9 (debe fallar)
        service = PartnerService(None)
        assert service._validate_nit_dv("900123456", "9") is False

    def test_invalid_nit_characters(self):
        service = PartnerService(None)
        assert service._validate_nit_dv("ABC123", "1") is False

    def test_empty_nit(self):
        service = PartnerService(None)
        assert service._validate_nit_dv("", "0") is False

    def test_nit_with_dots_and_spaces(self):
        # Cleanup debe aceptar formato formateado "900.123.456"
        service = PartnerService(None)
        assert service._validate_nit_dv("900.123.456", "8") is True

    def test_lowercase_dv_k(self):
        # DV k minuscula debe validarse igual que K
        service = PartnerService(None)
        assert service._validate_nit_dv("100007", "k") is True


class TestPartnerService:
    def test_create_partner_valid(self, db_session, test_company):
        service = PartnerService(db_session)
        partner_data = PartnerCreate(
            nit="900123456",
            dv="8",
            name="Test Partner S.A.S",
            partner_type="CUSTOMER",
            responsibility_fiscal="RESPONSABLE IVA",
            email="partner@test.com",
            phone="3001234567",
            address="Calle 10 #20-30",
        )
        partner = service.create_partner(partner_data, test_company.id)
        assert partner.nit == "900123456"
        assert partner.dv == "8"
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

    def test_create_partner_with_dv_k(self, db_session, test_company):
        # Cubre el caso especial remainder==1 -> "K"
        service = PartnerService(db_session)
        partner_data = PartnerCreate(
            nit="100007",
            dv="K",
            name="Partner con DV K",
            partner_type="CUSTOMER",
            responsibility_fiscal="NO RESPONSABLE",
        )
        partner = service.create_partner(partner_data, test_company.id)
        assert partner.dv == "K"