from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = ([
    path('admin/', admin.site.urls),
    # path('crud/', include('myapp.urls')),
    path('', include('main.urls')),
    path('manager/', include('manager.urls')),
    path('const/', include('construction.urls')),
    path('contract/', include('contract.urls')),
    path('customer/', include('customer.urls')),
])
# 다른 url 패턴들
# 이미지 URL 설정
# static 파일 서빙 추가
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)