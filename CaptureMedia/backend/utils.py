import re


PLATFORM_PATTERNS = [
    ('youtube', [
        r'(?:youtube\.com/watch\?.*v=|youtu\.be/|youtube\.com/shorts/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
    ]),
    ('tiktok', [r'tiktok\.com/']),
    ('instagram', [r'instagram\.com/(?:p|reel|tv)/']),
    ('twitter', [r'(?:twitter|x)\.com/\w+/status/']),
    ('facebook', [r'facebook\.com/(?:watch|video|reel|\w+/videos)/']),
    ('whatsapp', [r'(?:wa\.me|whatsapp\.com/)']),
]


def detect_media_platform(url):
    if not url:
        return ''
    for platform, patterns in PLATFORM_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return platform
    return 'other'


def extract_youtube_id(url):
    match = re.search(
        r'(?:youtube\.com/watch\?.*v=|youtu\.be/|youtube\.com/shorts/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        url
    )
    return match.group(1) if match else None
