from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages

from .forms import LoginForm, RegisterForm
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
    context = {
        'user': request.user,
        'manager_page': True,  # 관리자 페이지일 경우 True로 설정
    }
    return render(request, 'manager.html', context)

# login 페이지
def login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                request.session['user'] = user.id
                return redirect('/manager')
            else:
                form.add_error(None, '아이디 또는 비밀번호가 잘못되었습니다.')
        else:
            print("폼 유효성 검사 실패:", form.errors)
    else:
        form = LoginForm()
    context = {
        'form': form,
        'manager_page': True,
    }
    return render(request, 'login.html', context)

#logout
def logout_view(request):
    logout(request)
    return redirect('/manager')   # 아! 로그인을 안했을 때!, user_id 가 없을 때? (세션이 만료되었을 때?)

# 회원가입 페이지
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    member = form.save()  # RegisterForm의 save() 메서드 호출
                    messages.success(request, '회원가입이 완료되었습니다')
                    return redirect('/manager')
            except Exception as e:
                logger.error(f"에러 발생: {e}")
                messages.error(request, '데이터 저장 중 문제가 발생했습니다.')
                raise
        else:
            context = {
                'form': form,
                'manager_page': True,
            }
            return render(request, 'register.html', context)
    else:
        form = RegisterForm()
        context = {
            'form': form,
            'manager_page': True,
        }
        return render(request, 'register.html', context)

# 전화번호 유효 검사
def is_valid_phone(phone):
    if phone is None:  # None 처리
        return False
    if phone.isdigit() and 10 <= len(phone) <= 15:  # 숫자 여부와 길이 확인
        return True
    return False
