from ninja import Router, Form
from ninja.errors import HttpError
from ninja.pagination import paginate, LimitOffsetPagination
from django.db.utils import IntegrityError

from .models import Article, FullArticle, Category
from .schemas import ArticleSchema, ArticleInput

router = Router(tags=["Articles"])


@router.get("/categories", response=list[str])
@paginate(LimitOffsetPagination)
def list_categories(request):
    return Category.objects.values_list(flat=True)


@router.post("/category/create")
def create_category(request, name: str):
    try:
        Category.objects.create(name=name)
        return 201
    except IntegrityError:
        raise HttpError(400, "Duplicate")



@router.get("/articles", response=list[ArticleSchema])
@paginate(LimitOffsetPagination)
def list_articles(request):
    return FullArticle.objects.all()


@router.post("/article/create")
def create_article(request, data: Form[ArticleInput]):
    Article.create_with_data(data=data)
    return 201


@router.post("/article/update/{id}")
def update_article(request, id: int, data: Form[ArticleInput]):
    # should have been a put method, but it was causing errors
    if article := Article.objects.filter(pk=id).first():
        article.update_with_data(data=data)
        return 201
    raise HttpError(404, "Not found")


@router.get("/article/{id}", response=ArticleSchema)
def get_article(request, id: int):
    if article := FullArticle.objects.filter(article_id=id).first():
        return article
    raise HttpError(404, "Not found")
