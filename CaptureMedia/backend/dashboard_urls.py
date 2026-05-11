from django.urls import path
from . import dashboard_views as views

app_name = 'dashboard'

urlpatterns = [
    # Auth
    path('login/', views.dashboard_login, name='login'),
    path('logout/', views.dashboard_logout, name='logout'),

    # Home
    path('', views.dashboard_index, name='index'),

    # Articles
    path('articles/', views.articles_list, name='articles_list'),
    path('articles/ajouter/', views.article_add, name='article_add'),
    path('articles/<int:pk>/modifier/', views.article_edit, name='article_edit'),
    path('articles/<int:pk>/supprimer/', views.article_delete, name='article_delete'),
    path('articles/<int:pk>/toggle/', views.article_toggle_status, name='article_toggle'),

    # Catégories
    path('categories/', views.categories_list, name='categories_list'),
    path('categories/ajouter/', views.category_add, name='category_add'),
    path('categories/<int:pk>/modifier/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/supprimer/', views.category_delete, name='category_delete'),

    # Tags
    path('tags/', views.tags_list, name='tags_list'),
    path('tags/ajouter/', views.tag_add, name='tag_add'),
    path('tags/<int:pk>/supprimer/', views.tag_delete, name='tag_delete'),

    # Commentaires
    path('commentaires/', views.comments_list, name='comments_list'),
    path('commentaires/<int:pk>/action/', views.comment_action, name='comment_action'),
    path('commentaires/<int:pk>/supprimer/', views.comment_delete, name='comment_delete'),

    # Médias
    path('medias/', views.media_library, name='media_library'),
    path('medias/inutilises/', views.media_unused, name='media_unused'),
    path('medias/upload/', views.media_upload, name='media_upload'),
    path('medias/<int:pk>/supprimer/', views.media_delete, name='media_delete'),

    # Newsletter
    path('newsletter/', views.newsletter_list, name='newsletter_list'),
    path('newsletter/envoyer/', views.newsletter_send, name='newsletter_send'),
    path('newsletter/historique/', views.newsletter_history, name='newsletter_history'),
    path('newsletter/<int:pk>/supprimer/', views.newsletter_delete, name='newsletter_delete'),

    # Publicités
    path('publicites/', views.ads_list, name='ads_list'),
    path('publicites/ajouter/', views.ad_add, name='ad_add'),
    path('publicites/<int:pk>/modifier/', views.ad_edit, name='ad_edit'),
    path('publicites/<int:pk>/supprimer/', views.ad_delete, name='ad_delete'),
    path('publicites/<int:pk>/toggle/', views.ad_toggle, name='ad_toggle'),

    # Breaking News
    path('breaking-news/', views.breaking_news_list, name='breaking_news_list'),
    path('breaking-news/ajouter/', views.breaking_news_add, name='breaking_news_add'),
    path('breaking-news/<int:pk>/toggle/', views.breaking_news_toggle, name='breaking_news_toggle'),
    path('breaking-news/<int:pk>/supprimer/', views.breaking_news_delete, name='breaking_news_delete'),

    # Sondages
    path('sondages/', views.polls_list, name='polls_list'),
    path('sondages/ajouter/', views.poll_add, name='poll_add'),
    path('sondages/<int:pk>/modifier/', views.poll_edit, name='poll_edit'),
    path('sondages/<int:pk>/supprimer/', views.poll_delete, name='poll_delete'),
    path('sondages/<int:pk>/toggle/', views.poll_toggle, name='poll_toggle'),

    # Utilisateurs
    path('utilisateurs/', views.users_list, name='users_list'),
    path('utilisateurs/ajouter/', views.user_add, name='user_add'),
    path('utilisateurs/<int:pk>/modifier/', views.user_edit, name='user_edit'),
    path('utilisateurs/<int:pk>/supprimer/', views.user_delete, name='user_delete'),

    # Paramètres & Profil
    path('parametres/', views.settings_view, name='settings'),
    path('profil/', views.profile_view, name='profile'),
]
