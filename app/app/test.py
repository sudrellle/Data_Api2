from django.test import SimpleTestCase
from rest_framework.test import APIClient
from app import calc

class Test_CALC(SimpleTestCase):
    def test(self):
        res=calc.caldulate(4,9)
        self.assertEqual(res,13)

    def test_sub(self):
        re_sub=calc.calculate_sub(10,5) 
        self.assertEqual(re_sub,5)  

"""class TestViews(SimpleTestCase):
    def test_gretings(self):
        client=APIClient()
        res=client.get('/greetings') 
        self.assertEqual(res.status_code,200) 
        self.assertEqual(
            res.data,['hello','bonjour','hi','holla']
        )  """    