import pytest
from app.services.electronic_billing_service import ElectronicBillingService
from decimal import Decimal


class TestElectronicBillingService:
    def test_generate_cufe_deterministic(self, db_session):
        service = ElectronicBillingService(db_session)
        cufe1 = service.generate_cufe(
            company_nit="900123456",
            company_dv="7",
            invoice_number="FE-001",
            invoice_date="2026-04-01T12:00:00",
            invoice_total=Decimal("119000.00"),
            company_regimen="COMUN",
        )
        cufe2 = service.generate_cufe(
            company_nit="900123456",
            company_dv="7",
            invoice_number="FE-001",
            invoice_date="2026-04-01T12:00:00",
            invoice_total=Decimal("119000.00"),
            company_regimen="COMUN",
        )
        assert cufe1 == cufe2

    def test_generate_cufe_different_inputs(self, db_session):
        service = ElectronicBillingService(db_session)
        cufe1 = service.generate_cufe(
            company_nit="900123456",
            company_dv="7",
            invoice_number="FE-001",
            invoice_date="2026-04-01T12:00:00",
            invoice_total=Decimal("119000.00"),
            company_regimen="COMUN",
        )
        cufe2 = service.generate_cufe(
            company_nit="900123456",
            company_dv="7",
            invoice_number="FE-002",
            invoice_date="2026-04-01T12:00:00",
            invoice_total=Decimal("119000.00"),
            company_regimen="COMUN",
        )
        assert cufe1 != cufe2

    def test_generate_cufe_length(self, db_session):
        service = ElectronicBillingService(db_session)
        cufe = service.generate_cufe(
            company_nit="900123456",
            company_dv="7",
            invoice_number="FE-001",
            invoice_date="2026-04-01T12:00:00",
            invoice_total=Decimal("119000.00"),
            company_regimen="COMUN",
        )
        assert len(cufe) == 96

    def test_format_date(self, db_session):
        from datetime import datetime

        service = ElectronicBillingService(db_session)
        dt = datetime(2026, 4, 1, 12, 30, 45)
        formatted = service._format_date(dt)
        assert formatted == "2026-04-01T12:30:45"

    def test_format_decimal(self, db_session):
        service = ElectronicBillingService(db_session)
        assert service._format_decimal(Decimal("119000.5")) == "119000.50"
        assert service._format_decimal(Decimal("100")) == "100.00"
