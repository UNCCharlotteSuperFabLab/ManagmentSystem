from django.test import TestCase

from .models import SpaceUser


# This test checks if the canvas id is not null for a known user
class SpaceUserModelTests(TestCase):
    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)
                
    def test_get_canvas_id(self):
        user = SpaceUser(niner_id=801380523, email="bwolfe14@charlotte.edu").get_canvas_id_from_canvas()
        self.assertIsNotNone(user.canvas_id)        
        