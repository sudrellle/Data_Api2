from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import date, timedelta
from django.core.exceptions import ValidationError

# URLs
CREATE_USER_URL = reverse('user:create')
TOKEN_USER_URL = reverse('user:token')
MOI_URL = reverse('user:moi')

def create_user(**params):
    """Helper function pour créer un utilisateur"""
    return get_user_model().objects.create_user(**params)

class PublicUserApi(TestCase):
    """Tests spécifiques à la validation d'âge"""

    def setUp(self):
        self.client = APIClient()
        self.base_payload = {
            'email': 'test@gmail.com',
            'password': 'Testpass123',
            'name': 'Test Name',
            'genre': 'F'
        }

    def test_create_user_age_exactly_12(self):
        """Test création d'utilisateur ayant exactement 12 ans"""
        # Calculer la date pour quelqu'un qui a exactement 12 ans aujourd'hui
        today = date.today()
        birth_date_12_years = date(today.year - 12, today.month, today.day)
        
        payload = self.base_payload.copy()
        payload['date_naissance'] = birth_date_12_years.strftime('%Y-%m-%d')
        
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        user = get_user_model().objects.get(email=payload['email'])
        self.assertEqual(user.get_age(), 12)

    def test_create_user_age_more_than_12(self):
        """Test création d'utilisateur ayant plus de 12 ans"""
        # Calculer la date pour quelqu'un qui a 15 ans
        today = date.today()
        birth_date_15_years = date(today.year - 15, today.month, today.day)
        
        payload = self.base_payload.copy()
        payload['date_naissance'] = birth_date_15_years.strftime('%Y-%m-%d')
        
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        user = get_user_model().objects.get(email=payload['email'])
        self.assertEqual(user.get_age(), 15)

    def test_create_user_age_less_than_12(self):
        """Test que les utilisateurs de moins de 12 ans ne peuvent pas créer de compte"""
        # Calculer la date pour quelqu'un qui a 10 ans
        today = date.today()
        birth_date_10_years = date(today.year - 10, today.month, today.day)
        
        payload = self.base_payload.copy()
        payload['date_naissance'] = birth_date_10_years.strftime('%Y-%m-%d')
        
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Vérifier le message d'erreur
        self.assertIn('date_naissance', res.data)
        error_message = str(res.data['date_naissance'][0])
        self.assertIn('12 ans', error_message)
        self.assertIn('10 ans', error_message)
        
        # Vérifier que l'utilisateur n'a pas été créé
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_user_birthday_not_passed_this_year(self):
        """Test pour un utilisateur dont l'anniversaire n'est pas encore passé cette année"""
        today = date.today()
        
        
        if today.month == 1:
            future_month = 12
            birth_year = today.year - 12 - 1  
        else:
            future_month = today.month + 1 if today.month < 12 else 1
            birth_year = today.year - 12
        
        
        if today.month == 12 and future_month == 1:
            birth_year = today.year - 12
        
        birth_date = date(birth_year, future_month, min(today.day, 28))  # 28 pour éviter les problèmes de février
        
        payload = self.base_payload.copy()
        payload['date_naissance'] = birth_date.strftime('%Y-%m-%d')
        
        res = self.client.post(CREATE_USER_URL, payload)
        
        # Calculer l'âge réel pour vérifier notre logique
        calculated_age = today.year - birth_date.year
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            calculated_age -= 1
        
        if calculated_age >= 12:
            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        else:
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_future_birth_date(self):
        """Test qu'une date de naissance dans le futur est rejetée"""
        # Date dans le futur (dans 30 jours)
        future_date = date.today() + timedelta(days=30)
        
        payload = self.base_payload.copy()
        payload['date_naissance'] = future_date.strftime('%Y-%m-%d')
        
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Vérifier le message d'erreur
        self.assertIn('date_naissance', res.data)
        error_message = str(res.data['date_naissance'][0])
        self.assertIn('futur', error_message)

    def test_create_user_tomorrow_birth_date(self):
        """Test qu'une date de naissance de demain est rejetée"""
        tomorrow = date.today() + timedelta(days=1)
        
        payload = self.base_payload.copy()
        payload['date_naissance'] = tomorrow.strftime('%Y-%m-%d')
        
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_today_birth_date(self):
        """Test qu'une date de naissance d'aujourd'hui est rejetée (âge = 0)"""
        today = date.today()
        
        payload = self.base_payload.copy()
        payload['date_naissance'] = today.strftime('%Y-%m-%d')
        
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Vérifier le message d'erreur contient l'âge 0
        error_message = str(res.data['date_naissance'][0])
        self.assertIn('0 ans', error_message)

    def test_create_user_without_birth_date(self):
        """Test qu'un utilisateur sans date de naissance ne peut pas créer de compte"""
        payload = self.base_payload.copy()
        # Pas de date_naissance
        
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Vérifier le message d'erreur
        self.assertIn('date_naissance', res.data)

    def test_create_user_empty_birth_date(self):
        """Test qu'une date de naissance vide est rejetée"""
        payload = self.base_payload.copy()
        payload['date_naissance'] = ''
        
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_age_method(self):
        """Test de la méthode get_age() du modèle User"""
        # Créer un utilisateur avec une date de naissance connue
        today = date.today()
        birth_date_15_years = date(today.year - 15, today.month, today.day)
        
        user = create_user(
            email='test@gmail.com',
            password='testpass123',
            name='Test Name',
            genre='F',
            date_naissance=birth_date_15_years
        )
        
        self.assertEqual(user.get_age(), 15)

    def test_get_age_method_no_birth_date(self):
        """Test de la méthode get_age() sans date de naissance"""
        # Créer un superuser sans date de naissance
        User = get_user_model()
        user = User.objects.create_superuser(
            email='admin@gmail.com',
            password='adminpass123',
            name='Admin'
        )
        
        self.assertIsNone(user.get_age())

class PrivateUserApiTest(TestCase):
    def setUp(self):
        self.user=create_user(
            email='test@gmail.com',
            password='testpass123',
            name='Test Name',
            genre='F',
            date_naissance='2001-04-08'
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




class SuperUserCreationTest(TestCase):
    """Tests pour la création de superuser"""

    def test_create_superuser_without_personal_fields(self):
        """Test que le superuser peut être créé sans genre et date de naissance"""
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            email='admin@gmail.com',
            password='adminpass123',
            name='Admin User'
        )
        
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
        self.assertIsNone(admin_user.genre)
        self.assertIsNone(admin_user.date_naissance)
        self.assertEqual(admin_user.email, 'admin@gmail.com')

    def test_create_superuser_with_personal_fields(self):
        """Test que le superuser peut être créé avec genre et date de naissance (optionnel)"""
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            email='admin@gmail.com',
            password='adminpass123',
            name='Admin User',
            genre='H',
            date_naissance='1985-01-01'
        )
        
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
        self.assertEqual(admin_user.genre, 'H')
        self.assertEqual(str(admin_user.date_naissance), '1985-01-01')