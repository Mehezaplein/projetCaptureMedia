from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from .models import (Article, Category, Comment, Poll, PollChoice, Newsletter, MediaFile,
                     SiteSettings, Advertisement, DonationChannel, DonationCampaign, Donation)

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

    # Incrémenter les vues sans réécrire tout l'objet (évite de gonfler/altérer les autres champs)
    Article.objects.filter(pk=article.pk).update(views_count=F('views_count') + 1)
    article.views_count += 1

    # Articles similaires (même catégorie)
    related_articles = Article.objects.filter(
        status='published',
        category=article.category
    ).exclude(pk=article.pk).order_by('-published_at')[:3]

    # Commentaires approuvés
    comments = article.comments.filter(status='approved').order_by('-created_at')

    # Les commentaires sont activés si le réglage global ET l'article l'autorisent
    site_settings = SiteSettings.get_settings()
    comments_enabled = site_settings.enable_comments and article.allow_comments

    context = {
        'article': article,
        'related_articles': related_articles,
        'comments': comments,
        'comments_enabled': comments_enabled,
    }
    return render(request, "article_detail.html", context)

def CategoryArticlesPage(request, slug):
    """Articles d'une catégorie spécifique."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    articles_qs = Article.objects.filter(status='published', category=category).order_by('-published_at')

    per_page = SiteSettings.get_settings().articles_per_page or 10
    paginator = Paginator(articles_qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'category': category,
        'articles': page_obj,
        'page_obj': page_obj,
    }
    return render(request, "category_articles.html", context)

def SearchPage(request):
    """Résultats de recherche d'articles."""
    query = request.GET.get('q', '')
    page_obj = None
    if query:
        articles_qs = Article.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            status='published'
        ).distinct().order_by('-published_at')
        per_page = SiteSettings.get_settings().articles_per_page or 10
        paginator = Paginator(articles_qs, per_page)
        page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'query': query,
        'articles': page_obj,
        'page_obj': page_obj,
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

def VideosPage(request):
    """Fil Vidéos / Reportages : articles publiés possédant un média externe."""
    base_qs = Article.objects.filter(status='published').exclude(
        Q(media_url__isnull=True) | Q(media_url='')
    )

    platform = request.GET.get('platform', '')
    qs = base_qs.order_by('-published_at')
    if platform:
        qs = qs.filter(media_platform=platform)

    # Plateformes réellement présentes (pour les puces de filtre)
    available_platforms = list(
        base_qs.exclude(media_platform='').values_list('media_platform', flat=True).distinct()
    )

    per_page = SiteSettings.get_settings().articles_per_page or 12
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    platform_labels = {
        'youtube': 'YouTube', 'tiktok': 'TikTok', 'instagram': 'Instagram',
        'twitter': 'Twitter / X', 'facebook': 'Facebook', 'whatsapp': 'WhatsApp', 'other': 'Autre',
    }

    context = {
        'page_obj': page_obj,
        'videos': page_obj,
        'platform': platform,
        'available_platforms': available_platforms,
        'platform_labels': platform_labels,
    }
    return render(request, "videos.html", context)


def AboutPage(request):
    return render(request, "about.html")


def LegalPage(request):
    return render(request, "legal.html")

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
        site_settings = SiteSettings.get_settings()

        # Garde-fou : commentaires désactivés globalement ou sur l'article
        if not site_settings.enable_comments or not article.allow_comments:
            messages.error(request, "Les commentaires sont désactivés.")
            return redirect('article_detail', slug=slug)

        name = request.POST.get('name')
        email = request.POST.get('email')
        content = request.POST.get('content')

        if name and email and content:
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


# ─── Dons / Soutien ──────────────────────────────────────────────────────────

def SupportPage(request):
    """Page publique « Soutenir le média »."""
    site_settings = SiteSettings.get_settings()
    from django.utils import timezone as tz
    now = tz.now()

    campaign = DonationCampaign.objects.filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=now),
        is_active=True,
    ).order_by('-created_at').first()

    channels = DonationChannel.objects.filter(is_active=True).order_by('order', 'name')

    # Mur des donateurs : dons confirmés, non anonymes, avec mot de soutien en priorité
    donor_wall = Donation.objects.filter(status='confirmed', is_anonymous=False).order_by('-created_at')[:12]

    # Statistiques de confiance (preuve sociale)
    from django.db.models import Sum
    confirmed = Donation.objects.filter(status='confirmed')
    stats = {
        'donors_count': confirmed.count(),
        'total_collected': confirmed.filter(donation_type='financial').aggregate(
            t=Sum('amount'))['t'] or 0,
        'material_count': confirmed.filter(donation_type='material').count(),
    }

    # Montants suggérés (ancrage psychologique)
    suggested_amounts = [500, 1000, 2000, 5000, 10000]

    context = {
        'site_settings': site_settings,
        'campaign': campaign,
        'channels': channels,
        'donor_wall': donor_wall,
        'stats': stats,
        'suggested_amounts': suggested_amounts,
    }
    return render(request, "support.html", context)


def DonationCreate(request):
    """Enregistre un don (financier ou matériel) soumis par le public."""
    if request.method != 'POST':
        return redirect('support')

    donation_type = request.POST.get('donation_type', 'financial')
    donor_name = (request.POST.get('donor_name') or '').strip()
    donor_email = (request.POST.get('donor_email') or '').strip()
    donor_phone = (request.POST.get('donor_phone') or '').strip()
    is_anonymous = request.POST.get('is_anonymous') == 'on'
    message = (request.POST.get('message') or '').strip()
    campaign_id = request.POST.get('campaign') or None

    if not donor_name and not is_anonymous:
        messages.error(request, "Veuillez indiquer votre nom ou cocher « don anonyme ».")
        return redirect('support')

    donation = Donation(
        donation_type=donation_type if donation_type in ('financial', 'material') else 'financial',
        donor_name=donor_name or 'Anonyme',
        donor_email=donor_email,
        donor_phone=donor_phone,
        is_anonymous=is_anonymous,
        message=message,
        campaign_id=campaign_id,
        status='pending',
    )

    if donation.donation_type == 'financial':
        amount_raw = (request.POST.get('amount') or '').strip().replace(' ', '')
        if not amount_raw.isdigit() or int(amount_raw) <= 0:
            messages.error(request, "Veuillez indiquer un montant valide.")
            return redirect('support')
        donation.amount = int(amount_raw)
        channel_id = request.POST.get('channel') or None
        donation.channel_id = channel_id
        donation.transaction_reference = (request.POST.get('transaction_reference') or '').strip()
    else:
        item = (request.POST.get('item_description') or '').strip()
        if not item:
            messages.error(request, "Veuillez décrire le matériel que vous souhaitez offrir.")
            return redirect('support')
        donation.item_description = item
        ev = (request.POST.get('estimated_value') or '').strip().replace(' ', '')
        if ev.isdigit():
            donation.estimated_value = int(ev)

    donation.save()
    messages.success(
        request,
        "Merci infiniment pour votre soutien ! Votre don a bien été enregistré. "
        "Notre équipe le confirmera après réception."
    )
    return redirect('support')
