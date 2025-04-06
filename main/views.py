import datetime
import json
from math import radians, sin, cos, sqrt, atan2

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
# from main.models import Question, Post
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db import transaction
from main.forms import ParticipantForm
from main.models import Participant
from placeBoard.models import PlaceBoard
import logging
logger = logging.getLogger(__name__)

# 1-1. 갓파더위크 설명
def godfather_info(request):

    return render( request, 'godfather_info.html')

def event_map(request):
    try:
        # PlaceBoard 모델에서 필요한 데이터만 가져옴
        places_list = list(PlaceBoard.objects.values('id','place', 'address', 'latitude', 'longitude', 'area'))
        unique_areas = PlaceBoard.objects.values_list('area', flat=True).distinct()

        if not places_list:
            messages.warning(request, "매장 데이터가 없습니다.")
    except Exception as e:
        messages.error(request, f"데이터를 불러오는 중 문제가 발생했습니다: {str(e)}")
        places_list = []
        unique_areas = []

    context = {
        'NAVER_MAP_CLIENT_ID': settings.NAVER_MAP_CLIENT_ID,
        'places_json': json.dumps(places_list),
        'unique_areas': unique_areas,
    }

    return render(request, 'event_map.html', context)


def haversine(lat1, lon1, lat2, lon2):  # 거리 계산
    R = 6371.0  # 지구 반지름(km)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

# 3-A-1. 전체 업장 리스트 노출
def place_list(request):
    query = request.GET.get('q')
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')


    if query:
        # 검색어가 있는 경우
        place_list = PlaceBoard.objects.filter(place__icontains=query)
    else:
        # 검색어가 없는 경우
        place_list = PlaceBoard.objects.all().order_by('id')

        if lat and lng:
            try:
                user_lat = float(lat)
                user_lng = float(lng)

                # 위도와 경도 값이 없는 객체 제외
                place_list = place_list.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

                places_with_distance = []
                for place in place_list:
                    dist = haversine(user_lat, user_lng, place.latitude, place.longitude)
                    place.distance = dist  # 장소 객체에 거리 속성 추가
                    try:
                        places_with_distance.append(place)
                    except Exception as e:
                        print(f"Error appending place to list: {e}")

                # 거리 순으로 정렬
                places_with_distance.sort(key=lambda x: x.distance)
                place_list = places_with_distance

            except (ValueError, TypeError) as e:
                print(f"위치 정보 변환 오류: {e}")

    paginator = Paginator(place_list, 10)  # 기본 목록을 사용
    page = request.GET.get('page')
    places = paginator.get_page(page)

    # 현재 페이지 번호를 정수형으로 변환
    current_page = places.number

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
        'places': places,
        'page_numbers': page_numbers,
        'has_previous_group': start_page > 1,
        'has_next_group': end_page < total_pages,
        'previous_group_page': start_page - 1,
        'next_group_page': end_page + 1,
        'query_string': query_string,
    }

    return render(request, 'placeList.html', context)

#3-A-2. 업장 클릭 시, 업장 정보 노출
def place(request, place_id):
    place = get_object_or_404(PlaceBoard, pk=place_id)
    return render(request, 'place.html', {'place': place})

# 3-B-1. 개인 정보 제공 동의 페이지 노출 (팝업 or 페이지)
def event_check(request):

    return render( request, 'eventCheck.html')

# 3-B-2. 개인 정보 인력 (이름, 휴대폰 번호, 사진)
def events(request):
    if request.method == "GET":
        form = ParticipantForm()
        place_list = PlaceBoard.objects.all()
        return render(request, 'event.html', {'form': form, 'place_list': place_list})

    elif request.method == "POST":
        form = ParticipantForm(request.POST, request.FILES) # request.FILES 추가(이미지)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            num = form.cleaned_data.get('num')
            receipt_image = form.cleaned_data.get('receiptImage')
            place_id = form.cleaned_data.get('placeId')
            now = timezone.now()
            time_threshold = now - datetime.timedelta(hours=12)
            place_board = PlaceBoard.objects.get(id=place_id)

            dupl_place_time_check = Participant.objects.filter(
                Q(name=name) & Q(num=num) & Q(placeId=place_id) & Q(date__gte=time_threshold)
            ).exists()
            dupl_place_check = Participant.objects.filter(
                Q(name=name) & Q(num=num) & Q(placeId=place_id)
            ).exists()
            dupl_part_check = Participant.objects.filter(
                Q(name=name) & Q(num=num)
            ).exists()
            # 시간,장소, 참가자 중복
            if dupl_place_time_check:
                messages.error(request, "이미 등록되었습니다.")
                duplicate_check = Participant.objects.filter(
                    Q(name=name) & Q(num=num)
                )
                # 중복된 id 목록에서 첫 번째 id를 가져옵니다
                return redirect('stamp', id=duplicate_check.first().id)
            else:
                # 참가자 중복
                if dupl_part_check:
                    # 기존 참가자 중복이 아니라면 중복으로 변경
                    existing_participant = Participant.objects.filter(
                        Q(name=name) & Q(num=num) & Q(dupl=False)
                    ).first()
                    if existing_participant:
                        existing_participant.dupl = True
                        # 트랜잭션 내에서 데이터 저장
                        try:
                            with transaction.atomic():
                                existing_participant.save()
                        except Exception as e:
                            logger.error(f"에러 발생: {e}")  # 에러 기록  # 에러 기록
                            raise  # 예외 재발생 (상위 레벨에서 처리)


                # 새 참여자 등록
                new_participant = create_participant(name, num, place_id, receipt_image, dupl_part_check)
                # 업체 중복 참여자 및 참여자 수 등록
                update_place_board(place_board, dupl_place_check)

                messages.success(request, "참가자가 성공적으로 등록되었습니다.")
                return redirect('stamp', id=new_participant.id)

        else:
            # 폼이 유효하지 않은 경우 오류 메시지 표시
            error_message = form.errors.as_json()
            messages.error(request, "입력창에 모두 올바르게 입력했는지 확인해주세요.")
            place_list = PlaceBoard.objects.all()
            return render(request, 'event.html', {'form': form, 'place_list': place_list})

        place_list = PlaceBoard.objects.all()
        return render(request, 'event.html', {'form': form, 'place_list': place_list})

    return HttpResponse(status=405)  # Method Not Allowed

