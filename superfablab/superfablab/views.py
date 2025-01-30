from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required, user_passes_test
from django.http import HttpResponse
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib.auth import get_user_model

from users.models import KeyholderHistory


def staff_required(view_func):
    return user_passes_test(lambda u: u.space_level >= get_user_model().SpaceLevel.KEYHOLDER)(view_func)

def open_required(view_func):
    return user_passes_test(lambda u: u.space_level >= get_user_model().SpaceLevel.VOLUNTEER)(view_func)

def index(request):
    context ={
        'user_can_open_space': request.user.space_level >= get_user_model().SpaceLevel.VOLUNTEER
    }
    return render(request, 'index.html', context)

def profile(request):
    return coming_soon(request)


def coming_soon(request):
    return render(request, 'coming_soon.html')

@open_required
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



