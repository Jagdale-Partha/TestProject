from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('user', 'Donor'),
        ('ngo', 'NGO'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Made optional for initial migration
    address = models.TextField(blank=True, null=True)  # Made optional for initial migration
    verified = models.BooleanField(default=False)

    # Add these to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set",
        related_query_name="user",
    )

class DropOffLocation(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class DonationCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

class DonationRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('submitted', 'Submitted at Drop-off'),
        ('allocated', 'Allocated to NGO'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(DonationCategory, on_delete=models.CASCADE)
    items_description = models.TextField()
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    image = models.ImageField(upload_to='donation_images/')
    dropoff_location = models.ForeignKey(DropOffLocation, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.category.name}"

class NGORequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('fulfilled', 'Fulfilled'),
    )
    
    ngo = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(DonationCategory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ngo.username} - {self.category.name}"

class Allocation(models.Model):
    donation = models.ForeignKey(DonationRequest, on_delete=models.CASCADE)
    ngo_request = models.ForeignKey(NGORequest, on_delete=models.CASCADE)
    allocated_quantity = models.PositiveIntegerField()
    allocated_at = models.DateTimeField(auto_now_add=True)
    received = models.BooleanField(default=False)
    received_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.donation.id} allocated to {self.ngo_request.ngo.username}"