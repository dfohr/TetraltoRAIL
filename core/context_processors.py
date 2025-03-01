from django.conf import settings

def settings_context(request):
    """
    Make Django settings available in templates.
    """
    return {'settings': settings} 