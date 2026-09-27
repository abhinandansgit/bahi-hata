import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bahihata.settings")

application = get_wsgi_application()

try:
    from django.core.management import call_command
    call_command("migrate", interactive=False)
except Exception as e:
    print("[*] Vercel startup migration status:", e)

app = application
handler = application

