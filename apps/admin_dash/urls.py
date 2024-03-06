from django.urls import path, include
from .views import UserDashViewSet,UserManagementInfoViewSet,UserManagementViewSet,AdminDashboardViewSet,TransactionViewSet,TransactionInfoViewSet
app_name = 'admin_dash'

urlpatterns = [
    path('admin-dash/', AdminDashboardViewSet.as_view(), name='admin-dash'),

    path('users-dash/', UserDashViewSet.as_view(), name='users-dash'),
    path('user-management/', UserManagementViewSet.as_view(), name='users-management'),
    path('user-management-info/<int:pk>/', UserManagementInfoViewSet.as_view(), name='users-management-info'),
    path('transaction-management/', TransactionViewSet.as_view(), name='transaction-management'),
    path('transaction-management-info/<str:order_id>/', TransactionInfoViewSet.as_view(), name='transaction-management-info'),
]