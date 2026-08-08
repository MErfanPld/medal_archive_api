# Generated data migration: seed permission catalog and default roles.

from django.db import migrations


def seed_permissions_and_roles(apps, schema_editor):
    Permission = apps.get_model('users', 'Permission')
    Role = apps.get_model('users', 'Role')
    RolePermission = apps.get_model('users', 'RolePermission')

    # Inline catalog (must stay in sync with users.permission_catalog)
    permissions = [
        ("users.view", "View users", "List and retrieve users"),
        ("users.create", "Create users", "Invite / create users"),
        ("users.update", "Update users", "Activate, deactivate, or update users"),
        ("users.delete", "Delete users", "Delete users"),
        ("roles.view", "View roles", "List and retrieve roles"),
        ("roles.create", "Create roles", "Create roles"),
        ("roles.update", "Update roles", "Update roles and their permissions"),
        ("roles.delete", "Delete roles", "Delete roles"),
        ("roles.assign", "Assign roles", "Assign or replace roles on users"),
        ("permissions.view", "View permissions", "List application permissions"),
        ("categories.view", "View categories", "List and retrieve categories"),
        ("categories.create", "Create categories", "Create categories"),
        ("categories.update", "Update categories", "Update categories"),
        ("categories.delete", "Delete categories", "Delete categories"),
        ("medals.view", "View medals", "List and retrieve medals"),
        ("medals.create", "Create medals", "Create medals"),
        ("medals.update", "Update medals", "Update medals"),
        ("medals.delete", "Delete medals", "Delete medals"),
        ("products.view", "View products", "List and retrieve products"),
        ("products.create", "Create products", "Create products"),
        ("products.update", "Update products", "Update products"),
        ("products.delete", "Delete products", "Delete products"),
        ("reports.view", "View reports", "View collection and system reports"),
        ("search.use", "Use search", "Use search and advanced filtering"),
    ]

    perm_by_code = {}
    for codename, name, description in permissions:
        obj, _ = Permission.objects.get_or_create(
            codename=codename,
            defaults={'name': name, 'description': description},
        )
        perm_by_code[codename] = obj

    role_defs = {
        'admin': {
            'name': 'Admin',
            'description': 'Full management access to users, roles, and collection content',
            'permissions': list(perm_by_code.keys()),
        },
        'curator': {
            'name': 'Curator',
            'description': 'Manage collection content (categories, medals, products)',
            'permissions': [
                'categories.view', 'categories.create', 'categories.update',
                'medals.view', 'medals.create', 'medals.update', 'medals.delete',
                'products.view', 'products.create', 'products.update', 'products.delete',
                'reports.view', 'search.use',
            ],
        },
        'viewer': {
            'name': 'Viewer',
            'description': 'Read-only access to collection content and reports',
            'permissions': [
                'categories.view', 'medals.view', 'products.view',
                'reports.view', 'search.use',
            ],
        },
    }

    for codename, meta in role_defs.items():
        role, _ = Role.objects.get_or_create(
            codename=codename,
            defaults={
                'name': meta['name'],
                'description': meta['description'],
                'is_active': True,
            },
        )
        for pcode in meta['permissions']:
            perm = perm_by_code[pcode]
            RolePermission.objects.get_or_create(role=role, permission=perm)


def unseed(apps, schema_editor):
    # Non-destructive reverse: leave data in place (roles may already be assigned).
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_permissions_and_roles, unseed),
    ]
