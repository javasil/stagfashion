from web.models import Order


def run():
    Order.objects.filter(is_ordered=False).delete()
