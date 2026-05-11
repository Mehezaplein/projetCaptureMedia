from .models import Comment, SiteSettings, Category, BreakingNews, Advertisement, Article, Poll
from django.db.models import F
from django.utils import timezone


def get_active_ads():
    today = timezone.now().date()
    qs = Advertisement.objects.filter(
        is_active=True,
        start_date__lte=today,
        end_date__gte=today
    )
    ads_by_position = {
        'ads_header': list(qs.filter(position='header').order_by('?')[:3]),
        'ads_sidebar_top': list(qs.filter(position='sidebar_top').order_by('?')[:2]),
        'ads_sidebar_bottom': list(qs.filter(position='sidebar_bottom').order_by('?')[:2]),
        'ads_article_top': list(qs.filter(position='article_top').order_by('?')[:1]),
        'ads_article_bottom': list(qs.filter(position='article_bottom').order_by('?')[:1]),
        'ads_footer': list(qs.filter(position='footer').order_by('?')[:2]),
        'ads_popup': list(qs.filter(position='popup').order_by('?')[:1]),
    }
    shown_ids = []
    for ads_list in ads_by_position.values():
        shown_ids.extend(ad.id for ad in ads_list)
    if shown_ids:
        Advertisement.objects.filter(id__in=shown_ids).update(impressions=F('impressions') + 1)
    return ads_by_position


def dashboard_context(request):
    ctx = {}
    if request.user.is_authenticated and request.user.is_staff:
        ctx['pending_comments_count'] = Comment.objects.filter(status='pending').count()

    try:
        ctx['site_settings'] = SiteSettings.get_settings()
        ctx['global_categories'] = Category.objects.filter(is_active=True).order_by('order')
        ctx['global_breaking_news'] = BreakingNews.objects.filter(is_active=True).order_by('order', '-created_at')[:5]
        ctx['global_suggestions'] = Article.objects.filter(status='published').order_by('-views_count')[:5]
        ctx['global_active_poll'] = Poll.objects.filter(is_active=True).order_by('-created_at').first()
        ctx['global_active_polls'] = list(Poll.objects.filter(is_active=True).prefetch_related('choices').order_by('-created_at')[:3])

        ctx.update(get_active_ads())

    except Exception:
        pass
    return ctx
