"""
Canonical application permission codenames and default role matrices.

Format: <resource>.<action>

Adding a future module only requires:
  1. Append codenames here
  2. Seed them (data migration or management command)
  3. Declare permission_map / required_permission on views

Display names (name / description) are Persian for API and UI.
Codenames remain English and are the stable keys for ACL logic.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Permission catalog
# ---------------------------------------------------------------------------

PERMISSIONS: list[tuple[str, str, str]] = [
    # (codename, display name, description)
    # Users
    ("users.view", "مشاهده کاربران", "لیست و مشاهده کاربران"),
    ("users.create", "ایجاد کاربر", "دعوت و ایجاد کاربر جدید"),
    ("users.update", "ویرایش کاربر", "فعال، غیرفعال یا بروزرسانی کاربران"),
    ("users.delete", "حذف کاربر", "حذف کاربران"),
    # Roles
    ("roles.view", "مشاهده نقش‌ها", "لیست و مشاهده نقش‌ها"),
    ("roles.create", "ایجاد نقش", "ایجاد نقش جدید"),
    ("roles.update", "ویرایش نقش", "ویرایش نقش و دسترسی‌های آن"),
    ("roles.delete", "حذف نقش", "حذف نقش"),
    ("roles.assign", "اختصاص نقش", "اختصاص یا جایگزینی نقش‌های کاربر"),
    # Permissions
    ("permissions.view", "مشاهده دسترسی‌ها", "لیست دسترسی‌های برنامه"),
    # Categories
    ("categories.view", "مشاهده دسته‌بندی‌ها", "لیست و مشاهده دسته‌بندی‌ها"),
    ("categories.create", "ایجاد دسته‌بندی", "ایجاد دسته‌بندی جدید"),
    ("categories.update", "ویرایش دسته‌بندی", "ویرایش و بروزرسانی دسته‌بندی"),
    ("categories.delete", "حذف دسته‌بندی", "حذف دسته‌بندی"),
    # Medals
    ("medals.view", "مشاهده مدال‌ها", "لیست و مشاهده مدال‌ها"),
    ("medals.create", "ثبت مدال", "ثبت مدال جدید"),
    ("medals.update", "ویرایش مدال", "ویرایش و بروزرسانی مدال"),
    ("medals.delete", "حذف مدال", "حذف مدال"),
    # Products
    ("products.view", "مشاهده محصولات", "لیست و مشاهده محصولات"),
    ("products.create", "ایجاد محصول", "ایجاد محصول جدید"),
    ("products.update", "ویرایش محصول", "ویرایش محصول"),
    ("products.delete", "حذف محصول", "حذف محصول"),
    # Reports / Search
    ("reports.view", "مشاهده گزارش‌ها", "مشاهده گزارش‌های مجموعه و سیستم"),
    ("search.use", "استفاده از جستجو", "استفاده از جستجوی پیشرفته و فیلترینگ"),
]

PERMISSION_CODENAMES: frozenset[str] = frozenset(c for c, _, _ in PERMISSIONS)

# ---------------------------------------------------------------------------
# Default role matrices (codename -> permission codenames)
# ---------------------------------------------------------------------------

ROLE_ADMIN = "admin"
ROLE_CURATOR = "curator"
ROLE_VIEWER = "viewer"

DEFAULT_ROLES: dict[str, dict] = {
    ROLE_ADMIN: {
        "name": "مدیر",
        "description": "دسترسی کامل به کاربران، نقش‌ها و محتوای مجموعه",
        "permissions": sorted(PERMISSION_CODENAMES),
    },
    ROLE_CURATOR: {
        "name": "متصدی مجموعه",
        "description": "مدیریت محتوای مجموعه (دسته‌بندی‌ها، مدال‌ها، محصولات)",
        "permissions": [
            "categories.view",
            "categories.create",
            "categories.update",
            "medals.view",
            "medals.create",
            "medals.update",
            "medals.delete",
            "products.view",
            "products.create",
            "products.update",
            "products.delete",
            "reports.view",
            "search.use",
        ],
    },
    ROLE_VIEWER: {
        "name": "مشاهده‌گر",
        "description": "دسترسی فقط‌خواندنی به محتوای مجموعه و گزارش‌ها",
        "permissions": [
            "categories.view",
            "medals.view",
            "products.view",
            "reports.view",
            "search.use",
        ],
    },
}
