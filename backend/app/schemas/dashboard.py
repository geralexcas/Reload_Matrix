from pydantic import BaseModel

class DashboardStats(BaseModel):
    partners: int
    products: int
    invoices: int
    repairs: int
