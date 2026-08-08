from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'مدیریت کاربران'

    def ready(self):
        # اتصال سیگنال‌ها (در صورت نیاز به لاگ‌گیری امنیتی بیشتر)
        import users.signals  # noqa
