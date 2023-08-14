from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Customer, Request, UpdateCustomer, UpdateProfile


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


class UpdateProfileForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone_number = forms.CharField()
    address = forms.CharField()
    postal_code = forms.CharField()
    twitter_handle = forms.CharField()

    class Meta:
        model = UpdateProfile
        fields = ["first_name", "last_name", "email",
                  "phone_number", "address", "postal_code",
                  "twitter_handle"]


class AnalysisForm(forms.Form):
    insert_words = forms.CharField(max_length=255)


class tweetScrape(forms.Form):
    insert_Twitter_thread_URL = forms.CharField(max_length=255)


class haterSearch(forms.Form):
    twitter_handle = forms.CharField(max_length=255)
