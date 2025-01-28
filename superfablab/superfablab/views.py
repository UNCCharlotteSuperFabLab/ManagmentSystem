from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib.auth import get_user_model

from users.models import KeyholderHistory

import django_filters

def index(request):
    return render(request, 'index.html')

def profile(request):
    return coming_soon(request)


def coming_soon(request):
    return render(request, 'coming_soon.html')



@permission_required("SpaceUser.view")
def users_in_space(request):
    current_keyholder = KeyholderHistory.objects.get_current_keyholder()

    users_from_last_login = get_user_model().objects.filter(last_login__date=timezone.now().date())
    users_from_activity_logs = get_user_model().objects.filter(visit__still_in_the_space=True).distinct()

    active_users = []

    for user in users_from_activity_logs:
        active_users.append({"user": user, "method": "in_person"})

    for user in users_from_last_login:
        if not any(u["user"] == user for u in active_users):
            active_users.append({"user": user, "method": "online"})

    context = {
        "active_users": active_users, 
        "keyholder": current_keyholder
    }

    return render(request, "users_in_space.html", context)



