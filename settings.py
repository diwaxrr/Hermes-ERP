INSTALLED_APPS = [
    # ... otras apps de Django
    'central',  # <-- Tu aplicación del núcleo
    'rest_framework', # <-- DRF para las APIs
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hermes_db',  # <--- Nombre de tu base de datos en PG
        'USER': 'hermes', # <--- Tu usuario de PG
        'PASSWORD': 'YHT54GCdhy7', # <--- Tu contraseña de PG
        'HOST': 'localhost',
        'PORT': '5433',
    }
}