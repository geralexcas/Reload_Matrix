from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.sql import company as company_model, user as user_model
from app.schemas import accounting as accounting_schema
from app.services import accounting_service
from app.core.database import get_db
from app.api.v1.deps import get_current_user

router = APIRouter()


# Chart of Accounts endpoints
@router.post(
    "/chart-of-accounts/",
    response_model=accounting_schema.ChartOfAccountsResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_chart_of_accounts(
    coa: accounting_schema.ChartOfAccountsCreate,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Create a new chart of accounts entry.
    In a real system, you would want to verify that the user belongs to the company.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    return service.create_chart_of_accounts(coa, company_id)


@router.get(
    "/chart-of-accounts/",
    response_model=List[accounting_schema.ChartOfAccountsResponse],
)
def read_chart_of_accounts(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Retrieve chart of accounts for a company.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    return service.get_chart_of_accounts(company_id, skip=skip, limit=limit)


@router.get(
    "/chart-of-accounts/{coa_id}",
    response_model=accounting_schema.ChartOfAccountsResponse,
)
def read_chart_of_account(
    coa_id: int,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Retrieve a specific chart of accounts entry.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    db_coa = service.get_chart_of_account_by_id(coa_id, company_id)
    if db_coa is None:
        raise HTTPException(status_code=404, detail="Chart of accounts not found")
    return db_coa


@router.put(
    "/chart-of-accounts/{coa_id}",
    response_model=accounting_schema.ChartOfAccountsResponse,
)
def update_chart_of_account(
    coa_id: int,
    coa: accounting_schema.ChartOfAccountsCreate,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Update a chart of accounts entry.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    db_coa = service.update_chart_of_accounts(coa_id, coa, company_id)
    if db_coa is None:
        raise HTTPException(status_code=404, detail="Chart of accounts not found")
    return db_coa


@router.delete("/chart-of-accounts/{coa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chart_of_account(
    coa_id: int,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Delete a chart of accounts entry.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    success = service.delete_chart_of_accounts(coa_id, company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chart of accounts not found")
    return None


# Journal Entry endpoints
@router.post(
    "/journal-entries/",
    response_model=accounting_schema.JournalEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_journal_entry(
    je: accounting_schema.JournalEntryCreate,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Create a new journal entry.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    return service.create_journal_entry(je, company_id)


@router.post(
    "/journal-entries/with-lines/",
    response_model=accounting_schema.JournalEntryWithLinesResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_journal_entry_with_lines(
    je_with_lines: accounting_schema.JournalEntryWithLinesCreate,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Create a new journal entry with lines.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    return service.create_journal_entry_with_lines(je_with_lines, company_id)


@router.get(
    "/journal-entries/", response_model=List[accounting_schema.JournalEntryResponse]
)
def read_journal_entries(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Retrieve journal entries for a company.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    return service.get_journal_entries(company_id, skip=skip, limit=limit)


@router.get(
    "/journal-entries/{je_id}",
    response_model=accounting_schema.JournalEntryWithLinesResponse,
)
def read_journal_entry(
    je_id: int,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Retrieve a specific journal entry with its lines.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    db_je = service.get_journal_entry_with_lines(je_id, company_id)
    if db_je is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return db_je


@router.get(
    "/journal-entries/{entry_id}/lines",
    response_model=accounting_schema.JournalEntryLinesDetailResponse,
)
def read_journal_entry_lines_detail(
    entry_id: int,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Get detailed lines for a specific journal entry.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    detail = service.get_journal_entry_lines_detail(entry_id, company_id)
    if detail is None:
        raise HTTPException(
            status_code=404, detail="Journal entry not found or not accessible"
        )
    return detail



@router.post(
    "/journal-entries/{je_id}/post/",
    response_model=accounting_schema.JournalEntryResponse,
)
def post_journal_entry(
    je_id: int,
    company_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Post a journal entry (mark it as posted to the ledger).
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    db_je = service.post_journal_entry(je_id, company_id)
    if db_je is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found or already posted",
        )
    return db_je


@router.get("/trial-balance", response_model=accounting_schema.TrialBalanceResponse)
def get_trial_balance(
    company_id: int,
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Generate trial balance for the company.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    result = service.get_trial_balance(
        company_id=company_id,
        date_from=date_from,
        date_to=date_to,
    )
    return result


@router.get("/libro-mayor/")
def get_libro_mayor(
    company_id: int,
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    account_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Genera el Libro Mayor generalizado.
    Muestra movimientos y saldos por cuenta contable.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    result = service.get_libro_mayor(
        company_id=company_id,
        date_from=date_from,
        date_to=date_to,
        account_code=account_code,
    )
    return result


@router.get("/libro-ventas/")
def get_libro_ventas(
    company_id: int,
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Genera el Libro de Ventas según normativa colombiana.
    Registra todas las facturas de venta con desglose de IVA y retenciones.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    result = service.get_libro_ventas(
        company_id=company_id,
        date_from=date_from,
        date_to=date_to,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/libro-compras/")
def get_libro_compras(
    company_id: int,
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Genera el Libro de Compras según normativa colombiana.
    Registra todas las facturas de compra con desglose de IVA soportado y retenciones.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    result = service.get_libro_compras(
        company_id=company_id,
        date_from=date_from,
        date_to=date_to,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/declaracion-iva/")
def get_declaracion_iva(
    company_id: int,
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Declaración de IVA (Formulario 300 DIAN).
    IVA generado - IVA soportado = IVA a pagar o a favor.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    result = service.get_declaracion_iva(
        company_id=company_id,
        date_from=date_from,
        date_to=date_to,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/reporte-retenciones/")
def get_reporte_retenciones(
    company_id: int,
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Reporte de Retenciones en la fuente y en el IVA.
    Incluye Retefuente y ReteIVA por factura.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    result = service.get_reporte_retenciones(
        company_id=company_id,
        date_from=date_from,
        date_to=date_to,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/reporte-egresos/")
def get_reporte_egresos(
    company_id: int,
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Reporte de Egresos (Compras y Gastos).
    Registra todas las salidas de dinero por compras o gastos.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    result = service.get_reporte_egresos(
        company_id=company_id,
        date_from=date_from,
        date_to=date_to,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/reporte-ingresos/")
def get_reporte_ingresos(
    company_id: int,
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Reporte de Ingresos para declaración de renta.
    Clasifica ingresos operacionales y no operacionales.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    result = service.get_reporte_ingresos(
        company_id=company_id,
        date_from=date_from,
        date_to=date_to,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/reporte-patrimonio/")
def get_reporte_patrimonio(
    company_id: int,
    cut_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Reporte de Patrimonio (Activos - Pasivos = Patrimonio).
    Basado en saldos del Libro Mayor al corte.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    result = service.get_reporte_patrimonio(
        company_id=company_id,
        cut_date=cut_date,
    )
    
    # DEBUG LOG
    print(f"DEBUG PATRIMONIO [{company_id}]: {result.get('patrimonio_desglose')}")
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/estado-resultados/")
def get_estado_resultados(
    company_id: int,
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Estado de Resultados: Ingresos - Costos - Gastos = Utilidad Neta.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    try:
        result = service.get_estado_resultados(
            company_id=company_id, date_from=date_from, date_to=date_to
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.get("/balance-general/")
def get_balance_general(
    company_id: int,
    cut_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Balance General: Activos = Pasivos + Patrimonio.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    try:
        result = service.get_balance_general(company_id=company_id, cut_date=cut_date)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.get("/formulario-350/")
def get_formulario_350(
    company_id: int,
    year: int = Query(..., ge=2020, le=2030),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Formulario 350 - Declaración de Renta Persona Jurídica.
    Genera los datos para la declaración de renta según formato DIAN.
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = accounting_service.AccountingService(db)
    try:
        result = service.get_formulario_350(company_id=company_id, year=year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result
