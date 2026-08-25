"""Seed permissions for banknotes, seals, tasbih, rings, knives, antiques, stamps."""

from django.db import migrations

MODULES = [
    ("banknotes", "اسکناس", "اسکناس‌ها"),
    ("seals", "مهر", "مهرها"),
    ("tasbih", "تسبیح", "تسبیح‌ها"),
    ("rings", "انگشتر", "انگشترها"),
    ("knives", "چاقو", "چاقوها"),
    ("antiques", "آنتیک", "آنتیک‌ها"),
    ("stamps", "تمبر", "تمبرها"),
]

ACTIONS = [
    ("view", "مشاهده {pl}", "لیست و مشاهده {pl}"),
    ("create", "ثبت {sg}", "ایجاد {sg} جدید"),
    ("update", "ویرایش {sg}", "ویرایش {sg}"),
    ("delete", "حذف {sg}", "حذف {sg}"),
]


def seed(apps, schema_editor):
    Permission = apps.get_model('users', 'Permission')
    Role = apps.get_model('users', 'Role')
    RolePermission = apps.get_model('users', 'RolePermission')
    perm_objs = []
    for code, sg, pl in MODULES:
        for action, name_tpl, desc_tpl in ACTIONS:
            codename = f'{code}.{action}'
            name = name_tpl.format(sg=sg, pl=pl)
            description = desc_tpl.format(sg=sg, pl=pl)
            p, _ = Permission.objects.get_or_create(
                codename=codename,
                defaults={'name': name, 'description': description},
            )
            if p.name != name or p.description != description:
                p.name = name
                p.description = description
                p.save(update_fields=['name', 'description'])
            perm_objs.append(p)

    admin = Role.objects.filter(codename='admin').first()
    if admin:
        for p in perm_objs:
            RolePermission.objects.get_or_create(role=admin, permission=p)

    curator = Role.objects.filter(codename='curator').first()
    if curator:
        for p in perm_objs:
            RolePermission.objects.get_or_create(role=curator, permission=p)

    viewer = Role.objects.filter(codename='viewer').first()
    if viewer:
        for p in perm_objs:
            if p.codename.endswith('.view'):
                RolePermission.objects.get_or_create(role=viewer, permission=p)


def unseed(apps, schema_editor):
    Permission = apps.get_model('users', 'Permission')
    codes = [f'{c}.{a}' for c, _, _ in MODULES for a, _, _ in ACTIONS]
    Permission.objects.filter(codename__in=codes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_merge_20260815_0908'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
