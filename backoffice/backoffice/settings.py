"""
Django settings for backoffice project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-dlfjc5^wg)x@k$xq524hp9lf0c=gsgg@^hs_2h!=vta0wxy9oc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'rest_framework',
    'drf_yasg',
    'admin_interface',
    'colorfield',
    'jazzmin', 
    'm3d_app',
    'mapa_malvinas',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'backoffice.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'backoffice.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# En backoffice/backoffice/settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Esta es la línea importante

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'm3d_app/static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'es'

# Define la zona horaria para Argentina
TIME_ZONE = 'America/Argentina/Buenos_Aires'

USE_I18N = True  
USE_L10N = True  
USE_TZ = True  

# En backoffice/backoffice/settings.py
JAZZMIN_SETTINGS = {
    # Título en la barra del navegador
    "site_title": "Malvinas 3D Admin",
    # Título en la barra lateral
    "site_header": "Malvinas 3D",
    # Título en el index
    "site_brand": "Malvinas 3D",
    # Logo del sitio
    "site_logo": "img/m.png",  # Ruta relativa a STATIC_URL
    "site_icon": "img/m.png", 
    "welcome_sign": "Bienvenido al panel de administración de Malvinas 3D",
    # Copyright
    "copyright": "Malvinas 3D © 2025",
    # Enlaces en el menú superior
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        # Cambiado para redirigir a malvinas3d.com.ar
        {"name": "Vista del sitio", "url": "https://malvinas3d.com.ar/", "new_window": True},
    ],
    # Íconos personalizados - asegurar que todos los íconos de la barra lateral sean blancos
    "icons": {
        "m3d_app.suscriptor": "fas fa-users",
        "m3d_app.bloque": "fas fa-cubes",
        "m3d_app.impresora": "fas fa-print",
        "m3d_app.nodorecepcion": "fas fa-map-marker-alt",
        "m3d_app.particularconimpresora": "fas fa-user-check",
        "m3d_app.particularsinimpresora": "fas fa-user",
        "m3d_app.institucionconimpresora": "fas fa-building",
        "m3d_app.institucionsinimpresora": "fas fa-university",
        "auth.user": "fas fa-user-shield",
        "auth.group": "fas fa-users-cog",
    },
    # Tema oscuro para que los íconos se vean en blanco
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    # UI Tweaks
    "ui_tweaks": {
        "navbar_small_text": False,
        "footer_small_text": False,
        "body_small_text": False,
        "brand_small_text": False,
        "brand_colour": "navbar-dark",
        "accent": "accent-primary",
        "navbar": "navbar-dark",
        "no_navbar_border": True,
        "sidebar": "sidebar-dark-primary",
        "sidebar_nav_small_text": False,
        "sidebar_disable_expand": False,
        "sidebar_nav_child_indent": True,
        "sidebar_nav_compact_style": True,
        "sidebar_nav_legacy_style": False,
        "sidebar_nav_flat_style": False,
        # Asegurarse de que los íconos de la barra lateral son blancos
        "button_classes": {
            "primary": "btn-primary",
            "secondary": "btn-secondary",
            "info": "btn-info",
            "warning": "btn-warning",
            "danger": "btn-danger",
            "success": "btn-lighter-success",  # Usaremos una clase personalizada
        }
    },
    # Personalización de modelos en dashboard
    "order_with_respect_to": [
        "m3d_app.suscriptor", 
        "m3d_app.bloque", 
        "m3d_app.nodorecepcion",
        "m3d_app.impresora",
        "m3d_app.particularconimpresora",
        "m3d_app.particularsinimpresora",
        "m3d_app.institucionconimpresora",
        "m3d_app.institucionsinimpresora",
    ],
    # CSS personalizado
    "custom_css": "jazzmin/custom.css",  # Crearemos este archivo
}
