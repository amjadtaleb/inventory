from typing import Optional
from django.db.models import F
from ninja import Router, Form
from ninja.errors import HttpError

from .models import PricedArticle, Article
from .schemas import ArticleSchema, ArticleInput

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


@router.post("/article/update/{id}")
def update_article(request, id: int, data: Form[ArticleInput]):
    # should have been a put method, but it was causing errors
    if article := Article.objects.filter(pk=id).first():
        article.update_with_data(data=data)
        return 201
    raise HttpError(404, "Not found")


@router.post("/article/create")
def create_article(request, data: Form[ArticleInput]):
    Article.create_with_data(data=data)
    return 201


@router.get("/article/{id}", response=ArticleSchema)
def get_article(request, id: int):
    if (
        article := PricedArticle.recents.annotate(
            quantity=F("article__inventoryarticle__quantity"),
            date_created=F("article__date_created"),
            reference=F("article__reference"),
            name=F("article__name"),
            description=F("article__description"),
        )
        .filter(article_id=id)
        .first()
    ):
        return article
    raise HttpError(404, "Not found")
