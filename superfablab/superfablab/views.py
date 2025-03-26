from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta, localtime
from django.db.models.functions import TruncDate
from django.db.models import Count, Avg, ExpressionWrapper, Q, F, DurationField


from users.models import KeyholderHistory
from visit_tracking.models import Visit
from tools_and_trainings.models import Training, TrainingCategory


def staff_required(view_func):
    return user_passes_test(lambda u: u.space_level >= get_user_model().SpaceLevel.KEYHOLDER)(view_func)

def open_required(view_func):
    return user_passes_test(lambda u: u.space_level >= get_user_model().SpaceLevel.VOLUNTEER)(view_func)

def index(request):
    context ={
        'user_can_open_space': not request.user.is_anonymous and request.user.space_level >= get_user_model().SpaceLevel.VOLUNTEER,
        'user_can_train': not request.user.is_anonymous and Training.objects.filter(user=request.user, training_level__gte=Training.TrainingLevels.TRAINER).exists(),

    }
    return render(request, 'index.html', context)

def profile(request):
    visits = Visit.objects.filter(user__niner_id=request.user.niner_id).order_by('-enter_time')
        
    last_week_hours, total_hours = request.user.get_hours()
    
    context = {
        'all_time_visits':visits,
        'total_hours':total_hours,
        'last_week_hours':last_week_hours
    }
    
    return render(request, 'profile.html', context)

def coming_soon(request):
    return render(request, 'coming_soon.html')

def stats(request):
    visits_by_day = (
        Visit.objects
        .annotate(day=TruncDate("enter_time"))
        .values("day")
        .annotate(unique_visitors=Count("user", distinct=True)) 
        .order_by("-unique_visitors")
    )
    
    if visits_by_day.exists():
        busiest = visits_by_day.first()
    else:
        busiest = None
    
    context = {
        'highest_unique': busiest
    }
    return render(request, 'stats.html', context)

def users_per_day_chart(request):
    visits_by_day = (
        Visit.objects
        .annotate(day=TruncDate("enter_time"))
        .values("day")
        .annotate(
            unique_visitors=Count("user", distinct=True),
            avg_visit_length=Avg(
                ExpressionWrapper(
                    F("exit_time") - F("enter_time"),
                    output_field=DurationField()
                ),
                filter=Q(forgot_to_signout=False) | Q(forgot_to_signout__isnull=True)
            )
        )
        .order_by("day")
    )
    
    recorded_data = {entry["day"]: {"users": entry["unique_visitors"], "avg_length": entry["avg_visit_length"]} for entry in visits_by_day}
    
    start_date = min(recorded_data.keys())
    end_date = now().date()
    full_date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    
    complete_data = {
        date: {
            "users": recorded_data.get(date, {}).get("users", 0),
            "avg_length": recorded_data.get(date, {}).get("avg_length", None)
        }
        for date in full_date_range
    }

    data = {
        "labels": [date.strftime("%a %Y-%m-%d") for date in complete_data.keys()],
        "values": [entry["users"] for entry in complete_data.values()],
        "avg_lengths": [(entry["avg_length"].total_seconds() / 3600) if entry["avg_length"] else 0 for entry in complete_data.values()]
    }
    
    return JsonResponse(data)


@open_required
def users_in_space(request):
    current_keyholder = KeyholderHistory.objects.get_current_keyholder()

    users_from_last_login = get_user_model().objects.filter(last_login__date=timezone.now().date())
    users_from_activity_logs = get_user_model().objects.filter(visit__still_in_the_space=True).distinct()

    active_users = []

    for user in users_from_activity_logs:
        active_users.append({"user": user, "method": "in_person", "trainings": Training.objects.get_users_trainings(user)})        


    for user in users_from_last_login:
        if not any(u["user"] == user for u in active_users):
            active_users.append({"user": user, "method": "online"})
    context = {
        "active_users": active_users, 
        "keyholder": current_keyholder,
        "all_trainings": TrainingCategory.objects.all().distinct()
    }

    return render(request, "users_in_space.html", context)



