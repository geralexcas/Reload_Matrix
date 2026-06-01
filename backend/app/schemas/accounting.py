from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


# Chart of Accounts Schema
class ChartOfAccountsBase(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    account_type: str  # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE, COST
    is_active: bool = True
    parent_id: Optional[int] = None

    @field_validator("account_type")
    @classmethod
    def account_type_must_be_valid(cls, v):
        allowed = ["ASSET", "LIABILITY", "EQUITY", "REVENUE", "EXPENSE", "COST"]
        if v not in allowed:
            raise ValueError(f"Account type must be one of {allowed}")
        return v

    model_config = {"from_attributes": True}


class ChartOfAccountsCreate(ChartOfAccountsBase):
    pass


class ChartOfAccountsResponse(ChartOfAccountsBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Journal Entry Schema
class JournalEntryBase(BaseModel):
    entry_date: datetime
    description: str = Field(..., max_length=500)
    reference: Optional[str] = Field(None, max_length=100)
    is_posted: bool = False

    model_config = {"from_attributes": True}


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryResponse(JournalEntryBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Journal Entry Line Schema
class JournalEntryLineBase(BaseModel):
    account_id: int
    debit_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    credit_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    description: Optional[str] = Field(None, max_length=255)

    @field_validator("debit_amount", "credit_amount")
    @classmethod
    def amounts_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("Amounts must be non-negative")
        return v

    model_config = {"from_attributes": True}


class JournalEntryLineCreate(JournalEntryLineBase):
    pass


class JournalEntryLineResponse(JournalEntryLineBase):
    id: int
    journal_entry_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# Journal Entry with Lines (for creating a journal entry with lines in one go)
class JournalEntryWithLinesCreate(BaseModel):
    entry_date: datetime
    description: str = Field(..., max_length=500)
    reference: Optional[str] = Field(None, max_length=100)
    lines: List[JournalEntryLineCreate]

    @field_validator("lines")
    @classmethod
    def must_have_at_least_one_line(cls, v):
        if len(v) < 1:
            raise ValueError("Journal entry must have at least one line")
        return v

    model_config = {"from_attributes": True}


# For responses, we might want to include the lines
class JournalEntryWithLinesResponse(JournalEntryResponse):
    lines: List[JournalEntryLineResponse] = []

    model_config = {"from_attributes": True}


class JournalEntryLineDetail(JournalEntryLineBase):
    id: int
    account_code: str
    account_name: str

    model_config = {"from_attributes": True}


class JournalEntryLinesDetailResponse(BaseModel):
    entry_id: int
    entry_date: datetime
    description: str
    reference: Optional[str] = None
    is_posted: bool
    lines: List[JournalEntryLineDetail] = []
    total_debit: Decimal = Decimal("0.00")
    total_credit: Decimal = Decimal("0.00")
    is_balanced: bool = False

    model_config = {"from_attributes": True}


class TrialBalanceAccount(BaseModel):
    account_id: int
    account_code: str
    account_name: str
    account_type: str
    debit_balance: Decimal = Decimal("0.00")
    credit_balance: Decimal = Decimal("0.00")
    net_balance: Decimal = Decimal("0.00")

    model_config = {"from_attributes": True}


class TrialBalanceResponse(BaseModel):
    company_id: int
    period: str
    generated_at: datetime
    accounts: List[TrialBalanceAccount] = []
    total_debit_balance: Decimal = Decimal("0.00")
    total_credit_balance: Decimal = Decimal("0.00")
    is_balanced: bool = False
    difference: Decimal = Decimal("0.00")

    model_config = {"from_attributes": True}


# Libro Mayor Schema
class MayorAccountLine(BaseModel):
    entry_date: datetime
    reference: Optional[str] = None
    description: Optional[str] = None
    debit: Decimal = Decimal("0.00")
    credit: Decimal = Decimal("0.00")
    balance: Decimal = Decimal("0.00")

    model_config = {"from_attributes": True}


class MayorAccountSummary(BaseModel):
    account_code: str
    account_name: str
    account_type: str
    initial_balance: Decimal = Decimal("0.00")
    total_debits: Decimal = Decimal("0.00")
    total_credits: Decimal = Decimal("0.00")
    final_balance: Decimal = Decimal("0.00")
    lines: List[MayorAccountLine] = []

    model_config = {"from_attributes": True}


class MayorResponse(BaseModel):
    company_id: int
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    accounts: List[MayorAccountSummary] = []
    grand_total_debits: Decimal = Decimal("0.00")
    grand_total_credits: Decimal = Decimal("0.00")

    model_config = {"from_attributes": True}


# Libro de Ventas Schema
class SalesBookEntry(BaseModel):
    invoice_id: int
    invoice_number: str
    invoice_date: datetime
    partner_nit: Optional[str] = None
    partner_name: str
    partner_responsibility: Optional[str] = None
    base_iva_19: Decimal = Decimal("0.00")
    iva_19: Decimal = Decimal("0.00")
    base_iva_5: Decimal = Decimal("0.00")
    iva_5: Decimal = Decimal("0.00")
    base_no_iva: Decimal = Decimal("0.00")
    total_iva: Decimal = Decimal("0.00")
    base_retencion: Decimal = Decimal("0.00")
    retencion_iva: Decimal = Decimal("0.00")
    retencion_fuente: Decimal = Decimal("0.00")
    total_invoice: Decimal = Decimal("0.00")
    estado_dian: Optional[str] = None

    model_config = {"from_attributes": True}


class SalesBookResponse(BaseModel):
    company_id: int
    company_name: str
    company_nit: str
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    entries: List[SalesBookEntry] = []
    totals: dict = {}

    model_config = {"from_attributes": True}


# Libro de Compras Schema
class PurchaseBookEntry(BaseModel):
    invoice_id: int
    invoice_number: str
    invoice_date: datetime
    partner_nit: Optional[str] = None
    partner_name: str
    partner_responsibility: Optional[str] = None
    base_iva_19: Decimal = Decimal("0.00")
    iva_19: Decimal = Decimal("0.00")
    base_iva_5: Decimal = Decimal("0.00")
    iva_5: Decimal = Decimal("0.00")
    base_no_iva: Decimal = Decimal("0.00")
    total_iva: Decimal = Decimal("0.00")
    base_retencion: Decimal = Decimal("0.00")
    retencion_iva: Decimal = Decimal("0.00")
    retencion_fuente: Decimal = Decimal("0.00")
    total_invoice: Decimal = Decimal("0.00")
    estado_dian: Optional[str] = None

    model_config = {"from_attributes": True}


class PurchaseBookResponse(BaseModel):
    company_id: int
    company_name: str
    company_nit: str
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    entries: List[PurchaseBookEntry] = []
    totals: dict = {}

    model_config = {"from_attributes": True}


# Declaración de IVA Schema (Formulario 300 DIAN)
class IVASectionItem(BaseModel):
    concept: str
    base: Decimal = Decimal("0.00")
    tax_amount: Decimal = Decimal("0.00")

    model_config = {"from_attributes": True}


class IVADeclarationResponse(BaseModel):
    company_id: int
    company_name: str
    company_nit: str
    company_dv: str
    regimen: str
    period: str
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    iva_generado: List[IVASectionItem] = []
    total_iva_generado: Decimal = Decimal("0.00")
    iva_soportado: List[IVASectionItem] = []
    total_iva_soportado: Decimal = Decimal("0.00")
    iva_a_pagar: Decimal = Decimal("0.00")
    iva_a_favor: Decimal = Decimal("0.00")
    es_a_pagar: bool = True

    model_config = {"from_attributes": True}


# Reporte de Retenciones Schema
class RetencionEntry(BaseModel):
    invoice_id: int
    invoice_number: str
    invoice_date: datetime
    partner_nit: Optional[str] = None
    partner_name: str
    concept: str
    base_retencion: Decimal = Decimal("0.00")
    tarifa: Decimal = Decimal("0.00")
    valor_retencion: Decimal = Decimal("0.00")
    invoice_type: str

    model_config = {"from_attributes": True}


class RetencionesResponse(BaseModel):
    company_id: int
    company_name: str
    company_nit: str
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    entries: List[RetencionEntry] = []
    totals: dict = {}

    model_config = {"from_attributes": True}


# Reporte de Ingresos Schema
class IngresoEntry(BaseModel):
    source: str
    invoice_id: Optional[int] = None
    invoice_number: Optional[str] = None
    date: datetime
    partner_name: Optional[str] = None
    base: Decimal = Decimal("0.00")
    tax_amount: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")

    model_config = {"from_attributes": True}


class IngresosResponse(BaseModel):
    company_id: int
    company_name: str
    company_nit: str
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    entries: List[IngresoEntry] = []
    totals: dict = {}

    model_config = {"from_attributes": True}


# Reporte de Patrimonio Schema
class PatrimonioAccount(BaseModel):
    account_code: str
    account_name: str
    balance: Decimal = Decimal("0.00")

    model_config = {"from_attributes": True}


class PatrimonioResponse(BaseModel):
    company_id: int
    company_name: str
    company_nit: str
    cut_date: Optional[datetime] = None
    activos: List[PatrimonioAccount] = []
    total_activos: Decimal = Decimal("0.00")
    pasivos: List[PatrimonioAccount] = []
    total_pasivos: Decimal = Decimal("0.00")
    patrimonio: Decimal = Decimal("0.00")

    model_config = {"from_attributes": True}


# Estado de Resultados Schema
class EstadoResultadosAccount(BaseModel):
    account_code: str
    account_name: str
    balance: Decimal = Decimal("0.00")

    model_config = {"from_attributes": True}


class EstadoResultadosResponse(BaseModel):
    company_id: int
    company_name: str
    company_nit: str
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    ingresos: List[EstadoResultadosAccount] = []
    total_ingresos: Decimal = Decimal("0.00")
    costos: List[EstadoResultadosAccount] = []
    total_costos: Decimal = Decimal("0.00")
    gastos: List[EstadoResultadosAccount] = []
    total_gastos: Decimal = Decimal("0.00")
    utilidad_bruta: Decimal = Decimal("0.00")
    utilidad_neta: Decimal = Decimal("0.00")

    model_config = {"from_attributes": True}


# Balance General Schema
class BalanceGeneralAccount(BaseModel):
    account_code: str
    account_name: str
    balance: Decimal = Decimal("0.00")

    model_config = {"from_attributes": True}


class BalanceGeneralResponse(BaseModel):
    company_id: int
    company_name: str
    company_nit: str
    cut_date: Optional[datetime] = None
    activos: List[BalanceGeneralAccount] = []
    total_activos: Decimal = Decimal("0.00")
    pasivos: List[BalanceGeneralAccount] = []
    total_pasivos: Decimal = Decimal("0.00")
    patrimonio: List[BalanceGeneralAccount] = []
    total_patrimonio: Decimal = Decimal("0.00")
    ecuacion_verificada: bool = False

    model_config = {"from_attributes": True}


# Formulario 350 - Declaración de Renta
class Formulario350Response(BaseModel):
    formulario: str = "350"
    periodo_gravable: int
    company_id: int
    company_name: str
    company_nit: str
    regimen: str
    ingresos_ordinarios: Decimal = Decimal("0.00")
    costos: Decimal = Decimal("0.00")
    deducciones: Decimal = Decimal("0.00")
    renta_liquida: Decimal = Decimal("0.00")
    tarifa_aplicable: float = 0.0
    impuesto_renta: Decimal = Decimal("0.00")
    detalle_ingresos: List[EstadoResultadosAccount] = []
    detalle_costos: List[EstadoResultadosAccount] = []
    detalle_gastos: List[EstadoResultadosAccount] = []

    model_config = {"from_attributes": True}
