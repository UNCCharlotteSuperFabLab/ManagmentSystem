from django.db import models
from django.conf import settings


# Create your models here.
class Association(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="visit", blank=True, null=True)
    email = models.EmailField()
    association_text = models.TextField()
    
    