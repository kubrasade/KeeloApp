from django.db import models
from core.models import BaseModel

class ContactFormModel(BaseModel):
    name= models.CharField(max_length=50)
    surname= models.CharField(max_length=50)
    email= models.EmailField()
    phone= models.CharField(max_length=20)
    message= models.TextField()

    class Meta:
        verbose_name= "Contact Form"
        verbose_name_plural= "Contact Forms"

    def __str__(self):
        return f"{self.name} {self.surname}"
