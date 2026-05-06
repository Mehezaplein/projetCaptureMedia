from django.shortcuts import render, redirect


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


# ── Anciennes pages admin → redirigées vers le dashboard ──────────────────────

def AddAnnoncePage(request):
    return redirect('/dashboard/articles/ajouter/')


def AddAdminPage(request):
    return redirect('/dashboard/utilisateurs/ajouter/')


def ListeAdminPage(request):
    return redirect('/dashboard/utilisateurs/')


def EditAdminPage(request):
    return redirect('/dashboard/utilisateurs/')
