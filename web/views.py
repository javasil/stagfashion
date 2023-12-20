import uuid

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.shortcuts import resolve_url
from .tables import OrderTable
from phonepe.sdk.pg.env import Env
from phonepe.sdk.pg.payments.v1.models.request.pg_pay_request import PgPayRequest
from phonepe.sdk.pg.payments.v1.payment_client import PhonePePaymentClient
from django_tables2 import SingleTableView

from .forms import OrderForm
from .forms import OrderItemForm
from .forms import ProvinceSelectionForm
from .models import Branch
from .models import Category
from .models import Order
from .models import OrderItem
from .models import Product
from .models import Slider
from .models import SubCategory

merchant_id = settings.PHONEPE_MERCHANT_ID
salt_key = settings.PHONEPE_SALT_KEY
salt_index = 2
env = Env.PROD

# merchant_id = "PGTESTPAYUAT68"
# salt_key = "92c553c6-a487-48e9-9b4d-efaeab3624c7"
# salt_index = 1
# env = Env.SIMULATOR

should_publish_events = True
phonepe_client = PhonePePaymentClient(merchant_id, salt_key, salt_index, env)


def get_or_create_order(request):
    order = Order.objects.filter(session_key=request.session.session_key, is_ordered=False).first()
    if not order:
        order = Order.objects.create(session_key=request.session.session_key, is_ordered=False)
    return order


class IndexView(TemplateView):
    template_name = "web/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sliders"] = Slider.objects.filter(is_active=True)
        context["object_list"] = Product.objects.filter(is_active=True, is_highlited=True)
        return context


class ProductListView(ListView):
    template_name = "web/products.html"
    model = Product
    paginate_by = 52

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Products"
        return context


class CategoryProductListView(ListView):
    template_name = "web/products.html"
    model = Product
    paginate_by = 52

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.get_object().name
        return context

    def get_object(self):
        return get_object_or_404(Category, slug=self.kwargs["slug"])

    def get_queryset(self):
        return Product.objects.filter(is_active=True, subcategory__category=self.get_object())


class SubcategoryProductListView(ListView):
    template_name = "web/products.html"
    model = Product
    paginate_by = 52

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.get_object().name
        return context

    def get_object(self):
        return get_object_or_404(SubCategory, slug=self.kwargs["slug"])

    def get_queryset(self):
        return Product.objects.filter(is_active=True, subcategory=self.get_object())


