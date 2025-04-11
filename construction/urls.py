from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.construction_list, name='construction_list'),
    path('write/', views.register_construction, name='construction_register'),
    path('detail/<int:pk>/', views.construction_detail, name='construction_detail'),
    path('update/<int:pk>/', views.board_update, name='board_update'),
    path('upload_image_url/', views.upload_image_view, name='upload_image_url'),
]