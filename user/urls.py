from django.urls import path
from .views import temp_login

app_name = "user"

urlpatterns = [
    path("login/", temp_login, name="login"),
]
