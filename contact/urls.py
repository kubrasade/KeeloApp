from django.urls import path
from .views import ContactFormCreateAPIView, ContactFormListAPIView, ContactFormDetailAPIView

urlpatterns = [
    path('form/create/', ContactFormCreateAPIView.as_view(), name='contact-form-create'),  
    path('form/', ContactFormListAPIView.as_view(), name='contact-form-list'), 
    path('form/<int:pk>/', ContactFormDetailAPIView.as_view(), name='contact-form-detail'),  
]