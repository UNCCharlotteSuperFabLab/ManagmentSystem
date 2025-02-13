from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from .models import Training, TrainingCategory
from django.utils.timezone import now, localtime
from visit_tracking.models import Visit
from users.models import SpaceUser
from django.contrib.auth.decorators import permission_required, user_passes_test
from django.contrib.auth import get_user_model



def staff_required(view_func):
    return user_passes_test(lambda u: u.space_level >= get_user_model().SpaceLevel.KEYHOLDER)(view_func)

def certify_ability(view_func):
    return user_passes_test(lambda u: Training.objects.filter(user=u, training_level__gte=Training.TrainingLevels.TRAINER).exists() )(view_func)


@certify_ability
def create_training(request):
    if request.POST:
        print(f"POST {request.POST}")
        user = SpaceUser.objects.get(niner_id=request.POST['user'])
        category = TrainingCategory.objects.get(id=request.POST['category'])
        certifier = request.user
        training = Training.objects.create(user=user, category=category, training_level=request.POST['level'], certifier=certifier)

        return redirect("home")
    
    available_trainings = {}
    
    for training in TrainingCategory.objects.all():
        try:
            to = Training.objects.get(category=training, user=request.user, training_level__gte=Training.TrainingLevels.TRAINER)
            available_trainings[training] = []
            for training_level in Training.TrainingLevels.choices:
                if training_level[0] < to.training_level:
                    available_trainings[training].append(training_level)
                    continue
                    
                if to.training_level == Training.TrainingLevels.CERTIFIER:
                    available_trainings[training].append(training_level)
        except Exception as e:
            print(Training.objects.get(category=training, user=request.user))
        
    
    context = {
        "current_visits": list(Visit.objects.get_signed_in_users()),
        "available_trainings": available_trainings,
    }
    
    return render(request, "training_form.html", context)