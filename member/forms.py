from django import forms

from member.models import BoardMember
from django.contrib.auth.hashers import check_password



class LoginForm(forms.Form):
    # LoginForm 에서 입력받을 값은 2개 (아이디, 패스워드)
    username = forms.CharField(error_messages={
        'required':'아이디를 입력하세요!'
    },max_length=100, label="사용자이름")
    # 비밀번호를 텍스트가 아닌 패스워드 타입으로 만들려면 widget 을 지정해야 한다.
    password = forms.CharField(error_messages={
        'required':'비밀번호를 입력하세요!'
    },widget=forms.PasswordInput, max_length=100, label="비밀번호")

    def clean(self):
        cleaned_data = super().clean()
        # 처음 값이 들어왔다 는 검증 진행
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        # cleaned_data 의 첫 검증이 끝난 데이터 에서 이제 값이 들어있나 확인하기
        if username and password:
            try:
                member = BoardMember.objects.get(username=username)
            except BoardMember.DoesNotExist:
                self.add_error('username', '아이디가 없습니다!')
                return
                # 예외처리를 하고 return 을 실행해서 바로 아래 코드를 실행하지 않고 빠져나오게 한다.

            # 세션처리는 views 내 login 함수에서! 검증만 한다.
            # 위에 (forms.py) from django.contrib.auth.hashers import check_password 입력
            if not check_password(password, member.password):
            # check_password 의 앞 password 는 입력받은 값, 뒤는 모델안에 저장되어 있는 값
                self.add_error('password', '비밀번호가 다릅니다!')
            else:
                self.user_id = member.id