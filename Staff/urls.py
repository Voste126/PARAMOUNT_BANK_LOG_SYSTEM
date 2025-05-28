from django.urls import path
from . import views
from .views import ResendOTPView, GetUserCredentialsView, AdminUpdateUserCredentialsView, AdminGetUserCredentialsView, AdminCreateUserView

urlpatterns = [
    path('register/', views.StaffRegisterView.as_view(), name='staff-register'),
    path('verify-otp/', views.OTPVerifyView.as_view(), name='verify-otp'),
    path('login/request/', views.OTPLoginRequestView.as_view(), name='otp-login-request'),
    path('login/verify/', views.OTPLoginVerifyView.as_view(), name='otp-login-verify'),
    path('all/', views.StaffListView.as_view(), name='staff-list'),
    path('update-credentials/', views.UpdateUserCredentialsView.as_view(), name='update-credentials'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('get-user-credentials/<str:user_id>/', GetUserCredentialsView.as_view(), name='get-user-credentials'),
    path('admin/update-user/', AdminUpdateUserCredentialsView.as_view(), name='admin-update-user'),
    path('admin/get-user-credentials/<int:user_id>/', AdminGetUserCredentialsView.as_view(), name='admin-get-user-credentials'),
    path('admin/create-user/', AdminCreateUserView.as_view(), name='admin-create-user'),
    path('admin/delete-user/<int:user_id>/', views.AdminDeleteUserView.as_view(), name='admin-delete-user'),
]
