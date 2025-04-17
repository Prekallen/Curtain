import requests
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction


from manager.models import Manager
from .forms import ConstructionForm, ConstItemFormSet, ItemImageFormSet
from .models import Construction, ConstItem, ItemImage
import logging

logger = logging.getLogger(__name__)

# session 검사
def session_check(request):
    if not request.session.get('user'):
        return redirect('/manager/login/')
    # 세션에 'user' 키를 불러올 수 없으면, 로그인하지 않은 사용자이므로 로그인 페이지로 리다이렉트 한다.

# 시공 목록
def construction_list(request):
    search_type = request.GET.get('search_type', 'address')
    query = request.GET.get('q')

    all_consts = Construction.objects.all().order_by('-id')

    if query:
        if search_type == 'address':
            all_consts = all_consts.filter(address__icontains=query)
        elif search_type == 'housing_type':
            all_consts = all_consts.filter(housing_type__icontains=query)
        elif search_type == 'item_type':
            all_consts = all_consts.filter(item_type__icontains=query)

    page = int(request.GET.get('p', 1))
    paginator = Paginator(all_consts, 10)
    consts = paginator.get_page(page)

    current_page = consts.number
    total_pages = paginator.num_pages
    page_group = (current_page - 1) // 10
    start_page = page_group * 10 + 1
    end_page = min(start_page + 9, total_pages)
    page_numbers = range(start_page, end_page + 1)

    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_params.pop('p', None)
    query_string = query_params.urlencode()

    context = {
        'admin_page': True,
        'consts': consts,
        'page_numbers': page_numbers,
        'has_previous_group': start_page > 1,
        'has_next_group': end_page < total_pages,
        'previous_group_page': start_page - 1,
        'next_group_page': end_page + 1,
        'query_string': query_string,
        'search_type': search_type,
        'query': query,
    }
    return render(request, 'construction_list.html', context)

# 시공 등록
def register_construction(request):
    session_check(request)

    if request.method == 'POST':
        form = ConstructionForm(request.POST)
        const_item_formset = ConstItemFormSet(request.POST, request.FILES, prefix='items')

        image_formsets = []
        image_formsets_valid = True
        total_item_forms = int(request.POST.get('items-TOTAL_FORMS', 0))

        for i in range(total_item_forms):
            image_formset = ItemImageFormSet(
                request.POST,
                request.FILES,
                prefix=f'images-{i}'
            )
            image_formsets.append(image_formset)
            if not image_formset.is_valid():
                image_formsets_valid = False

        if form.is_valid() and const_item_formset.is_valid() and image_formsets_valid:
            with transaction.atomic():
                user_id = request.session.get('user')
                member = Manager.objects.get(pk=user_id)
                construction = form.save(commit=False)
                construction.manager = member
                construction.writer = member.name
                _save_board_with_lat_long(construction, construction.address)
                construction.save()

                const_items = const_item_formset.save(commit=False)
                for idx, const_item in enumerate(const_items):
                    const_item.construction = construction
                    const_item.save()

                    image_formset = image_formsets[idx]
                    images = image_formset.save(commit=False)
                    for img in images:
                        img.item = const_item
                        img.save()

            return redirect('const/list')
    else:
        form = ConstructionForm()
        const_item_formset = ConstItemFormSet(queryset=ConstItem.objects.none(), prefix='items')
        image_formsets = [ItemImageFormSet(queryset=ItemImage.objects.none(), prefix=f'images-{i}')
                          for i in range(len(const_item_formset.forms))]

    paired_forms = zip(const_item_formset.forms, image_formsets)
    return render(request, 'register_construction.html', {
        'form': form,
        'const_item_formset': const_item_formset,
        'image_formsets': image_formsets,
        'paired_forms': paired_forms,
    })


 # 시공 상세
def construction_detail(request, pk):
    # pk 에 해당하는 글을 가지고 올 수 있게 된다.
    context = {
        'admin_page': True,  # 관리자 페이지일 경우 True로 설정
    }
    try:
        const = Construction.objects.get(pk=pk)
        context['const'] = const
    except Construction.DoesNotExist:
        raise Http404('시공 게시물을 찾을 수 없습니다')

    instance = get_object_or_404(Construction, pk=pk)
    # 게시물의 내용을 찾을 수 없을 때 내는 오류 message.
    # 리스트 페이지의 모든 게시물을 가져오고 페이지네이터로 나눕니다.
    all_posts = Construction.objects.all().order_by('-id')
    paginator = Paginator(all_posts, 10) # 페이지당 10개의 게시물
    # 수정된 게시물이 속한 페이지를 찾습니다.
    page_number = None

    for page in paginator.page_range:
        if instance in paginator.page(page).object_list:
            page_number = page

            break
    if page_number:
        context['page_number'] = page_number

    return render(request, 'construction_detail.html', context)

