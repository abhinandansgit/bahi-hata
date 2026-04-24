from .translations import TRANSLATIONS

def translations(request):
    """
    Context processor to provide translations to all templates.
    """
    # Get language from session, default to English
    lang = request.session.get('language', 'en')
    
    # Ensure language exists in our dictionary
    if lang not in TRANSLATIONS:
        lang = 'en'
        
    return {
        't': TRANSLATIONS[lang],
        'current_lang': lang,
        'is_odia': lang == 'or'
    }
