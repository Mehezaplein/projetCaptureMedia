from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexPage, name="index"),
    path('article/<slug:slug>/', views.ArticleDetailPage, name="article_detail"),
    path('category/<slug:slug>/', views.CategoryArticlesPage, name="category_articles"),
    path('search/', views.SearchPage, name="search"),
    path('newsletter/signup/', views.NewsletterSignup, name="newsletter_signup"),
    path('poll/vote/<int:poll_id>/', views.PollVote, name="poll_vote"),
    path('mediatheque/', views.MediathequePage, name="mediatheque"),
    path('article/<slug:slug>/comment/', views.AddComment, name="add_comment"),
    
    path('ad/click/<int:ad_id>/', views.AdClick, name="ad_click"),
    path('newsletter/unsubscribe/', views.NewsletterUnsubscribe, name="newsletter_unsubscribe"),

    path('login/', views.LoginPage, name="login"),
    path('signUp/', views.Sign_upPage, name="signUp"),
    path('contact/', views.ContactPage, name="contact"),
    path('forgot/', views.ForgotPage, name="forgot"),
]
