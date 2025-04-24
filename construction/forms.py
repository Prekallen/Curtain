from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
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
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class ConstItemForm(forms.ModelForm):
    item_type = forms.ChoiceField(
        choices=ConstItem.ITEM_TYPE_CHOICES,
        label="품목",
        required=True
    )
    item_name = forms.CharField(max_length=20, label="이름", required=False)
    item_detail = forms.CharField(widget=forms.Textarea, label="설명", required=False)

    class Meta:
        model = ConstItem
        exclude = ['id']  # 또는 fields 에 id를 포함하지 않기
        fields = ['item_type', 'item_name', 'item_detail']

class ConstructionUpdateForm(ConstructionForm):
    def clean(self):
        cleaned_data = super().clean()
        # 필요 시 추가 유효성 검사
        return cleaned_data

class UpdateConstItemForm(ConstItemForm):
    def clean(self):
        cleaned_data = super().clean()
        if not self.cleaned_data.get('DELETE', False):
            images = self.image_formset
            if images.total_form_count() == 0:
                raise forms.ValidationError('이미지를 하나 이상 등록해주세요.')
        return cleaned_data

RegisterConstItemFormSet = inlineformset_factory(
    Construction,
    ConstItem,
    form=ConstItemForm,
    extra=1,
    can_delete=True
)
# Update용 ConstItemFormSet
UpdateConstItemFormSet = inlineformset_factory(
    Construction,
    ConstItem,
    form=UpdateConstItemForm,
    extra=0,
    can_delete=True
)

class ItemImageForm(forms.ModelForm):
    image_path = forms.ImageField(required=True, label='이미지')

    class Meta:
        model = ItemImage
        fields = ['image_path']


class BaseItemImageFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        images = [form for form in self.forms if form.cleaned_data and not form.cleaned_data.get('DELETE', False)]
        if len(images) > 5:
            raise ValidationError("이미지는 품목당 최대 5개까지만 업로드할 수 있습니다.")

        if not self.instance.pk and len(images) < 1:
            raise ValidationError("최소 한 개 이상의 이미지를 등록해야 합니다.")


ItemImageFormSet = inlineformset_factory(
    ConstItem,
    ItemImage,
    form=ItemImageForm,
    formset=BaseItemImageFormSet,
    extra=1,
    can_delete=True,
    min_num=0,  # 최소 이미지 수 없음
)

# Update용 ItemImageFormSet
def get_item_image_formset(is_update=False):
    class ItemImageForm(forms.ModelForm):
        class Meta:
            model = ItemImage
            fields = '__all__'

    return inlineformset_factory(
        ConstItem,
        ItemImage,
        form=ItemImageForm,
        extra=0 if is_update else 1,
        can_delete=True  # 수정 시 삭제 허용
    )