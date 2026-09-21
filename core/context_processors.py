from django.conf import settings
from .translations import TRANSLATIONS

def translations(request):
    """
    Context processor to provide translations and global settings to all templates.
    """
    # Get language from session, default to English
    lang = request.session.get('language', 'en')
    
    # Ensure language exists in our dictionary
    if lang not in TRANSLATIONS:
        lang = 'en'
        
    return {
        't': TRANSLATIONS[lang],
        'current_lang': lang,
        'is_odia': lang == 'or',
        'GOOGLE_CLIENT_ID': getattr(settings, 'GOOGLE_CLIENT_ID', ''),
        'SUPABASE_URL': getattr(settings, 'SUPABASE_URL', ''),
        'SUPABASE_ANON_KEY': getattr(settings, 'SUPABASE_ANON_KEY', ''),
    }

