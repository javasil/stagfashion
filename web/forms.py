from django import forms

from .models import Order
from .models import OrderItem


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ("product_option", "quantity")
        widgets = {
            "product_option": forms.RadioSelect(attrs={"class": "form-control", "required": "required"}),
            "quantity": forms.Select(attrs={"class": "form-control", "required": "required"}),
        }


class ProvinceSelectionForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("province",)
        widgets = {"province": forms.Select(attrs={"class": "form-control", "required": "required"})}


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            "first_name",
            "last_name",
            "address_line_1",
            "address_line_2",
            "city",
            "district",
            "province",
            "pincode",
            "mobile",
            "alternate_mobile",
            "notes",
        )
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "First Name", "required": "required"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Last Name", "required": "required"}
            ),
            "address_line_1": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Address Line 1", "required": "required"}
            ),
            "address_line_2": forms.TextInput(attrs={"class": "form-control", "placeholder": "Address Line 2"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "City", "required": "required"}),
            "district": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "District", "required": "required"}
            ),
            "province": forms.Select(attrs={"class": "form-control", "required": "required"}),
            "pincode": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Pincode", "required": "required"}
            ),
            "mobile": forms.TextInput(attrs={"class": "form-control", "placeholder": "Mobile", "required": "required"}),
            "alternate_mobile": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Alternate Mobile", "required": "required"}
            ),
            "notes": forms.Textarea(attrs={"class": "form-control", "placeholder": "Notes"}),
        }
