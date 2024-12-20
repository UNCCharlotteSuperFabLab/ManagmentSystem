from django.db import models, transaction
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.timezone import now




class VisitManager(models.Manager):
    def get_signed_in_users(self):
        return get_user_model().objects.filter(
            visit__still_in_the_space=True
        ).distinct()
    
    def scan(self, niner_id:int):
        user, created = get_user_model().objects.get_or_create(niner_id=niner_id)
        with transaction.atomic():
            active_vist = self.filter(user=user, still_in_the_space=True).first()
            
            if active_vist:
                active_vist:Visit
                #sign out
                active_vist.exit_time = now()
                active_vist.still_in_the_space = False
                active_vist.save()
            else:
                #sign in
                self.create(user=user, enter_time=now(), still_in_the_space=True)
            
        return user
        

# Create your models here.
class Visit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="visit")
    enter_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True)
    still_in_the_space = models.BooleanField(default=True)
    
    objects = VisitManager()