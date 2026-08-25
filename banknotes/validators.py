from django.conf import settings
from rest_framework.exceptions import ValidationError

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
ALLOWED_IMAGE_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}


def _ext(name: str) -> str:
    if not name or '.' not in name:
        return ''
    return '.' + name.rsplit('.', 1)[-1].lower()


def validate_banknotes_image(uploaded_file):
    max_bytes = getattr(settings, 'COLLECTION_IMAGE_MAX_BYTES', 10 * 1024 * 1024)
    name = getattr(uploaded_file, 'name', '') or ''
    content_type = getattr(uploaded_file, 'content_type', '') or ''
    size = getattr(uploaded_file, 'size', 0) or 0
    if size <= 0:
        raise ValidationError('فایل خالی مجاز نیست.')
    if size > max_bytes:
        raise ValidationError(f'حجم تصویر بیش از حد مجاز است ({max_bytes} بایت).')
    if _ext(name) not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(f'پسوند تصویر نامعتبر است.')
    if content_type and content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise ValidationError(f'نوع محتوای تصویر نامعتبر است: {content_type}')
