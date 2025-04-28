import os, io
import logging
import requests
from pillow_heif import register_heif_opener
from PIL import Image

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import JsonResponse, Http404, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST


from manager.models import Manager
from .forms import (
    ConstructionForm,
    RegisterConstItemFormSet,
    UpdateConstItemFormSet,
    ItemImageFormSet,
    UpdateItemImageFormSet,
    get_item_image_formset,
)
from .models import Construction, ConstItem, ItemImage


logger = logging.getLogger(__name__)

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
        'manager_page': True,
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
@login_required(login_url='/manager/login/')
def register_construction(request):
    if request.method == 'POST':
        form = ConstructionForm(request.POST)
        const_item_formset = RegisterConstItemFormSet(request.POST, request.FILES, prefix='items')
        image_formsets = []
        image_formsets_valid = True
        total_item_forms = int(request.POST.get('items-TOTAL_FORMS', 0))
        ItemImageFormSet = get_item_image_formset(is_update=False)

        # 각 ConstItem에 대응되는 이미지 FormSet 생성
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
            try:
                with transaction.atomic():
                    member = request.user
                    construction = form.save(commit=False)
                    construction.manager = member
                    construction.writer = member.name
                    _save_board_with_lat_long(construction, construction.address)
                    construction.save()

                    const_items = const_item_formset.save(commit=False)

                    for idx, const_item in enumerate(const_items):
                        const_item.const_id = construction
                        const_item.save()

                        image_formset = image_formsets[idx]
                        images = image_formset.save(commit=False)

                        for img in images:
                            img.item_id = const_item
                            img.save()

                        # 삭제된 이미지 처리
                        for obj in image_formset.deleted_objects:
                            obj.delete()

                    const_item_formset.save_m2m()  # if using m2m fields

                return redirect('/const/list')
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                messages.error(request, f"저장 중 예외 발생: {e}")
                return redirect('/const/register')
    else:
        form = ConstructionForm()
        const_item_formset = RegisterConstItemFormSet(queryset=ConstItem.objects.none(), prefix='items')
        ItemImageFormSet = get_item_image_formset(is_update=False)
        image_formsets = [
            ItemImageFormSet(queryset=ItemImage.objects.none(), prefix=f'images-{i}')
            for i in range(len(const_item_formset.forms))
        ]

    paired_forms = list(zip(const_item_formset.forms, image_formsets))

    return render(request, 'register_construction.html', {
        'form': form,
        'const_item_formset': const_item_formset,
        'image_formsets': image_formsets,
        'paired_forms': paired_forms,
        'manager_page': True,
    })

@login_required(login_url='/manager/login/')
def construction_update(request, pk):
    instance = get_object_or_404(Construction, pk=pk)
    ItemImageFormSet = get_item_image_formset(is_update=True)

    if request.method == "POST":
        construction_form = ConstructionForm(request.POST, request.FILES, instance=instance)
        const_item_formset = UpdateConstItemFormSet(request.POST, request.FILES, instance=instance)

        # 이미지 Formset 연결
        attach_image_formsets(ItemImageFormSet, const_item_formset, request)

        # 폼 유효성 검사
        construction_valid = construction_form.is_valid()
        items_valid = const_item_formset.is_valid()

        # 삭제된 항목 무시
        if construction_valid and items_valid:
            try:
                with transaction.atomic():
                    # 부모 구성 저장
                    construction = construction_form.save(commit=False)
                    construction.manager = request.user
                    construction.writer = request.user.name
                    _save_board_with_lat_long(construction, construction.address)
                    construction.save()

                    # 자식 폼셋에서 삭제된 항목 삭제
                    for form in const_item_formset:
                        if form.cleaned_data.get('DELETE') is True:
                            if form.instance.pk:
                                # 연결된 이미지도 삭제할 경우 처리 필요
                                form.instance.delete()
                        else:
                            # 삭제되지 않은 경우 저장
                            const_item = form.save(commit=False)
                            const_item.construction = construction
                            const_item.save()

                    # 이미지 폼셋 처리
                    for item_form in const_item_formset:
                        if hasattr(item_form, 'image_formset') and item_form.image_formset.is_valid():
                            item_form.image_formset.save()

                    messages.success(request, "시공 정보가 성공적으로 수정되었습니다.")
                    return redirect("construction_list")
            except Exception as e:
                messages.error(request, f"시공 정보 저장 중 오류가 발생하였습니다: {e}")
        else:
            messages.error(request, "입력한 정보에 오류가 있습니다. 다시 확인해주세요.")

    else:
        construction_form = ConstructionForm(instance=instance)
        const_item_formset = UpdateConstItemFormSet(instance=instance)
        attach_image_formsets(ItemImageFormSet, const_item_formset, request)

    return render(request, 'construction_update.html', {
        'construction_form': construction_form,
        'const_item_formset': const_item_formset,
        'construction': instance,
        'manager_page': True,
    })

