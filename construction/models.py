from django.db import models
from curtain.utils import get_lat_lng


class Construction(models.Model):
    id              = models.AutoField(primary_key=True, verbose_name='기본키')
    address         = models.TextField(max_length=100, verbose_name="주소")
    housing_type    = models.CharField(max_length=40, verbose_name="주거 형태")
    manager         = models.ForeignKey('manager.Manager', on_delete=models.SET_NULL, null=True, verbose_name='작성 담당자')
    writer          = models.CharField(max_length=100, blank=True, null=True, verbose_name='작성자')
    #위도 경도
    latitude        = models.FloatField(null=True, blank=True, verbose_name="위도")
    longitude       = models.FloatField(null=True, blank=True, verbose_name="경도")
    created_at      = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at      = models.DateTimeField(auto_now=True, verbose_name="최종 수정일")

    def __str__(self):
        return f"시공 ID: {self.id}, 주소: {self.address}"

    def save(self, *args, **kwargs):
        if self.address and (not self.latitude or not self.longitude):
            lat, lng = get_lat_lng(self.address)
            if lat and lng:
                self.latitude = lat
                self.longitude = lng
            else:
                print(f"{self.address}의 좌표를 찾을 수 없습니다.")
        super().save(*args, **kwargs)

    class Meta:
        db_table            = 'construction'
        verbose_name        = '시공'
        verbose_name_plural = '시공'

class ConstItem(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='기본키')
    # on_delete=models.CASCADE Construction이 삭제 되면 ConstItem도 삭제
    const_id    = models.ForeignKey(Construction, on_delete=models.CASCADE, related_name='items')
    ITEM_TYPE_CHOICES = [
        ('innerCurtain', '속 커튼'),
        ('outerCurtain', '겉 커튼'),
        ('blind', '블라인드'),
        ('etc', '기타'),
    ]
    item_type   = models.CharField(max_length=20, verbose_name='품목', choices=ITEM_TYPE_CHOICES)
    item_name   = models.CharField(max_length=20, verbose_name="아이템 이름", null=True, blank=True)# 필수 입력 값이 아님
    item_detail = models.TextField(verbose_name="아이템 설명", null=True, blank=True)# 필수 입력 값이 아님

    def __str__(self):
        return f"{self.get_item_type_display()}: {self.item_name or '이름 없음'}"

    class Meta:
        indexes = [
            models.Index(fields=['const_id', 'item_type']),
        ]

class ItemImage(models.Model):
    id          = models.AutoField(primary_key=True, verbose_name='기본키')
    # on_delete=models.CASCADE ConstItme이 삭제 되면 ItemImage도 삭제
    item_id     = models.ForeignKey(ConstItem, on_delete=models.CASCADE, related_name='images')
    image_path  = models.ImageField(upload_to='images/', null=True, blank=True)

    def __str__(self):
        return f"이미지 ID: {self.id}, 경로: {self.image_path.name if self.image_path else '없음'}"

    class Meta:
        indexes = [
            models.Index(fields=['item_id']),
        ]