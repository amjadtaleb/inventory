"""Test Sales:
- Create a tax Assign a Tax to the category
- Taxing all categories, and categorizing all articles means no FullArticle with tax=None
- FullArticle inherits category tax
- FullArticle inherits most recent category tax
- FullArticle inherits most recent active category tax: not future ones
- Purchace:
    - test add aricle: when amount in stock and not
    - test update article: increase ok and not
    - test remove article: when amount is valid and not
    - test cancel purchace
    - test total order value
    - test tax: for recent and old
    - TODO: order price should account for article price upon order creation
"""

import pytest
from sales.models import Tax, CategoryTax, OrderArticle, PurchaceOrder
from inventory.models import FullArticle


def test_tax(tax_0_21: Tax, tax_0_12: Tax, tax_0_0: Tax):
    assert float(tax_0_21.value) == 0.21
    assert float(tax_0_12.value) == 0.12
    assert float(tax_0_0.value) == 0.04


def test_taxed_category(
    tax_0_21, tax_0_12, tax_0_0, taxed_category_active, taxed_category_obsolete, taxed_category_future
):
    assert taxed_category_active.tax.value == tax_0_21.value
    assert taxed_category_obsolete.tax.value == tax_0_12.value
    assert taxed_category_future.tax.value == tax_0_0.value


def test_taxed_category_order(product_category, taxed_category_active, taxed_category_obsolete):
    assert taxed_category_obsolete.valid_from < taxed_category_active.valid_from


def test_no_fullarticle_with_no_cat(db, priced_article_recent, taxed_category_active):
    fl = FullArticle.objects.filter(category__isnull=True).first()
    assert fl is None


def test_fullarticle_cat_tax(db, priced_article_recent, taxed_category_active):
    fl = FullArticle.objects.first()
    assert float(fl.tax) == taxed_category_active.tax.value


def test_fullarticle_cat_recent_tax(db, priced_article_recent, taxed_category_active, taxed_category_obsolete):
    assert CategoryTax.objects.count() == 2
    fl = FullArticle.objects.first()
    assert float(fl.tax) == taxed_category_active.tax.value


def test_fullarticle_cat_recent_active_tax(
    db, priced_article_recent, taxed_category_active, taxed_category_obsolete, taxed_category_future
):
    assert CategoryTax.objects.count() == 3
    fl = FullArticle.objects.first()
    assert float(fl.tax) == taxed_category_active.tax.value


############# Edit Order
def test_purchace_order_add_article_ok(db, purchace_order_recent, inventory_article_10):
    """Article removed from stock and added to order"""
    amount = 1
    old_stock = inventory_article_10.quantity
    assert OrderArticle.objects.count() == 0

    purchace_order_recent.update_article(
        article_id=inventory_article_10.article_id,
        quantity=amount,
    )

    the_article = OrderArticle.objects.first()
    inventory_article_10.refresh_from_db()
    assert the_article.quantity == amount
    assert inventory_article_10.quantity == old_stock - amount


def test_purchace_order_add_article_not_enough_stock(db, purchace_order_recent, inventory_article_10):
    with pytest.raises(ValueError, match="Article out of stock"):
        purchace_order_recent.update_article(
            article_id=inventory_article_10.article_id,
            quantity=inventory_article_10.quantity + 1,
        )


def test_purchace_order_add_article_multiple_ok(db, purchace_order_recent, inventory_article_10):
    amount = 1
    cycles = 2
    old_stock = inventory_article_10.quantity
    for _ in range(cycles):
        purchace_order_recent.update_article(
            article_id=inventory_article_10.article_id,
            quantity=amount,
        )

    the_article = OrderArticle.objects.first()
    inventory_article_10.refresh_from_db()
    assert the_article.quantity == amount * cycles
    assert inventory_article_10.quantity == old_stock - amount * cycles


def test_purchace_order_add_article_multiple_ko(db, purchace_order_recent, inventory_article_10):
    cycles = 2
    amount = inventory_article_10.quantity
    with pytest.raises(ValueError, match="Article out of stock"):
        for _ in range(cycles):
            purchace_order_recent.update_article(
                article_id=inventory_article_10.article_id,
                quantity=amount,
            )


