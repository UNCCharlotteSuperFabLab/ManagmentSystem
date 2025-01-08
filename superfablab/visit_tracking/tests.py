from django.test import TestCase

from .models import Visit
from django.contrib.auth import get_user_model


# Create your tests here.
class VisitTests(TestCase):
    def test_sign_in(self):
        user = Visit.objects.scan(1)
        
        signed_in_users = Visit.objects.get_signed_in_users()
        self.assertEqual(signed_in_users.first(), user)
    
    def test_sign_out(self):
        user = Visit.objects.scan(1)
        
        Visit.objects.scan(1)
        
        signed_in_users = Visit.objects.get_signed_in_users()
        self.assertFalse(signed_in_users)
    
    def test_multiple_scans(self):
        for i in range(10):
            user = Visit.objects.scan(1)
            if i%2 == 0:
               self.assertEqual(Visit.objects.get_signed_in_users().first(), user)         
            else:
                self.assertFalse(Visit.objects.get_signed_in_users())
    def test_multiple_users(self):
        user1 = Visit.objects.scan(1)
        user2 = Visit.objects.scan(2)
        
        self.assertEqual(len(Visit.objects.get_signed_in_users()), 2)

        

        