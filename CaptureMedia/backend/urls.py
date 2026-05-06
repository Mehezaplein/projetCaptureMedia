from django.urls import path 
from . import views
urlpatterns = [
    path('forgot' , views.ForgotPage , name="forgot"),
    path('' , views.IndexPage , name="index"),
    path('login' , views.LoginPage , name="login"),
    path('signUp' , views.Sign_upPage , name="signUp"),
    path('ajouterAdmin' , views.AddAdminPage , name="ajouterAdmin"),
    path('listeAdmin' , views.ListeAdminPage , name="listeAdmin"),
    path('modifierAdmin', views.EditAdminPage, name="modifierAdmin")
]
