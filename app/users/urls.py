from django.urls import path
from users import views
from .views import get_users,request_password_reset,reset_password
app_name='user'


urlpatterns=[
    path('create/',views.CreateUserView.as_view(),name='create'),
    path('token/',views.CreateTokenView.as_view(),name='token'),
    path("moi/",views.ManageApiView.as_view(),name='moi'),
    path("get_users/", get_users),
   path("password-reset/", request_password_reset, name="password_reset"),
    path("password-reset/confirm/", reset_password, name="password_reset_confirm"),
]