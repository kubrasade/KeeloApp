from rest_framework import generics
from .models import ContactFormModel
from .serializers import ContactFormModelSerializer
from rest_framework.permissions import  IsAdminUser

class ContactFormCreateAPIView(generics.CreateAPIView):
    queryset = ContactFormModel.objects.all()
    serializer_class = ContactFormModelSerializer

class ContactFormListAPIView(generics.ListAPIView):
    queryset = ContactFormModel.objects.all()
    serializer_class = ContactFormModelSerializer
    permission_classes = [IsAdminUser]  

class ContactFormDetailAPIView(generics.RetrieveAPIView):
    queryset = ContactFormModel.objects.all()
    serializer_class = ContactFormModelSerializer
    permission_classes = [IsAdminUser]  