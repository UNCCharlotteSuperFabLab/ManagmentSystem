from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from users.models import SpaceUser


# Name validator
name_validator = RegexValidator(
    regex=r"^[A-Za-z][A-Za-z'\- ]*$",
    message="Only letters, spaces, hyphens, and apostrophes are allowed."
)

# List of allowed email domains
ALLOWED_EMAIL_DOMAINS = [
    "charlotte.edu",
    "uncc.edu",
]

# Email domain validator
def validate_email_domain(value):
    domain = value.split("@")[-1].lower()

    if domain not in ALLOWED_EMAIL_DOMAINS:
        allowed = ", ".join(ALLOWED_EMAIL_DOMAINS)
        raise ValidationError(
            f"Email must be from one of the following domains: {allowed}"
        )


# User Form Class
class NewUserForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        validators=[name_validator],
        max_length=20,
        widget=forms.TextInput(attrs={
            "placeholder": "Jane",
            "class": "input is-text is-size-1",
            "autofocus": True,
        })
    )

    last_name = forms.CharField(
        required=True,
        validators=[name_validator],
        max_length=20,
        widget=forms.TextInput(attrs={
            "placeholder": "Doe",
            "class": "input is-text is-size-1",
        })
    )

    email = forms.EmailField(
        required=True,
        validators=[validate_email_domain],
        widget=forms.TextInput(attrs={
            "placeholder": "jdoe1@charlotte.edu",
            "class": "input is-text is-size-1",
        })
    )

    class Meta:
        model = SpaceUser
        fields = ['first_name', 'last_name', 'email']  # Include fields you want to collect
