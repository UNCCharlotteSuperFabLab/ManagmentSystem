from django.test import TestCase

from .models import SpaceUser

from dotenv import dotenv_values

# Create your tests here.
class SpaceUserModelTests(TestCase):
    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)
        self.config = dotenv_values("/Users/philip/Projects/fablab/ManagmentSystem/.env")
    
    def test_get_niner_engage_data(self):
        user = SpaceUser(niner_id=801276949).niner_engage_get_updated_values(self.config)
        self.assertIsNotNone(user.email)
            
    def test_get_canvas_id(self):
        user = SpaceUser(niner_id=801276949, email="psmit145@charlotte.edu").get_canvas_id_from_canvas(self.config)
        self.assertIsNotNone(user.canvas_id)        
        