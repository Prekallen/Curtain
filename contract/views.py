import requests
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction

from manager.models import Manager
from .forms import ContractForm
from .models import Contract
import logging
logger = logging.getLogger(__name__)


# Create your views here.
# session 검사
def session_check(request):
    if not request.session.get('user'):
        return redirect('/member/login/')
    # 세션에 'user' 키를 불러올 수 없으면, 로그인하지 않은 사용자이므로 로그인 페이지로 리다이렉트 한다.

# 목록
def board_list(request):
    search_type = request.GET.get('search_type', 'place')
    query = request.GET.get('q')

    if query:
        if search_type == 'place':
            all_boards = Contract.objects.filter(place__icontains=query)
        elif search_type == 'region':
            all_boards = Contract.objects.filter(area__icontains=query)
    else:
        all_boards = Contract.objects.all().order_by('-id')

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
    return render(request, 'contract_list.html', context)

# 작성
def board_write(request):
    session_check(request)

    if request.method == "POST":
        form = BoardForm(request.POST, request.FILES)

        if form.is_valid():
            # form의 모든 validators 호출 유효성 검증 수행
            user_id = request.session.get('user')
            manager = Manager.objects.get(pk=user_id)

            board = form.save(commit=False)  # 폼 데이터를 임시 저장
            board.manager = manager
            board.writer = manager.name

            # 트랜잭션 내에서 데이터 저장
            try:
                with transaction.atomic():
                    board.save()
            except Exception as e:
                logger.error(f"에러 발생: {e}")  # 에러 기록  # 에러 기록
                raise  # 예외 재발생 (상위 레벨에서 처리)

            return redirect('/board/list/?p=1')
    else:
        form = ContractForm()
    context = {
        'admin_page': True,  # 관리자 페이지일 경우 True로 설정
        'form': form,
    }
    return render(request, 'contract_write.html', context)

 #
def board_detail(request, pk):
    # pk 에 해당하는 글을 가지고 올 수 있게 된다.
    context = {
        'admin_page': True,  # 관리자 페이지일 경우 True로 설정
    }
    try:
        board = Contract.objects.get(pk=pk)
        context['board'] = board
    except Contract.DoesNotExist:
        raise Http404('계약서를 찾을 수 없습니다')

    instance = get_object_or_404(Contract, pk=pk)
    # 게시물의 내용을 찾을 수 없을 때 내는 오류 message.
    # 리스트 페이지의 모든 게시물을 가져오고 페이지네이터로 나눕니다.
    all_posts = Contract.objects.all().order_by('-id')
    paginator = Paginator(all_posts, 10) # 페이지당 10개의 게시물
    # 수정된 게시물이 속한 페이지를 찾습니다.
    page_number = None

    for page in paginator.page_range:
        if instance in paginator.page(page).object_list:
            page_number = page

            break
    if page_number:
        context['page_number'] = page_number

    return render(request, 'contract_detail.html', context)

def board_update(request, pk):
    session_check(request)
    instance = get_object_or_404(Contract, pk=pk)
    try:
        pre_board = Contract.objects.get(pk=pk)
    except Contract.DoesNotExist:
        raise Http404('계약서를 찾을 수 없습니다')

    if request.method == "POST":
        form = ContractForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            board = form.save(commit=False)
            user_id = request.session.get('user')
            manager = Manager.objects.get(pk=user_id)
            board.manager = manager.id
            board.writer = manager.name

            # 트랜잭션 내에서 데이터 저장
            try:
                with transaction.atomic():
                    board.save()
            except Exception as e:
                logger.error(f"에러 발생: {e}")  # 에러 기록  # 에러 기록
                raise  # 예외 재발생 (상위 레벨에서 처리)

            # 리스트 페이지의 모든 게시물을 가져오고 페이지네이터로 나눕니다.
            all_posts = Contract.objects.all().order_by('-id')
            paginator = Paginator(all_posts, 10)  # 페이지당 10개의 게시물
            page_number = None
            for page in paginator.page_range:
                if instance in paginator.page(page).object_list:
                    page_number = page
                    break
            if page_number:
                return redirect(f'/board/list/?p={page_number}')
        else:
            # 폼 오류 처리
            print('form_error : ' + str(form.errors))  # 폼의 오류 메시지 출력

    else:
        form = ContractForm(instance=instance)

    return render(request, 'board_update.html', {'form':form,'board':pre_board,'admin_page':True})
