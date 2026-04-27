from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import xml.etree.ElementTree as ET
from xml.dom import minidom

from app.models.sql.invoicing import Invoice, InvoiceItem
from app.models.sql import company as company_model
from app.models.sql import partners as partner_model


class ElectronicBillingService:
    """
    Servicio para generación de facturación electrónica XML UBL 2.1
    conforme a la Resolución DIAN 000042 de 2020.
    """

    NAMESPACE_UBL = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    NAMESPACE_CAC = (
        "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    )
    NAMESPACE_CBC = (
        "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    )
    NAMESPACE_EXT = (
        "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    )
    NAMESPACE_STS = (
        "urn:oasis:names:specification:ubl:schema:xsd:SignatureAggregateComponents-2"
    )
    NAMESPACE_DS = "http://www.w3.org/2000/09/xmldsig#"

    def __init__(self, db: Session):
        self.db = db

    def generate_cufe(
        self,
        company_nit: str,
        company_dv: str,
        invoice_number: str,
        invoice_date: str,
        invoice_total: Decimal,
        company_regimen: str,
    ) -> str:
        """
        Genera el CUFE (Código Único de Factura Electrónica) según especificaciones DIAN.

        El CUFE se genera con el hash SHA-384 de la concatenación de:
        - NIT del emisor
        - Dígito de verificación
        - Número de factura
        - Fecha de la factura
        - Total de la factura
        - Régimen tributario
        """
        cufe_string = (
            f"{company_nit}"
            f"{company_dv}"
            f"{invoice_number}"
            f"{invoice_date}"
            f"{invoice_total}"
            f"{company_regimen}"
        )
        cufe = hashlib.sha384(cufe_string.encode("utf-8")).hexdigest()
        return cufe

    def _format_date(self, dt: datetime) -> str:
        """Format date to UBL format: YYYY-MM-DDThh:mm:ss[-hh:mm]"""
        return dt.strftime("%Y-%m-%dT%H:%M:%S")

    def _format_decimal(self, value: Decimal) -> str:
        """Format decimal for UBL"""
        return f"{value:.2f}"

    def generate_ubl_xml(self, invoice_id: int, company_id: int) -> Optional[str]:
        """
        Genera el XML UBL 2.1 para una factura electrónica colombiana.
        """
        invoice = (
            self.db.query(Invoice)
            .filter(
                Invoice.id == invoice_id,
                Invoice.company_id == company_id,
            )
            .first()
        )
        if not invoice:
            return None

        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not company:
            return None

        partner = (
            self.db.query(partner_model.Partner)
            .filter(partner_model.Partner.id == invoice.partner_id)
            .first()
        )

        ns_ubl = f"{{{self.NAMESPACE_UBL}}}"
        ns_cac = f"{{{self.NAMESPACE_CAC}}}"
        ns_cbc = f"{{{self.NAMESPACE_CBC}}}"

        root = ET.Element(f"{ns_ubl}Invoice")
        root.set("xmlns", self.NAMESPACE_UBL)
        root.set("xmlns:cac", self.NAMESPACE_CAC)
        root.set("xmlns:cbc", self.NAMESPACE_CBC)
        root.set("xmlns:ext", self.NAMESPACE_EXT)
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")

        # UBLVersionID
        ubl_version = ET.SubElement(root, f"{ns_cbc}UBLVersionID")
        ubl_version.text = "UBL 2.1"

        # CustomizationID
        customization = ET.SubElement(root, f"{ns_cbc}CustomizationID")
        customization.text = "19"

        # ProfileID
        profile = ET.SubElement(root, f"{ns_cbc}ProfileID")
        profile.text = "DIAN 2.1"

        # InvoiceTypeCode
        invoice_type_code = ET.SubElement(root, f"{ns_cbc}InvoiceTypeCode")
        invoice_type_code.text = "01" if invoice.invoice_type == "SALE" else "02"

        # ID (Número de factura)
        inv_id = ET.SubElement(root, f"{ns_cbc}ID")
        inv_id.text = invoice.invoice_number

        # IssueDate
        issue_date = ET.SubElement(root, f"{ns_cbc}IssueDate")
        issue_date.text = invoice.issue_date.strftime("%Y-%m-%d")

        # IssueTime
        issue_time = ET.SubElement(root, f"{ns_cbc}IssueTime")
        issue_time.text = invoice.issue_date.strftime("%H:%M:%S")

        # DueDate (if applicable)
        if invoice.due_date:
            due_date = ET.SubElement(root, f"{ns_cbc}DueDate")
            due_date.text = invoice.due_date.strftime("%Y-%m-%d")

        # InvoiceTypeCode with DIAN specifics
        invoice_type = ET.SubElement(root, f"{ns_cbc}InvoiceTypeCode")
        invoice_type.set("schemeAgencyID", "195")
        invoice_type.set("schemeName", "Factura de Venta Electrónica")
        invoice_type.text = "01" if invoice.invoice_type == "SALE" else "02"

        # Note for tax regime
        if company.regimen == "SIMPLE":
            note = ET.SubElement(root, f"{ns_cbc}Note")
            note.text = "Tratamiento especial - Régimen Simple de Tributación"

        # TaxTotal
        tax_total = ET.SubElement(root, f"{ns_cbc}TaxTotal")
        tax_amount_el = ET.SubElement(
            root, f"{ns_cbc}TaxAmount", currencyID=invoice.currency
        )
        tax_total_amount = sum(item.tax_amount for item in invoice.items)
        tax_amount_el.text = self._format_decimal(tax_total_amount)

        # LegalMonetaryTotal
        legal_monetary = ET.SubElement(root, f"{ns_cac}LegalMonetaryTotal")

        line_extension = ET.SubElement(
            legal_monetary, f"{ns_cbc}LineExtensionAmount", currencyID=invoice.currency
        )
        subtotal = sum(item.line_total for item in invoice.items)
        line_extension.text = self._format_decimal(subtotal)

        tax_exclusive = ET.SubElement(
            legal_monetary, f"{ns_cbc}TaxExclusiveAmount", currencyID=invoice.currency
        )
        tax_exclusive.text = self._format_decimal(subtotal)

        tax_inclusive = ET.SubElement(
            legal_monetary, f"{ns_cbc}TaxInclusiveAmount", currencyID=invoice.currency
        )
        tax_inclusive.text = self._format_decimal(invoice.total_amount)

        payable = ET.SubElement(
            legal_monetary, f"{ns_cbc}PayableAmount", currencyID=invoice.currency
        )
        payable.text = self._format_decimal(invoice.total_amount)

        # AccountingSupplierParty (Empresa emisora)
        supplier = ET.SubElement(root, f"{ns_cac}AccountingSupplierParty")
        supplier_party = ET.SubElement(supplier, f"{ns_cac}Party")

        supplier_ident = ET.SubElement(supplier_party, f"{ns_cac}PartyIdentification")
        supplier_id = ET.SubElement(supplier_ident, f"{ns_cbc}ID")
        supplier_id.set("schemeAgencyID", "195")
        supplier_id.set("schemeName", "31")
        supplier_id.text = company.nit

        supplier_name = ET.SubElement(supplier_party, f"{ns_cac}PartyName")
        name_el = ET.SubElement(supplier_name, f"{ns_cbc}Name")
        name_el.text = company.name

        supplier_address = ET.SubElement(supplier_party, f"{ns_cac}PostalAddress")
        if company.address:
            address_line = ET.SubElement(supplier_address, f"{ns_cbc}AddressLine")
            line_el = ET.SubElement(address_line, f"{ns_cbc}Line")
            line_el.text = company.address

        # AccountingCustomerParty (Cliente)
        customer = ET.SubElement(root, f"{ns_cac}AccountingCustomerParty")
        customer_party = ET.SubElement(customer, f"{ns_cac}Party")

        if partner and partner.nit:
            customer_ident = ET.SubElement(
                customer_party, f"{ns_cac}PartyIdentification"
            )
            customer_id = ET.SubElement(customer_ident, f"{ns_cbc}ID")
            customer_id.set("schemeAgencyID", "195")
            customer_id.set(
                "schemeName", "31" if partner.partner_type != "SUPPLIER" else "31"
            )
            customer_id.text = partner.nit

        if partner:
            customer_name = ET.SubElement(customer_party, f"{ns_cac}PartyName")
            customer_name_el = ET.SubElement(customer_name, f"{ns_cbc}Name")
            customer_name_el.text = partner.name

        # InvoiceLines
        for idx, item in enumerate(invoice.items, 1):
            invoice_line = ET.SubElement(root, f"{ns_cac}InvoiceLine")

            line_id = ET.SubElement(invoice_line, f"{ns_cbc}ID")
            line_id.text = str(idx)

            line_qty = ET.SubElement(
                invoice_line, f"{ns_cbc}InvoicedQuantity", unitCode="C62"
            )
            line_qty.text = self._format_decimal(item.quantity)

            line_amount = ET.SubElement(
                invoice_line,
                f"{ns_cbc}LineExtensionAmount",
                currencyID=invoice.currency,
            )
            line_amount.text = self._format_decimal(item.line_total)

            # Item description
            item_el = ET.SubElement(invoice_line, f"{ns_cac}Item")
            item_name = ET.SubElement(item_el, f"{ns_cbc}Name")
            item_name.text = item.description

            # Price
            price = ET.SubElement(invoice_line, f"{ns_cac}Price")
            price_amount = ET.SubElement(
                price, f"{ns_cbc}PriceAmount", currencyID=invoice.currency
            )
            price_amount.text = self._format_decimal(item.unit_price)

        # Generate CUFE
        invoice_date_str = invoice.issue_date.strftime("%Y-%m-%dT%H:%M:%S")
        cufe = self.generate_cufe(
            company_nit=company.nit,
            company_dv=company.dv,
            invoice_number=invoice.invoice_number,
            invoice_date=invoice_date_str,
            invoice_total=invoice.total_amount,
            company_regimen=company.regimen,
        )

        # Pretty print XML
        rough_string = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")

        return pretty_xml.decode("utf-8")

    def send_to_dian(self, invoice_id: int, company_id: int) -> dict:
        """
        Envía la factura electrónica a la DIAN.

        En producción, esto requiere:
        1. Conexión SOAP/REST al servicio web de la DIAN
        2. Certificado digital para firma
        3. XML firmado digitalmente

        Esta implementación simula el proceso y actualiza el estado.
        """
        invoice = (
            self.db.query(Invoice)
            .filter(
                Invoice.id == invoice_id,
                Invoice.company_id == company_id,
            )
            .first()
        )
        if not invoice:
            return {"success": False, "error": "Invoice not found"}

        if invoice.estado_dian == "ACEPTADO":
            return {"success": True, "message": "Invoice already accepted by DIAN"}

        # Generate XML if not already generated
        if not invoice.xml_ubl:
            xml_content = self.generate_ubl_xml(invoice_id, company_id)
            if not xml_content:
                return {"success": False, "error": "Failed to generate UBL XML"}
            invoice.xml_ubl = xml_content

        # Generate CUFE if not already generated
        if not invoice.cufe:
            company = (
                self.db.query(company_model.Company)
                .filter(company_model.Company.id == company_id)
                .first()
            )
            invoice_date_str = invoice.issue_date.strftime("%Y-%m-%dT%H:%M:%S")
            invoice.cufe = self.generate_cufe(
                company_nit=company.nit,
                company_dv=company.dv,
                invoice_number=invoice.invoice_number,
                invoice_date=invoice_date_str,
                invoice_total=invoice.total_amount,
                company_regimen=company.regimen,
            )

        # Update status to ENVIADO
        invoice.estado_dian = "ENVIADO"
        self.db.commit()
        self.db.refresh(invoice)

        # In production, here you would:
        # 1. Sign the XML with digital certificate
        # 2. Send to DIAN web service
        # 3. Wait for response
        # 4. Update estado_dian based on response

        return {
            "success": True,
            "invoice_id": invoice.id,
            "cufe": invoice.cufe,
            "estado_dian": invoice.estado_dian,
            "message": "Invoice sent to DIAN successfully",
        }

    def update_dian_status(
        self,
        invoice_id: int,
        company_id: int,
        status: str,
        motivo_rechazo: Optional[str] = None,
    ) -> Optional[Invoice]:
        """
        Actualiza el estado de la factura según respuesta de la DIAN.
        """
        allowed = ["BORRADOR", "ENVIADO", "ACEPTADO", "RECHAZADO"]
        if status not in allowed:
            raise ValueError(f"Status must be one of {allowed}")

        invoice = (
            self.db.query(Invoice)
            .filter(
                Invoice.id == invoice_id,
                Invoice.company_id == company_id,
            )
            .first()
        )
        if invoice:
            invoice.estado_dian = status
            if motivo_rechazo:
                invoice.motivo_rechazo = motivo_rechazo
            self.db.commit()
            self.db.refresh(invoice)
        return invoice

    def get_invoice_xml(self, invoice_id: int, company_id: int) -> Optional[str]:
        """
        Obtiene el XML UBL de una factura electrónica.
        """
        invoice = (
            self.db.query(Invoice)
            .filter(
                Invoice.id == invoice_id,
                Invoice.company_id == company_id,
            )
            .first()
        )
        if not invoice:
            return None

        if not invoice.xml_ubl:
            return self.generate_ubl_xml(invoice_id, company_id)

        return invoice.xml_ubl
