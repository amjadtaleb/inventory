from django.db import models, transaction
from .schemas import ArticleInput


class Category(models.Model):
    name = models.SlugField(primary_key=True)
    "examples: cars, books, basics, services"


def set_default_category():
    cat, created = Category.objects.get_or_create(name="services")
    return cat


class Article(models.Model):
    """Base article model, unaware of prices or inventory status"""

    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    reference = models.SlugField(db_index=True, allow_unicode=False, unique=True)
    name = models.SlugField(null=False)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=set_default_category)

    def __str__(self) -> str:
        return f"Article {self.reference}:{self.name}"

    def update_related(self, data: ArticleInput):
        if data.category is not None:
            category, created = Category.objects.get_or_create(name=data.category)
            self.category = category
            self.save()
        if data.price is not None:
            PricedArticle.objects.create(
                article=self,
                price=data.price,
            )
        if data.quantity is not None:
            InventoryArticle.objects.update_or_create(
                article=self,
                defaults={"quantity": data.quantity},
            )

    def update_with_data(self, data: ArticleInput):
        with transaction.atomic():
            for i in "reference", "name", "description":
                # These atts should not be empty, if none was provided fallback to existing value
                setattr(self, i, getattr(data, i) or getattr(self, i))
            self.save()
            self.update_related(data)

    @classmethod
    def create_with_data(cls, data: ArticleInput):
        with transaction.atomic():
            article = cls.objects.create(
                reference=data.reference,
                name=data.name,
                description=data.description,
            )
            article.save()
            article.update_related(data)
            return article


class PricedArticleRecent(models.Manager):
    """Filter objects with something like `DISTINCT ON...ORDER BY set_at DESC`"""

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .extra(
                where=[
                    """EXISTS (SELECT 1 FROM `inventory_pricedarticle` ts
                    WHERE (
                    `inventory_pricedarticle`.`article_id`, `inventory_pricedarticle`.`set_at`
                    ) IN (
                        SELECT `article_id`, max(`set_at`)
                        FROM `inventory_pricedarticle`
                        GROUP BY `article_id`)
                    )"""
                ]
            )
        )


class PricedArticle(models.Model):
    """Add a price to Article and keep track of price changes.
    Use PricedArticle.recents to get objects filtered by most recent price change
    """

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=28, decimal_places=2, db_index=True)
    set_at = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = models.Manager()
    recents = PricedArticleRecent()

    def __str__(self) -> str:
        # it would be nice to print self.article.reference, but that will cause a new DB call unless select related is set
        return f"Priced Article: {self.article_id}: {self.price}"  # type: ignore


class InventoryArticle(models.Model):
    """Add inventory awareness to Article
    Once the article is added to inventory it should not be deleted from the database, the quantity should be set to 0
    """

    article = models.OneToOneField(Article, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"InventoryArticle {self.article_id}:{self.quantity}"  # type: ignore

    def save(self, *args, **kwargs) -> None:
        with transaction.atomic():
            super().save(*args, **kwargs)
            InventoryAudit(article=self.article, new_state=self.quantity).save()


class InventoryAudit(models.Model):
    """Keep track of all changes in inventory.
    Ideally we should use a DB trigger"""

    article = models.ForeignKey(Article, on_delete=models.PROTECT)
    event_date = models.DateTimeField(auto_now=True, db_index=True)
    new_state = models.PositiveIntegerField()  # should match InventoryArticle.quantity

    def __str__(self) -> str:
        return f"InventoryArticleLog {self.article_id}@{self.event_date}"  # type: ignore


class FullArticle(models.Model):
    """Base article model, unaware of prices or inventory status"""

    class Meta:
        managed = False
        db_table = "taxed_article"

    article = models.ForeignKey(Article, primary_key=True, on_delete=models.DO_NOTHING)
    price = models.DecimalField(max_digits=28, decimal_places=2)
    set_at = models.DateTimeField()
    quantity = models.PositiveIntegerField()
    date_created = models.DateTimeField()
    reference = models.SlugField()
    name = models.SlugField()
    description = models.TextField()
    tax = models.DecimalField(max_digits=3, decimal_places=3)
