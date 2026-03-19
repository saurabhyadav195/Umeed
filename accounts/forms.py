from django import forms
from django.contrib.auth import get_user_model
from .models import VerificationDocument

User = get_user_model()

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'role',
            'organization_name',
            'contact_person',
            'phone',
            'email',
            'password',
            'street',
            'city',
            'district',
            'state',
            'pincode',
            'agreed_terms',
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        if not cleaned_data.get("agreed_terms"):
            raise forms.ValidationError("You must agree to Terms & Conditions")

        return cleaned_data

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = VerificationDocument
        fields = ['document_type', 'file']