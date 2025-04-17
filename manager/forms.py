from django import forms
from manager.models import Manager
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='아이디',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '아이디'})
    )
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '비밀번호'})
    )

    class Meta:
        fields = ['username', 'password']

class RegisterForm(forms.Form):
    username = forms.CharField(error_messages={'required': '아이디를 입력하세요!'}, max_length=150, label="아이디")
    password = forms.CharField(error_messages={'required': '비밀번호를 입력하세요!'}, widget=forms.PasswordInput, max_length=100, label="비밀번호")
    password_confirm = forms.CharField(error_messages={'required': '비밀번호를 다시 입력하세요!'}, widget=forms.PasswordInput, max_length=100, label="비밀번호 확인")
    name = forms.CharField(error_messages={'required': '이름을 입력하세요!'}, max_length=100, label="이름")
    phone = forms.CharField(error_messages={'required': '전화 번호를 입력하세요.'}, max_length=20, label="전화 번호",
                            validators=[
                                RegexValidator(
                                    regex=r'^\d+$',
                                    message="유효한 전화번호를 입력하세요. 숫자만 입력 가능합니다."
                                )
                            ])
    email = forms.EmailField(label="이메일", required=False, max_length=150)  # 선택 입력
    address = forms.CharField(label="주소", required=False, widget=forms.Textarea)  # 선택 입력

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', '비밀번호가 일치하지 않습니다!')

        if username:
            if Manager.objects.filter(username=username).exists():
                self.add_error('username', '이미 사용 중인 아이디입니다!')

        return cleaned_data

    def save(self):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        name = cleaned_data.get('name')
        phone = cleaned_data.get('phone')

        manager = Manager(
            username=username,
            password=make_password(password), # 비밀번호 해싱
            name=name,
            phone=phone
        )
        manager.save()
        return manager