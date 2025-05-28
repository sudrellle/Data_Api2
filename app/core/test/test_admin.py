from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

class AdminTest(TestCase):
    def setUp(self):
        self.client=Client()
        self.admin_user=get_user_model().objects.create_superuser(
            email='user@gmail.com',
            password='testpass123'
        )
        self.client.force_login(self.admin_user)
        self.user=get_user_model().objects.create_user(
            email='esther@gmail.com',
            password='testpass123',
            name='Test user'

        )

    def test_users_list(self):
        url=reverse('admin:core_user_changelist') 
        res=self. client.get(url)  
        self.assertContains(res,self.user.name)
        self.assertContains(res,self.user.email)

    def test_edit_user(self):
        url=reverse('admin:core_user_change',args=[self.user.id])
        res=self.client.get(url)
        self.assertEqual(res.status_code,200)

    def test_create_user_page(self):
            pass



