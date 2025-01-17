from django.urls import path
from . import views

app_name = 'station'

urlpatterns = [
    path('scan/', views.scan, name='scan'),
    path("new-user/<int:niner_id>/", views.new_user_form, name="new_user_form"),
    path('close/', views.close_space, name="close_space")

]
