import admin_thumbnails
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin, ExportActionModelAdmin

from .models import AvailableSize
from .models import Badge
from .models import Branch
from .models import Category
from .models import Order
from .models import OrderItem
from .models import OrderUpdate
from .models import Product
from .models import ProductImage
from .models import ProductSize
from .models import Slider
from .models import SocialMedia
from .models import SubCategory
from django.utils.html import format_html


class ProductImageInline(admin.TabularInline):
    extra = 0
    model = ProductImage
    fields = ('image_preview', 'image',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        return format_html('<img src="{}" width="80" height="100" />', obj.image.url)
    
    image_preview.short_description = 'Image Preview'


class OrderItemInline(admin.TabularInline):
    extra = 0
    model = OrderItem


class OrderUpdateInline(admin.StackedInline):
    extra = 0
    model = OrderUpdate


class AvailableSizeInline(admin.TabularInline):
    model = AvailableSize
    extra = 0
    autocomplete_fields = ("size",)


@admin.register(ProductSize)
class ProductSizeAdmin(ImportExportModelAdmin):
    list_display = ("name", "code", "short_code")
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ("name", "slug", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("name",)
    list_filter = ("is_active",)


@admin.register(SubCategory)
class SubCategoryAdmin(ImportExportModelAdmin):
    list_display = ("name", "slug", "is_active", "get_productcount", "size_chart")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("name",)
    list_filter = ("is_active", "category")


@admin.register(Product)
@admin_thumbnails.thumbnail("image")
class ProductAdmin(ImportExportModelAdmin):
    list_display = (
        "name",
        "subcategory",
        "badge",
        "priority",
        "sale_price",
        "offer_price",
        "is_highlited",
        "max_stock",
        "ordered_count",
    )
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("item_status", "subcategory", "is_highlited", "badge", "is_active")
    list_editable = ("is_highlited",)
    inlines = (ProductImageInline, AvailableSizeInline)
    search_fields = ("name",)
    ordering = ("name",)
    autocomplete_fields = ("subcategory",)

    class Media:
        css = {"all": ("extra_admin/css/style.css",)}


@admin.register(Slider)
class SliderAdmin(ImportExportModelAdmin):
    list_display = ("__str__", "is_active")
    search_fields = ("name",)
    ordering = ("name",)
    list_filter = ("is_active",)


@admin.register(Branch)
class BranchAdmin(ImportExportModelAdmin):
    list_display = ("name", "is_active", "is_launched", "address", "phone", "email")
    search_fields = ("name",)
    ordering = ("name",)
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(SocialMedia)
class SocialMediaAdmin(ImportExportModelAdmin):
    list_display = ("media", "link")
    search_fields = ("media",)


@admin.register(Order)
class OrderAdmin(ExportActionModelAdmin):
    list_display = (
        "order_id",
        "first_name",
        "last_name",
        "city",
        "pincode",
        "status",
        "subtotal",
        "province",
        "shipping",
        "payable",
        "is_ordered",
        "created",
        "updated",
    )
    readonly_fields = (
        "order_id",
        "first_name",
        "last_name",
        "city",
        "pincode",
        "subtotal",
        "shipping",
        "completed_at",
        "payable",
        "is_ordered",
        "is_orphan",
        "unique_transaction_id",
        "created",
        "updated",
        "session_key",
        "province",
        "address_line_1",
        "address_line_2",
        "mobile",
    )
    search_fields = ("order_id", "first_name", "last_name", "city", "pincode")
    list_filter = ("is_ordered", "status", "is_orphan")
    inlines = (OrderItemInline, OrderUpdateInline)

    def get_queryset(self, request):
        qs = super().get_queryset(request).filter(is_ordered=True)
        return qs

    def has_add_permission(self, request):
        return False


@admin.register(Badge)
class BadgeAdmin(ImportExportModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
