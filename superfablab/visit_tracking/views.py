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
    dont_override = False
    
    current_keyholder = KeyholderHistory.objects.get_current_keyholder()
    if current_keyholder is None:
        keyholder_name = None
        keyholder_img_url = ""
    else:
        keyholder_name = f"{current_keyholder.keyholder.first_name} {current_keyholder.keyholder.last_name}"
        if current_keyholder.keyholder.user_picture:
            keyholder_img_url = current_keyholder.keyholder.user_picture.url
        else:
            keyholder_img_url = "https://upload.wikimedia.org/wikipedia/commons/1/14/No_Image_Available.jpg"
    user = None
    if request.method == 'POST' and 'barcode' in request.POST:
        barcode = request.POST['barcode']
        redirect_val = request.POST.get('redirect', None)
        user, created = SpaceUser.objects.get_or_create(niner_id=barcode)
        if 'assign_keyholder' in request.POST:
            if request.POST['assign_keyholder'] == "true":
                if current_keyholder and user == current_keyholder.keyholder:
                    return render(request, "status/error.html", {'error':"don't reasign the same keyholder"}, status=400)
                try:
                    if not Visit.objects.filter(user__niner_id=barcode, still_in_the_space=True).exists():
                        Visit.objects.scan(barcode)
                    KeyholderHistory.objects.create_keyholder_history(user)
                    if current_keyholder:
                        current_keyholder.exit_time = now()
                        current_keyholder.save()
                        if request.POST.get("sign_out_current_keyholder", None) == "true":
                            Visit.objects.filter(user=current_keyholder.keyholder, still_in_the_space=True).update(still_in_the_space=False, exit_time=now())
                except ValueError as e:
                    return render(request, 'status/error.html', {"error": "{e}"}, status=504)
                return redirect('station:scan')
            else:
                dont_override = True
                print("not overriding")
                    
        if created or (not user.first_name or not user.last_name or not user.email):
            return redirect('station:new_user_form', niner_id=barcode)
        
        if current_keyholder is None:
            try:
                if user.keyholder.is_keyholder:
                    first_keyholder_modal = True
                else:
                    return render(request, "status/error.html", {'error':'Need a keyholder to sign in first'}, status=400)
            except Keyholder.DoesNotExist:
                return render(request, "status/error.html", {'error':'Need a keyholder to sign in first'}, status=400)
        elif user == current_keyholder.keyholder:
            if Visit.objects.filter(still_in_the_space=True).count() == 1:
                current_keyholder.exit_time = now()
                current_keyholder.save()
                user = Visit.objects.scan(barcode)
                return redirect("station:scan")
            else:
                current_keyholder_modal = True
        elif not Visit.objects.filter(user=user, still_in_the_space=True).exists() \
            and not dont_override\
            and hasattr(user, 'keyholder')\
            and user.keyholder\
            and user.keyholder.priority > current_keyholder.keyholder.keyholder.priority:
            first_keyholder_modal = True
        else:
            print("scanning")
            user = Visit.objects.scan(barcode)

        if redirect_val:
            return redirect(redirect_val)
        
        # return redirect('station:scan')
    
    today_start = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    todays_transactions = Visit.objects.annotate(
        last_activity=Coalesce('exit_time', 'enter_time')).filter(
        enter_time__range=(today_start, today_end)).order_by('-last_activity')[:10]

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
        'keyholder':current_keyholder,
        'weekly_hours':Visit.objects.get_hours_this_week(),
        'user': user
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
