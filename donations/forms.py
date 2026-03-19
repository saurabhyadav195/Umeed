from django import forms
from .models import Donation
from location.models import Address
from django.utils import timezone

class DonationForm(forms.ModelForm):

    expiry_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Donation
        fields = [
            'address',
            'food_name',
            'quantity',
            'description',
            'expiry_time',
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        # Only show user's own branches
        self.fields['address'].queryset = Address.objects.filter(user=user)

    def clean_expiry_time(self):
        expiry = self.cleaned_data['expiry_time']
        if expiry <= timezone.now():
            raise forms.ValidationError("Expiry time must be in the future.")
        return expiry