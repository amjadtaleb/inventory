from ninja import Router, Form
from ninja.pagination import paginate, LimitOffsetPagination
from ninja.errors import HttpError
from django.db.utils import IntegrityError

from inventory.models import Category
from .models import Tax, CategoryTax, PurchaceOrder, DetailedPurchaceOrder
from .schemas import TaxSchema, CategoryTaxScheme, OrderSchema, OrderBasicSchema

router = Router(tags=["Orders"])


@router.get("/taxes", response=list[TaxSchema])
@paginate(LimitOffsetPagination)
def list_taxes(request):
    return Tax.objects.all()


@router.post("/taxes/add")
def add_tax(request, tax: Form[TaxSchema]):
    tax, created = Tax.objects.get_or_create(
        reference=tax.reference,
        defaults={"value": tax.value},
    )  # type: ignore
    if created:
        return 201
    raise HttpError(400, "Duplicate")


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
        raise HttpError(404, "Cateory not found")
    raise HttpError(404, "Tax not found")


@router.get("orders", response=list[OrderBasicSchema])
@paginate(LimitOffsetPagination)
def list_orders(request):
    return PurchaceOrder.objects.all()


@router.post("order/create")
def create_order(request, reference: str):
    try:
        PurchaceOrder.objects.create(
            reference=reference,
            created_by_id=1,  # assuming super user was created
        )
        return 201
    except IntegrityError:
        raise HttpError(400, "Duplicate")


@router.post("order/updateitem/{reference}")
def update_order(request, reference: str, article_id: int, quantity_change: int):
    """Add or remove items from an order.
    
    **quantity_change** could be positive to add items to the order or negative to remove them
    """
    if quantity_change == 0:
        raise HttpError(400, "Change cannot be zero")
    if order := PurchaceOrder.objects.filter(reference=reference).first():
        try:
            order.update_article(article_id=article_id, quantity=quantity_change)
        except ValueError as e:
            raise HttpError(400, e.args[0])
        return 201
    raise HttpError(404, "Order not found")


@router.get("order/view/{reference}", response=OrderSchema | int)
def order_details(request, order_id: int):
    if order := DetailedPurchaceOrder.aggregate_order(order_id):
        return order
    raise HttpError(404, "Not found")
