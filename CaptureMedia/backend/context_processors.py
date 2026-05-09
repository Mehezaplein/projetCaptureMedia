from .models import Comment, SiteSettings, Category, BreakingNews, Advertisement, Article, Poll
from django.utils import timezone

def dashboard_context(request):
    """Injecte les données globales dans tous les templates."""
    ctx = {}
    if request.user.is_authenticated and request.user.is_staff:
        ctx['pending_comments_count'] = Comment.objects.filter(status='pending').count()
    
    try:
        ctx['site_settings'] = SiteSettings.get_settings()
        ctx['global_categories'] = Category.objects.filter(is_active=True).order_by('order')
        ctx['global_breaking_news'] = BreakingNews.objects.filter(is_active=True).order_by('order', '-created_at')[:5]
        
        # Publicités globales
        today = timezone.now().date()
        ctx['global_top_ads'] = Advertisement.objects.filter(
            position='header', is_active=True,
            start_date__lte=today, end_date__gte=today
        ).order_by('?')[:3]
        
        # Suggestions globales (les plus lus)
        ctx['global_suggestions'] = Article.objects.filter(status='published').order_by('-views_count')[:5]
        
        # Le sondage actif le plus récent uniquement
        ctx['global_active_poll'] = Poll.objects.filter(is_active=True).order_by('-created_at').first()
        
    except Exception:
        pass
    return ctx
