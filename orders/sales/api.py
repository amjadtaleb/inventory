from typing import Optional
from ninja import Router, Form
from django.db.utils import IntegrityError

from inventory.models import Category
from .models import Tax, CategoryTax, PurchaceOrder, DetailedPurchaceOrder
from .schemas import TaxSchema, CategoryTaxScheme, OrderSchema

router = Router(tags=['Orders'])


@router.get("/taxes", response=list[TaxSchema])
def list_taxes(request, offset: int = 0, limit: Optional[int] = None):
    return Tax.objects.all()[slice(offset, limit)]


@router.post("/taxes/add")
def add_tax(request, tax: Form[TaxSchema]):
    tax, created = Tax.objects.get_or_create(
        reference=tax.reference,
        defaults={"value": tax.value},
    )  # type: ignore
    if created:
        return 201
    return 400  # duplicate


@router.post("/taxes/assign")
def assign_tax(request, data: Form[CategoryTaxScheme]):
    if tax := Tax.objects.filter(reference=data.tax).first():
        if cat := Category.objects.filter(name=data.category).first():
            CategoryTax.objects.create(
                category=cat,
                tax=tax,
                valid_from=data.valid_from,
            )
            return 201
    return 404


@router.post("order/create")
def create_order(request, reference: str):
    try:
        PurchaceOrder.objects.create(
            reference=reference,
            created_by_id=1,  # assuming super user was created
        )
        return 201
    except IntegrityError:
        return 400  # duplicate


@router.post("order/additem/{reference}")
def update_order(request, reference: str, article_id: int, quantity: int):
    if order := PurchaceOrder.objects.filter(reference=reference).first():
        try:
            order.add_article(article_id=article_id, quantity=quantity)
        except ValueError:
            return 400  # out of stock
        return 201
    return 404  # no such order


@router.get("order/view/{reference}", response=OrderSchema)
def order_details(request, order_id: int):
    if order := DetailedPurchaceOrder.aggregate_order(order_id):
        return order
    return 404
