from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('add/', views.product_create, name='product_create'),
    path('update/<int:id>/', views.product_update, name='product_update'),
    path('delete/<int:id>/', views.product_delete, name='product_delete'),
]