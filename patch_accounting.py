import re

with open("backend/app/services/accounting_service.py", "r") as f:
    content = f.read()

target = """            inv_number = getattr(inv, "invoice_number", getattr(inv, "purchase_number", "N/A"))
            inv_date = getattr(inv, "issue_date", getattr(inv, "purchase_date", None))

            entries.append(
                {
                    "invoice_id": inv.id,"""

replacement = """            inv_number = getattr(inv, "invoice_number", getattr(inv, "purchase_number", "N/A"))
            inv_date = getattr(inv, "issue_date", getattr(inv, "purchase_date", None))

            # Make sure invoice_id is unique across invoices and purchases
            source_prefix = "INV" if hasattr(inv, "invoice_number") else "PUR"
            unique_id = f"{source_prefix}-{inv.id}"

            entries.append(
                {
                    "invoice_id": unique_id,"""

new_content = content.replace(target, replacement)

with open("backend/app/services/accounting_service.py", "w") as f:
    f.write(new_content)

print("Patched accounting_service.py")
