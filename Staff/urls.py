from django.urls import path
from . import views
from .views import ResendOTPView

urlpatterns = [
    path('register/', views.StaffRegisterView.as_view(), name='staff-register'),
    path('verify-otp/', views.OTPVerifyView.as_view(), name='verify-otp'),
    path('login/request/', views.OTPLoginRequestView.as_view(), name='otp-login-request'),
    path('login/verify/', views.OTPLoginVerifyView.as_view(), name='otp-login-verify'),
    path('all/', views.StaffListView.as_view(), name='staff-list'),
    path('update-credentials/', views.UpdateUserCredentialsView.as_view(), name='update-credentials'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
