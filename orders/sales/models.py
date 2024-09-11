from django.db import models
from django.conf import settings
from django.db import transaction
from django.db.models import F

from inventory.models import Article, InventoryArticle, Category


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
    reference = models.SlugField()
    created_at = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def add_article(self, article, amount):
        """
        1- check stock
        2- add to order
        3- reduce stock
        """
        with transaction.atomic():
            if inventory_article := InventoryArticle.objects.filter(article=article, quantity__gte=amount).first():
                OrderArticle.objects.create(
                    purchaceorder=self,
                    article=article,
                    quantity=amount,
                )
                inventory_article.quantity -= amount
                inventory_article.save()
            else:
                raise ValueError("Out of stock")

    def cancel_order(self):
        "for article in order, return to inventory and clear from order then delete OrderArticle"
        with transaction.atomic():
            for article in self.articles.all():
                print(article)
                InventoryArticle.objects.filter(article=article.article).update(
                    quantity=F("quantity") + article.quantity
                )
                article.delete()


class OrderArticle(models.Model):
    purchace_order = models.ForeignKey(
        PurchaceOrder,
        on_delete=models.CASCADE,
        related_name="articles",
        related_query_name="article",
    )
    article = models.ForeignKey(InventoryArticle, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
