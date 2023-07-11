from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Customer, Request, UpdateCustomer


class RegistrationForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField()
    password_confirmation = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone_number = forms.IntegerField()
    address = forms.CharField()
    postal_code = forms.IntegerField()
    twitter_handle = forms.CharField()
    status = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Request
        fields = ["username", "password", "password_confirmation", "first_name", "last_name",
                  "email", "phone_number", "address", "postal_code",
                  "twitter_handle"]


class CreationForm(UserCreationForm):
    password1 = forms.CharField(label="Password")
    password2 = forms.CharField(label="Password confirmation")
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone_number = forms.IntegerField()
    address = forms.CharField()
    postal_code = forms.IntegerField()
    twitter_handle = forms.CharField()
    status = forms.ChoiceField(choices=Customer.STATUS)

    class Meta:
        model = Customer
        fields = ["username", "password1", "password2", "first_name", "last_name",
                  "email", "phone_number", "address", "postal_code",
                  "twitter_handle", "status"]


class UpdateForm(forms.ModelForm):
    username = forms.CharField()
    password1 = forms.CharField(label="Password")
    password2 = forms.CharField(label="Password confirmation")
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone_number = forms.IntegerField()
    address = forms.CharField()
    postal_code = forms.IntegerField()
    twitter_handle = forms.CharField()

    class Meta:
        model = UpdateCustomer
        fields = ["username", "password1", "password2", "first_name", "last_name",
                  "email", "phone_number", "address", "postal_code",
                  "twitter_handle"]


# class UpdateForm(UserChangeForm):
#     password = None
#
#     first_name = forms.CharField(required=False)
#     last_name = forms.CharField(required=False)
#     email = forms.EmailField(required=False)
#     phone_number = forms.IntegerField(required=False)
#     address = forms.CharField(required=False)
#     postal_code = forms.IntegerField(required=False)
#     twitter_handle = forms.CharField(required=False)
#
#     class Meta:
#         model = Customer
#         fields = ["first_name", "last_name", "email", "phone_number",
#                   "address", "postal_code", "twitter_handle"]


class AnalysisForm(forms.Form):
    tweets = forms.CharField(max_length=255)
