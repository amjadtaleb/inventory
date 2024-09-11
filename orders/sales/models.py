from django.db import models
from django.conf import settings
from django.db import transaction
from django.db.models import F

from inventory.models import InventoryArticle, Category


class Tax(models.Model):
    """Definition of taxes"""

    reference = models.SlugField(primary_key=True)
    value = models.DecimalField(max_digits=3, decimal_places=3)


class CategoryTax(models.Model):
    """Taxes over specific categories can vary over time, here we keep track of these changes"""

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE)
    valid_from = models.DateTimeField()


class PurchaceOrder(models.Model):
    reference = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_details(self) -> dict | None:
        return DetailedPurchaceOrder.aggregate_order(self.pk)

    def add_article(self, article_id, quantity):
        """
        1- check stock
        2- add to order: update if existing
        3- reduce stock
        """
        with transaction.atomic():
            if inventory_article := InventoryArticle.objects.filter(
                article_id=article_id, quantity__gte=quantity
            ).first():
                OrderArticle.objects.update_or_create(
                    purchace_order=self,
                    article_id=article_id,
                    create_defaults={"quantity": quantity},
                    defaults={"quantity": F("quantity") + quantity},
                )
                inventory_article.quantity -= quantity
                inventory_article.save()
            else:
                raise ValueError("Out of stock")

    def cancel_order(self):
        """for each OrderArticle in PurchaseOrder:
            - return the quantity to inventory
            - delete the OrderArticle
        Then delete the order itself
        """
        with transaction.atomic():
            for order_article in self.articles.all():  # type: ignore Djano does not make easy for pylance to get related items
                InventoryArticle.objects.filter(article=order_article.article.article).update(
                    # too many articles? it's OrderArticle.InventoryArticle.Article
                    # using article_id at anypoint might point to wrong PK
                    quantity=F("quantity") + order_article.quantity
                )
                order_article.delete()
            self.delete()


class OrderArticle(models.Model):
    purchace_order = models.ForeignKey(
        PurchaceOrder,
        on_delete=models.CASCADE,
        related_name="articles",
        related_query_name="article",
    )
    article = models.ForeignKey(InventoryArticle, on_delete=models.DO_NOTHING)
    quantity = models.PositiveIntegerField()


class JSON_ObjectAgg(models.aggregates.Aggregate):
    def __init__(self, *expressions, **extra):
        super().__init__(*expressions, **extra)

    function = "JSON_OBJECTAGG"
    output_field = models.JSONField()
    template = "%(function)s(%(expressions)s)"


class JSON_ArrayAgg(models.aggregates.Aggregate):
    function = "JSON_OBJECTAGG"
    output_field = models.JSONField()
    template = "%(function)s(%(distinct)s%(expressions)s)"


class DetailedPurchaceOrder(models.Model):
    """Readonly view, gets parsed"""

    class Meta:
        managed = False
        db_table = "order_details"

    # id is the same from PurchaceOrder.pk
    reference = models.SlugField()
    created_at = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    article = models.ForeignKey(InventoryArticle, on_delete=models.DO_NOTHING)
    article_reference = models.SlugField()
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=28, decimal_places=2)
    tax_value = models.DecimalField(max_digits=3, decimal_places=3)

    @classmethod
    def aggregate_order(cls, order_id: int) -> dict | None:
        return (
            cls.objects.filter(pk=order_id)
            .annotate(
                articles=JSON_ObjectAgg("article_reference", "quantity"),
                total_pre_tax=models.aggregates.Sum(F("price") * F("quantity")),
                total_texed=models.aggregates.Sum((F("price") + F("price") * F("tax_value")) * F("quantity")),
            )
            .values(
                "id",
                "reference",
                "created_at",
                "created_by_id",
                "articles",
                "total_pre_tax",
                "total_texed",
            )
            .first()
        )
