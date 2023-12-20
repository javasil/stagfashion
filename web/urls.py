from django.urls import path

from . import views


app_name = "web"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("products/", views.ProductListView.as_view(), name="product_list"),
    path("category/<str:slug>/", views.CategoryProductListView.as_view(), name="category_list"),
    path("subcategory/<str:slug>/", views.SubcategoryProductListView.as_view(), name="subcategory_list"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("privacy-policy/", views.PrivacyPolicyView.as_view(), name="privacy_policy"),
    path("terms-and-conditions/", views.TermsAndConditionsView.as_view(), name="terms_and_conditions"),
    path("cookies-policy/", views.CookiesPolicyView.as_view(), name="cookies_policy"),
    path("refund-policy/", views.RefundPolicyView.as_view(), name="refund_policy"),
    path("product/<str:slug>/", views.ProductView.as_view(), name="product_view"),
    path("branch/<str:slug>/", views.BranchView.as_view(), name="branch_view"),
    path("checkout/<str:pk>/", views.CheckoutView.as_view(), name="checkout"),
    path("payment/<str:pk>/", views.PaymentView.as_view(), name="payment"),
    path("callback/verify/<str:pk>/", views.PaymentCallback.as_view(), name="payment_callback"),
    path("complete-order/<str:pk>/", views.CompleteOrderView.as_view(), name="complete_order"),
    path("track/", views.TrackOrdersView.as_view(), name="track_orders"),
    path("cart/", views.CartView.as_view(), name="cart"),
    path("order/delete/<str:pk>/", views.RemoveCartItemView.as_view(), name="order_delete"),
    path("orders/", views.OrderListView.as_view(), name="order_list"),
    path("orders/refresh/", views.refresh_orders, name="order_refresh"),
    path("order/<str:pk>/", views.OrderDetailView.as_view(), name="order_view"),
]
