from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexPage, name="index"),
    path('login', views.LoginPage, name="login"),
    path('signUp', views.Sign_upPage, name="signUp"),
    path('contact', views.ContactPage, name="contact"),
    path('forgot', views.ForgotPage, name="forgot"),
]
