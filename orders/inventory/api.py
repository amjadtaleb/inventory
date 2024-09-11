from typing import Optional
from django.db.models import F
from ninja import Router

from .models import PricedArticle
from .schemas import ArticleSchema

router = Router()


@router.get("/articles", response=list[ArticleSchema])
def list_articles(request, offset: int = 0, limit: Optional[int] = None):
    return PricedArticle.recents.annotate(
        quantity=F("article__inventoryarticle__quantity"),
        date_created=F("article__date_created"),
        reference=F("article__reference"),
        name=F("article__name"),
        description=F("article__description"),
    ).values()[slice(offset, limit)]
