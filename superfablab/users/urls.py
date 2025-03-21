from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:user_id>/update_canvas_id", views.update_users_canvas_ID),
]
