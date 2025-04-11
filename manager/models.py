from django.db import models

class Manager(models.Model):
    id          = models.AutoField(primary_key=True, verbose_name='기본키')
    username    = models.CharField(max_length=150, unique=True, verbose_name='로그인 ID')
    name        = models.CharField(max_length=100, verbose_name='이름')
    email       = models.EmailField(max_length=100, verbose_name='유저전자메일', null=True, blank=True) # 필수 입력 값이 아님
    password    = models.CharField(max_length=100, verbose_name='유저PW')
    phone       = models.CharField(max_length=20, unique=True, verbose_name='전화번호')
    address     = models.TextField(max_length=100, verbose_name='주소', null=True, blank=True)# 필수 입력 값이 아님
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name='가입 날짜')
    updated_at  = models.DateTimeField(auto_now=True, verbose_name='마지막 수정일')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('username', 'phone')  # 두 필드 조합의 고유성 보장
        db_table            = 'app_manager'
        verbose_name        = '관리자'
        verbose_name_plural = '관리자'
