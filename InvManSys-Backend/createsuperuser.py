import os
import django
from django.contrib.auth import get_user_model

# --- DJANGO ENVIRONMENT SETUP ---
# Tells the script which settings file to use so it can access the database
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_core.settings')
# Initializes the Django application to allow model interaction outside of a standard server
django.setup()

# --- CONFIGURATION ---
# Fetches the user model currently active in the project (usually the default User model)
User = get_user_model()

# Retrieves credentials from environment variables (important for security on hosting platforms)
# It uses the provided strings as fallbacks if no environment variables are found
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'password123')

# --- LOGIC ---
# Checks if the superuser already exists to prevent integrity errors during automated deployments
if not User.objects.filter(username=username).exists():
    # Creates the user with full administrative privileges
    User.objects.create_superuser(username, email, password)
    print(f"Superuser {username} created successfully!")
else:
    # Skips creation if the user is already in the database
    print(f"Superuser {username} already exists.")