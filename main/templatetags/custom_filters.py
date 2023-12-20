from django.template import Library
from web.models import AvailableSize


register = Library()


@register.filter
def get_currency(value, user=None):
    return f"₹ {value}"


@register.filter
def check_stock(value):
    size = AvailableSize.objects.get(id=int(str(value)))
    if size.is_stockout:
        return "disabled"
    else:
        return ""
