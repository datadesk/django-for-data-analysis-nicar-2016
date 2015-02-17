import os
from django.core.exceptions import SuspiciousOperation

SECRET_KEY = "oxsha^)nxr80^^ti*-u-_=8ah19@8x-qqe)qhd5wd8)f402b+2"
EMAIL_HOST_USER = '' # Gmail username
EMAIL_HOST_PASSWORD = '' # Gmail password
ALLOWED_HOSTS = []
USE_X_FORWARDED_HOST = True
AWS_ACCESS_KEY_ID = '' # The shorter one
AWS_SECRET_ACCESS_KEY = '' # The longer one
AWS_BUCKET_NAME = '' # For your static files
AWS_BACKUP_BUCKET_NAME = '' # For database backups
AWS_BACKUP_BUCKET_DIRECTORY = '' # A prefix for the database backup key

try:
    from settings_dev import *
except ImportError:
    from settings_prod import *

# Settings paths that are handy to use other places
SETTINGS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.join(
    os.path.abspath(
        os.path.join(SETTINGS_DIR, os.path.pardir),
    ),
)

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Data Desk', 'datadesk@latimes.com'),
)
MANAGERS = ADMINS

# Gmail config
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Localization
TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Media and static files
MEDIA_ROOT = os.path.join(ROOT_DIR, 'media')
STATIC_ROOT = os.path.join(ROOT_DIR, 'static')
STATICFILES_DIRS = (
    os.path.join(ROOT_DIR, 'templates', 'static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Templates
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_DIRS = (
    os.path.join(ROOT_DIR, 'templates'),
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'django.core.context_processors.request',
    'toolbox.context_processors.env.environment',
    'toolbox.context_processors.sites.current_site',
)

# Web request stuff
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
ROOT_URLCONF = 'project.urls'
WSGI_APPLICATION = 'project.wsgi.application'

# Installed apps
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'south',
    'toolbox',
    'greeking',
    'building_and_safety',
)

# Logging
MUNIN_ROOT = '/var/cache/munin/www/'

def skip_suspicious_operations(record):
  if record.exc_info:
    exc_value = record.exc_info[1]
    if isinstance(exc_value, SuspiciousOperation):
      return False
  return True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'skip_suspicious_operations': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_suspicious_operations,
         },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', 'skip_suspicious_operations'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(ROOT_DIR, 'django.log'),
            'maxBytes': 1024*1024*5, # 5MB,
            'backupCount': 0,
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s|%(asctime)s|%(module)s|%(process)d|%(thread)d|%(message)s',
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s|%(message)s'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'finder': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'boundaries': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'building_and_safety': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

# Django debug toolbar configuration
if DEBUG_TOOLBAR:
    # Debugging toolbar middleware
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    # JavaScript panels for the deveopment debugging toolbar
    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    )
    # Debug toolbar app
    INSTALLED_APPS += ('debug_toolbar',)
    CONFIG_DEFAULTS = {
        'INTERCEPT_REDIRECTS': False,
    }
