from django.test import TestCase

from .models import SpaceUser


# Create your tests here.
class SpaceUserModelTests(TestCase):
    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)
    
    def test_get_niner_engage_data(self):
        with self.assertRaises(self.failureException):
            user = SpaceUser(niner_id=801276949).niner_engage_get_updated_values()
            self.assertIsNotNone(user.email)
            
    def test_get_canvas_id(self):
        user = SpaceUser(niner_id=801276949, email="psmit145@charlotte.edu").get_canvas_id_from_canvas()
        self.assertIsNotNone(user.canvas_id)        
        