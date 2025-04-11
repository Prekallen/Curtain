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
    path('places/', views.const_list, name='place_list'),
    # 시공 정보
    path('place/<int:place_id>/', views.const, name='place_detail'),
    # 개인 정보 제공 동의 페이지 
    path('check/', views.personal_info_check, name='eventCheck'),
    # 개인 정보 입력 (이름, 휴대폰 번호, 주소)
    path('quote/', views.request_quote, name='events'),
    # 완료 페이지
    path('complete/<int:id>/', views.request_quote, name='stamp'),
]

# 이미지 URL 설정
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)