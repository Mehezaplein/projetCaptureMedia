from django.shortcuts import render


def IndexPage(request):
    return render(request, "index.html")


def LoginPage(request):
    return render(request, "login.html")


def Sign_upPage(request):
    return render(request, "sign-up.html")


def ContactPage(request):
    return render(request, "contact.html")


def ForgotPage(request):
    return render(request, "forgot.html")
