from django.db import models

class Participant(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='기본키') # 기본키(Primary Key)
    name = models.CharField(max_length=100, verbose_name='이름') # 이름
    num = models.CharField(max_length=20,verbose_name='전화번호') # 전화번호
    # mail = models.EmailField(verbose_name='이메일') # 이메일
    receiptImage  = models.ImageField(upload_to='photos/', verbose_name="영수증 사진",default='photos/default_image.jpg')
    placeId = models.IntegerField(verbose_name='업체 기본키') # 업체 기본값
    dupl = models.BooleanField(default=False) # 중복 참여 여부
    date = models.DateTimeField(auto_now_add=True) # 참여일

    def __str__(self):
        return self.name

    class Meta:
        db_table            = 'event_participants'
        verbose_name        = '이벤트 참여자'
        verbose_name_plural = '이벤트 참여자'