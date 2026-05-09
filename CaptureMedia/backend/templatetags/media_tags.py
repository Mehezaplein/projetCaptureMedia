from django import template
from django.utils.safestring import mark_safe
from backend.utils import extract_youtube_id

register = template.Library()


PLATFORM_ICONS = {
    'youtube': 'bi-youtube',
    'tiktok': 'bi-tiktok',
    'instagram': 'bi-instagram',
    'twitter': 'bi-twitter-x',
    'facebook': 'bi-facebook',
    'whatsapp': 'bi-whatsapp',
    'other': 'bi-link-45deg',
}

PLATFORM_COLORS = {
    'youtube': '#FF0000',
    'tiktok': '#010101',
    'instagram': '#E1306C',
    'twitter': '#000000',
    'facebook': '#1877F2',
    'whatsapp': '#25D366',
    'other': '#6c757d',
}

PLATFORM_LABELS = {
    'youtube': 'YouTube',
    'tiktok': 'TikTok',
    'instagram': 'Instagram',
    'twitter': 'Twitter / X',
    'facebook': 'Facebook',
    'whatsapp': 'WhatsApp',
    'other': 'Lien externe',
}


@register.simple_tag
def embed_media(article):
    if not article.media_url:
        return ''

    platform = article.media_platform
    url = article.media_url

    if platform == 'youtube':
        video_id = extract_youtube_id(url)
        if video_id:
            return mark_safe(f'''
<div class="embed-media embed-youtube" style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:12px;margin:20px 0;">
  <iframe src="https://www.youtube.com/embed/{video_id}"
          style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;"
          allowfullscreen loading="lazy"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture">
  </iframe>
</div>''')

    if platform == 'tiktok':
        return mark_safe(f'''
<div class="embed-media embed-tiktok" style="display:flex;justify-content:center;margin:20px 0;">
  <blockquote class="tiktok-embed" cite="{url}" style="max-width:605px;min-width:325px;">
    <section></section>
  </blockquote>
  <script async src="https://www.tiktok.com/embed.js"></script>
</div>''')

    if platform == 'instagram':
        return mark_safe(f'''
<div class="embed-media embed-instagram" style="display:flex;justify-content:center;margin:20px 0;">
  <blockquote class="instagram-media"
              data-instgrm-permalink="{url}"
              data-instgrm-version="14"
              style="max-width:540px;width:100%;">
  </blockquote>
  <script async src="//www.instagram.com/embed.js"></script>
</div>''')

    if platform == 'twitter':
        return mark_safe(f'''
<div class="embed-media embed-twitter" style="display:flex;justify-content:center;margin:20px 0;">
  <blockquote class="twitter-tweet">
    <a href="{url}"></a>
  </blockquote>
  <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
</div>''')

    # Facebook, WhatsApp, other → lien stylisé
    icon = PLATFORM_ICONS.get(platform, 'bi-link-45deg')
    color = PLATFORM_COLORS.get(platform, '#6c757d')
    label = PLATFORM_LABELS.get(platform, 'Lien externe')

    return mark_safe(f'''
<div class="embed-media embed-link" style="margin:20px 0;">
  <a href="{url}" target="_blank" rel="noopener noreferrer"
     style="display:inline-flex;align-items:center;gap:10px;padding:14px 20px;
            background:{color};color:#fff;border-radius:10px;text-decoration:none;
            font-weight:600;font-size:15px;">
    <i class="bi {icon}" style="font-size:20px;"></i>
    Voir sur {label}
  </a>
</div>''')
