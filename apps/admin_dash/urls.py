from django.urls import path, include
from .views import UserDashViewSet,UserManagementViewSet,AdminDashboardViewSet
app_name = 'admin_dash'

urlpatterns = [
    path('admin-dash/', AdminDashboardViewSet.as_view(), name='admin-dash'),

    path('users-dash/', UserDashViewSet.as_view(), name='users-dash'),
    path('user-management/', UserManagementViewSet.as_view(), name='users-management'),
    
]