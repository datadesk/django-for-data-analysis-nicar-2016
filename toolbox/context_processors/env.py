from django.conf import settings


def environment(request):
    """
    Adds env-related context variables to the context.
    """
    return {
        'DEVELOPMENT': settings.DEVELOPMENT,
        'PRODUCTION': settings.PRODUCTION,
    }
