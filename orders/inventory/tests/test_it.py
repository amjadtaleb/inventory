import pytest
from django.db.models import ProtectedError
from django.db.utils import IntegrityError
from inventory.models import PricedArticle, InventoryAudit, Article


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


def test_priced_article_are_created_in_order(priced_article_old, priced_article_recent):
    assert priced_article_recent.set_at > priced_article_old.set_at


def test_priced_article_count(db, article1, priced_article_old, priced_article_recent):
    """Make sure we created the two reusable fixtures"""
    # Keep the injected dependencies as they are not set for reuse
    assert PricedArticle.objects.filter(article=article1).count() == 2


def test_priced_article_recents_one_per_article(db, article1, priced_article_old, priced_article_recent):
    assert PricedArticle.recents.filter(article=article1).count() == 1


def test_priced_article_recents_price(db, priced_article_recent, article1):
    priced = PricedArticle.recents.filter(article=article1).first()
    assert priced is not None  # don't cause the test to raise an AttributeError
    assert priced_article_recent.price == float(priced.price)


def test_articles_in_inventory(db, inventory_article_10):
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


def test_inventory_item_cannot_be_deleted(db, article1, inventory_article_10):
    with pytest.raises(ProtectedError):
        article1.delete()
