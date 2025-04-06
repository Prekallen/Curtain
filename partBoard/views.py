from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from main.models import Participant
from placeBoard.models import PlaceBoard
from django.db.models import Count

def part_list(request):
    # 전체 참여자 queryset
    queryset = Participant.objects.all()

    # GET 파라미터 읽기
    region = request.GET.get("region", "전체 지역")
    store = request.GET.get("store", "all")        # 매장은 PlaceBoard의 id 값 (문자열 "all"이면 전체)
    dupl = request.GET.get("dupl", "false")          # "true"이면 중복 참여만 필터링
    search_field = request.GET.get("search_field", "name")    # "name", "num" 또는 "both"
    search = request.GET.get("q", "")
    participation_count = request.GET.get('participation_count', '')

    # 업체(매장) 필터: store 값이 "all"이 아니라면 해당 업체 id로 필터링
    if store != "all":
        try:
            queryset = queryset.filter(placeId=int(store))
        except ValueError:
            pass

    # 지역 필터: "전체 지역"이 아닐 경우 해당 지역의 PlaceBoard id 목록으로 필터링
    if region != "전체 지역":
        place_ids = PlaceBoard.objects.filter(area=region).values_list("id", flat=True)
        queryset = queryset.filter(placeId__in=place_ids)

    # 중복 참여 필터: dupl가 "true"이면
    if dupl == "true":
        queryset = queryset.filter(dupl=True)

    # 검색 필터링
    if search_field == "name" and search:
        queryset = queryset.filter(name__icontains=search)
    elif search_field == "num" and search:
        queryset = queryset.filter(num__icontains=search)
    elif search_field == "both":
        # 'both'인 경우, URL에 별도로 전달된 name과 num 파라미터로 필터링
        search_name = request.GET.get("name", "")
        search_num = request.GET.get("num", "")
        # 이름과 전화번호 모두 조건에 부합하는 항목을 반환 (여기서는 icontains를 사용합니다)
        queryset = queryset.filter(name__icontains=search_name, num__icontains=search_num)
    elif search and not search_field:
        # 기본 OR 검색 (옵션)
        queryset = queryset.filter(Q(name__icontains=search) | Q(num__icontains=search))

    # 참여 횟수 필터링
    if participation_count:
        participation_count = int(participation_count)

        # 그룹화: name과 num이 동일한 데이터를 그룹화
        grouped_participants  = queryset.values('name', 'num').annotate(count=Count('id'))  # 각 그룹의 참여 횟수 계산

        # 참여 횟수 조건에 따라 그룹 필터링
        if participation_count >= 5:
            grouped_participants = grouped_participants .filter(count__gte=5)
        else:
            grouped_participants  = grouped_participants .filter(count=participation_count)

        # 필터링된 데이터에서 name과 num을 기반으로 다시 queryset 필터링
        queryset = queryset.filter(
            name__in=[p['name'] for p in grouped_participants],
            num__in=[p['num'] for p in grouped_participants]
        )

    if not participation_count:
        # participation_count가 없을 때 기본 필터링 상태 유지
        queryset = queryset  # 기존 필터링 유지, 초기화하지 않음

    # 드롭다운/자동완성을 위한 업체(매장) 목록 (autocomplete 용)
    store_list = PlaceBoard.objects.all().order_by("id")
    # 지역 목록은 중복 없이 가져오기
    region_list = PlaceBoard.objects.values_list("area", flat=True).distinct()

    context = {
        'admin_page': True,  # 관리자 페이지일 경우 True로 설정
        "participants": queryset.order_by("-date"),
        "store_list": store_list,
        "region_list": region_list,
        "selected_store": store,
        "selected_region": region,
        "dupl": dupl,
        "q": search,
        "search_field": search_field,
        'participation_count': str(participation_count),
    }
    return render(request, "partList.html", context)


# --- autocomplete view for 매장(업체) ---
def autocomplete(request):
    if 'term' in request.GET:
        qs = PlaceBoard.objects.filter(place__icontains=request.GET.get('term'))
        names = list()
        for place in qs:
            names.append({'label': place.place, 'value': place.id})
        return JsonResponse(names, safe=False)
    return JsonResponse([], safe=False)
