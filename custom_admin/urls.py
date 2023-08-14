from django.urls import path
from . import views
from django.urls import path
from .views import ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView, manage_users, edit_user, delete_user, change_password


app_name = 'custom_admin'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    # Add more URLs for user management, system settings, etc.
    path('manage_users/', manage_users, name='manage_users'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/add/', ProductCreateView.as_view(), name='product-add'),
    path('products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product-edit'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),

    path('edit_user/<int:user_id>/', edit_user, name='edit_user'),
    path('delete_user/<int:user_id>/', delete_user, name='delete_user'),
    path('change_password/<int:user_id>/', change_password, name='change_password'),
]

