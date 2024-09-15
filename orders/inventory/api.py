from ninja import Router, Form
from ninja.errors import HttpError
from ninja.pagination import paginate, LimitOffsetPagination
from django.db.utils import IntegrityError

from .models import Article, FullArticle, Category, StockAction
from .schemas import CategorySchema, ArticleSchema, ArticleInput, ArticleCreateInput

router = Router(tags=["Articles"])


@router.get("/categories", response=list[CategorySchema])
@paginate(LimitOffsetPagination)
def list_categories(request):
    return Category.objects.all()


@router.post("/category/create")
def create_category(request, category: Form[CategorySchema]):
    """Name will be converted to lower case"""
    try:
        Category.objects.create(name=category.name)
        return 201
    except IntegrityError:
        raise HttpError(400, "Duplicate")


@router.get("/articles", response=list[ArticleSchema])
@paginate(LimitOffsetPagination)
def list_articles(request):
    return FullArticle.objects.select_related("article__category").all()


@router.post("/article/create")
def create_article(request, data: Form[ArticleCreateInput]):
    try:
        Article.create_with_data(data=data)
        return 201
    except ValueError as err:
        raise HttpError(400, err.args[0])


@router.put("/article/update/{id}")
def update_article(request, id: int, data: ArticleInput):
    if article := Article.objects.filter(pk=id).first():
        article.update_with_data(data=data)
        return 201
    raise HttpError(404, "Not found")


@router.get("/article/{id}", response=ArticleSchema)
def get_article(request, id: int):
    if article := FullArticle.objects.filter(article_id=id).first():
        return article
    raise HttpError(404, "Not found")


@router.put("/article/price/update/{id}")
def update_article_price(request, id: int, price: float):
    try:
        Article.update_price(article_id=id, price=price)
    except Article.DoesNotExist:
        raise HttpError(404, "No matching articles")


@router.put("/article/stock/{action}/{id}")
def update_article_stock(request, id: int, action: StockAction, amount: int):
    try:
        if Article.update_stock(article_id=id, action=action, amount=amount) > 0:
            return 200
        raise HttpError(404, "No matching articles")
    except ValueError:
        raise HttpError(400, "amount should be positive integer")
