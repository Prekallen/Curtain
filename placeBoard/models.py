from django.db import models
from curtain.utils import get_lat_lng
from phonenumber_field.modelfields import PhoneNumberField

class PlaceBoard(models.Model):
    place       = models.CharField(max_length=50, verbose_name="업체명")
    placeNum    = models.CharField(max_length=20, verbose_name="업체 전화 번호")
    address     = models.TextField(max_length=100, verbose_name="주소")
    area        = models.CharField(max_length=50, verbose_name="지역")
    placeImage  = models.ImageField(upload_to='photos/', verbose_name="업체 사진")
    partNum     = models.IntegerField(default=0, verbose_name="참가자 수")
    duplPartNum = models.IntegerField(default=0, verbose_name="중복 참가자 수")
    writer      = models.ForeignKey('member.BoardMember', on_delete=models.CASCADE, verbose_name="작성자")
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at  = models.DateTimeField(auto_now=True, verbose_name="최종 수정일")

    #위도 경도
    latitude    = models.FloatField(null=True, blank=True, verbose_name="위도")
    longitude   = models.FloatField(null=True, blank=True, verbose_name="경도")

    def __str__(self):
        return self.place

    def save(self, *args, **kwargs):
        if self.address and (not self.latitude or not self.longitude):
            lat, lng = get_lat_lng(self.address)
            if lat and lng:
                self.latitude = lat
                self.longitude = lng
            else:
                print(f"{self.place}의 좌표를 찾을 수 없습니다.")
        super().save(*args, **kwargs)

    class Meta:
        db_table            = 'placeBoards'
        verbose_name        = '업체 게시판'
        verbose_name_plural = '업체 게시판'
# Create your models here.
