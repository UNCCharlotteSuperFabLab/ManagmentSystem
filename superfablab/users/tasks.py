from celery import shared_task
from .models import SpaceUser


@shared_task
def check_for_needed_invites():
    # Your task logic here
    print("This task runs every day at 5 PM!")
    users = SpaceUser.objects.all()
    for user in users:
        user.get_canvas_id_from_canvas()
        print(f"{user.get_full_name} - {user.canvas_id}")
        
@shared_task
def canvas_update(niner_id: int):
    SpaceUser.objects.get(niner_id=niner_id).get_canvas_id_from_canvas()
    