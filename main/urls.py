from django.urls import path, include
from main import views

# 이미지를 업로드하자
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    # ex: /main/
    # 웹사이트의 첫화면은 index 페이지이다 + URL이름은 index이다
    # 1. 진입 페이지
    path('', views.godfather_info, name='godfather_info'),
    # 2-1. 위치 기반 지도 맵 노출
    path('event_map/', views.event_map, name='event_map'),
    # 3-A-1. 전체 업장 리스트 노출
    path('places/', views.place_list, name='place_list'),
    #3-A-2. 업장 클릭 시, 업장 정보 노출
    path('place/<int:place_id>/', views.place, name='place_detail'),
    # 3-B-1. 개인 정보 제공 동의 페이지 노출 (팝업 or 페이지)
    path('eventCheck/', views.event_check, name='eventCheck'),
    # 3-B-2. 개인 정보 입력 (이름, 휴대폰 번호)
    path('events/', views.events, name='events'),
    # 4-1. 이벤트 참여 진행도 스템프 형식으로 노출
    path('stamp/<int:id>/', views.stamp, name='stamp'),

    # 개인 정보 입력시 placeId 반자동화 검색(Json)
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    # URL:8080/blog에 접속하면 blog 페이지 + URL이름은 blog이다
    #path('blog/', views.blog, name='blog'),
    # URL:8080/blog/숫자로 접속하면 게시글-세부페이지(posting)
    #path('blog/<int:pk>/', views.posting, name="posting"),
    # URL:8080/blog/new_post로 접속하면 새 게시글 작성
    #path('blog/new_post/', views.new_post, name='new_post'),
    # URL:8080/blog/숫자/remove로 접속하면 게시글 삭제(remove_post)
    #path('blog/<int:pk>/remove/', views.remove_post, name='remove_post'),
    # URL:8080/blog/숫자로 접속하면 게시글-세부페이지(posting)
    #path('blog/update/<int:pk>/', views.update_post, name="update_post"),
]

# 이미지 URL 설정
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)