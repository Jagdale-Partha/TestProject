from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
    

urlpatterns = [
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Donor views
    path('donation/new/', views.create_donation, name='create_donation'),
    
    # NGO views
    path('request/new/', views.create_request, name='create_request'),
    path('allocation/<int:pk>/received/', views.mark_received, name='mark_received'),
    
    # Admin views
    path('donation/<int:pk>/update/', views.update_donation_status, name='update_donation_status'),
    path('request/<int:pk>/update/', views.update_request_status, name='update_request_status'),
    path('allocate/', views.allocate_items, name='allocate_items'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Password reset URLs
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
