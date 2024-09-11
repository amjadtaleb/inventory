from typing import Optional
from ninja import Router, Form
from ninja.errors import HttpError

from .models import Article, FullArticle
from .schemas import ArticleSchema, ArticleInput

router = Router()


@router.get("/articles", response=list[ArticleSchema])
def list_articles(request, offset: int = 0, limit: Optional[int] = None):
    return FullArticle.objects.all()[slice(offset, limit)]


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
    if article := FullArticle.objects.filter(article_id=id).first():
        return article
    raise HttpError(404, "Not found")
