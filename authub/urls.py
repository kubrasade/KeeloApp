from django.urls import path
from .views import (
    UserRegistrationView,
    EmailVerificationView,
    UserLoginView,
    UserLogoutView,
    PasswordResetRequestView,
    PasswordResetView,
    TokenRefreshView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('verify-email/<str:uidb64>/<str:token>/', EmailVerificationView.as_view(), name='verify-email'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/<str:uidb64>/<str:token>/', PasswordResetView.as_view(), name='password-reset'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
] 