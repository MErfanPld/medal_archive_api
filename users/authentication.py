"""
JWT authentication that rejects inactive or locked users.

Trade-off (F4):
  Access tokens remain cryptographically valid until expiry (stateless JWT).
  SimpleJWT already loads the user from the database on each authenticated
  request; we reuse that lookup to refuse inactive/locked accounts immediately
  after deactivation or lockout, without introducing a token_version claim.

  Outstanding access tokens for a deactivated user are rejected within the
  next request that hits this authentication class. Refresh tokens are not
  automatically blacklisted on deactivation (logout / rotation still handle
  blacklist). Full immediate global revocation would require a shared
  denylist or a user token-version claim — intentionally not added here.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class ActiveUserJWTAuthentication(JWTAuthentication):
    """JWTAuthentication that additionally enforces is_active and lockout."""

    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        if not user.is_active:
            raise AuthenticationFailed(
                'User account is disabled.',
                code='user_inactive',
            )

        if getattr(user, 'is_locked', False):
            raise AuthenticationFailed(
                'User account is temporarily locked.',
                code='user_locked',
            )

        return user


# Register OpenAPI auth extension for drf-spectacular
try:
    from . import schema as _schema  # noqa: F401
except ImportError:
    pass
