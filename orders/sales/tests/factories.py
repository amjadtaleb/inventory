import factory
from faker import Faker

from django.contrib.auth import get_user_model
from sales.models import Tax, CategoryTax, PurchaceOrder
from inventory.tests.factories import CategoryFactory

fakes = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = "test"


class TaxFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tax
        django_get_or_create = ("reference",)

    reference = "vat"
    value = fakes.pydecimal(positive=True, left_digits=3, right_digits=3)


class CategoryTaxFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CategoryTax

    category = factory.SubFactory(CategoryFactory)
    tax = factory.SubFactory(TaxFactory)


class PurchaceOrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PurchaceOrder

    reference = fakes.slug()
    created_by = factory.SubFactory(UserFactory)
