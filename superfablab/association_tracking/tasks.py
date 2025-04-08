from celery import shared_task
from .models import Association

@shared_task
def check_for_new_user_associations(email):
    Association.objects.new_user_add(email)