from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta

from .models import (
    Article, Category, Tag, Comment, MediaFile,
    Newsletter, Advertisement, BreakingNews, Poll, PollChoice, SiteSettings
)


def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard:index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('dashboard:index')
        else:
            messages.error(request, "Identifiants invalides ou accès non autorisé.")
    return render(request, 'dashboard/login.html')


def dashboard_logout(request):
    logout(request)
    return redirect('dashboard:login')


# ─── Helpers ───────────────────────────────────────────────────────────────────

def is_htmx(request):
    return request.headers.get('HX-Request') == 'true'


def get_stats():
    now = timezone.now()
    last_30 = now - timedelta(days=30)
    return {
        'total_articles': Article.objects.count(),
        'published_articles': Article.objects.filter(status='published').count(),
        'draft_articles': Article.objects.filter(status='draft').count(),
        'total_categories': Category.objects.count(),
        'total_comments': Comment.objects.count(),
        'pending_comments': Comment.objects.filter(status='pending').count(),
        'total_users': User.objects.count(),
        'newsletter_subscribers': Newsletter.objects.filter(is_active=True).count(),
        'total_views': Article.objects.aggregate(total=Sum('views_count'))['total'] or 0,
        'active_ads': Advertisement.objects.filter(is_active=True).count(),
        'active_breaking': BreakingNews.objects.filter(is_active=True).count(),
        'active_polls': Poll.objects.filter(is_active=True).count(),
        'recent_articles': Article.objects.filter(created_at__gte=last_30).count(),
        'recent_comments': Comment.objects.filter(created_at__gte=last_30).count(),
    }


# ─── Dashboard Home ────────────────────────────────────────────────────────────

@login_required
def dashboard_index(request):
    stats = get_stats()
    recent_articles = Article.objects.select_related('author', 'category').order_by('-created_at')[:5]
    recent_comments = Comment.objects.select_related('article').order_by('-created_at')[:5]
    top_articles = Article.objects.filter(status='published').order_by('-views_count')[:5]
    categories_data = Category.objects.annotate(
        count=Count('articles', filter=Q(articles__status='published'))
    ).order_by('-count')[:6]
    context = {
        'stats': stats,
        'recent_articles': recent_articles,
        'recent_comments': recent_comments,
        'top_articles': top_articles,
        'categories_data': categories_data,
        'page_title': 'Tableau de bord',
        'active_menu': 'dashboard',
    }
    return render(request, 'dashboard/index.html', context)


# ─── Articles ──────────────────────────────────────────────────────────────────

@login_required
def articles_list(request):
    qs = Article.objects.select_related('author', 'category').order_by('-created_at')
    search = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')

    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(excerpt__icontains=search))
    if status_filter:
        qs = qs.filter(status=status_filter)
    if category_filter:
        qs = qs.filter(category_id=category_filter)

    paginator = Paginator(qs, 15)
    page = paginator.get_page(request.GET.get('page', 1))

    categories = Category.objects.filter(is_active=True)
    context = {
        'page_obj': page,
        'categories': categories,
        'search': search,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'page_title': 'Articles',
        'active_menu': 'articles',
    }
    if is_htmx(request):
        return render(request, 'dashboard/articles/_table.html', context)
    return render(request, 'dashboard/articles/list.html', context)


