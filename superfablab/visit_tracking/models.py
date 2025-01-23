from django.db import models, transaction
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta

class VisitManager(models.Manager):
    def get_signed_in_users(self):
        return get_user_model().objects.filter(
            visit__still_in_the_space=True
        ).distinct()
    
    def scan(self, niner_id:int):
        user, created = get_user_model().objects.get_or_create(niner_id=niner_id)
        with transaction.atomic():
            active_vist = self.filter(user=user, still_in_the_space=True).first()
            print(active_vist)
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
    
    def get_hours_this_week(self):
        one_week_ago = now() - timedelta(weeks=1)

        visits = self.filter(enter_time__gte=one_week_ago, still_in_the_space=False).exclude(forgot_to_signout=True)
        
        total_seconds = sum((visit.exit_time - visit.enter_time).total_seconds() for visit in visits)
        return total_seconds / 3600

# Create your models here.
class Visit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="visit")
    enter_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    still_in_the_space = models.BooleanField(default=True)
    forgot_to_signout = models.BooleanField(null=True, blank=True)
    
    objects = VisitManager()
    
    @property
    def description(self):
        return f"IN" if self.still_in_the_space else "OUT"
