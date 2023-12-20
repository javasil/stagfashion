import uuid

from colorfield.fields import ColorField
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField


class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = ThumbnailerImageField(upload_to="web/categories")
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(
        "Mark as Active", default=True, help_text="Disabled Item will not be visible in the website"
    )

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Categories"

    def get_subcategories(self):
        return SubCategory.objects.filter(is_active=True, category=self)

    def get_products_count(self):
        return Product.objects.filter(subcategory__category=self).count()

    def get_absolute_url(self):
        return reverse("web:category_list", kwargs={"slug": self.slug})

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    size_chart = models.ImageField(upload_to="web/size_charts", blank=True, null=True)
    is_active = models.BooleanField(
        "Mark as Active", default=True, help_text="Disabled Item will not be visible in the website"
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Sub Categories"

    def get_products(self):
        return Product.objects.filter(is_active=True, subcategory=self)

    def get_productcount(self):
        return self.get_products().count()

    def get_absolute_url(self):
        return reverse("web:subcategory_list", kwargs={"slug": self.slug})

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Product(models.Model):
    STATUS_CHOICES = (("Available", "Available"), ("LaunchingSoon", "Launching Soon"))
    BOOL_CHOICES = ((True, "Yes"), (False, "NO"))

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = ThumbnailerImageField(upload_to="web/products")
    item_status = models.CharField(max_length=100, choices=STATUS_CHOICES, default="Available")
    badge = models.ForeignKey("Badge", on_delete=models.CASCADE, blank=True, null=True)
    is_highlited = models.BooleanField("Show in Homepage", default=False, choices=BOOL_CHOICES)
    is_active = models.BooleanField(
        "Mark as Active",
        default=True,
        help_text="Disabled Item will not be visible in the website",
        choices=BOOL_CHOICES,
    )
    priority = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Product"
        ordering = ("-priority",)

    def get_absolute_url(self):
        return reverse("web:product_view", kwargs={"slug": self.slug})

    def get_images(self):
        return ProductImage.objects.filter(product=self)

    def get_sizes(self):
        return AvailableSize.objects.filter(product=self)

    def get_size_codes(self):
        qs = ProductSize.objects.filter(availablesize__in=self.get_sizes())
        dataset = set(qs.values_list('short_code', flat=True).distinct())
        return sorted(dataset, key=lambda x: x)

    def ordered_count(self):
        orders = OrderItem.objects.filter(order__is_ordered=True, product_option__product=self)
        return sum([x.quantity for x in orders])

    def max_stock(self):
        return max([x.opening_stock for x in self.get_sizes()])

    def __str__(self):
        return self.name


class Badge(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Badges"

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = ThumbnailerImageField(upload_to="web/products")

    def __str__(self):
        return self.product.name


class ProductSize(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    short_code = models.CharField(max_length=255)

    class Meta:
        verbose_name = _("Product Size")
        verbose_name_plural = _("Product Sizes")
        ordering = ("name",)

    def __str__(self):
        return f"{self.name}"


class AvailableSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(ProductSize, on_delete=models.CASCADE)
    opening_stock = models.IntegerField()
    item_code = models.CharField(max_length=255, blank=True, null=True)

    waist = models.CharField(max_length=100, blank=True, null=True)
    rise = models.CharField(max_length=100, blank=True, null=True)
    thighs = models.CharField("Thighs", max_length=100, blank=True, null=True)
    length = models.CharField("Outseam Length", max_length=100, blank=True, null=True)
    inseem_length = models.CharField("Inseam Length", max_length=100, blank=True, null=True)
    bottom_size = models.CharField("Bottom Hem", max_length=100, blank=True, null=True)
    is_stockout = models.BooleanField(default=False, choices=((True, "Yes"), (False, "No")))

    def status(self):
        ordered_count = self.ordered_count()
        max_stock = max([x.opening_stock for x in self.get_sizes()])
        if ordered_count >= max_stock:
            return "OutofStock"
        else:
            return self.item_status

    def ordered_count(self):
        orders = OrderItem.objects.filter(order__is_ordered=True, product_option=self)
        return sum([x.quantity for x in orders])

    class Meta:
        verbose_name = _("Available Size")
        verbose_name_plural = _("Available Sizes")
        ordering = ("product",)

    def __str__(self):
        return f"{self.size.code}"


class Slider(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    image = ThumbnailerImageField("Desktop Image", upload_to="web/sliders")
    mini_image = ThumbnailerImageField("Mobile Image", upload_to="web/sliders")
    button_text = models.CharField(max_length=100, default="Shop Now")
    button_link = models.CharField(max_length=100, default="/products")
    is_active = models.BooleanField(
        "Mark as Active", default=True, help_text="Disabled Item will not be visible in the website"
    )
    text_color = ColorField(default="#000")

    class Meta:
        ordering = ("name",)
        verbose_name = "Slider"
        verbose_name_plural = "Sliders"

    def __str__(self):
        return self.name if self.name else self.button_text


class Branch(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=100)
    address = models.TextField(max_length=100)
    is_active = models.BooleanField(
        "Mark as Active", default=True, help_text="Disabled Item will not be visible in the website"
    )
    photo = ThumbnailerImageField(upload_to="web/branches", blank=True, null=True)
    is_launched = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse("web:branch_view", kwargs={"slug": self.slug})

    class Meta:
        ordering = ("name",)
        verbose_name = "Branch"
        verbose_name_plural = "Branches"

    def __str__(self):
        return self.name


class SocialMedia(models.Model):
    SOCIAL_CHOICES = (
        ("lni-behance-original", "behance"),
        ("lni-facebook-original", "facebook"),
        ("lni-instagram-original", "instagram"),
        ("lni-linkedin-original", "linkedin"),
        ("lni-paypal-original", "paypal"),
        ("lni-spotify-original", "spotify"),
        ("lni-telegram-original", "telegram"),
        ("lni-twitter-original", "twitter"),
    )
    media = models.CharField(choices=SOCIAL_CHOICES, max_length=50)
    link = models.URLField()

    def __str__(self):
        return self.media


def generate_order_id():
    timestamp = timezone.now().strftime("%y%m%d")
    unique_id = uuid.uuid4().hex[:6]
    return f"{timestamp}{unique_id.upper()}"


class Order(models.Model):
    unique_transaction_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, blank=True, null=True)
    created = models.DateTimeField(db_index=True, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    order_id = models.CharField(max_length=220, default=generate_order_id)
    session_key = models.CharField(max_length=220, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    province = models.ForeignKey(
        "main.Province", verbose_name="State / Province", on_delete=models.CASCADE, blank=True, null=True
    )
    payable = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_orphan = models.BooleanField(default=True)
    is_ordered = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    address_line_1 = models.CharField("Address 1", max_length=100, blank=True, null=True)
    address_line_2 = models.CharField("Address 2", max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    mobile = models.CharField(max_length=100, blank=True, null=True)
    alternate_mobile = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=100,
        default="Pending",
        choices=(
            ("Pending", "Pending"),
            ("Placed", "Order Placed"),
            ("Shipped", "Order Shipped"),
            ("InTransit", "In Transit"),
            ("Delivered", "Order Delivered"),
            ("Cancelled", "Order Cancelled"),
        ),
    )

    def get_items(self):
        return OrderItem.objects.filter(order=self)

    def get_updates(self):
        return OrderUpdate.objects.filter(order=self)

    def get_items_count(self):
        return self.get_items().count()

    def total(self):
        return sum([x.subtotal() for x in self.get_items()])

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return f"{self.order_id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_option = models.ForeignKey(AvailableSize, verbose_name="Select Size:",on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 11)])
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.product_option.product}: {self.product_option.size} - {self.quantity}"

    def subtotal(self):
        return self.price * self.quantity


class OrderUpdate(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("timestamp",)

    def __str__(self):
        return self.title
