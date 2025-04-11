import json
from math import radians, sin, cos, sqrt, atan2

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db import transaction
from main.forms import CustomerForm
from customer.models import Customer
from construction.models import Construction
import logging

logger = logging.getLogger(__name__)

# 커튼 소개
def curtain_intro(request):

    return render( request, 'curtain_intro.html')

# 시공한 곳 [지도 표기]
def const_map(request):
    try:
        # Construction 모델에서 필요한 데이터만 가져옴
        consts_list = list(Construction.objects.values('id', 'address', 'latitude', 'longitude', 'housing_type'))
        housing_type = Construction.objects.values_list('housing_type', flat=True).distinct()

        if not consts_list:
            messages.warning(request, "시공 데이터가 없습니다.")
    except Exception as e:
        messages.error(request, f"데이터를 불러오는 중 문제가 발생했습니다: {str(e)}")
        consts_list = []
        housing_type = []

    context = {
        'NAVER_MAP_CLIENT_ID': settings.NAVER_MAP_CLIENT_ID,
        'const_json': json.dumps(consts_list),
        'housing_type': housing_type,
    }

    return render(request, 'const_map.html', context)


def haversine(lat1, lon1, lat2, lon2):  # 거리 계산
    R = 6371.0  # 지구 반지름(km)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

# 시공 리스트
def const_list(request):
    query = request.GET.get('q')
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')


    if query:
        # 검색어가 있는 경우
        const_list = Construction.objects.filter(place__icontains=query)
    else:
        # 검색어가 없는 경우
        const_list = Construction.objects.all().order_by('id')

        if lat and lng:
            try:
                user_lat = float(lat)
                user_lng = float(lng)

                # 위도와 경도 값이 없는 객체 제외
                const_list = const_list.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

                consts_with_distance = []
                for const in const_list:
                    dist = haversine(user_lat, user_lng, const.latitude, const.longitude)
                    const.distance = dist  # 장소 객체에 거리 속성 추가
                    try:
                        consts_with_distance.append(const)
                    except Exception as e:
                        print(f"Error appending place to list: {e}")

                # 거리 순으로 정렬
                consts_with_distance.sort(key=lambda x: x.distance)
                const_list = consts_with_distance

            except (ValueError, TypeError) as e:
                print(f"위치 정보 변환 오류: {e}")

    paginator = Paginator(const_list, 10)  # 기본 목록을 사용
    page = request.GET.get('page')
    consts = paginator.get_page(page)

    # 현재 페이지 번호를 정수형으로 변환
    current_page = consts.number

    # 총 페이지 수
    total_pages = paginator.num_pages

    # 페이지 그룹 계산
    page_group = (current_page - 1) // 10
    start_page = page_group * 10 + 1
    end_page = min(start_page + 9, total_pages)
    page_numbers = range(start_page, end_page + 1)

    # 기존의 GET 파라미터에서 'page'를 제거하여 query_string 생성
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()

    context = {
        'consts': consts,
        'page_numbers': page_numbers,
        'has_previous_group': start_page > 1,
        'has_next_group': end_page < total_pages,
        'previous_group_page': start_page - 1,
        'next_group_page': end_page + 1,
        'query_string': query_string,
    }

    return render(request, 'const_list.html', context)

# 시공 클릭 시, 시공 정보 & 사진
def const(request, const_id):
    const = get_object_or_404(Construction, pk=const_id)
    return render(request, 'const.html', {'const': const})

# 개인 정보 제공 동의 페이지 노출 (팝업 or 페이지)
def personal_info_check(request):

    return render( request, 'personal_info_check.html')

# 견적 신청 (이름, 휴대폰 번호, 주소)
def request_quote(request):
    if request.method == "GET":
        form = CustomerForm()
        return render(request, 'request_quote.html', {'form': form})

    elif request.method == "POST":
        # request.FILES 추가(이미지)
        form = CustomerForm(request.POST) # ,request.FILES)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            phone = form.cleaned_data.get('phone')
            address = form.cleaned_data.get('address')
            now = timezone.now()

            # 새 참여자 등록
            save_customer = Customer(
                name    =name,
                phoen   =phone,
                address =address,
                create_at    =timezone.now()
            )
            # 트랜잭션 내에서 데이터 저장
            try:
                with transaction.atomic():
                    save_customer.save()
            except Exception as e:
                logger.error(f"에러 발생: {e}")  # 에러 기록  # 에러 기록
                messages.error(request, "방문 견적 신청 중 오류가 발생했습니다.") # 사용자에게 더 친절한 오류 메시지
                return render(request, 'request_quote.html', {'form': form}) # 오류 발생 시 폼을 다시 보여줌

            messages.success(request, "방문 견적이 신청되었습니다.")
            return redirect('request_complete', id=save_customer.id)

        else:
            # 폼이 유효하지 않은 경우 오류 메시지 표시
            error_message = form.errors.as_json()
            messages.error(request, "입력창에 모두 올바르게 입력했는지 확인해주세요.")
            return render(request, 'request_quote.html', {'form': form})

    return HttpResponse(status=405)  # Method Not Allowed

# 견적 신청 완료
def request_complete(request, id):
    # 전달받은 id를 기준으로 첫번째 참가자를 가져옵니다.
    customer = get_object_or_404(Customer, id=id)

    context = {
        'customer': customer,  # 기준 참가자 정보

    }
    return render(request, 'request_complete.html', context)
