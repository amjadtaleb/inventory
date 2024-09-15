import factory
from faker import Faker


from inventory.models import Category, Article, PricedArticle, InventoryArticle

fakes = Faker()


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ("name",)

    name = fakes.slug()


class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article

    reference = fakes.slug()
    name = fakes.slug()
    description = fakes.text()
    category = factory.SubFactory(CategoryFactory)


class PricedArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PricedArticle

    article = factory.SubFactory(ArticleFactory)
    price = 14.44


class InventoryArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InventoryArticle

    article = factory.SubFactory(ArticleFactory)
    quantity = 10
