"""Default placeholder images for medal seeding."""
from __future__ import annotations

from pathlib import Path

from django.core.files import File

from medals.related_models import MedalImage, MedalImageType


def _generate_placeholder_png(path: Path, title: str, bg, accent) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    w, h = 640, 640
    img = Image.new('RGB', (w, h), bg)
    draw = ImageDraw.Draw(img)
    margin = 40
    draw.ellipse([margin, margin, w - margin, h - margin], outline=accent, width=8)
    draw.ellipse([margin + 30, margin + 30, w - margin - 30, h - margin - 30], outline=accent, width=3)
    cx, cy = w // 2, h // 2
    draw.ellipse([cx - 80, cy - 80, cx + 80, cy + 80], fill=accent)
    draw.rectangle([0, h - 90, w, h], fill=(30, 30, 30))
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), title, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, h - 62), title, fill=(255, 255, 255), font=font)
    img.save(path, format='PNG')


def default_medal_image_path() -> Path:
    path = Path(__file__).resolve().parent / 'static' / 'medals' / 'defaults' / 'default_medal.png'
    if not path.is_file():
        _generate_placeholder_png(path, 'Medal', (245, 236, 220), (184, 134, 11))
    return path


def ensure_primary_image(medal) -> bool:
    """Attach default primary image if the medal has none. Returns True if created."""
    if medal.images.exists():
        return False
    src = default_medal_image_path()
    if not src.is_file():
        return False
    with src.open('rb') as fh:
        img = MedalImage(
            medal=medal,
            image_type=MedalImageType.FRONT,
            caption='تصویر پیش‌فرض',
            ordering=0,
            is_primary=True,
            original_filename=src.name,
            file_size=src.stat().st_size,
        )
        img.image.save(f'default_{medal.pk}.png', File(fh), save=True)
    return True
