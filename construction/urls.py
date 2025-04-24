from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.construction_list, name='construction_list'),
    path('register/', views.register_construction, name='construction_register'),
    path('detail/<int:pk>/', views.construction_detail, name='construction_detail'),
    path('update/<int:pk>/', views.construction_update, name='construction_update'),
    path('delete/<int:pk>/', views.construction_delete, name='construction_delete'),
    path('bulk_delete/', views.bulk_delete_construction, name='bulk_delete_construction'),
    path('upload_image_url/', views.upload_image_view, name='upload_image_url'),
    path('construction/image/delete/', views.delete_item_image, name='delete_item_image'),
]