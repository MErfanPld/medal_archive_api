"""Seed coins.* permissions and attach to default roles."""

from django.db import migrations


COIN_PERMS = [
    ("coins.view", "مشاهده سکه و پول", "لیست و مشاهده سکه‌ها، اسکناس‌ها و اقلام پولی"),
    ("coins.create", "ثبت سکه و پول", "ایجاد سکه، اسکناس یا قلم پولی جدید"),
    ("coins.update", "ویرایش سکه و پول", "ویرایش اقلام سکه و پول"),
    ("coins.delete", "حذف سکه و پول", "حذف اقلام سکه و پول"),
]


def seed(apps, schema_editor):
    Permission = apps.get_model('users', 'Permission')
    Role = apps.get_model('users', 'Role')
    RolePermission = apps.get_model('users', 'RolePermission')

    perm_objs = []
    for codename, name, description in COIN_PERMS:
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
        view_perm = next(p for p in perm_objs if p.codename == 'coins.view')
        RolePermission.objects.get_or_create(role=viewer, permission=view_perm)


def unseed(apps, schema_editor):
    Permission = apps.get_model('users', 'Permission')
    Permission.objects.filter(codename__in=[c for c, _, _ in COIN_PERMS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_merge_20260815_0908'),
        ('coins', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
