from django.db import models
from django.conf import settings
from location.models import Address
from django.utils import timezone

class Donation(models.Model):

    STATUS_CHOICES = (
        ('available', 'Available'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    )

    restaurant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)

    food_name = models.CharField(max_length=200)
    quantity = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    expiry_time = models.DateTimeField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)

    def check_and_update_expiry(self):
        if self.expiry_time <= timezone.now() and self.status != 'expired':
            self.status = 'expired'
            self.save()

    def __str__(self):
        return self.food_name
    
class DonationRequest(models.Model):

    REQUEST_STATUS = (
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    ngo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='requested')
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('donation', 'ngo')  # prevents duplicate request

    def __str__(self):
        return f"{self.ngo.organization_name} → {self.donation.food_name}"
    

class DonationQuery(models.Model):

    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Query for {self.donation.food_name}"