from typing import Optional
from ninja import Router, Form

from inventory.models import Category
from .models import Tax, CategoryTax
from .schemas import TaxSchema, CategoryTaxScheme

router = Router()


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
