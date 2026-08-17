"""Default placeholder images for coin/banknote seeding."""
from __future__ import annotations

from pathlib import Path

from django.core.files import File

from coins.models import ItemType
from coins.related_models import CoinImage, CoinImageType


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


def default_coin_image_path(item_type: str) -> Path:
    base = Path(__file__).resolve().parent / 'static' / 'coins' / 'defaults'
    if item_type == ItemType.BANKNOTE:
        path = base / 'default_banknote.png'
        if not path.is_file():
            _generate_placeholder_png(path, 'Banknote', (235, 245, 235), (46, 125, 50))
        if path.is_file():
            return path
    path = base / 'default_coin.png'
    if not path.is_file():
        _generate_placeholder_png(path, 'Coin', (230, 240, 245), (70, 130, 180))
    return path


def ensure_primary_image(coin) -> bool:
    """Attach default primary image if the coin has none. Returns True if created."""
    if coin.images.exists():
        return False
    src = default_coin_image_path(coin.item_type)
    if not src.is_file():
        return False
    with src.open('rb') as fh:
        img = CoinImage(
            coin=coin,
            image_type=CoinImageType.FRONT,
            caption='تصویر پیش‌فرض',
            ordering=0,
            is_primary=True,
            original_filename=src.name,
            file_size=src.stat().st_size,
        )
        img.image.save(f'default_{coin.pk}.png', File(fh), save=True)
    return True
