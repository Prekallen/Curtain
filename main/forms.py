from django import forms
from customer.models import Customer
from django.core.validators import RegexValidator

class RegionLevel1Form(forms.Form):
    region_level1 = forms.CharField(
        label='광역시/도',
        widget=forms.Select(choices=[('', '선택하세요')]),
        required=True
    )
    # migration 초기 생성시 customer app model 접근 때문에 추가
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['region_level1'].widget.choices = [('', '선택하세요')] + list(Customer.objects.values_list('region_level1', 'region_level1').distinct().order_by('region_level1'))

class RegionLevel2Form(forms.Form):
    region_level2 = forms.CharField(
        label='시/군/구',
        widget=forms.Select(choices=[('', '선택하세요')]),
        required=True
    )

class RegionLevel3Form(forms.Form):
    region_level3 = forms.CharField(
        label='읍/면/동',
        widget=forms.Select(choices=[('', '선택하세요')]),
        required=True
    )

class DetailedAddressForm(forms.Form):
    detailed_address = forms.CharField(
        label='상세 주소',
        max_length=100,
        required=True,
        error_messages={
            'required': '주소를 입력해주세요.'
        },
    )

class ContactInfoForm(forms.Form):
    name = forms.CharField(
        label='이름',
        max_length=50,
        required=True,
        error_messages={
            'required': '이름을 입력해주세요.'
        },
    )
    phone = forms.CharField(
        label='휴대폰 번호',
        max_length=20,
        widget=forms.TextInput(attrs={'oninput': "this.value=this.value.replace(/[^0-9]/g,'');"}),
        error_messages={
            'required': '전화 번호를 입력하세요.'
        },
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message="유효한 전화번호를 입력하세요. 숫자만 입력 가능합니다."
            )
        ]
    )
    agree_personal_info = forms.BooleanField(
        label='개인정보 제공 동의',
        widget=forms.CheckboxInput(),
        required=True,
        error_messages={
            'required': '개인정보 제공 동의를 체크해주세요.'
        },
    )