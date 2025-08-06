from datetime import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import *
from .forms import *
from django.db.models import Q
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


def is_admin(user):
    return user.user_type == 'admin'

def is_ngo(user):
    return user.user_type == 'ngo'

def is_donor(user):
    return user.user_type == 'user'

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Only allow donor registration through this form
            user.user_type = 'user'
            user.save()
            messages.success(request, 'Registration successful! Please wait for admin approval.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'donation_app/register.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.user_type == 'admin':
        return admin_dashboard(request)
    elif request.user.user_type == 'ngo':
        return ngo_dashboard(request)
    else:
        return user_dashboard(request)

@login_required
@user_passes_test(is_donor)
def user_dashboard(request):
    donations = DonationRequest.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'donations': donations,
        'status_counts': {
            'pending': donations.filter(status='pending').count(),
            'approved': donations.filter(status='approved').count(),
            'submitted': donations.filter(status='submitted').count(),
            'allocated': donations.filter(status='allocated').count(),
        }
    }
    return render(request, 'donation_app/user_dashboard.html', context)

@login_required
@user_passes_test(is_ngo)
def ngo_dashboard(request):
    requests = NGORequest.objects.filter(ngo=request.user).order_by('-created_at')
    allocations = Allocation.objects.filter(ngo_request__ngo=request.user)
    
    context = {
        'requests': requests,
        'allocations': allocations,
        'status_counts': {
            'pending': requests.filter(status='pending').count(),
            'approved': requests.filter(status='approved').count(),
            'fulfilled': requests.filter(status='fulfilled').count(),
        }
    }
    return render(request, 'donation_app/ngo_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    pending_donations = DonationRequest.objects.filter(status='pending')
    pending_requests = NGORequest.objects.filter(status='pending')
    submitted_donations = DonationRequest.objects.filter(status='submitted')
    
    context = {
        'pending_donations': pending_donations,
        'pending_requests': pending_requests,
        'submitted_donations': submitted_donations,
        'donation_count': DonationRequest.objects.count(),
        'ngo_count': CustomUser.objects.filter(user_type='ngo').count(),
        'user_count': CustomUser.objects.filter(user_type='user').count(),
    }
    return render(request, 'donation_app/admin_dashboard.html', context)

@login_required
@user_passes_test(is_donor)
def create_donation(request):
    if request.method == 'POST':
        form = DonationRequestForm(request.POST, request.FILES)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.user = request.user
            # Simple spam check - reject if same user has made more than 3 pending requests
            pending_count = DonationRequest.objects.filter(user=request.user, status='pending').count()
            if pending_count >= 3:
                messages.warning(request, 'You have too many pending donations. Please wait for approval of previous requests.')
                return redirect('dashboard')
            
            donation.save()
            messages.success(request, 'Donation request submitted successfully!')
            return redirect('dashboard')
    else:
        form = DonationRequestForm()
    return render(request, 'donation_app/donation_form.html', {'form': form})

@login_required
@user_passes_test(is_ngo)
def create_request(request):
    if request.method == 'POST':
        form = NGORequestForm(request.POST)
        if form.is_valid():
            ngo_request = form.save(commit=False)
            ngo_request.ngo = request.user
            ngo_request.save()
            messages.success(request, 'Request submitted successfully!')
            return redirect('dashboard')
    else:
        form = NGORequestForm()
    return render(request, 'donation_app/request_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def update_donation_status(request, pk):
    donation = get_object_or_404(DonationRequest, pk=pk)
    if request.method == 'POST':
        form = DonationStatusUpdateForm(request.POST, instance=donation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Donation status updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = DonationStatusUpdateForm(instance=donation)
    return render(request, 'donation_app/update_donation_status.html', {'form': form, 'donation': donation})

@login_required
@user_passes_test(is_admin)
def update_request_status(request, pk):
    ngo_request = get_object_or_404(NGORequest, pk=pk)
    if request.method == 'POST':
        form = NGORequestStatusUpdateForm(request.POST, instance=ngo_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Request status updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = NGORequestStatusUpdateForm(instance=ngo_request)
    return render(request, 'donation_app/update_request_status.html', {'form': form, 'ngo_request': ngo_request})

@login_required
@user_passes_test(is_admin)
def allocate_items(request):
    if request.method == 'POST':
        form = AllocationForm(request.POST)
        if form.is_valid():
            allocation = form.save()
            # Update donation status
            allocation.donation.status = 'allocated'
            allocation.donation.save()
            # Update NGO request status if fully fulfilled
            total_allocated = Allocation.objects.filter(ngo_request=allocation.ngo_request).aggregate(sum('allocated_quantity'))['allocated_quantity__sum'] or 0
            if total_allocated >= allocation.ngo_request.quantity:
                allocation.ngo_request.status = 'fulfilled'
                allocation.ngo_request.save()
            messages.success(request, 'Items allocated successfully!')
            return redirect('admin_dashboard')
    else:
        form = AllocationForm()
    
    # Only show submitted donations and approved requests
    form.fields['donation'].queryset = DonationRequest.objects.filter(status='submitted')
    form.fields['ngo_request'].queryset = NGORequest.objects.filter(status='approved')
    
    return render(request, 'donation_app/allocate_items.html', {'form': form})

@login_required
@user_passes_test(is_ngo)
def mark_received(request, pk):
    allocation = get_object_or_404(Allocation, pk=pk, ngo_request__ngo=request.user)
    if request.method == 'POST':
        allocation.received = True
        allocation.received_at = timezone.now()
        allocation.save()
        messages.success(request, 'Thank you for confirming receipt of items!')
        return redirect('dashboard')
    return render(request, 'donation_app/mark_received.html', {'allocation': allocation})

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Register'))