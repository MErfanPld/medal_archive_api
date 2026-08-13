# Data migration: update Permission and Role display names/descriptions to Persian.
# Codenames and relations are left unchanged.

from django.db import migrations


def update_labels_to_persian(apps, schema_editor):
    Permission = apps.get_model('users', 'Permission')
    Role = apps.get_model('users', 'Role')

    # Must stay in sync with users.permission_catalog.PERMISSIONS
    permissions = [
        ("users.view", "مشاهده کاربران", "لیست و مشاهده کاربران"),
        ("users.create", "ایجاد کاربر", "دعوت و ایجاد کاربر جدید"),
        ("users.update", "ویرایش کاربر", "فعال، غیرفعال یا بروزرسانی کاربران"),
        ("users.delete", "حذف کاربر", "حذف کاربران"),
        ("roles.view", "مشاهده نقش‌ها", "لیست و مشاهده نقش‌ها"),
        ("roles.create", "ایجاد نقش", "ایجاد نقش جدید"),
        ("roles.update", "ویرایش نقش", "ویرایش نقش و دسترسی‌های آن"),
        ("roles.delete", "حذف نقش", "حذف نقش"),
        ("roles.assign", "اختصاص نقش", "اختصاص یا جایگزینی نقش‌های کاربر"),
        ("permissions.view", "مشاهده دسترسی‌ها", "لیست دسترسی‌های برنامه"),
        ("categories.view", "مشاهده دسته‌بندی‌ها", "لیست و مشاهده دسته‌بندی‌ها"),
        ("categories.create", "ایجاد دسته‌بندی", "ایجاد دسته‌بندی جدید"),
        ("categories.update", "ویرایش دسته‌بندی", "ویرایش و بروزرسانی دسته‌بندی"),
        ("categories.delete", "حذف دسته‌بندی", "حذف دسته‌بندی"),
        ("medals.view", "مشاهده مدال‌ها", "لیست و مشاهده مدال‌ها"),
        ("medals.create", "ثبت مدال", "ثبت مدال جدید"),
        ("medals.update", "ویرایش مدال", "ویرایش و بروزرسانی مدال"),
        ("medals.delete", "حذف مدال", "حذف مدال"),
        ("products.view", "مشاهده محصولات", "لیست و مشاهده محصولات"),
        ("products.create", "ایجاد محصول", "ایجاد محصول جدید"),
        ("products.update", "ویرایش محصول", "ویرایش محصول"),
        ("products.delete", "حذف محصول", "حذف محصول"),
        ("reports.view", "مشاهده گزارش‌ها", "مشاهده گزارش‌های مجموعه و سیستم"),
        ("search.use", "استفاده از جستجو", "استفاده از جستجوی پیشرفته و فیلترینگ"),
    ]

    for codename, name, description in permissions:
        Permission.objects.filter(codename=codename).update(
            name=name,
            description=description,
        )

    # Must stay in sync with users.permission_catalog.DEFAULT_ROLES
    role_defs = {
        'admin': {
            'name': 'مدیر',
            'description': 'دسترسی کامل به کاربران، نقش‌ها و محتوای مجموعه',
        },
        'curator': {
            'name': 'متصدی مجموعه',
            'description': 'مدیریت محتوای مجموعه (دسته‌بندی‌ها، مدال‌ها، محصولات)',
        },
        'viewer': {
            'name': 'مشاهده‌گر',
            'description': 'دسترسی فقط‌خواندنی به محتوای مجموعه و گزارش‌ها',
        },
    }

    for codename, meta in role_defs.items():
        Role.objects.filter(codename=codename).update(
            name=meta['name'],
            description=meta['description'],
        )


def noop_reverse(apps, schema_editor):
    # Reverse is intentionally non-destructive (labels only).
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_seed_rbac_permissions'),
    ]

    operations = [
        migrations.RunPython(update_labels_to_persian, noop_reverse),
    ]
