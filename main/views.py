import json
from math import radians, sin, cos, sqrt, atan2

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from main.forms import RegionLevel1Form, RegionLevel2Form, RegionLevel3Form, DetailedAddressForm, ContactInfoForm
from customer.models import Customer
from construction.models import Construction, ConstItem, ItemImage
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
        # 검색어가 있는 경우 (모델 필드명 'place'를 'address'로 변경)
        const_list = Construction.objects.filter(address__icontains=query)
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
                    const.distance = dist  # 시공 객체에 거리 속성 추가
                    try:
                        consts_with_distance.append(const)
                    except Exception as e:
                        print(f"Error appending construction to list: {e}")

                # 거리 순으로 정렬
                consts_with_distance.sort(key=lambda x: x.distance)
                const_list = consts_with_distance

            except (ValueError, TypeError) as e:
                print(f"위치 정보 변환 오류: {e}")

    paginator = Paginator(const_list, 10)  # 기본 목록을 사용
    page = request.GET.get('page')
    constructions = paginator.get_page(page)

    # 현재 페이지 번호를 정수형으로 변환
    current_page = constructions.number
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
        'constructions': constructions,
        'page_numbers': page_numbers,
        'has_previous_group': start_page > 1,
        'has_next_group': end_page < total_pages,
        'previous_group_page': start_page - 1,
        'next_group_page': end_page + 1,
        'query_string': query_string,
    }

    return render(request, 'const_list.html', context)

# 시공 클릭 시, 시공 정보 & 사진 (팝업으로 제공)
def const_detail(request, construction_id):
    construction = get_object_or_404(Construction, pk=construction_id)
    const_items = ConstItem.objects.filter(const_id=construction)
    item_images = {}
    for item in const_items:
        images = ItemImage.objects.filter(item_id=item)
        item_images[item.id] = images

    context = {
        'construction': construction,
        'const_items': const_items,
        'item_images': item_images,
    }
    return render(request, 'construction_detail_popup.html', context) # 팝업 내용을 위한 템플릿

# 주소 받기
def get_regions(request):
    parent = request.GET.get("parent")  # 선택한 상위 지역
    level = request.GET.get("level")  # 현재 요청한 레벨 (level1, level2 등)

    # 예제 데이터 (실제로는 DB 또는 다른 소스에서 불러옴)
    data = {
        "level1": ["서울특별시", "부산광역시", "대구광역시"],
        "서울특별시": ["종로구", "중구", "강남구"],
        "종로구": ["사직동", "부암동", "청운효자동"],
    }

    # level1 선택시 하위 지역 리턴
    results = data.get(parent, []) if level != "level1" else data["level1"]

    return JsonResponse({"regions": results})

# 개인 정보 제공 동의 페이지 노출 (팝업 or 페이지)
def personal_info_check(request):

    return render( request, 'personal_info_check.html')

# 견적 신청 (이름, 휴대폰 번호, 주소)
def request_quote_flow(request):
    if request.method == 'GET':
        region_level1_form = RegionLevel1Form()
        return render(request, 'request_quote_flow.html', {'region_level1_form': region_level1_form})
    return redirect('request_quote_flow_step1')

def get_region_level2(request):
    region_level1 = request.GET.get('region_level1')
    if region_level1:
        regions = list(Customer.objects.filter(region_level1=region_level1).values_list('region_level2', flat=True).distinct().order_by('region_level2'))
        return JsonResponse({'regions': regions})
    return JsonResponse({'regions': []})

def get_region_level3(request):
    region_level1 = request.GET.get('region_level1')
    region_level2 = request.GET.get('region_level2')
    if region_level1 and region_level2:
        regions = list(Customer.objects.filter(region_level1=region_level1, region_level2=region_level2).values_list('region_level3', flat=True).distinct().order_by('region_level3'))
        return JsonResponse({'regions': regions})
    return JsonResponse({'regions': []})

def request_quote_flow_step1(request):
    if request.method == 'POST':
        region_level1_form = RegionLevel1Form(request.POST)
        if region_level1_form.is_valid():
            request.session['region_level1'] = region_level1_form.cleaned_data['region_level1']
            region_level2_form = RegionLevel2Form()
            return render(request, 'request_quote_flow_step2.html', {'region_level2_form': region_level2_form})
        else:
            return render(request, 'request_quote_flow.html', {'region_level1_form': region_level1_form, 'error': '광역시/도를 선택해주세요.'})
    else:
        return redirect('request_quote_flow')