class ProductView(DetailView):
    model = Product

    def get_form(self):
        return OrderItemForm(self.request.POST or None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_form()
        form.fields["product_option"].queryset = self.object.get_sizes()
        context["form"] = form
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        order = get_or_create_order(request)

        if form.is_valid():
            data = form.save(commit=False)
            product = data.product_option.product
            data.product = self.get_object()
            data.order = order
            data.price = product.offer_price if product.offer_price else product.price
            data.save()
        return redirect("web:product_view", slug=self.get_object().slug)


class RemoveCartItemView(View):
    def post(self, request, *args, **kwargs):
        order_item = OrderItem.objects.get(pk=kwargs["pk"])
        order_item.delete()
        return JsonResponse(
            {
                "success": True,
                "message": "Item removed successfully!",
                "data": {
                    "order_total": order_item.order.total(),
                    "order_items_count": order_item.order.get_items_count(),
                },
            }
        )


class CartView(View):
    template_name = "web/cart.html"
    model = Order
    form_class = ProvinceSelectionForm

    def get_object(self):
        return get_or_create_order(self.request)

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        form = self.form_class(instance=order)
        return render(request, self.template_name, {"object": order, "form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            order = self.get_object()
            order.province = form.cleaned_data["province"]
            order.save()
        print("cart page")
        return redirect("web:checkout", pk=self.get_object().pk)


class CheckoutView(DetailView):
    template_name = "web/checkout.html"
    form_class = OrderForm
    model = Order

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        form = self.form_class(instance=order)
        return render(request, self.template_name, {"object": order, "form": form})

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        form = self.form_class(request.POST or None, instance=order)

        if form.is_valid():
            data = form.save(commit=False)
            data.user = self.request.user
            data.is_orphan = False
            data.save()
            return redirect("web:payment", pk=order.pk)
        print(form.errors)
        return render(request, self.template_name, {"object": order, "form": form})

    def get_success_url(self):
        return reverse_lazy("web:payment", kwargs={"pk": self.object.pk})


class AboutView(TemplateView):
    template_name = "web/about.html"


class ContactView(TemplateView):
    template_name = "web/contact.html"


class PrivacyPolicyView(TemplateView):
    template_name = "web/privacy_policy.html"


class TermsAndConditionsView(TemplateView):
    template_name = "web/terms_and_conditions.html"


class CookiesPolicyView(TemplateView):
    template_name = "web/cookies_policy.html"


class RefundPolicyView(TemplateView):
    template_name = "web/refund_policy.html"


class BranchView(DetailView):
    model = Branch
    template_name = "web/branch_detail.html"


class TrackOrdersView(ListView):
    template_name = "web/trackorders.html"
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("query")
        print(query)
        return Order.objects.filter(is_ordered=True, order_id=query) if query else Order.objects.none()


class PaymentView(DetailView):
    template_name = "web/payment.html"
    model = Order

    def get(self, request, pk, *args, **kwargs):
        order = self.get_object()
        unique_id = uuid.uuid4()
        order.unique_transaction_id = unique_id
        order.save()

        # PHONEPE PAYMENT GATEWAY STARTS HERE
        unique_transaction_id = str(order.unique_transaction_id)
        ui_redirect_url = request.build_absolute_uri("/") + "complete-order/" + str(order.id) + "/"
        s2s_callback_url = request.build_absolute_uri("/") + "callback/verify/" + str(order.id) + "/"
        amount = int(order.payable * 100)
        id_assigned_to_user_by_merchant = f"STAG_{order.id}"

        print("\nInitialising pay page request .......", "\n\n")
        pay_page_request = PgPayRequest.pay_page_pay_request_builder(
            merchant_transaction_id=unique_transaction_id,
            amount=amount,
            merchant_user_id=id_assigned_to_user_by_merchant,
            callback_url=s2s_callback_url,
            redirect_url=ui_redirect_url,
        )
        print("pay_page_request", "\n", pay_page_request, "\n\n")

        pay_page_response = phonepe_client.pay(pay_page_request)
        print("pay_page_response", "\n", pay_page_response, "\n\n")

        pay_page_url = pay_page_response.data.instrument_response.redirect_info.url
        return redirect(pay_page_url)
        return True


class PaymentCallback(DetailView):
    template_name = "web/callback.html"
    model = Order

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        unique_transaction_id = str(order.unique_transaction_id)
        body_string = request.body
        x_verify_header_data = request.headers.get('X-VERIFY')
        is_valid = phonepe_client.verify_response(x_verify=x_verify_header_data, response=body_string)

        print("data", "\n", body_string, "\n\n")
        print("x_verify_header_data", "\n", x_verify_header_data, "\n\n")
        print("is_valid", "\n", is_valid, "\n\n")

        return render(request, self.template_name, {})


class CompleteOrderView(DetailView):
    model = Order
    template_name = "web/complete-order.html"

    def get_object(self):
        return get_object_or_404(Order, pk=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        unique_transaction_id = str(order.unique_transaction_id)
        transaction_status_response = phonepe_client.check_status(merchant_transaction_id=unique_transaction_id)        
        if transaction_status_response.success:
            print(order, transaction_status_response.success, transaction_status_response.data.state)
            if str(transaction_status_response.data.state) == "COMPLETED":
                order.is_ordered = True
                order.save()
        context = {
            "object": order,
            "transaction_status_response": transaction_status_response,
        }
        return render(request, self.template_name, context)


class OrderListView(SingleTableView):
    template_name = "web/orders.html"
    model = Order
    table_class = OrderTable
    paginate_by = 50

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect(resolve_url(settings.LOGIN_URL))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Orders"
        return context

    def get_queryset(self):
        return Order.objects.filter(is_ordered=True)


class OrderDetailView(DetailView):
    model = Order
    template_name = "web/order_detail.html"

    def get_queryset(self):
        return Order.objects.filter(is_ordered=True)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect(resolve_url(settings.LOGIN_URL))
        return super().dispatch(request, *args, **kwargs)


def refresh_orders(request):
    Order.objects.filter(orderitem__isnull=True).delete()
    orders_list = Order.objects.filter(is_ordered=False, status="Pending", province__isnull=False, first_name__isnull=False, last_name__isnull=False)
    for order in orders_list:
        merchant_id = settings.PHONEPE_MERCHANT_ID
        merchant_transaction_id = str(order.unique_transaction_id)
        transaction_status_response = phonepe_client.check_status(merchant_transaction_id=merchant_transaction_id)
        if transaction_status_response.success:
            print(order, transaction_status_response.success, transaction_status_response.data.state)
            if str(transaction_status_response.data.state) == "COMPLETED":
                order.is_ordered = True
                order.save()
    return redirect("web:order_list")