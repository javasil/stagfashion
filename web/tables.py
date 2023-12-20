import django_tables2 as tables
from .models import Order


class OrderTable(tables.Table):
    order_id = tables.Column(verbose_name="Order ID", linkify=("web:order_view", {"pk": tables.A("pk")}))

    class Meta:
        model = Order
        template_name = "django_tables2/bootstrap.html"
        fields = (
            "order_id",
            "first_name",
            "last_name",
            "city",
            "district",
            "mobile",
            "subtotal",
            "completed_at",
            "status",
        )
        attrs = {"class": "table table-striped table-bordered table-hover"}
