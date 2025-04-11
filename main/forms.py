from django import forms
from customer.models import Customer
from django.core.validators import RegexValidator

class CustomerForm(forms.ModelForm):
    # 입력받을 값 [name, phone, address,]
    name = forms.CharField(error_messages={
       'required': '이름을 입력해주세요.'
    }, max_length=50, label="이름",
    )
    phone = forms.CharField(error_messages={
        'required': '전화 번호를 입력하세요.'
    }, max_length=20, label="전화 번호",
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message="유효한 전화번호를 입력하세요. 숫자만 입력 가능합니다."
            )
        ]
    )
    detail_address = forms.CharField(error_messages={
        'required': '주소를 입력해주세요.'
    }, max_length=100, label="주소",
    )


    class Meta:
        model = Customer
        fields = ['name', 'phone',  'detail_address']