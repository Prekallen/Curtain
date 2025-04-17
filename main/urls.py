from django.urls import path, include
from main import views

# 이미지를 업로드하자
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    # 커튼 소개
    path('', views.curtain_intro, name='curtain_intro'),
    # 위치 기반 지도 맵 노출[시공 위치 핀, 팝업]
    path('const_map/', views.const_map, name='const_map'),
    # 시공 리스트
    path('list/', views.const_list, name='const_list'),
    # 시공 정보
    path('detail/<int:place_id>/', views.const_detail, name='const_detail'),
    # 개인 정보 입력 (이름, 휴대폰 번호, 주소)
    path('request_quote/', views.request_quote_flow, name='request_quote_flow'),
    path('request_quote/get_region_level2/', views.get_region_level2, name='get_region_level2'),
    path('request_quote/get_region_level3/', views.get_region_level3, name='get_region_level3'),
    path('request_quote/step1/', views.request_quote_flow_step1, name='request_quote_flow_step1'),
    path('request_quote/step2/', views.request_quote_flow_step2, name='request_quote_flow_step2'),
    path('request_quote/step3/', views.request_quote_flow_step3, name='request_quote_flow_step3'),
    path('request_quote/step4/', views.request_quote_flow_step4, name='request_quote_flow_step4'),
    path('request_quote/submit/', views.submit_request_quote, name='submit_request_quote'),
    path('personal_info_policy/', views.personal_info_policy, name='personal_info_policy'),
    # 완료 페이지
    path('complete/<int:id>/', views.request_complete, name='request_complete'),
]
