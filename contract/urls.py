from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.contract_list, name='contract_list'),
    path('write/', views.register_contract, name='register_contract'),
    path('detail/<int:pk>/', views.contract_detail, name='contract_detail'),
    path('update/<int:pk>/', views.contract_update, name='contract_update'),
    path('delete/<int:pk>/', views.contract_delete, name='contract_delete'),
    path('bulk_delete/', views.bulk_delete_contract, name='bulk_delete_contract'), # bulk_delete URL 추가

]