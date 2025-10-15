from __future__ import annotations

import requests

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import FileExtensionValidator
from django.core.mail import send_mail


from django.utils.timezone import now, localtime, timedelta


from typing import Dict, Tuple

from canvasapi import Canvas
from canvasapi.user import User as CanvasUser

import os

class SpaceUserManager(BaseUserManager):
    def create_user(self, niner_id, password=None, **extra_fields) -> SpaceUser:
        if not niner_id:
            raise ValueError('The Niner ID must be set')
        user = self.model(niner_id=niner_id, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, niner_id, password=None, **extra_fields) -> SpaceUser:
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Create the superuser using the create_user method
        return self.create_user(niner_id, password, **extra_fields)

    def get_or_create(self, niner_id) -> Tuple[SpaceUser, bool]:
        user = self.filter(niner_id=niner_id).first()
        if user:
            return (user, False)

        user = self.model(niner_id=niner_id)
        user.save()
        return (user, True)

    

# Create your models here.
class SpaceUser(AbstractBaseUser, PermissionsMixin):
    niner_id = models.IntegerField(primary_key=True)
    canvas_id = models.IntegerField(blank=True, null=True)
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    user_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )


    
    class SpaceLevel(models.IntegerChoices):
        USER = 0
        VOLUNTEER = 30
        KEYHOLDER = 70
        STAFF = 100
    
    space_level = models.IntegerField(choices=SpaceLevel.choices, default=SpaceLevel.USER)
    keyholder_priority = models.IntegerField(default=-10)
    
    USERNAME_FIELD="niner_id"
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    groups = models.ManyToManyField('auth.Group', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', blank=True)

    
    objects = SpaceUserManager()
    
    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self) -> str:
        return f"{self.first_name}"
    
    @property
    def last_week_hours(self):
        one_week_ago = now() - timedelta(weeks=1)
        last_week_visits = Visit.objects.filter(user__niner_id=self.niner_id, enter_time__gte=one_week_ago, still_in_the_space=False).exclude(forgot_to_signout=True)
        return sum((visit.exit_time - visit.enter_time).total_seconds() for visit in last_week_visits) / 3600

    @property
    def all_time_hours(self):
        all_time_visits = Visit.objects.filter(user__niner_id=self.niner_id, still_in_the_space=False).exclude(forgot_to_signout=True)
        return sum((visit.exit_time - visit.enter_time).total_seconds() for visit in all_time_visits) / 3600
    
    @property
    def all_time_visits(self):
        return Visit.objects.filter(user__niner_id=self.niner_id, still_in_the_space=False).exclude(forgot_to_signout=True).count()
        
    @property
    def last_visit(self):
        return localtime(Visit.objects.filter(user__niner_id=self.niner_id).order_by("-enter_time").first().enter_time)
    
    def get_hours(self):    
        return self.last_week_hours, self.all_time_hours

    
    def __str__(self):
        return self.get_full_name()
    
    def __eq__(self, value):
        if isinstance(value, SpaceUser):
            return self.niner_id == value.niner_id
        return False

    def __hash__(self):
        return hash(self.niner_id)
    
    def __repr__(self):
        return f"space_user({self.niner_id}, {self.first_name}, {self.last_name}, {self.email}, {self.canvas_id})" + super().__repr__()
        
    def get_canvas_id_from_canvas(self) -> SpaceUser:
        print("getting canvas id")
        if self.canvas_id:
            return self
        if not self.email:
            return self
        if not (self.email.endswith("@charlotte.edu") or self.email.endswith("@uncc.edu")):
            return self
        canvas = Canvas("https://instructure.charlotte.edu", os.getenv("CANVAS_API_KEY"))
        course = canvas.get_course(231237)
        for couse_user in course.get_users():
            couse_user: CanvasUser
            profile = couse_user.get_profile()
            email_address = self.email[:self.email.find("@")]
            if profile["primary_email"] == f"{email_address}@charlotte.edu":
                self.canvas_id = profile["id"]
                break
        
        if not self.canvas_id:
            subject = "Join the Canvas Page for the Super Fab Lab"
            html_content = f"<html><body><h1> Thanks for visiting the SFL {self.get_full_name()}! </h1> <p> We hope you had an amazing time! Please click <a href='https://uncc.instructure.com/enroll/E6NPBA'>this link</a> to join our canvas page and do trainings </p</body></html>"
            to = [{"email":self.email,"name":self.get_full_name()}]
            # email.delay(to, subject, html_content)
            send_mail(subject, "test", "super-fab-lab@c4glenn.com", [self.email], html_message=html_content)

            print("sending email")
            return self#Send email invite?
        else:
            self.save()
            return self
        
    #function that returns the canvas id without emailing the user    
        # This method attempts to retrieve and set the user's Canvas ID by matching their email with users in a specific Canvas course.
        # Steps:
        # 1. If the user already has a canvas_id, return self.
        # 2. If the user does not have an email, return self.
        # 3. If the email is not a charlotte.edu or uncc.edu address, return self.
        # 4. Connect to the Canvas API using the API key from environment variables.
        # 5. Get the specified course (hardcoded ID: 231237).
        # 6. Iterate through all users in the course:
        #    a. Get each user's profile.
        #    b. Compare the primary email to the current user's email (charlotte.edu only).
        #    c. If a match is found, set self.canvas_id to the Canvas profile ID and break.
        # 7. Save the user and return self.
    def get_canvas_id(self) -> SpaceUser:
        from .tasks import canvas_user_list
        print("getting canvas id")
        if self.canvas_id:
            canvas_user_list.update({self.canvas_id: self}) #add to the canvas user list
            return self
        if not self.email:
            return self
        if not (self.email.endswith("@charlotte.edu") or self.email.endswith("@uncc.edu")):
            return self
        canvas = Canvas("https://instructure.charlotte.edu", os.getenv("CANVAS_API_KEY"))
        course = canvas.get_course(231237)
        for couse_user in course.get_users():
            couse_user: CanvasUser
            profile = couse_user.get_profile()
            email_address = self.email[:self.email.find("@")]
            if profile["primary_email"] == f"{email_address}@charlotte.edu":
                self.canvas_id = profile["id"]
                canvas_user_list.update({self.canvas_id: self}) #add to the canvas user list
                break
        self.save()
        return self    

class KeyholderHistoryManager(models.Manager):
    def get_current_keyholder(self) -> KeyholderHistory:
        return KeyholderHistory.objects.filter(exit_time__isnull=True).order_by('-start_time').first()
    def is_keyholder(self, user:SpaceUser) -> bool:
        return user.space_level >= user.SpaceLevel.KEYHOLDER  
    def can_open(self, user:SpaceUser) -> bool:
        return user.space_level >= user.SpaceLevel.VOLUNTEER
    def create_keyholder_history(self, user:SpaceUser) -> KeyholderHistory:
        if self.can_open(user):
            keyholder_history = self.create(keyholder=user, start_time=now())
            return keyholder_history
        else:
            raise ValueError("User must be a keyholder")
class KeyholderHistory(models.Model):
    keyholder = models.ForeignKey(SpaceUser, on_delete=models.CASCADE, related_name="keyholder_history")
    start_time = models.DateTimeField()
    exit_time = models.DateTimeField(null=True, blank=True)
    objects = KeyholderHistoryManager()
    
    
from visit_tracking.models import Visit