def construction_update(request, pk):
    session_check(request)
    instance = get_object_or_404(Construction, pk=pk)

    if request.method == "POST":
        form = ConstructionForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            construction = form.save(commit=False)
            user_id = request.session.get('user')
            manager = Manager.objects.get(pk=user_id)
            construction.manager = manager
            construction.writer = manager.name
            _save_board_with_lat_long(construction, construction.address)

            try:
                with transaction.atomic():
                    construction.save()
                messages.success(request, "시공 정보가 성공적으로 수정되었습니다.")
                return redirect('construction_list')
            except Exception as e:
                logger.error(f"시공 정보 수정 중 오류 발생: {e}")
                messages.error(request, f"시공 정보 수정 중 오류가 발생했습니다: {e}")
                return redirect('construction_update', pk=pk)
        else:
            logger.error(f"ConstructionForm 수정 오류: {form.errors}")
            messages.error(request, "입력하신 정보가 유효하지 않습니다. 다시 확인해주세요.")

    else:
        form = ConstructionForm(instance=instance)

    return render(request, 'construction_update.html', {'form':form,'construction':instance,'admin_page':True})

def construction_delete(request, pk):
    session_check(request)
    construction = get_object_or_404(Construction, pk=pk)

    if request.method == "POST":
        try:
            with transaction.atomic():
                # 관련된 ConstItem 및 ItemImage 먼저 삭제 (on_delete=CASCADE 설정되어 있다면 생략 가능)
                ConstItem.objects.filter(const_id=construction).delete()
                construction.delete()
            messages.success(request, f"시공 ID {pk}가 성공적으로 삭제되었습니다.")
            return redirect('construction_list')
        except Exception as e:
            messages.error(request, f"시공 삭제 중 오류가 발생했습니다: {e}")
            return redirect('construction_detail', pk=pk)  # 또는 목록 페이지로 리다이렉트
    else:
        # POST 요청이 아니면 삭제를 수행하지 않고 상세 페이지로 리다이렉트하거나 오류 메시지를 표시
        messages.error(request, "잘못된 접근입니다.")
        return redirect('construction_detail', pk=pk)

def bulk_delete_construction(request):
    session_check(request)
    if request.method == "POST":
        construction_ids = request.POST.getlist('construction_ids')
        if construction_ids:
            try:
                with transaction.atomic():
                    # on_delete=models.CASCADE 설정에 따라 ConstItem과 ItemImage도 함께 삭제됩니다.
                    Construction.objects.filter(id__in=construction_ids).delete()
                messages.success(request, f"{len(construction_ids)}개의 시공 정보를 성공적으로 삭제했습니다.")
            except Exception as e:
                messages.error(request, f"시공 정보 삭제 중 오류가 발생했습니다: {e}")
        else:
            messages.warning(request, "삭제할 시공 정보를 선택해주세요.")
    return redirect('construction_list')

def upload_image_view(request):
    if request.method == 'POST' and request.FILES.get('placeImage'):
        # 세션에서 사용자 ID를 가져옵니다.
        user_id = request.session.get('user')

        # 사용자 정보가 세션에 존재하는지 확인합니다.
        if not user_id:
            return JsonResponse({'error': '사용자가 로그인되지 않았습니다.'}, status=400)

        try:
            member = Manager.objects.get(pk=user_id)
        except Manager.DoesNotExist:
            return JsonResponse({'error': '사용자를 찾을 수 없습니다.'}, status=400)

        image = request.FILES['placeImage']
        instance = Construction.objects.create(
            placeImage=image,
            writer=member  # 작성자 정보를 추가합니다.
        )
        return JsonResponse({'url': instance.placeImage.url})
    return JsonResponse({'error': '파일 업로드 실패'}, status=400)

# 네이버 맵 API를 사용하여 위도와 경도 검색
def _save_board_with_lat_long(board, address):
    latitude, longitude = get_lat_long(address)
    board.latitude = latitude
    board.longitude = longitude
    board.save()

# 네이버맵 API 위도 경도 가져오기
def get_lat_long(address):
    client_id = 'YOUR_NAVER_MAP_CLIENT_ID'
    client_secret = 'YOUR_NAVER_MAP_CLIENT_SECRET'
    url = f"https://openapi.naver.com/v1/search/local.json?query={address}"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            item = data['items'][0]
            return item['mapx'], item['mapy']  # 경도, 위도 값
    return None, None