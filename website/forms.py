from django import forms
from django.contrib.auth.forms import UserCreationForm

from . import models



class RegisterUserForm(UserCreationForm):
    class Meta:
        model = models.UserAccount
        fields = ['username','first_name','last_name','email','telephone','password1','password2']


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = models.UserAddress
        fields = ['city','post_address','address']


class UpdateUserForm(forms.ModelForm):
    class  Meta:
        model = models.UserAccount
        fields = ['username','first_name','last_name','email','telephone']


class ContactForm(forms.ModelForm):
    class Meta:
        model = models.Contact
        fields = ['name','email','message']