from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'address', 'user_type')

class DonationRequestForm(forms.ModelForm):
    class Meta:
        model = DonationRequest
        fields = ('category', 'items_description', 'quantity', 'image', 'dropoff_location')
        widgets = {
            'items_description': forms.Textarea(attrs={'rows': 3}),
        }

class NGORequestForm(forms.ModelForm):
    class Meta:
        model = NGORequest
        fields = ('category', 'quantity', 'purpose')
        widgets = {
            'purpose': forms.Textarea(attrs={'rows': 3}),
        }

class DonationStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = DonationRequest
        fields = ('status', 'rejection_reason')
        widgets = {
            'rejection_reason': forms.Textarea(attrs={'rows': 3}),
        }

class NGORequestStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = NGORequest
        fields = ('status',)

class AllocationForm(forms.ModelForm):
    class Meta:
        model = Allocation
        fields = ('donation', 'ngo_request', 'allocated_quantity')