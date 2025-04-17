from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class ManagerManager(BaseUserManager):  # 커스텀 매니저
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class Manager(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True, verbose_name='기본키')
    username = models.CharField(max_length=150, unique=True, verbose_name='로그인 ID')
    name = models.CharField(max_length=100, verbose_name='이름')
    email = models.EmailField(max_length=100, verbose_name='유저 전자메일', null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, verbose_name='전화번호')
    address = models.TextField(max_length=100, verbose_name='주소', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='가입 날짜')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='마지막 수정일')

    is_active = models.BooleanField(default=True, verbose_name='활성화 여부')
    is_staff = models.BooleanField(default=False, verbose_name='스태프 여부')

    objects = ManagerManager()  # 커스텀 매니저 연결

    USERNAME_FIELD = 'username'  # 고유 식별 필드
    REQUIRED_FIELDS = ['email', 'name']  # 추가 필수 필드

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'app_manager'
        verbose_name = '관리자'
        verbose_name_plural = '관리자'