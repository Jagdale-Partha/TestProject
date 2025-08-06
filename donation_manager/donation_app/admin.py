from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'user_type', 'verified')
    list_filter = ('user_type', 'verified')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'address', 'user_type', 'verified')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'address', 'user_type')}),
    )

class DonationRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'category', 'dropoff_location')
    search_fields = ('user__username', 'items_description')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_selected', 'reject_selected']
    
    def approve_selected(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f"{queryset.count()} donations approved successfully.")
    approve_selected.short_description = "Approve selected donations"
    
    def reject_selected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} donations rejected successfully.")
    reject_selected.short_description = "Reject selected donations"

class NGORequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'ngo', 'category', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('ngo__username', 'purpose')
    readonly_fields = ('created_at', 'updated_at')

class AllocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'donation', 'ngo_request', 'allocated_quantity', 'received')
    list_filter = ('received',)
    search_fields = ('donation__user__username', 'ngo_request__ngo__username')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(DropOffLocation)
admin.site.register(DonationCategory)
admin.site.register(DonationRequest, DonationRequestAdmin)
admin.site.register(NGORequest, NGORequestAdmin)
admin.site.register(Allocation, AllocationAdmin)