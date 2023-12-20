from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Country(models.Model):
    name = models.CharField(_("Country Name"), max_length=128)
    currency_name = models.CharField(_("Currency Name"), max_length=128)
    symbol = models.CharField("Currency Symbol", max_length=128)
    symbol_native = models.CharField("Native Symbol", max_length=128)
    decimal_digits = models.PositiveIntegerField("Decimal Digits")
    code = models.CharField("Currency Code", max_length=128)
    name_plural = models.CharField("Plural Name", max_length=128)
    conversion_value = models.DecimalField(decimal_places=2, max_digits=15)

    class Meta:
        ordering = ("name",)
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")

    def __str__(self):
        return self.name


class Province(models.Model):
    name = models.CharField(_("State/Province Name"), max_length=128)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    shipping_charge = models.DecimalField(
        decimal_places=2, max_digits=15, help_text="In the currency this state follows"
    )

    class Meta:
        ordering = ("name",)
        verbose_name = _("State & Shipping Charge")
        verbose_name_plural = _("States & Shipping Charges")

    def __str__(self):
        return f"{self.country.name} - {self.name}"


class CustomUser(AbstractUser):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, default=5)

    def __str__(self):
        return self.username
