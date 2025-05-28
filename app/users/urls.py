from django.urls import path
from users import views

app_name='user'


urlpatterns=[
    path('create/',views.CreateUserView.as_view(),name='create'),
    path('token/',views.CreateTokenView.as_view(),name='token'),
    path("moi/",views.ManageApiView.as_view(),name='moi')
]