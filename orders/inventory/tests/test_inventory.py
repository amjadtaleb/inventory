"""Test Inventory:
- create product category:
    - test unique category name: PK in mariaDB appears to be case insensetive
- create a product:
    - test unique product reference
    - TODO: make name unique and test it
- create a priced product
- create an inventory product
    - update inventory product quantity
    - check inventory auditing: we should have two for creation and updating
- test price changes:
  - create multiple prices with different pricing times
  - check we have all prices
  - check full product price matches most recent price
- check the full product:
    - only priced articles result in fullarticles
    - priced but not inventoried will make a fullarticle with quantity None
    - fullarticle will use recent price when multiple pricing exists
    - article without a category will not have a tax
        In sales we will add category tax and check that fullartcle got it
"""

import pytest
from django.db.models import ProtectedError
from django.db.utils import IntegrityError
from inventory.models import PricedArticle, InventoryAudit, Article, Category, FullArticle


def test_new_category_raises(db, product_category):
    with pytest.raises(IntegrityError):
        Category.objects.create(name=product_category.name.upper())


def test_new_category_raises2(db, product_category):
    with pytest.raises(IntegrityError):
        Category.objects.create(name=product_category.name.lower())


def test_priced_article_fk(article1, priced_article_old, priced_article_recent):
    """Verify fixtures setup"""
    assert priced_article_old.article.name == article1.name
    assert priced_article_recent.article.name == article1.name


def test_article_unique_reference(article1):
    with pytest.raises(IntegrityError, match=rf".*1062.*{article1.reference}.*"):
        Article.objects.create(
            reference=article1.reference,
            description="",
            name="name",
        )


def test_priced_article_count(db, article1, priced_article_old, priced_article_recent):
    # Keep the injected dependencies as they are not set for reuse
    assert PricedArticle.objects.filter(article=article1).count() == 2


def test_priced_article_are_created_in_order(priced_article_old, priced_article_recent):
    """Make sure fixtures were set up correctly"""
    assert priced_article_recent.set_at > priced_article_old.set_at


def test_priced_article_recents_one_per_article(db, article1, priced_article_old, priced_article_recent):
    assert FullArticle.objects.filter(article=article1).count() == 1


def test_priced_article_recents_price(db, priced_article_recent, article1):
    priced = FullArticle.objects.filter(article=article1).first()
    assert priced is not None  # don't cause the test to raise an AttributeError
    assert priced_article_recent.price == float(priced.price)


def test_priced_article_no_inventory(db, priced_article_recent, article1):
    assert FullArticle.objects.filter(article=article1).first().quantity is None


def test_articles_in_inventory(inventory_article_10):
    assert inventory_article_10.quantity == 10


def test_inventory_item_first_audit(db, inventory_article_10):
    """Creating the first inventory item should be audited"""
    assert InventoryAudit.objects.count() == 1


def test_inventory_item_change_audit(db, inventory_article_10):
    """Updating an existing item should result in an additional audit row"""
    inventory_article_10.quantity = 12
    inventory_article_10.save()
    assert InventoryAudit.objects.count() == 2


def test_non_inventory_item_can_be_deleted(db, article1):
    article1.delete()


def test_priced_non_inventory_item_can_be_deleted(db, article1, priced_article_recent):
    article1.delete()


def test_inventory_item_cannot_be_deleted(db, article1, inventory_article_10):
    with pytest.raises(ProtectedError):
        article1.delete()


def test_unpriced_inventory_article_has_no_fullarticle(db, inventory_article_10):
    assert FullArticle.objects.filter(article=inventory_article_10.article).first() is None


def test_priced_article_has_fullarticle(db, article1, priced_article_recent, inventory_article_10):
    fl = FullArticle.objects.filter(article=article1).first()
    assert float(fl.price) == priced_article_recent.price
    assert fl.quantity == inventory_article_10.quantity


def test_fullarticle_recent_price(db, article1, priced_article_old, priced_article_recent):
    fl = FullArticle.objects.filter(article=article1).first()
    assert priced_article_recent.price != priced_article_old.price
    assert float(fl.price) == priced_article_recent.price


def test_fullarticle_no_cat_no_tax(db, priced_article_recent):
    fl = FullArticle.objects.filter(category__isnull=True).first()
    assert fl.tax is None
