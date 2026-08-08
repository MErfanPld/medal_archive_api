from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import (
    User,
    Role,
    Permission,
    RolePermission,
    UserRole,
    InviteLink,
)


# =========================================================
# User Role Inline
# =========================================================

class UserRoleInline(admin.TabularInline):
    model = UserRole
    fk_name = "user"

    extra = 0

    autocomplete_fields = [
        "role",
    ]

    readonly_fields = [
        "assigned_by",
        "assigned_at",
    ]


# =========================================================
# User Admin
# =========================================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    ordering = [
        "-date_joined",
    ]

    list_display = [
        "username",
        "email",
        "is_active",
        "is_locked_display",
        "is_staff",
        "date_joined",
    ]

    list_filter = [
        "is_active",
        "is_staff",
    ]

    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
    ]

    readonly_fields = [
        "date_joined",
        "updated_at",
        "last_login",
        "last_login_ip",
        "failed_login_attempts",
        "locked_until",
        "created_by",
    ]

    # =====================================================
    # Edit User
    # =====================================================

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "password",
                ),
            },
        ),
        (
            "اطلاعات شخصی",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                ),
            },
        ),
        (
            "دسترسی‌ها",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "must_change_password",
                ),
            },
        ),
        (
            "امنیت",
            {
                "fields": (
                    "failed_login_attempts",
                    "locked_until",
                    "last_login",
                    "last_login_ip",
                ),
            },
        ),
        (
            "تاریخچه",
            {
                "fields": (
                    "created_by",
                    "date_joined",
                    "updated_at",
                ),
            },
        ),
    )

    # =====================================================
    # Add User
    # =====================================================

    add_fieldsets = (
        (
            None,
            {
                "classes": (
                    "wide",
                ),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    # =====================================================
    # Inline
    # =====================================================

    inlines = [
        UserRoleInline,
    ]

    # =====================================================
    # Locked Status
    # =====================================================

    @admin.display(
        description="وضعیت قفل",
    )
    def is_locked_display(self, obj):

        if obj.is_locked:
            return format_html(
                '<span style="color:red;font-weight:bold;">{}</span>',
                "قفل‌شده",
            )

        return format_html(
            '<span style="color:green;">{}</span>',
            "فعال",
        )

    # =====================================================
    # Save User
    # =====================================================

    def save_model(
        self,
        request,
        obj,
        form,
        change,
    ):
        if not change:
            obj.created_by = request.user

        super().save_model(
            request,
            obj,
            form,
            change,
        )

    # =====================================================
    # Save Role Inline
    # =====================================================

    def save_formset(
        self,
        request,
        form,
        formset,
        change,
    ):
        instances = formset.save(
            commit=False
        )

        for instance in instances:

            if isinstance(
                instance,
                UserRole,
            ):
                if not instance.assigned_by_id:
                    instance.assigned_by = request.user

            instance.save()

        formset.save_m2m()


# =========================================================
# Role Permission Inline
# =========================================================

class RolePermissionInline(admin.TabularInline):

    model = RolePermission

    extra = 0

    autocomplete_fields = [
        "permission",
    ]


# =========================================================
# Role Admin
# =========================================================

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):

    list_display = [
        "name",
        "codename",
        "is_active",
        "created_at",
    ]

    list_filter = [
        "is_active",
    ]

    search_fields = [
        "name",
        "codename",
    ]

    ordering = [
        "name",
    ]

    inlines = [
        RolePermissionInline,
    ]


# =========================================================
# Permission Admin
# =========================================================

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):

    list_display = [
        "codename",
        "name",
    ]

    search_fields = [
        "codename",
        "name",
    ]

    ordering = [
        "codename",
    ]


# =========================================================
# Invite Link Admin
# =========================================================

@admin.register(InviteLink)
class InviteLinkAdmin(admin.ModelAdmin):

    list_display = [
        "user",
        "created_by",
        "created_at",
        "expires_at",
        "is_used",
        "used_at",
    ]

    list_filter = [
        "is_used",
        "created_at",
        "expires_at",
    ]

    search_fields = [
        "user__username",
        "user__email",
        "created_by__username",
    ]

    readonly_fields = [
        field.name
        for field in InviteLink._meta.fields
    ]

    ordering = [
        "-created_at",
    ]

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False