from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.part_list, name='part_list'),
    # path('detail/<int:pk>/', views.board_detail),
    # path('update/<int:pk>/', views.board_update),
    # path('upload_image_url/', views.upload_image_view, name='upload_image'),
]