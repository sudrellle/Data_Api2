from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
CREATE_USER_URL=reverse('user:create')
TOKEN_USER_URL=reverse('user:token')
MOI_URL=reverse('user:moi')
def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApi(TestCase):
    def setUp(self):
        self.client=APIClient()

    def test_create_user_success(self):
        payload={'email':'test@gmail.com',
                 'password':'Testpass123',
                 'name':'Test Name'

        }
        res=self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        user=get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password',res.data)
    def test_user_email_exist(self):
        payload={
            'email':'test@gmail.com',
            'password':'testpass123',
            'name':'Test user'
        } 
        create_user(**payload) 
        res=self.client.post(CREATE_USER_URL,payload) 
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST) 
    
    def test_longueur_mot_passe(self):
        payload={
            'email':'test@gmail.com',
            'password':'test',
            'name':'Test user'
        }
        res=self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        user_exists=get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token(self):
        user_details={
            'name':'Test Name',
            'email':'test@gmail.com',
            'password':'Testpass123',  
        }  
        create_user(**user_details)
        payload={
            'email':user_details['email'],
            'password':user_details['password'],

        } 
        res = self.client.post(TOKEN_USER_URL, payload)
        self.assertEqual(res.status_code,status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        create_user(email='test@gmail.com',password='godpass')  
        payload={'email':'test@gmail.com', 'password': 'badpass'}
        res=self.client.post(TOKEN_USER_URL,payload)

        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)


    def test_create_blank_password(self):
        payload={'email':'test@gmail.com','password':''}
        res=self.client.post(TOKEN_USER_URL,payload)  
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)  

    def test_retrieve_user_unauthorize(self):
        res=self.client.get(MOI_URL)  
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)  

class PrivateUserApiTest(TestCase):
    def setUp(self):
        self.user=create_user(
            email='test@gmail.com',
            password='testpass123',
            name='Test Name'
        )
        self.client=APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_succes(self):
        res=self.client.get(MOI_URL)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,{
            'email':self.user.email,
            'name':self.user.name
        })    


    def test_post_me_not_allowed(self):
        res=self.client.post(MOI_URL,{})
        self.assertEqual(res.status_code,status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        payload={'name':'update name','password':'newpass'}    
        res=self.client.patch(MOI_URL,payload,format='json')
        self.user.refresh_from_db()
        self.assertEqual(self.user.name,payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code,status.HTTP_200_OK)
