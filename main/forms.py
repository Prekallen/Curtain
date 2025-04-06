from django import forms
from .models import Participant
from django.core.validators import RegexValidator
from member.models import BoardMember
from django.contrib.auth.hashers import check_password



class ParticipantForm(forms.ModelForm):
    # 입력받을 값 [place, placeNum, address, area, placeImage]
    name = forms.CharField(error_messages={
       'required': '이름을 입력해주세요.'
    }, max_length=50, label="이름",
    )
    num = forms.CharField(error_messages={
        'required': '전화 번호를 입력하세요.'
    }, max_length=20, label="전화 번호",
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message="유효한 전화번호를 입력하세요. 숫자만 입력 가능합니다."
            )
        ]
    )

    receiptImage = forms.ImageField(error_messages={
        'required': '영수증 사진을 올려주세요.'
    }, label="영수증 사진",
    )

    placeId = forms.IntegerField(error_messages={
        'required': '가게를 검색해 선택해 주세요.'
    }, label="가게",
    )


    class Meta:
        model = Participant
        fields = ['name', 'num',  'placeId', 'receiptImage']    #'email',

'''
 email = forms.EmailField(error_messages={
     'required': '이메일 입력하세요. ex)example@example.com '
 }, max_length=100, label="이메일",
 )
'''
