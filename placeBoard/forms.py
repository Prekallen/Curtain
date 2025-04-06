from django import forms
from .models import PlaceBoard
from django.core.validators import RegexValidator
from member.models import BoardMember
from django.contrib.auth.hashers import check_password



class BoardForm(forms.ModelForm):
    # 입력받을 값 [place, placeNum, address, area, placeImage]
    place = forms.CharField(error_messages={
       'required': '업체명을 입력하세요.'
    }, max_length=50, label="업체명",
    )
    placeNum = forms.CharField(error_messages={
        'required': '업체 전화 번호를 입력하세요.'
    }, max_length=20, label="전화 번호",
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message="유효한 전화번호를 입력하세요. 숫자만 입력 가능합니다."
            )
        ]
    )
    address = forms.CharField(error_messages={
        'required': '주소를 입력하세요.'
    }, max_length=100, label="주소",
    )
    area = forms.CharField(error_messages={
        'required': '지역을 입력하세요.'
    }, max_length=50, label="지역",
    )
    placeImage = forms.ImageField(error_messages={
        'required': '업체 사진을 올려주세요.'
    }, label="업체 사진",
    )

    class Meta:
        model = PlaceBoard
        fields = ['place', 'placeNum', 'address', 'area', 'placeImage']


