from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F
from django.http import JsonResponse
from django.contrib import messages
from .models import Article, Category, Comment, Poll, PollChoice, Newsletter, MediaFile, SiteSettings, Advertisement

def IndexPage(request):
    featured_articles = Article.objects.filter(status='published', is_featured=True).order_by('-published_at')[:8]
    latest_articles = Article.objects.filter(status='published').order_by('-published_at')[:6]

    context = {
        'featured_articles': featured_articles,
        'latest_articles': latest_articles,
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
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'comments': comments,
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
    if request.method == 'POST':
        choice_ids = request.POST.getlist('choice')
        if choice_ids:
            poll = get_object_or_404(Poll, pk=poll_id)
            for cid in choice_ids:
                PollChoice.objects.filter(pk=cid, poll_id=poll_id).update(votes=F('votes') + 1)

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                poll.refresh_from_db()
                choices_data = []
                for c in poll.choices.all():
                    choices_data.append({
                        'id': c.id,
                        'text': c.text,
                        'votes': c.votes,
                        'percentage': c.percentage,
                    })
                return JsonResponse({
                    'status': 'ok',
                    'total': poll.total_votes,
                    'choices': choices_data,
                })

            messages.success(request, "Merci pour votre vote !")
            return redirect(request.META.get('HTTP_REFERER', 'index'))

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'message': 'Choix invalide.'})
    messages.error(request, "Erreur lors du vote.")
    return redirect('index')

def MediathequePage(request):
    """Page d'affichage de la médiathèque (images, vidéos, etc.)."""
    media_files = MediaFile.objects.all().order_by('-id')
    context = {
        'media_files': media_files,
    }
    return render(request, "mediatheque.html", context)

def AdClick(request, ad_id):
    ad = get_object_or_404(Advertisement, pk=ad_id)
    Advertisement.objects.filter(pk=ad_id).update(clicks=F('clicks') + 1)
    return redirect(ad.url)


def NewsletterUnsubscribe(request):
    from django.utils import timezone as tz
    email = request.GET.get('email', '')
    success = False
    if email:
        try:
            sub = Newsletter.objects.get(email=email)
            if sub.is_active:
                sub.is_active = False
                sub.unsubscribed_at = tz.now()
                sub.save()
            success = True
        except Newsletter.DoesNotExist:
            success = True
    return render(request, "newsletter_unsubscribe.html", {'success': success, 'email': email})


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
            site_settings = SiteSettings.get_settings()
            status = 'approved' if not site_settings.comment_moderation else 'pending'
            Comment.objects.create(
                article=article,
                author_name=name,
                author_email=email,
                content=content,
                status=status,
            )
            if status == 'approved':
                messages.success(request, "Merci ! Votre commentaire a été publié.")
            else:
                messages.success(request, "Merci ! Votre commentaire est en attente de modération.")
        else:
            messages.error(request, "Veuillez remplir tous les champs.")

    return redirect('article_detail', slug=slug)
