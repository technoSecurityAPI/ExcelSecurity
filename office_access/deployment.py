import os
from .settings import *  # Import all base settings

# Use environment variables for sensitive values
SECRET_KEY = os.environ['SECRET']
DEBUG = False  # Turn off debug mode in production

ALLOWED_HOSTS = ['https://excelapiforsecurity.azurewebsites.net'] 

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


AZURE_REDIRECT_URI = 'https://excelapiforsecurity.azurewebsites.net/api/check_access'