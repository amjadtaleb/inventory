"""Test Sales:
- Create a tax Assign a Tax to the category
- Taxing all categories, and categorizing all articles means no FullArticle with tax=None
- FullArticle inherits category tax
- FullArticle inherits most recent category tax
- FullArticle inherits most recent active category tax: not future ones
- Purchace:
    - test add aricle
    - test remove article
    - test update article
    - test cancel purchace
    - test value
    - test tax: for recent and old
"""
from sales.models import Tax, CategoryTax
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
