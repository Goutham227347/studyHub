from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.user_dashboard, name='user'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('theme/', views.toggle_theme, name='toggle_theme'),
    path('admin/', views.admin_dashboard, name='admin'),
    path('admin/users/', views.manage_users, name='manage_users'),
    path('admin/moderate/', views.moderate_materials, name='moderate'),
    path('admin/moderate/<int:pk>/', views.moderate_action, name='moderate_action'),
]
