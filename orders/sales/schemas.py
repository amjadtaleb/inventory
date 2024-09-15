from datetime import datetime, date
from ninja import Schema


class TaxSchema(Schema):
    reference: str
    value: float


class CategoryTaxScheme(Schema):
    tax: str
    category: str
    valid_from: date


class OrderBasicSchema(Schema):
    id: int
    reference: str
    created_at: datetime


class OrderSchema(Schema):
    id: int
    reference: str
    created_at: datetime
    created_by_id: int
    articles: dict[str, int]  # TODO: find a better way to display this in the api docs
    total_pre_tax: float
    total_taxed: float
