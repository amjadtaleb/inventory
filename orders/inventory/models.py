from django.db import models, transaction


class Article(models.Model):
    """Base article model, unaware of prices or inventory status"""

    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    reference = models.SlugField(db_index=True, allow_unicode=False)
    name = models.SlugField(null=False)
    description = models.TextField()

    def __str__(self) -> str:
        return f"Article {self.reference}:{self.name}"


class PricedArticleRecent(models.Manager):
    """Filter objects with something like `DISTINCT ON...ORDER BY set_at DESC`"""

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .extra(
                where=[
                    """(`inventory_pricedarticle`.`article_id`, `inventory_pricedarticle`.`set_at`) IN (
                        SELECT `article_id`, max(`set_at`)
                        FROM `inventory_pricedarticle`
                        GROUP BY `article_id`)"""
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
