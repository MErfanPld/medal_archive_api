"""OpenAPI authentication extension for custom JWT class."""

from drf_spectacular.extensions import OpenApiAuthenticationExtension


class ActiveUserJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'users.authentication.ActiveUserJWTAuthentication'
    name = 'BearerAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': (
                'توکن دسترسی JWT. پس از ورود از /api/users/login/، '
                'مقدار access را به‌صورت Bearer ارسال کنید.'
            ),
        }
