from django.shortcuts import render, redirect
from django.utils.timezone import now, localtime
from django.db.models.functions import Coalesce

from .models import Visit
from users.models import SpaceUser
from .forms import NewUserForm

from datetime import timedelta


def scan(request):
    if request.method == 'GET' and 'barcode' in request.GET:
        barcode = request.GET['barcode']
        user = Visit.objects.scan(barcode)
        if not user.first_name or not user.last_name or not user.email:
            return redirect('station:new_user_form', niner_id=barcode)
        # Process the scanned card here (e.g., log attendance)
        return redirect('station:scan')
    
    today_start = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    todays_transactions = Visit.objects.annotate(
        last_activity=Coalesce('exit_time', 'enter_time')).filter(
        enter_time__range=(today_start, today_end)).order_by('-last_activity')


    # Example data
    number_present = Visit.objects.filter(still_in_the_space=True).count()
    unique_visitors_today = Visit.objects.filter(enter_time__range=(today_start, today_end)).distinct('user').count()
    keyholder_name = "John Doe"  # Replace with actual logic
    # todays_transactions = Visit.objects.filter(enter_time__range=(today_start, today_end))

    context = {
        'number_present': number_present,
        'unique_visitors_today': unique_visitors_today,
        'keyholder_name': keyholder_name,
        'todays_transactions': todays_transactions,
    }
    return render(request, 'station.html', context)


def new_user_form(request, niner_id):
    # Fetch the user or create a placeholder
    user = SpaceUser.objects.filter(niner_id=niner_id).first()
    config = dotenv_values("/Users/philip/Projects/fablab/ManagmentSystem/.env")
    
    if not user.first_name or not user.last_name or not user.email:
        user.niner_engage_get_updated_values(config)

    
    # Example: Fetch the first name from another source (replace with your logic)

    if request.method == 'POST':
        # Bind form data to the user instance
        form = NewUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('station:scan')  # Redirect back to the station view
    else:
        # Provide initial data for the form
        initial_data = {'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email} if user else {}
        form = NewUserForm(instance=user, initial=initial_data)

    return render(request, 'new_user_form.html', {'form': form})
