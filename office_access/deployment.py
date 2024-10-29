import os
from .settings import *  # Import all base settings

# Use environment variables for sensitive values
SECRET_KEY = os.environ['SECRET']
DEBUG = True  # Turn off debug mode in production

# Configure allowed hosts and CSRF trusted origins
ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']]
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['WEBSITE_HOSTNAME']]

# Add Whitenoise for serving static files in production
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Whitenoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configure Whitenoise static file settings
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# PostgreSQL configuration using the connection string
connection_string = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
parameters = dict(pair.split('=') for pair in connection_string.split(';') if pair)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': parameters['dbname'],
        'HOST': parameters['host'],
        'USER': parameters['user'],
        'PASSWORD': parameters['password'],
    }
}
