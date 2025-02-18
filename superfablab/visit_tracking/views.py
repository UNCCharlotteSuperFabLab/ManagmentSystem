from django.shortcuts import render, redirect
from django.utils.timezone import now, localtime
from django.db.models.functions import Coalesce
from django.db.models import Count


from typing import Tuple


from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


from .models import Visit
from users.models import SpaceUser, KeyholderHistory
from .forms import NewUserForm

from datetime import timedelta 

def close_space(request):
    if request.method == 'POST' and 'barcode' in request.POST:
        keyholder = KeyholderHistory.objects.get_current_keyholder()
        print(request.POST['barcode'], keyholder.keyholder.niner_id)
        if int(keyholder.keyholder.niner_id) != int(request.POST['barcode']):
            return render(request, 'status/error.html', {'error': 'tried to close space as non active keyholder'}, status=418)
        
        keyholder.exit_time = now()
        keyholder.save()
        Visit.objects.scan(request.POST['barcode'])
        
        for visit in Visit.objects.filter(still_in_the_space=True):
            visit.forgot_to_signout = True
            visit.still_in_the_space = False
            visit.exit_time = now()
            visit.save()
    return redirect('station:scan')

def set_forgot(request):
    if request.method == 'POST' and 'barcode' in request.POST:
        barcode = request.POST['barcode']
        visit = Visit.objects.filter(still_in_the_space=True, user__niner_id=barcode).first()
        visit.forgot_to_signout = True
        visit.still_in_the_space = False
        visit.exit_time = now()
        visit.save()
        redirect_val = request.POST.get('redirect', None)
        if redirect_val:
            return redirect(redirect_val)
    return redirect('station:scan')

def get_current_keyholder() -> Tuple[SpaceUser, str, str, KeyholderHistory]:
    """Gets information related to the current keyholder

    Returns:
        Tuple[Keyholder, str, str]: keyholder object, name, img_url
    """
    current_keyholder = KeyholderHistory.objects.get_current_keyholder()
    if not current_keyholder:
        return None, None, "https://upload.wikimedia.org/wikipedia/commons/1/14/No_Image_Available.jpg", None
    keyholder_name = f"{current_keyholder.keyholder.first_name} {current_keyholder.keyholder.last_name}"
    keyholder_img_url = current_keyholder.keyholder.user_picture.url if current_keyholder.keyholder.user_picture else "https://upload.wikimedia.org/wikipedia/commons/1/14/No_Image_Available.jpg"
    return current_keyholder.keyholder, keyholder_name, keyholder_img_url, current_keyholder

def assign_keyholder(user, request):
    current_keyholder, _, _, history = get_current_keyholder()
    if current_keyholder and user == current_keyholder:
        return render(request, "status/error.html", {'error':"don't reasign the same keyholder"}, status=400)

    if not Visit.objects.filter(user__niner_id=user.niner_id, still_in_the_space=True).exists():
        Visit.objects.scan(user.niner_id)
    try:
        KeyholderHistory.objects.create_keyholder_history(user)
    except ValueError as e:
        return render(request, "status/error.html", {'error':e}, status=504)

    if history:
        print("replacing keyholder")
        history.exit_time = now()
        history.save()
    
    if request.POST.get("sign_out_current_keyholder", None) == "true":
        Visit.objects.filter(user=current_keyholder, still_in_the_space=True).update(still_in_the_space=False, exit_time=now())
    
    return redirect('station:scan')

def leaderboard_of_shame():
    forgotten_signouts = (Visit.objects.filter(forgot_to_signout=True)
    .values("user")
    .annotate(times_forgot_to_signout=Count("id"))
    .order_by("-times_forgot_to_signout"))
    
    filterd_forgotten = []
    
    for entry in forgotten_signouts:
        visits = Visit.objects.filter(user=entry["user"]).count()
        if visits >= 2:
            entry["user"] = SpaceUser.objects.get(niner_id=entry["user"])
            entry["times_forgot_to_signout"] /= visits
            filterd_forgotten.append(entry)
            
    forgotten_signouts = list(filterd_forgotten)
    forgotten_signouts.sort(key=lambda x: x["times_forgot_to_signout"], reverse=True)
    

    return forgotten_signouts[:5]




