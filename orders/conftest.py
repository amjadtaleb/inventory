from django.utils.timezone import datetime, timedelta, make_aware
import pytest

from inventory.models import Article, PricedArticle, InventoryArticle

from pytest_factoryboy import register

from inventory.tests.factories import ArticleFactory, PricedArticleFactory, InventoryArticleFactory

register(ArticleFactory)
register(PricedArticleFactory)
register(InventoryArticleFactory)


@pytest.fixture
def article1(db, article_factory: ArticleFactory) -> Article:
    article = article_factory.create()
    return article


@pytest.fixture
def priced_article_old(db, article1: Article, priced_article_factory: PricedArticleFactory) -> PricedArticle:
    article = priced_article_factory.create(
        article=article1,
        price=12.22,
    )
    # django will override set_at because of auto_now_add so we have to reset it in a different statement
    article.set_at = make_aware(datetime.now() - timedelta(weeks=10))
    article.save(force_update=True, update_fields=["set_at"])
    return article


@pytest.fixture
def priced_article_recent(db, article1: Article, priced_article_factory: PricedArticleFactory):
    article = priced_article_factory.create(article=article1)
    return article


@pytest.fixture
def inventory_article_10(db, article1: Article, inventory_article_factory: InventoryArticleFactory) -> InventoryArticle:
    item = inventory_article_factory.create(article=article1)
    return item
