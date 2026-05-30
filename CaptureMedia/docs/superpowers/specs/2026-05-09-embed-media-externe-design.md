# Spec : Intégration de médias externes dans les articles

**Date :** 2026-05-09  
**Statut :** Implémenté

## Contexte

Capture Media est un journal qui publie aussi sur YouTube, TikTok, Instagram, WhatsApp, etc. Plutôt que de re-uploader des vidéos lourdes sur la plateforme, les rédacteurs collent un lien externe lors de la création d'un article. Le système détecte la plateforme et génère automatiquement l'embed approprié.

## Architecture

### Modèle — `backend/models.py`

Deux champs ajoutés à `Article` :
- `media_url` — `URLField(blank=True, null=True)` : l'URL collée
- `media_platform` — `CharField(choices, blank=True)` : détecté au `save()`

Plateformes : `youtube`, `tiktok`, `instagram`, `twitter`, `facebook`, `whatsapp`, `other`.

### Utilitaires — `backend/utils.py`

- `detect_media_platform(url)` — regex par plateforme, retourne la clé
- `extract_youtube_id(url)` — extrait l'ID vidéo pour construire l'iframe

### Template tag — `backend/templatetags/media_tags.py`

`{% embed_media article %}` génère le HTML selon `article.media_platform` :
- **YouTube** → `<iframe>` responsive 16:9
- **TikTok** → `<blockquote class="tiktok-embed">` + script officiel
- **Instagram** → `<blockquote class="instagram-media">` + script officiel
- **Twitter/X** → `<blockquote class="twitter-tweet">` + script officiel
- **Facebook / WhatsApp / other** → lien stylisé avec icône Bootstrap Icons

### Vues — `backend/dashboard_views.py`

`article_add` et `article_edit` récupèrent `media_url` depuis `request.POST` et l'assignent avant `save()`.

### Formulaire — `backend/templates/dashboard/articles/form.html`

Section "Média externe" dans la sidebar avec :
- Input URL avec placeholder explicite
- Aperçu dynamique JS (icône + couleur de la plateforme détectée)
- Bouton Effacer

## Ce qui n'est PAS dans le scope

- Plusieurs médias par article
- Validation que l'URL est accessible
- Cache des embeds
- La bibliothèque media existante (`MediaFile`) — inchangée
