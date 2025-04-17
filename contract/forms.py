from django import forms
from .models import Contract, InnerCurtain, OuterCurtain, Blind, Etc

class ContractForm(forms.ModelForm):
    # 입력받을 값 [down_pay]
    class Meta:
        model = Contract
        fields = ['down_pay']
        labels = {
            'down_pay': '계약금',
        }
        error_messages = {
            'down_pay': {
                'required': '계약금을 입력해 주세요.',
            },
        }

class InnerCurtainForm(forms.ModelForm):
    name = forms.CharField(error_messages={
        'required': '제품명을 입력해 주세요.'
    }, max_length=100,label="제품명")
    size = forms.DecimalField(error_messages={
        'required': '치수를 입력해 주세요.',
        'invalid' : '유효한 숫자를 입력해 주세요'
    },max_digits=10, decimal_places=2,label="제품명")
    unit_price = forms.DecimalField(error_messages={
        'required': '단가를 입력해 주세요.',
        'invalid' : '유효한 숫자를 입력해 주세요'
    }, max_digits=10, decimal_places=2, label="단가")

    class Meta:
        model = InnerCurtain
        fields = ['name', 'size', 'unit_price', 'quantity']

class OuterCurtainForm(forms.ModelForm):
    name = forms.CharField(error_messages={
        'required': '제품명을 입력해 주세요.'
    }, max_length=100,label="제품명")
    size = forms.DecimalField(error_messages={
        'required': '치수를 입력해 주세요.',
        'invalid' : '유효한 숫자를 입력해 주세요'
    }, max_digits=10, decimal_places=2, label="제품명")
    unit_price = forms.DecimalField(error_messages={
        'required': '단가를 입력해 주세요.',
        'invalid' : '유효한 숫자를 입력해 주세요'
    }, max_digits=10, decimal_places=2, label="단가")

    class Meta:
        model = OuterCurtain
        fields = ['name', 'size', 'unit_price', 'quantity']

class BlindForm(forms.ModelForm):
    name = forms.CharField(error_messages={
        'required': '제품명을 입력해 주세요.'
    }, max_length=100,label="제품명")
    size = forms.DecimalField(error_messages={
        'required': '치수를 입력해 주세요.',
        'invalid' : '유효한 숫자를 입력해 주세요'
    }, max_digits=10, decimal_places=2, label="제품명")
    unit_price = forms.DecimalField(error_messages={
        'required': '단가를 입력해 주세요.',
        'invalid' : '유효한 숫자를 입력해 주세요'
    }, max_digits=10, decimal_places=2, label="단가")

    class Meta:
        model = Blind
        fields = ['name', 'size', 'unit_price', 'quantity']

class EtcForm(forms.ModelForm):
    name = forms.CharField(error_messages={
        'required': '제품명을 입력해 주세요.'
    }, max_length=100,label="제품명")
    size = forms.DecimalField(error_messages={
        'required': '치수를 입력해 주세요.',
        'invalid' : '유효한 숫자를 입력해 주세요'
    }, max_digits=10, decimal_places=2, label="제품명")
    unit_price = forms.DecimalField(error_messages={
        'required': '단가를 입력해 주세요.',
        'invalid' : '유효한 숫자를 입력해 주세요'
    }, max_digits=10, decimal_places=2, label="단가")

    class Meta:
        model = Etc
        fields = ['name', 'size', 'unit_price', 'quantity']