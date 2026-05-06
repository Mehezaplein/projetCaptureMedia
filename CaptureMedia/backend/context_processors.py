from .models import Comment, SiteSettings


def dashboard_context(request):
    """Injecte le nombre de commentaires en attente et les paramètres du site dans tous les templates."""
    ctx = {}
    if request.user.is_authenticated and request.user.is_staff:
        ctx['pending_comments_count'] = Comment.objects.filter(status='pending').count()
    try:
        ctx['site_settings'] = SiteSettings.get_settings()
    except Exception:
        pass
    return ctx
