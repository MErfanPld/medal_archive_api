from django.urls import path

from .views import *

app_name = 'users'

urlpatterns = [
    # احراز هویت
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('me/', MeAPIView.as_view(), name='me'),

    # لینک دعوت یک‌بار مصرف
    path('invite/', InviteLinkCreateAPIView.as_view(), name='invite-create'),
    path('invite/<str:token>/consume/', InviteLinkConsumeAPIView.as_view(), name='invite-consume'),

    # مدیریت کاربران
    path('', UserListAPIView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'),
    path('<int:pk>/roles/', UserRoleAssignAPIView.as_view(), name='user-roles'),

    # ACL: نقش‌ها و مجوزها
    path('roles/', RoleListCreateAPIView.as_view(), name='role-list'),
    path('roles/<int:pk>/', RoleDetailAPIView.as_view(), name='role-detail'),
    path('permissions/', PermissionListAPIView.as_view(), name='permission-list'),
]