def attach_image_formsets(ItemImageFormSet, const_item_formset, request):
    """
    ConstItemForm에 연결된 이미지 Formset을 동적으로 연결
    """
    for form in const_item_formset.forms:
        if form.cleaned_data.get('DELETE', False):  # 삭제된 폼이라면 건너뛴다
            continue

        if form.instance.pk:  # 이미 저장된 ConstItem만 처리
            form.image_formset = ItemImageFormSet(
                data=request.POST or None,
                files=request.FILES or None,
                instance=form.instance
            )
        else:
            form.image_formset = None  # 새로 생성된 경우에는 비어 있는 FormSet 처리

def validate_image_formsets(const_item_formset):
    """
    ConstItemForm에 연결된 이미지 Formset 유효성 검사
    """
    for form in const_item_formset.forms:
        # 삭제되지 않았다면 검증 수행
        if hasattr(form, 'image_formset') and form.image_formset:
            image_formset = form.image_formset

            # 이미지 폼셋 자체의 유효성 검사
            if not image_formset.is_valid():
                return False

            # 최소 1개 이미지 존재 유효성 검사
            total_images = [
                frm for frm in image_formset.forms
                if frm.cleaned_data and not frm.cleaned_data.get('DELETE', False)
            ]
            if len(total_images) < 1:
                raise ValidationError("각 품목에는 최소 하나 이상의 이미지를 등록해야 합니다.")

    return True

def save_const_items(const_item_formset, construction):
    """
    ConstItem 저장 로직
    """
    const_items = const_item_formset.save(commit=False)
    for const_item in const_items:
        const_item.construction = construction
        const_item.save()
    const_item_formset.save_m2m()

def save_image_formsets(const_item_formset):
    """
    ConstItem에 연결된 이미지 폼셋 저장
    """
    for form in const_item_formset.forms:
        if hasattr(form, 'image_formset') and form.image_formset:
            image_formset = form.image_formset
            if image_formset.is_valid():
                image_formset.save()

@login_required
@require_POST
def delete_item_image(request):
    image_id = request.POST.get('image_id')
    if not image_id:
        return JsonResponse({'error': 'No image ID provided'}, status=400)

    try:
        image = ItemImage.objects.get(id=image_id)
        if image.image_path:
            image_path = image.image_path.path
            if os.path.exists(image_path):
                os.remove(image_path)  # 실제 파일 삭제
        image.delete()  # DB에서 삭제
        return JsonResponse({'success': True})
    except ItemImage.DoesNotExist:
        return JsonResponse({'error': 'Image not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def process_heic_file(image_file, file_name):
    """
    HEIC 파일을 JPEG로 변환합니다.
    """
    # HEIC 이미지를 PIL Image로 열기
    image = Image.open(image_file)
    output_buffer = io.BytesIO()  # 메모리 버퍼에 파일 저장
    image.save(output_buffer, format="JPEG")  # JPEG로 변환
    output_buffer.seek(0)  # 버퍼 포인터를 초기화

    # 변환된 파일을 Django File 객체로 반환
    return ContentFile(output_buffer.read(), name=f"{file_name.rsplit('.', 1)[0]}.jpeg")

def upload_image_view(request):
    """
    이미지 파일 업로드 뷰
    - HEIC 파일은 JPEG로 변환하여 저장
    - 기타 이미지 파일은 그대로 저장
    """
    if request.method == 'POST' and request.FILES.get('placeImage'):
        # 세션에서 사용자 ID를 가져옵니다.
        user_id = request.session.get('user')

        # 사용자 정보 확인
        if not user_id:
            return JsonResponse({'error': '로그인된 사용자가 아닙니다.'}, status=400)

        try:
            member = Manager.objects.get(pk=user_id)
        except Manager.DoesNotExist:
            return JsonResponse({'error': '사용자를 찾을 수 없습니다.'}, status=400)

        try:
            # 업로드된 파일 가져오기
            image = request.FILES['placeImage']
            file_name = image.name
            file_ext = file_name.split('.')[-1].lower()  # 파일 확장자 추출

            # HEIC 파일인 경우 변환
            if file_ext == 'heic':
                image = process_heic_file(image, file_name)

            # 모델 인스턴스 생성 및 저장
            instance = Construction.objects.create(
                placeImage=image,
                writer=member
            )

            # 저장된 이미지 URL 응답
            return JsonResponse({'url': instance.placeImage.url})

        except Exception as e:
            # 예외 발생 시 오류 메시지 리턴
            return JsonResponse({'error': f'파일 처리 중 문제가 발생했습니다: {str(e)}'}, status=500)

    return JsonResponse({'error': '이미지 업로드가 실패했습니다.'}, status=400)

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
# 시공 상세
@login_required(login_url='/manager/login/')
def construction_detail(request, pk):
    # pk 에 해당하는 글을 가지고 올 수 있게 된다.
    context = {
        'manager_page': True,  # 매니저 페이지일 경우 True로 설정
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

@login_required(login_url='/manager/login/')
def construction_delete(request, pk):

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

@login_required(login_url='/manager/login/')
def bulk_delete_construction(request):
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