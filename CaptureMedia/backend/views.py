from django.shortcuts import render

# Create your views here.

def ForgotPage (request):
    return render (request , "forgot.html")

def IndexPage (request):
    return render (request , "index.html")

def LoginPage(request):
    return render (request , "login.html")

def Sign_upPage(request):
    return render (request ,"sign-up.html")

def AddAdminPage(request):
    return render (request , "addAdmin.html")

def ListeAdminPage(request):
    return render (request , "listeAdmin.html")

def EditAdminPage(request):
    return render (request, "EditAdmin.html")
