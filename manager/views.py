from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from django.urls import reverse

from .forms import LoginForm
from .models import Manager
import logging
logger = logging.getLogger(__name__)

# email 유효성 검사
def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

#manager
@login_required(login_url='/manager/login/')
def manager(request):

    user_id = request.session.get('user')
    manager = get_object_or_404(Manager, pk=user_id)
    context = {
        'user': manager,
        'manager_page': True,  # 관리자 페이지일 경우 True로 설정
    }
    return render(request, 'manager.html', context)

# login 페이지
def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            # 세션 코드 검증
            request.session['user'] = form.user_id
            return redirect(reverse('manager'))
    else:
        form = LoginForm()  # 빈 폼 클래스 생성

    context = {
        'form': form,
        'manager_page': True,  # 관리자 페이지일 경우 True로 설정
    }
    return render(request, 'login.html', context)

#logout
def logout(request):
    if request.session.get('user'):
        del(request.session['user'])

    return redirect(reverse('manager'))   # 아! 로그인을 안했을 때!, user_id 가 없을 때? (세션이 만료되었을 때?)

# 회원가입 페이지
def register(request):
    if request.method == "GET":
        context = {
            'manager_page': True,  # 관리자 페이지일 경우 True로 설정
        }
        return render(request, 'register.html', context)
    if request.method == "POST":
        username = request.POST.get('username', None)
        phone = request.POST.get('phone', None)
        email = request.POST.get('email', None)
        address = request.POST.get('address', None)
        password = request.POST.get('password', None)
        re_password = request.POST.get('re_password', None)

        if not (username and password and re_password):
            messages.error(request, '필수 값을 입력해야 합니다')  # email, address 제외
        elif password != re_password:
            messages.error(request, '비밀번호가 다릅니다.')
        elif not is_valid_phone(phone):
            messages.error(request, '전화번호는 숫자만 입력하고 10자리 이상이어야 합니다.')
        elif email and not is_valid_email(email):  # email이 입력되었을 때만 검사
            messages.error(request, '유효하지 않은 이메일 형식입니다.')
        else:
            if Manager.objects.filter(username=username).exists():
                messages.error(request, '아이디가 중복입니다.')
            else:
                member = Manager(
                    username=username,
                    password=make_password(password),
                    phone=phone,
                    email=email,  # email이 없으면 None으로 전달
                    address=address  # address가 없으면 None으로 전달
                )
                try:
                    with transaction.atomic():
                        member.save()
                        messages.success(request, '회원가입이 완료되었습니다')
                        return redirect(reverse('manager'))
                except Exception as e:
                    logger.error(f"에러 발생: {e}")
                    messages.error(request, '데이터 저장 중 문제가 발생했습니다.')
                    raise
    return render(request, 'register.html')

# 전화번호 유효 검사
def is_valid_phone(phone):
    if phone is None:  # None 처리
        return False
    if phone.isdigit() and 10 <= len(phone) <= 15:  # 숫자 여부와 길이 확인
        return True
    return False
