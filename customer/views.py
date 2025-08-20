from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from customer.models import Customer
from contract.models import Contract
from django.db.models import Count

def customer_list(request):
    # 필터링 조건
    region_level1 = request.GET.get('region_level1', '')  # 광역시/도
    region_level2 = request.GET.get('region_level2', '')  # 시/군/구
    region_level3 = request.GET.get('region_level3', '')  # 읍/면/동
    q = request.GET.get('q', '')  # 고객 이름 또는 전화번호 검색

    # 고객 데이터 필터링
    customers = Customer.objects.all()

    if region_level1:
        customers = customers.filter(region_level1=region_level1)
    if region_level2:
        customers = customers.filter(region_level2=region_level2)
    if region_level3:
        customers = customers.filter(region_level3=region_level3)
    if q:
        customers = customers.filter(Q(name__icontains=q) | Q(phone__icontains=q))

    # 지역 필터링을 위한 선택지 추출
    region_level1_choices = Customer.objects.values_list('region_level1', flat=True).distinct()
    region_level2_choices = Customer.objects.values_list('region_level2', flat=True).distinct()
    region_level3_choices = Customer.objects.values_list('region_level3', flat=True).distinct()

    context = {
        'customers': customers,
        'region_level1_choices': region_level1_choices,
        'region_level2_choices': region_level2_choices,
        'region_level3_choices': region_level3_choices,
        'selected_region_level1': region_level1,
        'selected_region_level2': region_level2,
        'selected_region_level3': region_level3,
        'q': q
    }

    return render(request, 'customers.html', context)


# --- autocomplete view for 매장(업체) ---
def autocomplete(request):
    if 'term' in request.GET:
        qs = PlaceBoard.objects.filter(place__icontains=request.GET.get('term'))
        names = list()
        for place in qs:
            names.append({'label': place.place, 'value': place.id})
        return JsonResponse(names, safe=False)
    return JsonResponse([], safe=False)
