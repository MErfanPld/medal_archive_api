"""
Canonical application permission codenames and default role matrices.

Format: <resource>.<action>

Adding a future module only requires:
  1. Append codenames here
  2. Seed them (data migration or management command)
  3. Declare permission_map / required_permission on views
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Permission catalog
# ---------------------------------------------------------------------------

PERMISSIONS: list[tuple[str, str, str]] = [
    # (codename, display name, description)
    # Users
    ("users.view", "View users", "List and retrieve users"),
    ("users.create", "Create users", "Invite / create users"),
    ("users.update", "Update users", "Activate, deactivate, or update users"),
    ("users.delete", "Delete users", "Delete users"),
    # Roles
    ("roles.view", "View roles", "List and retrieve roles"),
    ("roles.create", "Create roles", "Create roles"),
    ("roles.update", "Update roles", "Update roles and their permissions"),
    ("roles.delete", "Delete roles", "Delete roles"),
    ("roles.assign", "Assign roles", "Assign or replace roles on users"),
    # Permissions
    ("permissions.view", "View permissions", "List application permissions"),
    # Categories (future modules — seeded so roles can be granted now)
    ("categories.view", "View categories", "List and retrieve categories"),
    ("categories.create", "Create categories", "Create categories"),
    ("categories.update", "Update categories", "Update categories"),
    ("categories.delete", "Delete categories", "Delete categories"),
    # Medals
    ("medals.view", "View medals", "List and retrieve medals"),
    ("medals.create", "Create medals", "Create medals"),
    ("medals.update", "Update medals", "Update medals"),
    ("medals.delete", "Delete medals", "Delete medals"),
    # Products
    ("products.view", "View products", "List and retrieve products"),
    ("products.create", "Create products", "Create products"),
    ("products.update", "Update products", "Update products"),
    ("products.delete", "Delete products", "Delete products"),
    # Reports / Search
    ("reports.view", "View reports", "View collection and system reports"),
    ("search.use", "Use search", "Use search and advanced filtering"),
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
        "name": "Admin",
        "description": "Full management access to users, roles, and collection content",
        "permissions": sorted(PERMISSION_CODENAMES),
    },
    ROLE_CURATOR: {
        "name": "Curator",
        "description": "Manage collection content (categories, medals, products)",
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
        "name": "Viewer",
        "description": "Read-only access to collection content and reports",
        "permissions": [
            "categories.view",
            "medals.view",
            "products.view",
            "reports.view",
            "search.use",
        ],
    },
}
