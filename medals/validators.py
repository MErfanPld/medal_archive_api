import os

from django.conf import settings
from rest_framework.exceptions import ValidationError

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
ALLOWED_IMAGE_CONTENT_TYPES = {
    'image/jpeg', 'image/png', 'image/webp', 'image/gif',
}

ALLOWED_FILE_EXTENSIONS = {'.pdf', '.txt', '.doc', '.docx', '.odt', '.rtf', '.csv', '.xlsx', '.xls'}
ALLOWED_FILE_CONTENT_TYPES = {
    'application/pdf',
    'text/plain',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.oasis.opendocument.text',
    'application/rtf',
    'text/csv',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/octet-stream',
}


def _ext(name: str) -> str:
    return os.path.splitext(name or '')[1].lower()


def validate_medal_image(uploaded_file):
    max_bytes = getattr(settings, 'MEDAL_IMAGE_MAX_BYTES', 10 * 1024 * 1024)
    name = getattr(uploaded_file, 'name', '') or ''
    content_type = getattr(uploaded_file, 'content_type', '') or ''
    size = getattr(uploaded_file, 'size', 0) or 0

    if size <= 0:
        raise ValidationError('Empty file is not allowed.')
    if size > max_bytes:
        raise ValidationError(f'Image exceeds maximum size of {max_bytes} bytes.')
    if _ext(name) not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'Invalid image extension. Allowed: {", ".join(sorted(ALLOWED_IMAGE_EXTENSIONS))}'
        )
    if content_type and content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise ValidationError(f'Invalid image content type: {content_type}')


def validate_medal_file(uploaded_file):
    max_bytes = getattr(settings, 'MEDAL_FILE_MAX_BYTES', 20 * 1024 * 1024)
    name = getattr(uploaded_file, 'name', '') or ''
    content_type = getattr(uploaded_file, 'content_type', '') or ''
    size = getattr(uploaded_file, 'size', 0) or 0

    if size <= 0:
        raise ValidationError('Empty file is not allowed.')
    if size > max_bytes:
        raise ValidationError(f'File exceeds maximum size of {max_bytes} bytes.')
    if _ext(name) not in ALLOWED_FILE_EXTENSIONS:
        raise ValidationError(
            f'Invalid file extension. Allowed: {", ".join(sorted(ALLOWED_FILE_EXTENSIONS))}'
        )
    if _ext(name) in {'.exe', '.bat', '.cmd', '.sh', '.js', '.msi', '.dll', '.com'}:
        raise ValidationError('Executable uploads are not allowed.')
    if content_type and content_type not in ALLOWED_FILE_CONTENT_TYPES:
        if content_type.startswith('application/x-') or content_type.startswith('application/javascript'):
            raise ValidationError(f'Invalid file content type: {content_type}')
