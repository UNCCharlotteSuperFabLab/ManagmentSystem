from celery import shared_task
from .models import SpaceUser
from canvasapi import Canvas
import os
from tools_and_trainings.models import Training, TrainingCategory, TrainingManager

def build_canvas_user_list():
    global canvas_user_list
    canvas_user_list = {}
    users = SpaceUser.objects.exclude(canvas_id=None).all()
    for user in users:
        canvas_user_list[user.canvas_id] = {
            "user": user,
            "trainings": Training.objects.get_users_trainings(user)
        }
    print("Built canvas user list: \n", canvas_user_list)

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

# This task will check if users have completed Canvas certification quizzes
# and update their space access accordingly.
@shared_task
def canvas_quiz_status():
    print("Starting canvas quiz status check...")
    from tools_and_trainings.views import create_training_internal
    canvas = Canvas("https://instructure.charlotte.edu", os.getenv("CANVAS_API_KEY"))
    course = canvas.get_course(231237)
    trainings = {
        "Orientation": 
        {
            "assignment": course.get_assignment(2633706),
            "category": TrainingCategory.objects.get(name="Orientation"),
        },
        "Resin Printing":
        {
            "assignment": course.get_assignment(2691739),
            "category": TrainingCategory.objects.get(name="Resin Printing"),
        },
        "Waterjet": 
        {
            "assignment": course.get_assignment(2694817),
            "category": TrainingCategory.objects.get(name="Waterjet"),
        },
        "Laser Cutter": 
        {
            "assignment": course.get_assignment(2694816),
            "category": TrainingCategory.objects.get(name="Laser Cutter"),
        },
        "3D Printer": 
        {
            "assignment": course.get_assignment(2691733),
            "category": TrainingCategory.objects.get(name="FDM Printing"),
        },
        "Policies and Procedures": 
        {
            "assignment": course.get_quiz(6792318), #this is labelled as a quiz in Canvas for some reason?
            "category": TrainingCategory.objects.get(name="Policies and Procedures"),
        },
    }

    training_level = Training.TrainingLevels.APPRENTICE #always set to apprentice for automated ceritification
    certifier = SpaceUser.objects.get(niner_id=801380523)#set to a default certifier account (Bayli Wolfe aka me)
    
    users = SpaceUser.objects.all()
    #for user in users:
    #    if not user.canvas_id:
    #        user.get_canvas_id() #gets canvas id if not already set

    users_with_ids = list(filter(lambda u: u.canvas_id is not None, users)) #returns users with canvas ids only
    print("Users with canvas ids: \n", users_with_ids)
    for user in users_with_ids:
        trainings_list = Training.objects.get_users_trainings(user) #get list of trainings for user
        user_training_categories = {t.category for t in trainings_list}

        for training in trainings: #iterate through each training defined above
            print(training)
            try:
                submissions = trainings[training]["assignment"].get_submission(user.canvas_id) #gets list of submissions for specific assignment
                print(submissions)
                training_category = trainings[training]['category']
                if training_category == "Policies and Procedures":
                    if submissions.grade < (100 * 7/8): #must score at least 87.5% on policies and procedures to be certified and get training
                        continue
                if submissions is None or training_category in user_training_categories:
                    continue #skip if no submissions or user already has training
                if submissions.workflow_state == "ungraded" or submissions.grade is None:
                    continue #skip if submission is ungraded or missing
                create_training_internal(user, training_category, training_level, certifier) #create orientation training for user
                print(f"Awarded {training} training to {user.get_full_name()}")
            except Exception:
                    print(f"Error processing training {training} for user {user.get_full_name()}: unable to find canvas id for submission. Skipping.")
                    continue
                
            
    
    print("Canvas quiz status check complete.")      




 