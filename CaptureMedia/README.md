# Capture Media — Plateforme de gestion éditoriale

Plateforme web Django pour **Capture Media**, un média engagé pour le peuple togolais.
Dashboard d'administration complet avec thème Jaune/Noir, mode clair/sombre, et interactions HTMX.

---

## Prérequis

- Python 3.10+
- pip

---

## Installation rapide

```bash
# 1. Cloner / accéder au dossier du projet
cd CaptureMedia

# 2. (Recommandé) Créer un environnement virtuel
python -m venv venv
# Windows :
venv\Scripts\activate
# Linux/macOS :
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Appliquer les migrations
python manage.py migrate

# 5. Créer un super-administrateur
python manage.py createsuperuser

# 6. Lancer le serveur de développement
python manage.py runserver
```

L'application sera disponible sur : **http://127.0.0.1:8000/**
Le dashboard admin sur : **http://127.0.0.1:8000/dashboard/**

---

## Dépendances principales

| Package | Version | Rôle |
|---|---|---|
| Django | >=5.0 | Framework web |
| django-browser-reload | 1.12+ | Rechargement automatique en développement |
| Pillow | >=10.0 | Traitement des images uploadées |
| python-slugify | >=8.0 | Génération de slugs pour les URLs |

> **HTMX** et **Quill.js** sont chargés via CDN (pas de dépendance pip).

---

## Structure du projet

```
CaptureMedia/
├── CaptureMedia/          # Configuration Django
│   ├── settings.py
│   └── urls.py
├── backend/               # Application principale
│   ├── models.py          # Tous les modèles (Article, Catégorie, Commentaire…)
│   ├── views.py           # Vues du site public
│   ├── dashboard_views.py # Vues du dashboard admin
│   ├── dashboard_urls.py  # URLs dashboard (préfixe /dashboard/)
│   ├── context_processors.py
│   └── templates/
│       ├── dashboard/     # Templates du dashboard
│       └── *.html         # Templates du site public
├── media/                 # Fichiers uploadés (générés)
├── requirements.txt
└── manage.py
```

---

## Fonctionnalités du Dashboard

### Contenu
- **Articles** — Rédaction avec éditeur riche (Quill), gestion du statut, image à la une, tags
- **Catégories** — Hiérarchie parent/enfant, réorganisation
- **Tags** — Gestion rapide avec ajout inline

### Médias & Interactions
- **Bibliothèque médias** — Upload drag & drop, prévisualisation, gestion par type
- **Commentaires** — Modération (approuver / rejeter / spam), filtres HTMX
- **Sondages** — Création avec choix dynamiques, résultats en temps réel
- **Newsletter** — Gestion des abonnés, export

### Info & Publicité
- **Breaking News** — Ticker en temps réel, activation/désactivation instantanée
- **Publicités** — Gestion des bannières par position, suivi clics/impressions

### Administration
- **Utilisateurs** — Création, rôles (super admin, rédacteur), activation
- **Paramètres du site** — Nom, logo, réseaux sociaux, modération, Analytics

---

## Accès au dashboard

1. Se connecter sur `/dashboard/login/`
2. Utiliser les identifiants du super-administrateur créé avec `createsuperuser`
3. Seuls les utilisateurs avec `is_staff = True` ont accès

---

## Variables d'environnement (production)

En production, remplacer dans `settings.py` :

```python
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = ['votre-domaine.com']
```

---

## Design

- **Couleurs** : Jaune `#F5C518` · Noir `#111111` · Blanc `#FFFFFF`
- **Mode clair/sombre** : Basculement via bouton dans la topbar, persisté en `localStorage`
- **Responsive** : Sidebar rétractable sur mobile
- **Interactivité** : HTMX pour les recherches, filtrages, toggles et suppressions sans rechargement

---

## Licence

Projet propriétaire — Capture Media © 2025
