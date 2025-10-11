"""
Create a Django superuser programmatically
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'veralign.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser created successfully!")
else:
    print("Superuser already exists.")