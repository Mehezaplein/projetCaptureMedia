from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from .models import Article, Category, Comment, Advertisement, Poll, PollChoice, Newsletter, MediaFile

def IndexPage(request):
    """Page d'accueil avec articles à la une, dernières actualités et sidebar."""
    # Plus d'articles à la une pour le slider
    featured_articles = Article.objects.filter(status='published', is_featured=True).order_by('-published_at')[:8]
    latest_articles = Article.objects.filter(status='published').order_by('-published_at')[:6]
    
    # Publicités (multiples)
    today = timezone.now().date()
    top_ads = Advertisement.objects.filter(
        position='header', is_active=True, 
        start_date__lte=today, end_date__gte=today
    ).order_by('?')[:3]
    
    sidebar_ads = Advertisement.objects.filter(
        position='sidebar_top', is_active=True,
        start_date__lte=today, end_date__gte=today
    ).order_by('-created_at')[:2]
    
    # Suggestions (basées sur les plus vus ou aléatoires)
    suggestions = Article.objects.filter(status='published').order_by('-views_count')[:5]
    
    # Sondage actif
    active_poll = Poll.objects.filter(is_active=True).first()
    
    context = {
        'featured_articles': featured_articles,
        'latest_articles': latest_articles,
        'suggestions': suggestions,
        'top_ads': top_ads,
        'sidebar_ads': sidebar_ads,
        'active_poll': active_poll,
    }
    return render(request, "index.html", context)

def ArticleDetailPage(request, slug):
    """Page de lecture d'un article."""
    article = get_object_or_404(Article, slug=slug, status='published')
    
    # Incrémenter les vues
    article.views_count += 1
    article.save()
    
    # Articles similaires (même catégorie)
    related_articles = Article.objects.filter(
        status='published', 
        category=article.category
    ).exclude(pk=article.pk).order_by('-published_at')[:3]
    
    # Commentaires approuvés
    comments = article.comments.filter(status='approved').order_by('-created_at')
    
    today = timezone.now().date()
    sidebar_ads = Advertisement.objects.filter(
        position='sidebar_top', is_active=True,
        start_date__lte=today, end_date__gte=today
    ).order_by('-created_at')[:2]

    context = {
        'article': article,
        'related_articles': related_articles,
        'comments': comments,
        'sidebar_ads': sidebar_ads,
    }
    return render(request, "article_detail.html", context)

def CategoryArticlesPage(request, slug):
    """Articles d'une catégorie spécifique."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    articles = Article.objects.filter(status='published', category=category).order_by('-published_at')
    
    context = {
        'category': category,
        'articles': articles,
    }
    return render(request, "category_articles.html", context)

def SearchPage(request):
    """Résultats de recherche d'articles."""
    query = request.GET.get('q', '')
    articles = []
    if query:
        articles = Article.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            status='published'
        ).distinct()
    
    context = {
        'query': query,
        'articles': articles,
    }
    return render(request, "search_results.html", context)

def NewsletterSignup(request):
    """Inscription newsletter avec support AJAX et redirection standard."""
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            sub, created = Newsletter.objects.get_or_create(email=email)
            msg = "Inscription réussie ! Merci de nous suivre." if created else "Vous êtes déjà inscrit à notre newsletter."
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': msg})
            
            messages.success(request, msg)
            return redirect(request.META.get('HTTP_REFERER', 'index'))
            
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'message': 'Email invalide.'})
    
    messages.error(request, "Erreur lors de l'inscription.")
    return redirect('index')

def PollVote(request, poll_id):
    """Voter pour un sondage."""
    if request.method == 'POST':
        choice_id = request.POST.get('choice')
        if choice_id:
            choice = get_object_or_404(PollChoice, pk=choice_id, poll_id=poll_id)
            choice.votes += 1
            choice.save()
            messages.success(request, "Merci pour votre vote !")
            return redirect(request.META.get('HTTP_REFERER', 'index'))
    messages.error(request, "Erreur lors du vote.")
    return redirect('index')

def MediathequePage(request):
    """Page d'affichage de la médiathèque (images, vidéos, etc.)."""
    media_files = MediaFile.objects.all().order_by('-id')
    context = {
        'media_files': media_files,
    }
    return render(request, "mediatheque.html", context)

def LoginPage(request):
    return render(request, "login.html")

def Sign_upPage(request):
    return render(request, "sign-up.html")

def ContactPage(request):
    return render(request, "contact.html")

def ForgotPage(request):
    return render(request, "forgot.html")

def AddComment(request, slug):
    """Ajouter un commentaire à un article."""
    if request.method == 'POST':
        article = get_object_or_404(Article, slug=slug)
        name = request.POST.get('name')
        email = request.POST.get('email')
        content = request.POST.get('content')
        
        if name and email and content:
            Comment.objects.create(
                article=article,
                author_name=name,
                author_email=email,
                content=content,
                status='pending'  # Par défaut en attente
            )
            messages.success(request, "Merci ! Votre commentaire est en attente de modération.")
        else:
            messages.error(request, "Veuillez remplir tous les champs.")
            
    return redirect('article_detail', slug=slug)
