from __future__ import annotations

from django.db import models
from django.conf import settings
from users.models import SpaceUser
from typing import List

class AssocationEntityManager(models.Manager):
    def add_bulk_users(emails: List[str], entity: AssociationEntities):
        for email in emails:
            try:
                user = SpaceUser.objects.get(email=email)
            except SpaceUser.DoesNotExist:
                user = None
                
            Association.objects.create(user=user, email=email, entity=entity)


class AssociationEntities(models.Model):
    short_name = models.TextField()
    description = models.TextField()
    contact = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contact", blank=True, null=True)

    objects = AssocationEntityManager()
    
    def __str__(self):
        return self.short_name
class AssociationManager(models.Manager):
    def new_user_add(self, email):
        user = SpaceUser.objects.get(email=email)
        for association in self.filter(email=email, user__isnull=True).all():
            association.user = user
            association.save()
    def create_associaton(self, entity: AssociationEntities, niner_id=None, email=None):
        pass

class Association(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user", blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    entity = models.ForeignKey(AssociationEntities, on_delete=models.CASCADE, related_name="entity")

    objects = AssociationManager()
    
    