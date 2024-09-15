from typing import Optional, Annotated, TypeVar
from pydantic import WrapValidator
from pydantic_core import PydanticUseDefault
from datetime import datetime
from ninja import Schema, Field


def _empty_str_to_default(v, handler, info):
    # https://django-ninja.dev/guides/input/form-params/
    if isinstance(v, str) and v == "":
        raise PydanticUseDefault
    return handler(v)


T = TypeVar("T")
EmptyStrToDefault = Optional[Annotated[T, WrapValidator(_empty_str_to_default)]]


class CategorySchema(Schema):
    name: str


class ArticleSchema(Schema):
    """FullArticle Schema"""

    id: int = Field(..., alias="article_id")
    reference: str
    name: str
    description: Optional[str]
    date_created: datetime
    price: Optional[float]
    date_priced: datetime = Field(..., alias="set_at")
    quantity: Optional[int]
    tax: Optional[float]
    category: Optional[str]


class ArticleCreateInput(Schema):
    reference: str
    name: str
    description: str
    price: float
    quantity: int
    category_name: str


class ArticleInput(Schema):
    """Like ArticleCreateInput, but everything should be optional"""

    reference: EmptyStrToDefault[str] = None
    name: EmptyStrToDefault[str] = None
    description: Optional[str] = None
    price: EmptyStrToDefault[float] = None
    quantity: EmptyStrToDefault[int] = None
    category_name: EmptyStrToDefault[str] = None
