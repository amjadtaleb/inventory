import factory
from faker import Faker


from inventory.models import Article, PricedArticle, InventoryArticle

fakes = Faker()


class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article

    reference = "ABC123"
    name = fakes.slug()
    description = fakes.text()


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
