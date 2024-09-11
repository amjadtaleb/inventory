from typing import Optional
from datetime import datetime
from ninja import Schema, Field


class ArticleSchema(Schema):
    id: int = Field(..., alias="article_id")
    reference: str
    name: str
    description: Optional[str]
    date_created: datetime
    price: Optional[float]
    date_priced: datetime = Field(..., alias="set_at")
    quantity: Optional[int]
