import os
from pathlib import Path
from dotenv import load_dotenv

# .env फाइल लोड करें
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = "django-insecure-your-secret-key-here"  # Hardcode for local dev


SOCIAL_AUTH_GITHUB_KEY = os.getenv('GITHUB_KEY')
SOCIAL_AUTH_GITHUB_SECRET = os.getenv('GITHUB_SECRET')
GITHUB_KEY='Ov23liHnQwxfmCi3H6Gc'
GITHUB_SECRET='6ce084514f382b65bdc090601bba094b6bd3de6d'
SOCIAL_AUTH_GITHUB_SCOPE = ['user:email']

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
# Django Secret Key
SECRET_KEY = os.getenv('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # Always True for local development

ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # Only localhost

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'mainapp',  # Your app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'social_core.backends.github.GithubOAuth2',
    'django.contrib.auth.backends.ModelBackend',  # Note: No parentheses
]

ROOT_URLCONF = 'portfolio.urls'

# SOCIAL_AUTH_GITHUB_KEY = 'Ov23liHnQwxfmCi3H6Gc'
# SOCIAL_AUTH_GITHUB_SECRET = '6ce084514f382b65bdc090601bba094b6bd3de6d'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'portfolio.wsgi.application'

# Database - Only SQLite (Simplified)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (Simplified)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'mainapp/static']
STATIC_ROOT = BASE_DIR / 'static'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Media files
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'



MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Email (Console output for testing)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Login URL
LOGIN_URL = '/accounts/login/'