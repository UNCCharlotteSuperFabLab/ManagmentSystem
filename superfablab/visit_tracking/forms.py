from django import forms
from users.models import SpaceUser

class NewUserForm(forms.ModelForm):
    class Meta:
        model = SpaceUser
        fields = ['first_name', 'last_name', 'email']  # Include fields you want to collect
