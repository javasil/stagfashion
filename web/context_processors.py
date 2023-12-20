from main.models import Country

from .models import Branch
from .models import Category
from .models import Order
from .models import SocialMedia


def get_or_create_order(request):
    order = Order.objects.filter(session_key=request.session.session_key, is_ordered=False).first()
    if not order:
        # If no existing order, create a new one
        order = Order.objects.create(session_key=request.session.session_key, is_ordered=False)
    return order


def main_context(request):
    if not request.session.session_key:
        request.session.create()

    order = get_or_create_order(request)
    order.subtotal = order.total()
    shipping = order.province.shipping_charge if order.province else 0
    order.payable = order.total() + shipping
    order.save()
    cart_items = order.get_items()

    if not Country.objects.filter(name="India").exists:
        Country(
            name="India",
            currency_name="Indian Rupee",
            symbol="Rs",
            symbol_native="₹",
            decimal_digits=2,
            code="INR",
            name_plural="Indian rupees",
            conversion_value="0.01",
        ).save()

    return {
        "domain": request.META["HTTP_HOST"],
        "socials": SocialMedia.objects.all(),
        "categories": Category.objects.filter(is_active=True),
        "branches": Branch.objects.filter(is_active=True),
        "order": order,
        "cart_items": cart_items,
        "file_version": "2.5",
    }
