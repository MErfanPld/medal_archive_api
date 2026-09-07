#!/usr/bin/env python
"""
Seed DEMO data for client presentation.

Covers:
  - categories (10)
  - medals (5)
  - coins (5)
  - banknotes (5)
  - seals / tasbih / rings / knives / antiques / stamps (5 each)

Run from project root (venv active):
  python scripts/seed_demo_all.py

Or:
  PYTHONPATH=. python scripts/seed_demo_all.py
"""
from __future__ import annotations

import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.db import transaction


def D(v):
    if v is None or v == "":
        return None
    return Decimal(str(v))


def get_cat(name: str, description: str = ""):
    from categories.models import Category

    defaults = {"is_active": True}
    if description:
        try:
            cat, _ = Category.objects.get_or_create(
                name=name, defaults={**defaults, "description": description}
            )
        except Exception:
            cat, _ = Category.objects.get_or_create(name=name, defaults=defaults)
    else:
        cat, _ = Category.objects.get_or_create(name=name, defaults=defaults)
    return cat


def create_if_missing(model, key_field: str, data: dict, extra=None):
    key = data[key_field]
    if model.objects.filter(**{key_field: key}).exists():
        print(f"  skip {key}")
        return 0
    payload = dict(data)
    if extra:
        payload.update(extra)
    model.objects.create(**payload)
    print(f"  create {key}")
    return 1
