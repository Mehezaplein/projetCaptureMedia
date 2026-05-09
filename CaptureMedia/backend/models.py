from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from .utils import detect_media_platform


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Image")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='children', verbose_name="Catégorie parente")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def articles_count(self):
        return self.articles.filter(status='published').count()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Nom")
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('archived', 'Archivé'),
    ]

    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter / X'),
        ('facebook', 'Facebook'),
        ('whatsapp', 'WhatsApp'),
        ('other', 'Autre'),
    ]

    title = models.CharField(max_length=300, verbose_name="Titre")
    slug = models.SlugField(unique=True, blank=True, max_length=350)
    excerpt = models.TextField(blank=True, verbose_name="Résumé", max_length=500)
    content = models.TextField(verbose_name="Contenu")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True,
                                  related_name='articles', verbose_name="Catégorie")
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles', verbose_name="Tags")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                related_name='articles', verbose_name="Auteur")
    featured_image = models.ImageField(upload_to='articles/', blank=True, null=True,
                                        verbose_name="Image à la une")
    media_url = models.URLField(blank=True, null=True, verbose_name="URL du média externe")
    media_platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, blank=True,
                                       verbose_name="Plateforme")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft',
                               verbose_name="Statut")
    is_featured = models.BooleanField(default=False, verbose_name="À la une")
    is_breaking = models.BooleanField(default=False, verbose_name="Breaking news")
    allow_comments = models.BooleanField(default=True, verbose_name="Autoriser les commentaires")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Vues")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Publié le")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        self.media_platform = detect_media_platform(self.media_url or '')
        super().save(*args, **kwargs)

    @property
    def comments_count(self):
        return self.comments.filter(status='approved').count()

    @property
    def pending_comments_count(self):
        return self.comments.filter(status='pending').count()


class Comment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('spam', 'Spam'),
    ]

    article = models.ForeignKey(Article, on_delete=models.CASCADE,
                                 related_name='comments', verbose_name="Article")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                related_name='replies', verbose_name="Réponse à")
    author_name = models.CharField(max_length=100, verbose_name="Nom")
    author_email = models.EmailField(verbose_name="Email")
    content = models.TextField(verbose_name="Commentaire")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending',
                               verbose_name="Statut")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Posté le")

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ['-created_at']

    def __str__(self):
        return f"Commentaire de {self.author_name} sur {self.article.title}"


class MediaFile(models.Model):
    TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Vidéo'),
        ('document', 'Document'),
        ('audio', 'Audio'),
    ]

    file = models.FileField(upload_to='media-library/%Y/%m/', verbose_name="Fichier")
    file_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type")
    title = models.CharField(max_length=200, blank=True, verbose_name="Titre")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Texte alternatif")
    file_size = models.PositiveIntegerField(default=0, verbose_name="Taille (octets)")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                     verbose_name="Uploadé par")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploadé le")

    class Meta:
        verbose_name = "Fichier média"
        verbose_name_plural = "Fichiers médias"
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title or self.file.name

    @property
    def file_size_display(self):
        size = self.file_size
        if size < 1024:
            return f"{size} o"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} Ko"
        else:
            return f"{size / (1024 * 1024):.1f} Mo"


class Newsletter(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=100, blank=True, verbose_name="Prénom")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name="Inscrit le")
    unsubscribed_at = models.DateTimeField(null=True, blank=True, verbose_name="Désinscrit le")

    class Meta:
        verbose_name = "Abonné newsletter"
        verbose_name_plural = "Abonnés newsletter"
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


class Advertisement(models.Model):
    POSITION_CHOICES = [
        ('header', 'En-tête'),
        ('sidebar_top', 'Barre latérale haut'),
        ('sidebar_bottom', 'Barre latérale bas'),
        ('article_top', "Début d'article"),
        ('article_bottom', "Fin d'article"),
        ('popup', 'Pop-up'),
        ('footer', 'Pied de page'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre")
    image = models.ImageField(upload_to='ads/', verbose_name="Image")
    url = models.URLField(verbose_name="URL de destination")
    position = models.CharField(max_length=30, choices=POSITION_CHOICES, verbose_name="Position")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    clicks = models.PositiveIntegerField(default=0, verbose_name="Clics")
    impressions = models.PositiveIntegerField(default=0, verbose_name="Impressions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Publicité"
        verbose_name_plural = "Publicités"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def ctr(self):
        if self.impressions > 0:
            return round((self.clicks / self.impressions) * 100, 2)
        return 0


class BreakingNews(models.Model):
    text = models.CharField(max_length=500, verbose_name="Texte")
    url = models.URLField(blank=True, verbose_name="Lien (optionnel)")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Expire le")

    class Meta:
        verbose_name = "Breaking News"
        verbose_name_plural = "Breaking News"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.text[:80]


class Poll(models.Model):
    question = models.CharField(max_length=300, verbose_name="Question")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    allow_multiple = models.BooleanField(default=False, verbose_name="Choix multiples")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Expire le")

    class Meta:
        verbose_name = "Sondage"
        verbose_name_plural = "Sondages"
        ordering = ['-created_at']

    def __str__(self):
        return self.question

    @property
    def total_votes(self):
        return sum(choice.votes for choice in self.choices.all())


class PollChoice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE,
                              related_name='choices', verbose_name="Sondage")
    text = models.CharField(max_length=200, verbose_name="Choix")
    votes = models.PositiveIntegerField(default=0, verbose_name="Votes")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Choix de sondage"
        verbose_name_plural = "Choix de sondages"
        ordering = ['order']

    def __str__(self):
        return self.text

    @property
    def percentage(self):
        total = self.poll.total_votes
        if total > 0:
            return round((self.votes / total) * 100, 1)
        return 0


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="Capture Media",
                                  verbose_name="Nom du site")
    site_tagline = models.CharField(max_length=200, blank=True, verbose_name="Slogan")
    site_description = models.TextField(blank=True, verbose_name="Description")
    logo = models.ImageField(upload_to='settings/', blank=True, null=True, verbose_name="Logo")
    favicon = models.ImageField(upload_to='settings/', blank=True, null=True,
                                 verbose_name="Favicon")
    contact_email = models.EmailField(blank=True, verbose_name="Email de contact")
    contact_phone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    contact_address = models.TextField(blank=True, verbose_name="Adresse")
    facebook_url = models.URLField(blank=True, verbose_name="Facebook")
    twitter_url = models.URLField(blank=True, verbose_name="Twitter/X")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram")
    youtube_url = models.URLField(blank=True, verbose_name="YouTube")
    tiktok_url = models.URLField(blank=True, verbose_name="TikTok")
    whatsapp_number = models.CharField(max_length=20, blank=True, verbose_name="WhatsApp")
    articles_per_page = models.PositiveIntegerField(default=10,
                                                     verbose_name="Articles par page")
    enable_comments = models.BooleanField(default=True,
                                           verbose_name="Activer les commentaires")
    comment_moderation = models.BooleanField(default=True,
                                              verbose_name="Modérer les commentaires")
    maintenance_mode = models.BooleanField(default=False, verbose_name="Mode maintenance")
    google_analytics_id = models.CharField(max_length=50, blank=True,
                                            verbose_name="Google Analytics ID")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"

    def __str__(self):
        return self.site_name

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
