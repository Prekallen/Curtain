from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404
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
        return redirect('/manager/login/')
    # 세션에 'user' 키를 불러올 수 없으면, 로그인하지 않은 사용자이므로 로그인 페이지로 리다이렉트 한다.

# 목록
def contract_list(request):
    search_type = request.GET.get('search_type', 'address')
    query = request.GET.get('q')
    sort_by = request.GET.get('sort_by')

    all_boards = Contract.objects.all()

    if query:
        if search_type == 'address':
            all_boards = all_boards.filter(address__icontains=query)
        elif search_type == 'complete':
            all_boards = all_boards.filter(complete__icontains=query)
        elif search_type == 'customer':
            all_boards = all_boards.filter(customer__icontains=query)
        elif search_type == 'create_at':
            all_boards = all_boards.filter(create_at__icontains=query)
        elif search_type == 'const_date':
            all_boards = all_boards.filter(const_date__icontains=query)

    if sort_by:
        if sort_by == 'customer':
            all_boards = all_boards.order_by('customer')
        elif sort_by == 'create_at':
            all_boards = all_boards.order_by('create_at')
        elif sort_by == 'const_date':
            all_boards = all_boards.order_by('const_date')
        else:
            all_boards = all_boards.order_by('-id') # 기본 정렬 유지
    else:
        all_boards = all_boards.order_by('-id') # 기본 정렬

    page = int(request.GET.get('p', 1))
    paginator = Paginator(all_boards, 10)
    boards = paginator.get_page(page)

    current_page = boards.number
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
        'boards': boards,
        'page_numbers': page_numbers,
        'has_previous_group': start_page > 1,
        'has_next_group': end_page < total_pages,
        'previous_group_page': start_page - 1,
        'next_group_page': end_page + 1,
        'query_string': query_string,
        'search_type': search_type,
        'query': query,
        'sort_by': sort_by, # 현재 정렬 상태 유지를 위해 추가
    }
    return render(request, 'contract_list.html', context)

# 작성
def register_contract(request):
    session_check(request)

    if request.method == "POST":
        form = ContractForm(request.POST, request.FILES)

        if form.is_valid():
            # form의 모든 validators 호출 유효성 검증 수행
            user_id = request.session.get('user')
            manager = Manager.objects.get(pk=user_id)

            contract = form.save(commit=False)  # 폼 데이터를 임시 저장
            contract.manager = manager
            contract.writer = manager.name
            contract.writer_phone = manager.phone

            # 트랜잭션 내에서 데이터 저장
            try:
                with transaction.atomic():
                    contract.save()
            except Exception as e:
                logger.error(f"에러 발생: {e}")  # 에러 기록  # 에러 기록
                messages.error(request, f"계약 등록 중 오류가 발생 (고객명: {contract.customer}): {e}")
                return redirect('register_contract')

            return redirect('/contract/list/?p=1')
    else:
        form = ContractForm()
    context = {
        'admin_page': True,  # 관리자 페이지일 경우 True로 설정
        'form': form,
    }
    return render(request, 'contract_write.html', context)

 #
def contract_detail(request, pk):
    # pk 에 해당하는 글을 가지고 올 수 있게 된다.
    context = {
        'admin_page': True,  # 관리자 페이지일 경우 True로 설정
    }
    try:
        contract = Contract.objects.get(pk=pk)
        context['contract'] = contract
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

def contract_update(request, pk):
    session_check(request)
    instance = get_object_or_404(Contract, pk=pk)
    try:
        pre_contract = Contract.objects.get(pk=pk)
    except Contract.DoesNotExist:
        raise Http404('계약서를 찾을 수 없습니다')

    if request.method == "POST":
        form = ContractForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            contract = form.save(commit=False)
            user_id = request.session.get('user')
            manager = Manager.objects.get(pk=user_id)
            contract.manager = manager
            contract.writer = manager.name
            contract.writer_phone = manager.phone

            # 트랜잭션 내에서 데이터 저장
            try:
                with transaction.atomic():
                    contract.save()
            except Exception as e:
                logger.error(f"에러 발생: {e}")  # 에러 기록  # 에러 기록
                messages.error(request, f"계약 수정 중 오류가 발생했습니다: {e}")
                return redirect('contract_update', pk=pk)

            # 리스트 페이지의 모든 게시물을 가져오고 페이지네이터로 나눕니다.
            all_posts = Contract.objects.all().order_by('-id')
            paginator = Paginator(all_posts, 10)  # 페이지당 10개의 게시물
            page_number = None
            for page in paginator.page_range:
                if instance in paginator.page(page).object_list:
                    page_number = page
                    break
            if page_number:
                return redirect(f'/contract/list/?p={page_number}')
        else:
            # 폼 오류 처리
            logger.error(f"에러 발생: 입력값 이 유효하지 않습니다.")  # 에러 기록  # 에러 기록
            messages.error(request, f"계약 수정 중 오류가 발생했습니다: 입력값") # 폼의 오류 메시지 출력

    else:
        form = ContractForm(instance=instance)

    return render(request, 'contract_update.html', {'form':form,'contract':pre_contract,'admin_page':True})

def contract_delete(request, pk):
    session_check(request)
    contract = get_object_or_404(Contract, pk=pk)

    if request.method == "POST":
        try:
            with transaction.atomic():
                contract.delete()
            messages.success(request, f"계약 ID {pk}가 성공적으로 삭제되었습니다.")
            return redirect('contract_list')
        except Exception as e:
            messages.error(request, f"계약 삭제 중 오류가 발생했습니다: {e}")
            return redirect('contract_detail', pk=pk)  # 또는 목록 페이지로 리다이렉트
    else:
        messages.error(request, "잘못된 접근입니다.")
        return redirect('contract_detail', pk=pk)

def bulk_delete_contract(request):
    session_check(request)
    if request.method == "POST":
        contract_ids = request.POST.getlist('contract_ids')
        if contract_ids:
            try:
                with transaction.atomic():
                    Contract.objects.filter(id__in=contract_ids).delete()
                messages.success(request, f"{len(contract_ids)}개의 계약이 성공적으로 삭제되었습니다.")
            except Exception as e:
                messages.error(request, f"계약 삭제 중 오류가 발생했습니다: {e}")
        else:
            messages.warning(request, "삭제할 계약을 선택해주세요.")
    return redirect('contract_list')