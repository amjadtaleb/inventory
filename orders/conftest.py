"""Fixtures for invetory tests, we also use these for sales testing
Inventory:
    - Category
    - Article
    - Priced Article: with price changes
    - Inventory Article
Sales:
    - Tax:
    - CategoryTax: multiple assignments
"""

from django.utils.timezone import datetime, timedelta, make_aware
import pytest
from pytest_factoryboy import register

from inventory.models import Category, Article, PricedArticle, InventoryArticle
from sales.models import Tax, CategoryTax

from inventory.tests.factories import CategoryFactory, ArticleFactory, PricedArticleFactory, InventoryArticleFactory
from sales.tests.factories import TaxFactory, CategoryTaxFactory


register(CategoryFactory)
register(ArticleFactory)
register(PricedArticleFactory)
register(InventoryArticleFactory)
# Sales
register(TaxFactory)
register(CategoryTaxFactory)


@pytest.fixture(autouse=True)
def product_category(db, category_factory: CategoryFactory) -> Category:
    category = category_factory.create()
    return category


@pytest.fixture(autouse=True)
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
    article.set_at = article.set_at - timedelta(weeks=10)
    article.save(force_update=True, update_fields=["set_at"])
    return article


@pytest.fixture
def priced_article_recent(db, article1: Article, priced_article_factory: PricedArticleFactory) -> PricedArticle:
    article = priced_article_factory.create(article=article1)
    return article


@pytest.fixture
def inventory_article_10(db, article1: Article, inventory_article_factory: InventoryArticleFactory) -> InventoryArticle:
    item = inventory_article_factory.create(article=article1)
    return item


######################
### Sales
######################
@pytest.fixture
def tax_0_21(db, tax_factory: TaxFactory) -> Tax:
    return tax_factory.create(reference="vat", value=0.21)


@pytest.fixture
def tax_0_12(db, tax_factory: TaxFactory) -> Tax:
    return tax_factory.create(reference="half", value=0.12)


@pytest.fixture
def tax_0_0(db, tax_factory: TaxFactory) -> Tax:
    return tax_factory.create(reference="reduced", value=0.04)


@pytest.fixture
def taxed_category_active(
    db, tax_0_21: Tax, product_category: Category, category_tax_factory: CategoryTaxFactory
) -> CategoryTax:
    return category_tax_factory.create(
        category=product_category,
        tax=tax_0_21,
        valid_from=make_aware(datetime.fromisoformat("2010-01-01")),
    )


@pytest.fixture
def taxed_category_obsolete(
    db, tax_0_12: Tax, product_category: Category, category_tax_factory: CategoryTaxFactory
) -> CategoryTax:
    return category_tax_factory.create(
        category=product_category,
        tax=tax_0_12,
        valid_from=make_aware(datetime.fromisoformat("1990-01-01")),
    )


@pytest.fixture
def taxed_category_future(
    db, tax_0_0: Tax, product_category: Category, category_tax_factory: CategoryTaxFactory
) -> CategoryTax:
    return category_tax_factory.create(
        category=product_category,
        tax=tax_0_0,
        valid_from=make_aware(datetime.fromisoformat("2040-01-01")),
    )
