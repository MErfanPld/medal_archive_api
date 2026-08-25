#!/usr/bin/env python3
"""Enable all 7 collection modules in settings.py and urls.py. Run from project root AFTER extracting collection_modules_COMPLETE.tgz"""
from pathlib import Path
import re

root = Path.cwd()
settings = root / "config" / "settings.py"
urls = root / "config" / "urls.py"

if not (root / "manage.py").exists():
    raise SystemExit("Run from project root")

# Verify modules exist
missing = [a for a in ["seals", "tasbih", "rings", "knives", "antiques", "stamps"] if not (root / a / "models.py").exists()]
if missing:
    raise SystemExit(
        "Missing models for: " + ", ".join(missing) + "\n"
        "First extract collection_modules_COMPLETE.tgz from Google Drive next to manage.py"
    )

s = settings.read_text(encoding="utf-8")
block = """    'users',
    'categories',
    'medals',
    'reports',
    'coins',
    'banknotes',
    'seals',
    'tasbih',
    'rings',
    'knives',
    'antiques',
    'stamps',
]"""
s2 = re.sub(r"    'users',.*?\]", block, s, count=1, flags=re.S)
if s2 == s:
    print("WARNING: could not patch INSTALLED_APPS automatically — edit config/settings.py manually")
else:
    settings.write_text(s2, encoding="utf-8")
    print("updated", settings)

u = urls.read_text(encoding="utf-8")
url_block = """urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/categories/', include('categories.urls')),
    path('api/medals/', include('medals.urls')),
    path('api/coins/', include('coins.urls')),
    path('api/banknotes/', include('banknotes.urls')),
    path('api/seals/', include('seals.urls')),
    path('api/tasbih/', include('tasbih.urls')),
    path('api/rings/', include('rings.urls')),
    path('api/knives/', include('knives.urls')),
    path('api/antiques/', include('antiques.urls')),
    path('api/stamps/', include('stamps.urls')),
    path('api/reports/', include('reports.urls')),
]"""
u2 = re.sub(r"urlpatterns = \[.*?\]", url_block, u, count=1, flags=re.S)
if u2 == u:
    print("WARNING: could not patch urlpatterns automatically — edit config/urls.py manually")
else:
    urls.write_text(u2, encoding="utf-8")
    print("updated", urls)

print("OK — next:")
print("  python manage.py makemigrations seals tasbih rings knives antiques stamps")
print("  python manage.py migrate")
print("  python manage.py check")
