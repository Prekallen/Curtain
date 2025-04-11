from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from main.models import Customer
from contract.models import Contract
from django.db.models import Count

def customer_list(request):
    # 전체 참여자 queryset
    queryset = Customer.objects.all()
    '''id = models.AutoField(primary_key=True, verbose_name='기본키')
    name = models.CharField(max_length=100, verbose_name='고객명')
    phone = models.CharField(max_length=20,verbose_name='전화번호')
    address = models.CharField(max_length=200, verbose_name='주소')
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='요청일')'''
    # GET 파라미터 읽기
    complete = request.GET.get("complete", "false")             # "true"이면  시공 까지 완료 필터링
    search_field = request.GET.get("search_field", "name")      # "name", "phone" 또는 "both"
    search = request.GET.get("q", "")
    created_by = request.GET.get("created_by", "null")          # 계약일
    const_date = request.GET.get("const_date", "null")          # 시공일



    # 시공 완료 필터
    if complete == "true":
        queryset = queryset.filter(dupl=True)

    # 검색 필터링
    if search_field == "name" and search:
        queryset = queryset.filter(name__icontains=search)
    elif search_field == "phone" and search:
        queryset = queryset.filter(num__icontains=search)
    elif search_field == "both":
        # 'both'인 경우, URL에 별도로 전달된 name과 num 파라미터로 필터링
        search_name = request.GET.get("name", "")
        search_num = request.GET.get("phone", "")
        # 이름과 전화번호 모두 조건에 부합하는 항목을 반환 (여기서는 icontains를 사용합니다)
        queryset = queryset.filter(name__icontains=search_name, phone__icontains=search_num)
    elif search and not search_field:
        # 기본 OR 검색 (옵션)
        queryset = queryset.filter(Q(name__icontains=search) | Q(phone__icontains=search))

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
