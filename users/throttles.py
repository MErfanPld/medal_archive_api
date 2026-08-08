from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    """محدودیت تلاش ورود بر اساس IP + username (جلوگیری از brute-force)"""
    scope = 'login'

    def get_cache_key(self, request, view):
        username = str(request.data.get('username', '')).lower()
        ident = f'{self.get_ident(request)}:{username}'
        return self.cache_format % {'scope': self.scope, 'ident': ident}


class InviteConsumeThrottle(SimpleRateThrottle):
    """محدودیت تلاش برای حدس زدن توکن دعوت"""
    scope = 'invite_consume'

    def get_cache_key(self, request, view):
        token = str(view.kwargs.get('token', ''))
        ident = f'{self.get_ident(request)}:{token[:16]}'
        return self.cache_format % {'scope': self.scope, 'ident': ident}


class InviteCreateThrottle(SimpleRateThrottle):
    """محدودیت ساخت لینک دعوت توسط ادمین"""
    scope = 'invite_create'

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}