@login_required
def article_add(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        excerpt = request.POST.get('excerpt', '').strip()
        category_id = request.POST.get('category') or None
        status = request.POST.get('status', 'draft')
        is_featured = request.POST.get('is_featured') == 'on'
        is_breaking = request.POST.get('is_breaking') == 'on'
        allow_comments = request.POST.get('allow_comments') == 'on'
        tags_input = request.POST.get('tags', '')

        if not title or not content:
            messages.error(request, "Le titre et le contenu sont obligatoires.")
        else:
            article = Article(
                title=title,
                content=content,
                excerpt=excerpt,
                category_id=category_id,
                author=request.user,
                status=status,
                is_featured=is_featured,
                is_breaking=is_breaking,
                allow_comments=allow_comments,
            )
            if 'featured_image' in request.FILES:
                article.featured_image = request.FILES['featured_image']
            article.save()

            # Tags
            for tag_name in [t.strip() for t in tags_input.split(',') if t.strip()]:
                tag, _ = Tag.objects.get_or_create(name=tag_name,
                                                    defaults={'slug': slugify(tag_name)})
                article.tags.add(tag)

            messages.success(request, f'Article "{title}" créé avec succès.')
            return redirect('dashboard:articles_list')

    categories = Category.objects.filter(is_active=True)
    tags = Tag.objects.all()
    context = {
        'categories': categories,
        'tags': tags,
        'page_title': 'Nouvel article',
        'active_menu': 'articles',
    }
    return render(request, 'dashboard/articles/form.html', context)


@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        article.title = request.POST.get('title', '').strip()
        article.content = request.POST.get('content', '').strip()
        article.excerpt = request.POST.get('excerpt', '').strip()
        article.category_id = request.POST.get('category') or None
        article.status = request.POST.get('status', 'draft')
        article.is_featured = request.POST.get('is_featured') == 'on'
        article.is_breaking = request.POST.get('is_breaking') == 'on'
        article.allow_comments = request.POST.get('allow_comments') == 'on'

        if 'featured_image' in request.FILES:
            article.featured_image = request.FILES['featured_image']

        article.save()

        # Tags
        tags_input = request.POST.get('tags', '')
        article.tags.clear()
        for tag_name in [t.strip() for t in tags_input.split(',') if t.strip()]:
            tag, _ = Tag.objects.get_or_create(name=tag_name,
                                                defaults={'slug': slugify(tag_name)})
            article.tags.add(tag)

        messages.success(request, f'Article mis à jour.')
        return redirect('dashboard:articles_list')

    categories = Category.objects.filter(is_active=True)
    tags = Tag.objects.all()
    article_tags = ', '.join(article.tags.values_list('name', flat=True))
    context = {
        'article': article,
        'categories': categories,
        'tags': tags,
        'article_tags': article_tags,
        'page_title': f'Modifier: {article.title[:40]}',
        'active_menu': 'articles',
    }
    return render(request, 'dashboard/articles/form.html', context)


@login_required
@require_POST
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    title = article.title
    article.delete()
    if is_htmx(request):
        return HttpResponse('')
    messages.success(request, f'Article "{title}" supprimé.')
    return redirect('dashboard:articles_list')


@login_required
@require_POST
def article_toggle_status(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.status == 'published':
        article.status = 'draft'
    else:
        article.status = 'published'
        if not article.published_at:
            article.published_at = timezone.now()
    article.save()
    if is_htmx(request):
        return render(request, 'dashboard/articles/_row.html', {'article': article})
    return redirect('dashboard:articles_list')


# ─── Catégories ────────────────────────────────────────────────────────────────

@login_required
def categories_list(request):
    qs = Category.objects.annotate(
        count=Count('articles', filter=Q(articles__status='published'))
    ).order_by('order', 'name')
    search = request.GET.get('q', '')
    if search:
        qs = qs.filter(name__icontains=search)

    context = {
        'categories': qs,
        'search': search,
        'page_title': 'Catégories',
        'active_menu': 'categories',
    }
    if is_htmx(request):
        return render(request, 'dashboard/categories/_table.html', context)
    return render(request, 'dashboard/categories/list.html', context)


@login_required
def category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        parent_id = request.POST.get('parent') or None
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'

        if not name:
            messages.error(request, "Le nom est obligatoire.")
        else:
            cat = Category(name=name, description=description,
                           parent_id=parent_id, order=order, is_active=is_active)
            if 'image' in request.FILES:
                cat.image = request.FILES['image']
            cat.save()
            messages.success(request, f'Catégorie "{name}" créée.')
            return redirect('dashboard:categories_list')

    parents = Category.objects.filter(parent=None, is_active=True)
    return render(request, 'dashboard/categories/form.html', {
        'parents': parents,
        'page_title': 'Nouvelle catégorie',
        'active_menu': 'categories',
    })


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST.get('name', '').strip()
        category.description = request.POST.get('description', '').strip()
        category.parent_id = request.POST.get('parent') or None
        category.order = request.POST.get('order', 0)
        category.is_active = request.POST.get('is_active') == 'on'
        if 'image' in request.FILES:
            category.image = request.FILES['image']
        category.save()
        messages.success(request, 'Catégorie mise à jour.')
        return redirect('dashboard:categories_list')

    parents = Category.objects.filter(parent=None, is_active=True).exclude(pk=pk)
    return render(request, 'dashboard/categories/form.html', {
        'category': category,
        'parents': parents,
        'page_title': f'Modifier: {category.name}',
        'active_menu': 'categories',
    })


@login_required
@require_POST
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    name = cat.name
    cat.delete()
    if is_htmx(request):
        return HttpResponse('')
    messages.success(request, f'Catégorie "{name}" supprimée.')
    return redirect('dashboard:categories_list')


# ─── Tags ──────────────────────────────────────────────────────────────────────

@login_required
def tags_list(request):
    qs = Tag.objects.annotate(count=Count('articles')).order_by('name')
    search = request.GET.get('q', '')
    if search:
        qs = qs.filter(name__icontains=search)
    context = {
        'tags': qs,
        'search': search,
        'page_title': 'Tags',
        'active_menu': 'tags',
    }
    if is_htmx(request):
        return render(request, 'dashboard/tags/_table.html', context)
    return render(request, 'dashboard/tags/list.html', context)


@login_required
@require_POST
def tag_add(request):
    name = request.POST.get('name', '').strip()
    if name:
        Tag.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
        messages.success(request, f'Tag "{name}" ajouté.')
    return redirect('dashboard:tags_list')


@login_required
@require_POST
def tag_delete(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    name = tag.name
    tag.delete()
    if is_htmx(request):
        return HttpResponse('')
    messages.success(request, f'Tag "{name}" supprimé.')
    return redirect('dashboard:tags_list')


# ─── Commentaires ──────────────────────────────────────────────────────────────

@login_required
def comments_list(request):
    qs = Comment.objects.select_related('article').order_by('-created_at')
    search = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    if search:
        qs = qs.filter(Q(content__icontains=search) | Q(author_name__icontains=search))
    if status_filter:
        qs = qs.filter(status=status_filter)

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_obj': page,
        'search': search,
        'status_filter': status_filter,
        'page_title': 'Commentaires',
        'active_menu': 'comments',
        'pending_count': Comment.objects.filter(status='pending').count(),
    }
    if is_htmx(request):
        return render(request, 'dashboard/comments/_table.html', context)
    return render(request, 'dashboard/comments/list.html', context)


@login_required
@require_POST
def comment_action(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    action = request.POST.get('action', '')
    if action == 'approve':
        comment.status = 'approved'
    elif action == 'reject':
        comment.status = 'rejected'
    elif action == 'spam':
        comment.status = 'spam'
    comment.save()
    if is_htmx(request):
        return render(request, 'dashboard/comments/_row.html', {'comment': comment})
    return redirect('dashboard:comments_list')


@login_required
@require_POST
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    if is_htmx(request):
        return HttpResponse('')
    return redirect('dashboard:comments_list')


# ─── Médias ────────────────────────────────────────────────────────────────────

@login_required
def media_library(request):
    qs = MediaFile.objects.select_related('uploaded_by').order_by('-uploaded_at')
    type_filter = request.GET.get('type', '')
    if type_filter:
        qs = qs.filter(file_type=type_filter)

    paginator = Paginator(qs, 24)
    page = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_obj': page,
        'type_filter': type_filter,
        'page_title': 'Bibliothèque médias',
        'active_menu': 'media',
    }
    if is_htmx(request):
        return render(request, 'dashboard/media/_grid.html', context)
    return render(request, 'dashboard/media/library.html', context)


@login_required
@require_POST
def media_upload(request):
    files = request.FILES.getlist('files')
    uploaded = []
    for f in files:
        ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''
        if ext in ('jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'):
            ftype = 'image'
        elif ext in ('mp4', 'avi', 'mov', 'mkv', 'webm'):
            ftype = 'video'
        elif ext in ('mp3', 'wav', 'ogg'):
            ftype = 'audio'
        else:
            ftype = 'document'
        mf = MediaFile.objects.create(
            file=f,
            file_type=ftype,
            title=f.name,
            file_size=f.size,
            uploaded_by=request.user,
        )
        uploaded.append(mf)
    messages.success(request, f'{len(uploaded)} fichier(s) uploadé(s).')
    if is_htmx(request):
        return render(request, 'dashboard/media/_uploaded.html', {'files': uploaded})
    return redirect('dashboard:media_library')


@login_required
@require_POST
def media_delete(request, pk):
    mf = get_object_or_404(MediaFile, pk=pk)
    mf.file.delete(save=False)
    mf.delete()
    if is_htmx(request):
        return HttpResponse('')
    return redirect('dashboard:media_library')


# ─── Newsletter ────────────────────────────────────────────────────────────────

@login_required
def newsletter_list(request):
    qs = Newsletter.objects.order_by('-subscribed_at')
    search = request.GET.get('q', '')
    active_filter = request.GET.get('active', '')

    if search:
        qs = qs.filter(Q(email__icontains=search) | Q(first_name__icontains=search))
    if active_filter == '1':
        qs = qs.filter(is_active=True)
    elif active_filter == '0':
        qs = qs.filter(is_active=False)

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_obj': page,
        'search': search,
        'active_filter': active_filter,
        'total_active': Newsletter.objects.filter(is_active=True).count(),
        'page_title': 'Newsletter',
        'active_menu': 'newsletter',
    }
    if is_htmx(request):
        return render(request, 'dashboard/newsletter/_table.html', context)
    return render(request, 'dashboard/newsletter/list.html', context)


@login_required
@require_POST
def newsletter_delete(request, pk):
    sub = get_object_or_404(Newsletter, pk=pk)
    sub.delete()
    if is_htmx(request):
        return HttpResponse('')
    return redirect('dashboard:newsletter_list')


# ─── Publicités ────────────────────────────────────────────────────────────────

@login_required
def ads_list(request):
    ads = Advertisement.objects.order_by('-created_at')
    context = {
        'ads': ads,
        'page_title': 'Publicités',
        'active_menu': 'ads',
    }
    return render(request, 'dashboard/ads/list.html', context)


@login_required
def ad_add(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        url = request.POST.get('url', '').strip()
        position = request.POST.get('position', '')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = request.POST.get('is_active') == 'on'

        if not title or not url or 'image' not in request.FILES:
            messages.error(request, "Titre, URL et image sont obligatoires.")
        else:
            Advertisement.objects.create(
                title=title, url=url, position=position,
                image=request.FILES['image'],
                start_date=start_date, end_date=end_date,
                is_active=is_active,
            )
            messages.success(request, f'Publicité "{title}" créée.')
            return redirect('dashboard:ads_list')

    return render(request, 'dashboard/ads/form.html', {
        'positions': Advertisement.POSITION_CHOICES,
        'page_title': 'Nouvelle publicité',
        'active_menu': 'ads',
    })


@login_required
def ad_edit(request, pk):
    ad = get_object_or_404(Advertisement, pk=pk)
    if request.method == 'POST':
        ad.title = request.POST.get('title', '').strip()
        ad.url = request.POST.get('url', '').strip()
        ad.position = request.POST.get('position', '')
        ad.start_date = request.POST.get('start_date')
        ad.end_date = request.POST.get('end_date')
        ad.is_active = request.POST.get('is_active') == 'on'
        if 'image' in request.FILES:
            ad.image = request.FILES['image']
        ad.save()
        messages.success(request, 'Publicité mise à jour.')
        return redirect('dashboard:ads_list')

    return render(request, 'dashboard/ads/form.html', {
        'ad': ad,
        'positions': Advertisement.POSITION_CHOICES,
        'page_title': f'Modifier: {ad.title}',
        'active_menu': 'ads',
    })


@login_required
@require_POST
def ad_delete(request, pk):
    ad = get_object_or_404(Advertisement, pk=pk)
    ad.image.delete(save=False)
    ad.delete()
    if is_htmx(request):
        return HttpResponse('')
    messages.success(request, 'Publicité supprimée.')
    return redirect('dashboard:ads_list')


@login_required
@require_POST
def ad_toggle(request, pk):
    ad = get_object_or_404(Advertisement, pk=pk)
    ad.is_active = not ad.is_active
    ad.save()
    if is_htmx(request):
        return render(request, 'dashboard/ads/_row.html', {'ad': ad})
    return redirect('dashboard:ads_list')


# ─── Breaking News ─────────────────────────────────────────────────────────────

@login_required
def breaking_news_list(request):
    items = BreakingNews.objects.order_by('order', '-created_at')
    context = {
        'items': items,
        'page_title': 'Breaking News',
        'active_menu': 'breaking_news',
    }
    return render(request, 'dashboard/breaking_news/list.html', context)


@login_required
@require_POST
def breaking_news_add(request):
    text = request.POST.get('text', '').strip()
    url = request.POST.get('url', '').strip()
    order = request.POST.get('order', 0)
    if text:
        item = BreakingNews.objects.create(text=text, url=url, order=order, is_active=True)
        messages.success(request, 'Breaking news ajouté.')
        if is_htmx(request):
            return render(request, 'dashboard/breaking_news/_row.html', {'item': item})
    return redirect('dashboard:breaking_news_list')


@login_required
@require_POST
def breaking_news_toggle(request, pk):
    item = get_object_or_404(BreakingNews, pk=pk)
    item.is_active = not item.is_active
    item.save()
    if is_htmx(request):
        return render(request, 'dashboard/breaking_news/_row.html', {'item': item})
    return redirect('dashboard:breaking_news_list')


@login_required
@require_POST
def breaking_news_delete(request, pk):
    item = get_object_or_404(BreakingNews, pk=pk)
    item.delete()
    if is_htmx(request):
        return HttpResponse('')
    return redirect('dashboard:breaking_news_list')


# ─── Sondages ──────────────────────────────────────────────────────────────────

@login_required
def polls_list(request):
    polls = Poll.objects.prefetch_related('choices').order_by('-created_at')
    context = {
        'polls': polls,
        'page_title': 'Sondages',
        'active_menu': 'polls',
    }
    return render(request, 'dashboard/polls/list.html', context)


@login_required
def poll_add(request):
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        description = request.POST.get('description', '').strip()
        allow_multiple = request.POST.get('allow_multiple') == 'on'
        choices = [c.strip() for c in request.POST.getlist('choices') if c.strip()]

        if not question or len(choices) < 2:
            messages.error(request, "Question et au moins 2 choix sont obligatoires.")
        else:
            poll = Poll.objects.create(
                question=question, description=description,
                allow_multiple=allow_multiple, is_active=True,
            )
            for i, choice_text in enumerate(choices):
                PollChoice.objects.create(poll=poll, text=choice_text, order=i)
            messages.success(request, f'Sondage créé.')
            return redirect('dashboard:polls_list')

    return render(request, 'dashboard/polls/form.html', {
        'page_title': 'Nouveau sondage',
        'active_menu': 'polls',
    })


@login_required
def poll_edit(request, pk):
    poll = get_object_or_404(Poll, pk=pk)
    if request.method == 'POST':
        poll.question = request.POST.get('question', '').strip()
        poll.description = request.POST.get('description', '').strip()
        poll.allow_multiple = request.POST.get('allow_multiple') == 'on'
        poll.is_active = request.POST.get('is_active') == 'on'
        poll.save()

        # Update choices
        poll.choices.all().delete()
        choices = [c.strip() for c in request.POST.getlist('choices') if c.strip()]
        for i, choice_text in enumerate(choices):
            PollChoice.objects.create(poll=poll, text=choice_text, order=i)

        messages.success(request, 'Sondage mis à jour.')
        return redirect('dashboard:polls_list')

    return render(request, 'dashboard/polls/form.html', {
        'poll': poll,
        'page_title': f'Modifier: {poll.question[:40]}',
        'active_menu': 'polls',
    })


@login_required
@require_POST
def poll_delete(request, pk):
    poll = get_object_or_404(Poll, pk=pk)
    poll.delete()
    if is_htmx(request):
        return HttpResponse('')
    messages.success(request, 'Sondage supprimé.')
    return redirect('dashboard:polls_list')


@login_required
@require_POST
def poll_toggle(request, pk):
    poll = get_object_or_404(Poll, pk=pk)
    poll.is_active = not poll.is_active
    poll.save()
    if is_htmx(request):
        return render(request, 'dashboard/polls/_row.html', {'poll': poll})
    return redirect('dashboard:polls_list')


# ─── Utilisateurs ──────────────────────────────────────────────────────────────

@login_required
def users_list(request):
    if not request.user.is_superuser:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard:index')

    qs = User.objects.annotate(articles_count=Count('articles')).order_by('-date_joined')
    search = request.GET.get('q', '')
    if search:
        qs = qs.filter(Q(username__icontains=search) | Q(email__icontains=search) |
                       Q(first_name__icontains=search) | Q(last_name__icontains=search))

    paginator = Paginator(qs, 15)
    page = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_obj': page,
        'search': search,
        'page_title': 'Utilisateurs',
        'active_menu': 'users',
    }
    if is_htmx(request):
        return render(request, 'dashboard/users/_table.html', context)
    return render(request, 'dashboard/users/list.html', context)


@login_required
def user_add(request):
    if not request.user.is_superuser:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard:index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'

        if not username or not password:
            messages.error(request, "Nom d'utilisateur et mot de passe sont obligatoires.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà.")
        else:
            user = User.objects.create_user(
                username=username, email=email,
                first_name=first_name, last_name=last_name,
                password=password, is_staff=is_staff, is_superuser=is_superuser,
            )
            messages.success(request, f'Utilisateur "{username}" créé.')
            return redirect('dashboard:users_list')

    return render(request, 'dashboard/users/form.html', {
        'page_title': 'Nouvel utilisateur',
        'active_menu': 'users',
    })


@login_required
def user_edit(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard:index')

    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.email = request.POST.get('email', '').strip()
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_superuser = request.POST.get('is_superuser') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'
        new_password = request.POST.get('password', '').strip()
        if new_password:
            user.set_password(new_password)
        user.save()
        messages.success(request, 'Utilisateur mis à jour.')
        return redirect('dashboard:users_list')

    return render(request, 'dashboard/users/form.html', {
        'user_obj': user,
        'page_title': f'Modifier: {user.username}',
        'active_menu': 'users',
    })


@login_required
@require_POST
def user_delete(request, pk):
    if not request.user.is_superuser:
        return HttpResponse('Accès refusé', status=403)
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('dashboard:users_list')
    user.delete()
    if is_htmx(request):
        return HttpResponse('')
    messages.success(request, 'Utilisateur supprimé.')
    return redirect('dashboard:users_list')


# ─── Paramètres ────────────────────────────────────────────────────────────────

@login_required
def settings_view(request):
    if not request.user.is_superuser:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard:index')

    site_settings = SiteSettings.get_settings()
    if request.method == 'POST':
        site_settings.site_name = request.POST.get('site_name', '').strip()
        site_settings.site_tagline = request.POST.get('site_tagline', '').strip()
        site_settings.site_description = request.POST.get('site_description', '').strip()
        site_settings.contact_email = request.POST.get('contact_email', '').strip()
        site_settings.contact_phone = request.POST.get('contact_phone', '').strip()
        site_settings.contact_address = request.POST.get('contact_address', '').strip()
        site_settings.facebook_url = request.POST.get('facebook_url', '').strip()
        site_settings.twitter_url = request.POST.get('twitter_url', '').strip()
        site_settings.instagram_url = request.POST.get('instagram_url', '').strip()
        site_settings.youtube_url = request.POST.get('youtube_url', '').strip()
        site_settings.tiktok_url = request.POST.get('tiktok_url', '').strip()
        site_settings.whatsapp_number = request.POST.get('whatsapp_number', '').strip()
        site_settings.articles_per_page = int(request.POST.get('articles_per_page', 10))
        site_settings.enable_comments = request.POST.get('enable_comments') == 'on'
        site_settings.comment_moderation = request.POST.get('comment_moderation') == 'on'
        site_settings.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
        site_settings.google_analytics_id = request.POST.get('google_analytics_id', '').strip()
        if 'logo' in request.FILES:
            site_settings.logo = request.FILES['logo']
        if 'favicon' in request.FILES:
            site_settings.favicon = request.FILES['favicon']
        site_settings.save()
        messages.success(request, 'Paramètres enregistrés.')
        if is_htmx(request):
            response = HttpResponse()
            response['HX-Trigger'] = 'showToast'
            return response
        return redirect('dashboard:settings')

    return render(request, 'dashboard/settings/index.html', {
        'settings': site_settings,
        'page_title': 'Paramètres',
        'active_menu': 'settings',
    })


# ─── Profil ────────────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    if request.method == 'POST':
        if request.POST.get('change_password'):
            # Formulaire changement mot de passe
            current = request.POST.get('current_password', '')
            new_pwd = request.POST.get('new_password', '').strip()
            confirm = request.POST.get('confirm_password', '').strip()
            if not request.user.check_password(current):
                messages.error(request, 'Mot de passe actuel incorrect.')
            elif not new_pwd:
                messages.error(request, 'Le nouveau mot de passe ne peut pas être vide.')
            elif new_pwd != confirm:
                messages.error(request, 'Les deux mots de passe ne correspondent pas.')
            else:
                request.user.set_password(new_pwd)
                request.user.save()
                # Reconnexion nécessaire après changement de mot de passe
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Mot de passe mis à jour avec succès.')
        else:
            # Formulaire informations personnelles
            request.user.first_name = request.POST.get('first_name', '').strip()
            request.user.last_name = request.POST.get('last_name', '').strip()
            request.user.email = request.POST.get('email', '').strip()
            request.user.save()
            messages.success(request, 'Profil mis à jour.')
        return redirect('dashboard:profile')

    return render(request, 'dashboard/profile.html', {
        'page_title': 'Mon profil',
        'active_menu': 'profile',
    })
