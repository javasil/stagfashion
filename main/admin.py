from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.forms import CheckboxSelectMultiple
from import_export.admin import ImportExportModelAdmin

from .models import Country
from .models import CustomUser
from .models import Province


@admin.register(Country)
class CountryAdmin(ImportExportModelAdmin):
    list_display = (
        "name",
        "currency_name",
        "symbol",
        "symbol_native",
        "decimal_digits",
        "code",
        "name_plural",
        "conversion_value",
    )
    search_fields = ("name",)


@admin.register(Province)
class ProvinceAdmin(ImportExportModelAdmin):
    list_display = ("name", "country", "shipping_charge")
    list_filter = ("country",)


class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "country", "is_staff", "is_superuser")
    list_filter = ("country",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "email", "country")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("username", "email", "password1", "password2", "country")}),
    )
    formfield_overrides = {models.ManyToManyField: {"widget": CheckboxSelectMultiple}}
    readonly_fields = ("last_login", "date_joined")
    autocomplete_fields = ("country",)


admin.site.register(CustomUser, CustomUserAdmin)
