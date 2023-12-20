from web.models import Order


def run():
    Order.objects.filter(orderitem__isnull=True).delete()
