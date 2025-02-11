from django.urls import path
from . import views

app_name = 'station'

urlpatterns = [
    path('create/', views.create_training, name="create_training"),
]