def new_participant(name, num, place_id ,receipt_image, dupl=False): #mail,
    save_participant = Participant(
        name=name,
        num=num,
        # mail=mail,
        receiptImage = receipt_image,
        placeId=place_id,
        date=timezone.now(),
        dupl=dupl,
    )
    # 트랜잭션 내에서 데이터 저장
    try:
        with transaction.atomic():
                save_participant.save()
    except Exception as e:
        logger.error(f"에러 발생: {e}")  # 에러 기록  # 에러 기록
        raise  # 예외 재발생 (상위 레벨에서 처리)

def create_participant(name, num, place_id, receipt_image, dupl):
    new_participant = Participant(
        name=name,
        num=num,
        placeId=place_id,
        receiptImage=receipt_image,
        dupl=dupl
    )
    # 트랜잭션 내에서 데이터 저장
    try:
        with transaction.atomic():
            new_participant.save()
            return new_participant
    except Exception as e:
        logger.error(f"에러 발생: {e}")  # 에러 기록  # 에러 기록
        raise  # 예외 재발생 (상위 레벨에서 처리)


def update_place_board(place_board, dupl):
    if dupl:
        place_board.duplPartNum += 1
        place_board.partNum += 1
    else:
        place_board.partNum += 1
    # 트랜잭션 내에서 데이터 저장
    try:
        with transaction.atomic():
            place_board.save()
    except Exception as e:
        logger.error(f"에러 발생: {e}")  # 에러 기록  # 에러 기록
        raise  # 예외 재발생 (상위 레벨에서 처리)



def autocomplete(request):
    if 'id' in request.GET:
        # placeId로 검색하는 로직 추가
        place_id = request.GET.get('id')
        qs = PlaceBoard.objects.filter(id=place_id)
        names = [{'label': place.place, 'value': place.id} for place in qs]
        return JsonResponse(names, safe=False)

    if 'term' in request.GET:
        qs = PlaceBoard.objects.filter(place__icontains=request.GET.get('term'))
        names = [{'label': place.place, 'value': place.id} for place in qs]
        return JsonResponse(names, safe=False)

    return JsonResponse([], safe=False)

# 4-1. 이벤트 참여 진행도 스템프 형식으로 노출 (경품 노출 예정)
def stamp(request, id):
    # 전달받은 id를 기준으로 첫번째 참가자를 가져옵니다.
    participant = get_object_or_404(Participant, id=id)

    # name과 num이 같은 모든 참가자 정보를 가져옵니다.
    duplicate_entries = Participant.objects.filter(
        Q(name=participant.name) & Q(num=participant.num)
    )

    # stamp_count는 중복 참가자 총 수 (0 ~ 6 사이, 6 초과는 6로 처리)
    participant_count = duplicate_entries.count()
    stamp_count = participant_count if participant_count <= 6 else 6

    # 중복 참가자들의 정보를 담을 리스트를 만듭니다.
    # 각 항목은 참가자의 receiptImage, date, 그리고 해당 참가자의 placeId를 통해 PlaceBoard의 place 정보를 함께 담습니다.
    duplicate_info = []
    for dup in duplicate_entries:
        # 각 참가자가 가진 placeId를 통해 PlaceBoard 정보 조회
        # (ForeignKey가 아니라 단순 id 필드라면 get_object_or_404 사용)
        place_board = get_object_or_404(PlaceBoard, id=dup.placeId)

        duplicate_info.append({
            'participant_id': dup.id,
            'receiptImage': dup.receiptImage,  # 실제 이미지 URL이나 이미지 객체
            'date': dup.date,
            'place': place_board.place,        # PlaceBoard의 장소 정보, 예를 들어 'place' 필드
            'placeId': dup.placeId,
        })

    context = {
        'participant': participant,  # 기준 참가자 정보
        'duplicates': duplicate_info,  # 중복된 각 참가자의 상세 정보 리스트
        'stamp_count': stamp_count,    # 0 ~ 6 사이의 참가 수로 스탬프 표시에 사용
    }
    return render(request, 'stamp.html', context)
