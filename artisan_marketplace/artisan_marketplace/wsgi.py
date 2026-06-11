import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the Django project directory to Python path for serverless imports
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artisan_marketplace.settings")

application = get_wsgi_application()
app = application
