from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.IndexPage, name="index"),
    path('article/<slug:slug>/', views.ArticleDetailPage, name="article_detail"),
    path('category/<slug:slug>/', views.CategoryArticlesPage, name="category_articles"),
    path('search/', views.SearchPage, name="search"),
    path('newsletter/signup/', views.NewsletterSignup, name="newsletter_signup"),
    path('poll/vote/<int:poll_id>/', views.PollVote, name="poll_vote"),
    path('videos/', views.VideosPage, name="videos"),
    # Ancien lien médiathèque → redirige vers le fil Vidéos
    path('mediatheque/', RedirectView.as_view(pattern_name='videos', permanent=True)),
    path('a-propos/', views.AboutPage, name="about"),
    path('mentions-legales/', views.LegalPage, name="legal"),
    path('article/<slug:slug>/comment/', views.AddComment, name="add_comment"),
    
    path('ad/click/<int:ad_id>/', views.AdClick, name="ad_click"),
    path('newsletter/unsubscribe/', views.NewsletterUnsubscribe, name="newsletter_unsubscribe"),

    # Dons / Soutien
    path('soutenir/', views.SupportPage, name="support"),
    path('soutenir/envoyer/', views.DonationCreate, name="donation_create"),

    path('login/', views.LoginPage, name="login"),
    path('signUp/', views.Sign_upPage, name="signUp"),
    path('contact/', views.ContactPage, name="contact"),
    path('forgot/', views.ForgotPage, name="forgot"),
]
