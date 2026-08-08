# فایل رزرو برای سیگنال‌های امنیتی/لاگ‌گیری آینده
# مثال پیشنهادی: اتصال به user_logged_in / user_login_failed برای audit log جامع‌تر
#
# from django.contrib.auth.signals import user_login_failed
# from django.dispatch import receiver
#
# @receiver(user_login_failed)
# def log_failed_login(sender, credentials, request, **kwargs):
#     ...
