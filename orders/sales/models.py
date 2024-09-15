from django.db import models
from django.conf import settings
from django.db import transaction
from django.db.models import F

from inventory.models import InventoryArticle, Category, Article


class Tax(models.Model):
    """Definition of taxes"""

    reference = models.SlugField(primary_key=True)
    value = models.DecimalField(max_digits=6, decimal_places=3)

    def __str__(self) -> str:
        return f"Tax: {self.reference}@{self.value}"


class CategoryTax(models.Model):
    """Taxes over specific categories can vary over time, here we keep track of these changes"""

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE)
    valid_from = models.DateTimeField()

    def __str__(self) -> str:
        return f"Category tax: {self.category.pk}@{self.tax.pk}"


class PurchaceOrder(models.Model):
    reference = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"PurchaceOrder: {self.reference} ({self.created_by.pk})"

    def get_details(self) -> dict | None:
        return DetailedPurchaceOrder.aggregate_order(self.pk)

    def update_article(self, article_id: int, quantity: int) -> None:
        if quantity > 0:
            self.add_article(article_id=article_id, quantity=quantity)
        else:
            self.remove_article(article_id=article_id, quantity=quantity)

    def add_article(self, article_id: int, quantity: int) -> None:
        """
        1- Check the stock
        2- Add/Update order_article
        3- update stock_article quantity
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
                raise ValueError("Article out of stock")

    def remove_article(self, article_id: int, quantity: int) -> None:
        """
        1- Check order articles
        2- Remove/Update order_article
        3- Update stock_article quantity
        """
        with transaction.atomic():
            if order_article := OrderArticle.objects.filter(
                purchace_order=self, article_id=article_id, quantity=abs(quantity)
            ).first():
                order_article.delete()

            elif order_article := OrderArticle.objects.filter(
                purchace_order=self, article_id=article_id, quantity__gt=abs(quantity)
            ).first():
                order_article.quantity += quantity  # it is already negative
                order_article.save()
            else:
                raise ValueError("Not enough articles in order to remove")
            InventoryArticle.objects.filter(article_id=article_id).update(
                quantity=F("quantity") - quantity  # adding a negative value
            )

    def cancel_order(self):
        """for each OrderArticle in PurchaseOrder:
            - return the quantity to inventory
            - delete the OrderArticle
        Then delete the order itself
        """
        with transaction.atomic():
            for order_article in self.articles.all():  # type: ignore Djano does not make easy for pylance to get related items
                InventoryArticle.objects.filter(article=order_article.article).update(
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
    article = models.ForeignKey(Article, on_delete=models.DO_NOTHING)
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
    article = models.ForeignKey(Article, on_delete=models.DO_NOTHING)
    article_reference = models.SlugField()
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=28, decimal_places=2)
    tax_value = models.DecimalField(max_digits=6, decimal_places=3)

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
