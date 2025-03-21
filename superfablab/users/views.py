from django.shortcuts import render, redirect
from django.http import HttpResponse
from users.models import SpaceUser
from .tasks import canvas_update

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the users index.")

def update_users_canvas_ID(request, user_id):
    canvas_update.delay(user_id)
    
    if request.POST and request.POST['redirect']:
        return redirect(request.POST['redirect'])
    
    
    
    return redirect("home")
    
