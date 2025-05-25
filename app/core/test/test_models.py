from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):
    def test_create_user(self):
        email='esther@gmail.com'
        password='Test2504'
        user=get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(email,email)
        self.assertEqual(password,password)
    
    def test_new_user_email(self):
        sample_emails=[
            ['test@EXAMPLE.com','test@example.com'],
            ['Test2@Example.com','Test2@example.com'],
              ['TEST3@Example.com','TEST3@example.com'],
            ['test4@example.com','test4@example.com']
            ]
        for email,expected in sample_emails:
            user=get_user_model().objects.create_user(email,'sample123')
            self.assertEqual(user.email,expected)



    def test_email_require(self):
            with self.assertRaises(ValueError):
               get_user_model().objects.create_user('','test123')  

    def test_create_super_user(self):
         user=get_user_model().objects.create_superuser(
            'esther@gmail.com',
            'Est@123'  
         )
         self.assertTrue(user.is_superuser) 
         self.assertTrue(user.is_staff)          