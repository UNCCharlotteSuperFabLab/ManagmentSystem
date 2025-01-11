from django.db import models
from django.conf import settings

class TrainingCategory(models.Model):
    name = models.TextField()
    canvas_id = models.IntegerField(null=True, blank=True)
    user_url = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.name

# Create your models here.
class Training(models.Model):
    class TrainingLevels(models.IntegerChoices):
        RED_DOT = 0
        GREEN_DOT = 30
        BLUE_DOT = 70
        YELLOW_DOT = 100
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trainings")
    category = models.ForeignKey(TrainingCategory, on_delete=models.PROTECT, related_name="trainings")
    training_level = models.IntegerField(choices=TrainingLevels.choices, default=TrainingLevels.RED_DOT)
    completed_on = models.DateTimeField(auto_now_add=True)