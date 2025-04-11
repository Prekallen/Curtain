import requests
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction


from manager.models import Manager
from .forms import ConstructionForm, ConstItemFormSet, ItemImageFormSet
from .models import Construction
import logging

logger = logging.getLogger(__name__)

# session 검사
def session_check(request):
    if not request.session.get('user'):
        return redirect('/manager/login/')
    # 세션에 'user' 키를 불러올 수 없으면, 로그인하지 않은 사용자이므로 로그인 페이지로 리다이렉트 한다.

# 시공 목록
def construction_list(request):
    search_type = request.GET.get('search_type', 'place')
    query = request.GET.get('q')

    if query:
        if search_type == 'address':
            all_boards = Construction.objects.filter(place__icontains=query)
        elif search_type == 'housing_type':
            all_boards = Construction.objects.filter(area__icontains=query)
    else:
        all_boards = Construction.objects.all().order_by('-id')

    # 변수명을 all_boards 로 바꿔주었다.
    page        = int(request.GET.get('p', 1))
    # p라는 값으로 받을거고, 없으면 첫번째 페이지로
    paginator   = Paginator(all_boards, 10)
    # Paginator 함수를 적용하는데, 첫번째 인자는 위에 변수인 전체 오브젝트, 2번째 인자는
    # 한 페이지당 오브젝트 10개씩 나오게 설정
    boards      = paginator.get_page(page)

    # 현재 페이지 번호를 정수형으로 변환
    current_page = boards.number

    # 총 페이지 수
    total_pages = paginator.num_pages

    # 페이지 그룹 계산
    page_group = (current_page - 1) // 10
    start_page = page_group * 10 + 1
    end_page = min(start_page + 9, total_pages)
    page_numbers = range(start_page, end_page + 1)

    # 기존의 GET 파라미터에서 'page, p'를 제거하여 query_string 생성
    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_params.pop('p', None)
    query_string = query_params.urlencode()

    context = {
        'admin_page': True,  # 관리자 페이지일 경우 True로 설정
        'boards': boards,
        'page_numbers': page_numbers,
        'has_previous_group': start_page > 1,
        'has_next_group': end_page < total_pages,
        'previous_group_page': start_page - 1,
        'next_group_page': end_page + 1,
        'query_string': query_string,
    }
    return render(request, 'construction_list.html', context)

# 시공 등록
def register_construction(request):
    session_check(request)

    if request.method == "POST":
        construction_form = ConstructionForm(request.POST, request.FILES)
        const_item_formset = ConstItemFormSet(prefix='const_items')
        item_image_formset = ItemImageFormSet(prefix='item_images')

        if construction_form.is_valid() and const_item_formset.is_valid() and item_image_formset.is_valid():
            # form의 모든 validators 호출 유효성 검증 수행
            user_id = request.session.get('user')
            member = Manager.objects.get(pk=user_id)

            construction = construction_form.save(commit=False)  # 폼 데이터를 임시 저장
            construction.manager = member.id
            construction.writer = member.name
            _save_board_with_lat_long(construction, construction.address)

            # 트랜잭션 내에서 데이터 저장
            try:
                with transaction.atomic():
                    construction.save()

                const_items = const_item_formset.save(commit=False)
                for item in const_items:
                    item.const_id = construction
                    item.save()

                for item_form in const_item_formset:
                    if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE'):
                        const_item = item_form.save()
                        image_formset = ItemImageFormSet(request.POST, request.FILES, prefix=f'item_images-{const_item_formset.forms.index(item_form)}')
                        if image_formset.is_valid():
                            images = image_formset.save(commit=False)
                            for image in images:
                                image.item_id = const_item
                                image.save()
                        else:
                            logger.error(f"ItemImageFormSet 오류: {image_formset.errors}")

            return redirect('/board/list/?p=1')
        else:
            logger.error(f"ConstructionForm 오류: {construction_form.errors}")
            logger.error(f"ConstItemFormSet 오류: {const_item_formset.errors}")
            logger.error(f"ItemImageFormSet 오류: {item_image_formset.errors}")

    context = {
        'admin_page': True,
        'form': construction_form,
        'const_item_formset': const_item_formset,
        'item_image_formset': item_image_formset,
    }
    return render(request, 'register_construction.html', context)

 # 시공 상세
def construction_detail(request, pk):
    # pk 에 해당하는 글을 가지고 올 수 있게 된다.
    context = {
        'admin_page': True,  # 관리자 페이지일 경우 True로 설정
    }
    try:
        board = Construction.objects.get(pk=pk)
        context['board'] = board
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

def board_update(request, pk):
    session_check(request)
    instance = get_object_or_404(Construction, pk=pk)
    try:
        pre_board = Construction.objects.get(pk=pk)
    except Construction.DoesNotExist:
        raise Http404('게시글을 찾을 수 없습니다')

    if request.method == "POST":
        form = ConstructionForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            board = form.save(commit=False)
            user_id = request.session.get('user')
            manager = Manager.objects.get(pk=user_id)
            board.manager = user_id
            board.writer = manager.name

            # 트랜잭션 내에서 데이터 저장
            try:
                with transaction.atomic():
                    _save_board_with_lat_long(board, board.address)
            except Exception as e:
                logger.error(f"에러 발생: {e}")
                raise

            # 리스트 페이지의 모든 게시물을 가져오고 페이지네이터로 나눕니다.
            all_posts = Construction.objects.all().order_by('-id')
            paginator = Paginator(all_posts, 10)  # 페이지당 10개의 게시물
            page_number = None
            for page in paginator.page_range:
                if instance in paginator.page(page).object_list:
                    page_number = page
                    break
            if page_number:
                return redirect(f'/construction/list/?p={page_number}')
        else:
            # 폼 오류 처리
            print('form_error : ' + str(form.errors))  # 폼의 오류 메시지 출력

    else:
        form = ConstructionForm(instance=instance)

    return render(request, 'construction_update.html', {'form':form,'board':pre_board,'admin_page':True})

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