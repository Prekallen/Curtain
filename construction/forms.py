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
        cleaned_data = super().clean()  # 기본 유효성 검사 호출
        # 폼 데이터가 변경되지 않았지만 유효성 검사를 통과하도록 처리
        if not self.has_changed():
            # 필드별 필요한 동작 추가 가능
            return cleaned_data

        # 변경된 데이터에 대해 추가 유효성 검사 (예: address)
        if 'address' in self.changed_data:
            address = cleaned_data.get('address')
            if not address:
                self.add_error('address', '주소를 입력해주세요.')

        # 다른 변경된 항목의 검증 추가 가능
        return cleaned_data


class UpdateConstItemForm(ConstItemForm):
    def clean(self):
        # 폼 삭제 여부 확인
        if self.cleaned_data.get('DELETE', False):
            print('폼 삭제됨: DELETE 체크됨')  # 디버깅 메시지
            return self.cleaned_data  # 삭제된 폼은 검증 무시

        # 폼 변경 사항 확인
        if not self.has_changed():
            return self.cleaned_data  # 변경되지 않았다면 기존 데이터 유지

        # 변경된 폼 내용 검증
        cleaned_data = super().clean()
        for form in self.forms:
            # 삭제된 폼 건너뜀
            if form.cleaned_data.get('DELETE', False):
                continue

            # 폼 수준에서 유효성 검사를 통과하지 못한 경우 추가 처리
            if not form.is_valid():
                raise forms.ValidationError("한 개 이상의 폼에 문제가 있습니다.")# 이미지 폼셋 검증 - DELETE 필드가 False인 경우에만 진행
        if hasattr(self, 'image_formset') and self.image_formset:
            if not self.image_formset.is_valid():
                raise forms.ValidationError("이미지 관련 유효성 검증에 실패했습니다.")

            # 최소 1개 이상의 이미지를 검증 (단, 삭제되지 않은 폼만 검사)
            total_images = [
                frm for frm in self.image_formset.forms
                if frm.cleaned_data and not frm.cleaned_data.get('DELETE', False)
            ]
            if len(total_images) < 1:
                raise forms.ValidationError("최소 하나 이상의 이미지를 등록해주세요.")

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
    parent_model=Construction,  # 부모 모델
    model=ConstItem,  # 자식 모델
    form=ConstItemForm,  # 사용할 Form 클래스
    fields=['item_type', 'item_name', 'item_detail'],  # 사용할 필드
    extra=0,  # 추가할 폼 개수
    can_delete=True  # 삭제 여부 처리
)

class ItemImageForm(forms.ModelForm):
    image_path = forms.ImageField(required=True, label='이미지')

    class Meta:
        model = ItemImage
        fields = ['image_path']

    def clean_image_path(self):
        image = self.cleaned_data.get('image_path')
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.heic']  # 허용할 확장자
        max_file_size = 10 * 1024 * 1024  # 파일 크기 제한 (10MB)
        if image:
            ext = image.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise ValidationError("허용되지 않는 파일 형식입니다. jpg, jpeg, png, heic 파일만 업로드 가능합니다.")
            if image.size > max_file_size:  # 파일 크기 제한 검사
                raise ValidationError("파일 크기는 5MB를 초과할 수 없습니다.")
        return image


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
class UpdateItemImageFormSet(BaseItemImageFormSet):
    def clean(self):
        super().clean()
        # POST 요청일 경우 유효성 검사
        if self.is_bound:
            total_images = 0

            # 폼셋 검증 중 삭제 항목을 제외하고 유효한 이미지만 확인
            for form in self.forms:
                if not form.is_valid(): # 폼 유효성 검사가 실패했으면 건너뛰는 로직 추가
                    continue
                if form.cleaned_data.get('DELETE'):  # DELETE 필드가 True인 경우 건너뜀
                    continue
                if form.cleaned_data:  # 유효한 데이터가 있는 경우 (삭제되지 않은 이미지)
                    total_images += 1

            # 최소 1개 이상의 이미지가 등록되었는지 확인
            if total_images < 1:
                raise ValidationError("최소 한 개 이상의 이미지를 등록해야 합니다.")

            # 최대 등록 가능 이미지 제한
            if total_images > 5:
                raise ValidationError("이미지는 최대 5개까지만 등록 가능합니다.")
