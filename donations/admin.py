from django.contrib import admin
from .models import Donation, DonationRequest

admin.site.register(Donation)
admin.site.register(DonationRequest)