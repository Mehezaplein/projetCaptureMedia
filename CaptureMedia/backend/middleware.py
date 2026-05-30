from django.shortcuts import render
from .models import SiteSettings


class MaintenanceModeMiddleware:
    """Affiche une page de maintenance au public quand le mode maintenance est activé.

    Le staff connecté, le dashboard, l'admin et les fichiers statiques/médias
    restent toujours accessibles pour pouvoir continuer à travailler.
    """

    EXEMPT_PREFIXES = ('/dashboard', '/admin', '/static', '/media', '/__reload__')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if not any(path.startswith(p) for p in self.EXEMPT_PREFIXES):
            # Le staff connecté contourne la maintenance
            if not (request.user.is_authenticated and request.user.is_staff):
                try:
                    settings_obj = SiteSettings.get_settings()
                except Exception:
                    settings_obj = None
                if settings_obj and settings_obj.maintenance_mode:
                    return render(request, 'maintenance.html',
                                  {'site_settings': settings_obj}, status=503)
        return self.get_response(request)
