from datetime import date
from ninja import Schema


class TaxSchema(Schema):
    reference: str
    value: float


class CategoryTaxScheme(Schema):
    tax: str
    category: str
    valid_from: date