def test_purchace_order_remove_article_completely(db, purchace_order_recent, inventory_article_10):
    """Article removed from order and returned to inventory"""
    amount = 2
    old_stock = inventory_article_10.quantity
    purchace_order_recent.update_article(
        article_id=inventory_article_10.article_id,
        quantity=amount,
    )
    inventory_article_10.refresh_from_db()
    assert OrderArticle.objects.count() == 1
    assert inventory_article_10.quantity == old_stock - amount

    purchace_order_recent.update_article(
        article_id=inventory_article_10.article_id,
        quantity=-amount,
    )
    inventory_article_10.refresh_from_db()
    assert OrderArticle.objects.count() == 0
    assert inventory_article_10.quantity == old_stock


def test_purchace_order_remove_article_partially(db, purchace_order_recent, inventory_article_10):
    """Add 2 units then remove 1"""
    add_amount = 2
    remove_amount = 1
    old_stock = inventory_article_10.quantity
    purchace_order_recent.update_article(
        article_id=inventory_article_10.article_id,
        quantity=add_amount,
    )
    the_order_article = OrderArticle.objects.first()
    inventory_article_10.refresh_from_db()
    assert OrderArticle.objects.count() == 1
    assert the_order_article.quantity == add_amount
    assert inventory_article_10.quantity == old_stock - add_amount

    purchace_order_recent.update_article(
        article_id=inventory_article_10.article_id,
        quantity=-remove_amount,
    )
    inventory_article_10.refresh_from_db()
    the_order_article.refresh_from_db()

    assert OrderArticle.objects.count() == 1  # there is still an order
    assert the_order_article.quantity == add_amount - remove_amount
    assert inventory_article_10.quantity == old_stock - add_amount + remove_amount


def test_purchace_order_remove_article_not_enough_in_order(db, purchace_order_recent, inventory_article_10):
    add_amount = 2
    remove_amount = 3
    purchace_order_recent.update_article(
        article_id=inventory_article_10.article_id,
        quantity=add_amount,
    )
    with pytest.raises(ValueError, match="Not enough articles in order to remove"):
        purchace_order_recent.update_article(
            article_id=inventory_article_10.article_id,
            quantity=-remove_amount,
        )


def test_cancel_order(db, purchace_order_recent, inventory_article_10):
    old_stock = inventory_article_10.quantity
    purchace_order_recent.update_article(
        article_id=inventory_article_10.article_id,
        quantity=1,
    )
    purchace_order_recent.cancel_order()
    inventory_article_10.refresh_from_db()
    assert inventory_article_10.quantity == old_stock
    assert OrderArticle.objects.count() == 0
    assert PurchaceOrder.objects.count() == 0


############# Calculate Total and Taxes
def test_purchace_order_total_value(
    purchace_order_recent, inventory_article_10, priced_article_recent, taxed_category_active
):
    add_amount = 3
    purchace_order_recent.update_article(
        article_id=inventory_article_10.article_id,
        quantity=add_amount,
    )
    assert float(purchace_order_recent.get_details()["total_pre_tax"]) == priced_article_recent.price * add_amount


def test_purchace_order_total_value_taxed(
    purchace_order_recent, inventory_article_10, priced_article_recent, taxed_category_active
):
    add_amount = 3
    purchace_order_recent.update_article(
        article_id=inventory_article_10.article_id,
        quantity=add_amount,
    )
    total = priced_article_recent.price * add_amount
    tax = total * taxed_category_active.tax.value
    assert float(purchace_order_recent.get_details()["total_taxed"]) == tax + total


def test_purchace_order_total_value_taxed_old(
    purchace_order_old, inventory_article_10, priced_article_recent, taxed_category_active, taxed_category_obsolete
):
    add_amount = 3
    purchace_order_old.update_article(
        article_id=inventory_article_10.article_id,
        quantity=add_amount,
    )
    total = priced_article_recent.price * add_amount
    tax = total * taxed_category_obsolete.tax.value
    assert float(purchace_order_old.get_details()["total_taxed"]) == tax + total
