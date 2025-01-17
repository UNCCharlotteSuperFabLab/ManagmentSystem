from django.shortcuts import render, redirect
from django.utils.timezone import now, localtime
from django.db.models.functions import Coalesce

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


from .models import Visit
from users.models import SpaceUser, Keyholder, KeyholderHistory
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

def scan(request):
    first_keyholder_modal = False
    current_keyholder_modal = False
    
    keyholder = KeyholderHistory.objects.get_current_keyholder()
    if keyholder is None:
        keyholder_name = None
        keyholder_img_url = ""
    else:
        keyholder_name = f"{keyholder.keyholder.first_name} {keyholder.keyholder.last_name}"
        if keyholder.keyholder.user_picture:
            keyholder_img_url = keyholder.keyholder.user_picture.url
        else:
            keyholder_img_url = "https://upload.wikimedia.org/wikipedia/commons/1/14/No_Image_Available.jpg"
    
    if request.method == 'POST' and 'barcode' in request.POST:
        barcode = request.POST['barcode']
        redirect_val = request.POST.get('redirect', None)
        user, created = SpaceUser.objects.get_or_create(niner_id=barcode)

        if 'assign_keyholder' in request.POST:
            try:
                if not Visit.objects.filter(user=keyholder.keyholder, still_in_the_space=True).exists():
                    Visit.objects.scan(barcode)
                KeyholderHistory.objects.create_keyholder_history(user)
                keyholder.exit_time = now()
                keyholder.save()
                Visit.objects.filter(user=keyholder.keyholder, still_in_the_space=True).update(still_in_the_space=False, exit_time=now())
            except ValueError as e:
                return render(request, 'status/error.html', {"error": "{e}"}, status=504)
            
            return redirect('station:scan')
            
        if created or (not user.first_name or not user.last_name or not user.email):
            return redirect('station:new_user_form', niner_id=barcode)
        
        if keyholder is None:
            if KeyholderHistory.objects.is_keyholder(user):
                first_keyholder_modal = True
        elif user == keyholder.keyholder:
            if Visit.objects.filter(still_in_the_space=True).count() == 1:
                keyholder.exit_time = now()
                keyholder.save()
                user = Visit.objects.scan(barcode)
            else:
                current_keyholder_modal = True
            
        else:
            user = Visit.objects.scan(barcode)

        if redirect_val:
            return redirect(redirect_val)
        
        # return redirect('station:scan')
    
    today_start = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    todays_transactions = Visit.objects.annotate(
        last_activity=Coalesce('exit_time', 'enter_time')).filter(
        enter_time__range=(today_start, today_end)).order_by('-last_activity')

    number_present = Visit.objects.filter(still_in_the_space=True).count()
    unique_visitors_today = Visit.objects.filter(enter_time__range=(today_start, today_end)).distinct('user').count()

    keyholder_list = Visit.objects.filter(still_in_the_space=True, user__keyholder__is_keyholder=True).distinct('user')

    context = {
        'number_present': number_present,
        'unique_visitors_today': unique_visitors_today,
        'keyholder_name': keyholder_name,
        'keyholder_img_url': keyholder_img_url,
        'todays_transactions': todays_transactions,
        'first_keyholder_modal': first_keyholder_modal,
        'current_keyholder_modal': current_keyholder_modal,
        'keyholders_list':keyholder_list,
        'keyholder':keyholder
    }
    return render(request, 'station.html', context)


def new_user_form(request, niner_id):
    # Fetch the user or create a placeholder
    user = SpaceUser.objects.filter(niner_id=niner_id).first()
    
    if not user.first_name or not user.last_name or not user.email:
        user.niner_engage_get_updated_values()

    
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