def scan(request):
    first_keyholder_modal = False
    current_keyholder_modal = False
    dont_override = False
    
    current_keyholder, keyholder_name, keyholder_img_url, history = get_current_keyholder()
    
    user = None
    if request.method == 'POST' and 'barcode' in request.POST:
        barcode = request.POST['barcode']
        redirect_val = request.POST.get('redirect', None)
        user, created = SpaceUser.objects.get_or_create(niner_id=barcode)
        if 'assign_keyholder' in request.POST:
            if request.POST['assign_keyholder'] == "true":
                return assign_keyholder(user, request)
            else:
                dont_override = True
                    
        if created or (not user.first_name or not user.last_name or not user.email):
            return redirect('station:new_user_form', niner_id=barcode)
        
        if current_keyholder is None:
            if user.space_level >= user.SpaceLevel.VOLUNTEER:
                first_keyholder_modal = True
            else:
                return render(request, "status/error.html", {'error':'Need a keyholder to sign in first'}, status=400)
        elif user == current_keyholder:
            if Visit.objects.filter(still_in_the_space=True).count() == 1:
                history.exit_time = now()
                history.save()
                user = Visit.objects.scan(barcode)
                return redirect("station:scan")
            else:
                current_keyholder_modal = True
        elif not Visit.objects.filter(user=user, still_in_the_space=True).exists() \
            and not dont_override\
            and user.space_level >= user.SpaceLevel.KEYHOLDER\
            and user.keyholder_priority > current_keyholder.keyholder_priority:
            first_keyholder_modal = True
        else:
            print("scanning")
            user = Visit.objects.scan(barcode)

        if redirect_val:
            return redirect(redirect_val)
        
        # return redirect('station:scan')
    
    today_start = localtime(now()).replace(hour=4, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    todays_transactions = Visit.objects.annotate(
        last_activity=Coalesce('exit_time', 'enter_time')).filter(
        enter_time__range=(today_start, today_end)).order_by('-last_activity')[:10]


    context = {
        'number_present': Visit.objects.filter(still_in_the_space=True).count(),
        'unique_visitors_today': Visit.objects.filter(enter_time__range=(today_start, today_end)).distinct('user').count(),
        'keyholders_list':Visit.objects.filter(still_in_the_space=True, user__space_level__gte=SpaceUser.SpaceLevel.KEYHOLDER).distinct('user'),
        'keyholder_name': keyholder_name,
        'keyholder_img_url': keyholder_img_url,
        'keyholder':current_keyholder,
        'currentkeyholderorvolunter': current_keyholder and current_keyholder.space_level >= SpaceUser.SpaceLevel.KEYHOLDER,
        'userkeyholderorvolunter': user and user.space_level >= SpaceUser.SpaceLevel.KEYHOLDER,
        'todays_transactions': todays_transactions,
        'first_keyholder_modal': first_keyholder_modal,
        'current_keyholder_modal': current_keyholder_modal,
        'weekly_hours':Visit.objects.get_hours_this_week(),
        'leaderboard_of_shame':leaderboard_of_shame(),
        'user': user
    }
    return render(request, 'station.html', context)


def new_user_form(request, niner_id):
    # Fetch the user or create a placeholder
    user = SpaceUser.objects.filter(niner_id=niner_id).first()
    
    # Example: Fetch the first name from another source (replace with your logic)

    if request.method == 'POST':
        # Bind form data to the user instance
        form = NewUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            Visit.objects.scan(niner_id)
            return redirect('station:scan')  # Redirect back to the station view
    else:
        # Provide initial data for the form
        initial_data = {'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email} if user else {}
        form = NewUserForm(instance=user, initial=initial_data)
        
    return render(request, 'new_user_form.html', initial_data)