def request_quote_flow_step2(request):
    if request.method == 'POST':
        region_level2_form = RegionLevel2Form(request.POST)
        if region_level2_form.is_valid():
            request.session['region_level2'] = region_level2_form.cleaned_data['region_level2']
            region_level3_form = RegionLevel3Form()
            return render(request, 'request_quote_flow_step3.html', {'region_level3_form': region_level3_form})
        else:
            return render(request, 'request_quote_flow_step2.html', {'region_level2_form': region_level2_form, 'error': '시/군/구를 선택해주세요.'})
    else:
        return redirect('request_quote_flow')

def request_quote_flow_step3(request):
    if request.method == 'POST':
        region_level3_form = RegionLevel3Form(request.POST)
        if region_level3_form.is_valid():
            request.session['region_level3'] = region_level3_form.cleaned_data['region_level3']
            detailed_address_form = DetailedAddressForm()
            return render(request, 'request_quote_flow_step4.html', {'detailed_address_form': detailed_address_form})
        else:
            return render(request, 'request_quote_flow_step3.html', {'region_level3_form': region_level3_form, 'error': '읍/면/동을 선택해주세요.'})
    else:
        return redirect('request_quote_flow')

def request_quote_flow_step4(request):
    if request.method == 'POST':
        detailed_address_form = DetailedAddressForm(request.POST)
        if detailed_address_form.is_valid():
            request.session['detailed_address'] = detailed_address_form.cleaned_data['detailed_address']
            contact_info_form = ContactInfoForm()
            return render(request, 'request_contact_info.html', {'contact_info_form': contact_info_form})
        else:
            return render(request, 'request_quote_flow_step4.html', {'detailed_address_form': detailed_address_form, 'error': '상세 주소를 입력해주세요.'})
    else:
        return redirect('request_quote_flow')

def submit_request_quote(request):
    if request.method == 'POST':
        contact_info_form = ContactInfoForm(request.POST)
        if contact_info_form.is_valid():
            if contact_info_form.cleaned_data['agree_personal_info']:
                name = contact_info_form.cleaned_data['name']
                phone = contact_info_form.cleaned_data['phone']
                region_level1 = request.session.get('region_level1')
                region_level2 = request.session.get('region_level2')
                region_level3 = request.session.get('region_level3')
                detailed_address = request.session.get('detailed_address')

                try:
                    with transaction.atomic():
                        Customer.objects.create(
                            name=name,
                            phone=phone,
                            region_level1=region_level1,
                            region_level2=region_level2,
                            region_level3=region_level3,
                            detailed_address=detailed_address,
                            create_at=timezone.now()
                        )
                    messages.success(request, "방문 견적이 신청되었습니다.")
                    # 세션 정보 초기화 (선택 사항)
                    for key in ['region_level1', 'region_level2', 'region_level3', 'detailed_address']:
                        if key in request.session:
                            del request.session[key]
                    return redirect('request_complete') # 완료 페이지로 리다이렉트 (별도 구현 필요)

                except Exception as e:
                    logger.error(f"견적 신청 저장 오류: {e}")
                    messages.error(request, "견적 신청 중 오류가 발생했습니다.")
                    return render(request, 'request_contact_info.html', {'contact_info_form': contact_info_form})
            else:
                messages.error(request, "개인정보 제공에 동의해야 신청이 가능합니다.")
                return render(request, 'request_contact_info.html', {'contact_info_form': contact_info_form})
        else:
            messages.error(request, "입력하신 정보를 확인해주세요.")
            return render(request, 'request_contact_info.html', {'contact_info_form': contact_info_form})
    else:
        return redirect('request_quote_flow')

def personal_info_policy(request):
    return render(request, 'personal_info_policy.html') # 개인정보보호법 안내문 템플릿

# 견적 신청 완료
def request_complete(request, id):
    # 전달받은 id를 기준으로 첫번째 참가자를 가져옵니다.
    customer = get_object_or_404(Customer, id=id)

    context = {
        'customer': customer,  # 기준 참가자 정보

    }
    return render(request, 'request_complete.html', context)
