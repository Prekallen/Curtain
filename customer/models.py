from django.db import models

class Customer(models.Model):
    id                  = models.AutoField(primary_key=True, verbose_name='기본키')
    name                = models.CharField(max_length=100, verbose_name='고객명')
    phone               = models.CharField(max_length=20, verbose_name='전화번호')
    region_level1       = models.CharField(max_length=50, verbose_name="광역시/도", blank=True, null=True)
    region_level2       = models.CharField(max_length=50, verbose_name="시/군/구", blank=True, null=True)
    region_level3       = models.CharField(max_length=50, verbose_name="읍/면/동", blank=True, null=True)
    detailed_address    = models.CharField(max_length=100, verbose_name="상세 주소")
    address             = models.TextField(max_length=100, verbose_name="주소", blank=True, null=True)
    create_at           = models.DateTimeField(auto_now_add=True, verbose_name='요청일')
    visit_schedule      = models.DateTimeField(verbose_name="방문 예정일", null=True, blank=True)
    VISIT_TIME_CHOICES = [
        ('morning', '오전 (09:00 ~ 12:00)'),
        ('afternoon', '오후 (13:00 ~ 18:00)'),
        ('evening', '저녁 (19:00 이후)'),
        ('specific', '특정 시간'),
    ]
    visit_preferred_time = models.CharField(
        max_length=10,
        verbose_name="방문 희망 시간대",
        choices=VISIT_TIME_CHOICES,
        null=True,
        blank=True
    )
    specific_visit_time = models.TimeField(
        verbose_name="특정 방문 시간",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table            = 'customer'
        verbose_name        = '고객'
        verbose_name_plural = '고객'