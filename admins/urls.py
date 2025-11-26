from django.urls import path, include
from .views import AdminLoginView, AdminLogoutView, AdminUserViewSet, AdminStaffViewSet, AdminGetView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register('users', AdminUserViewSet, basename='admin-users')
router.register('staff', AdminStaffViewSet, basename='admin-staff')

urlpatterns = [
    path('login/',AdminLoginView.as_view(), name='admin-login'),
    path('logout/', AdminLogoutView.as_view(), name='admin-logout'),
    path('me/<int:pk>/', AdminGetView.as_view(), name='admin-get-user'),
    path('', include(router.urls)),
]