from django import forms
from django.forms.models import inlineformset_factory
from .models import Construction, ConstItem, ItemImage

class ConstructionForm(forms.ModelForm):
    # 입력받을 값 [address, housing_type]
    class Meta:
        model = Construction
        fields = ['address', 'housing_type']
        labels = {
            'address': '주소',
            'housing_type': '주거 형태',
        }
        error_messages = {
            'address': {'required': '주소를 입력해주세요.'},
            'housing_type': {'required': '주거 형태를 입력해주세요.'},
        }

class ConstItemForm(forms.ModelForm):
    item_name = forms.CharField(max_length=20, label="이름", required=False)
    item_detail = forms.CharField(widget=forms.Textarea, label="설명", required=False)

    class Meta:
        model = ConstItem
        fields = ['item_type', 'item_name', 'item_detail']
        labels = {
            'item_type': '품목',
        }

ConstItemFormSet = inlineformset_factory(
    Construction,
    ConstItem,
    form=ConstItemForm,
    extra=1,
    can_delete=True
)

class ItemImageForm(forms.ModelForm):
    image_path = forms.ImageField(required=True, label='이미지')

    class Meta:
        model = ItemImage
        fields = ['image_path']

ItemImageFormSet = inlineformset_factory(
    ConstItem,
    ItemImage,
    form=ItemImageForm,
    extra=1,
    can_delete=True
)