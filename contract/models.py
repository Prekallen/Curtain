from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError

def calculate_item_total_price(size, unit_price, quantity):
    """아이템의 총 가격을 계산하여 반환합니다."""
    return size * unit_price * quantity

class Contract(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='기본키')
    # on_delete=models.CASCADE Customer가 삭제 되면 Contract도 삭제
    custom_id = models.ForeignKey('customer.Customer', on_delete=models.CASCADE, related_name='contracts')
    customer = models.CharField(max_length=100, blank=True, null=True, verbose_name='고객명')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='전화번호')
    address = models.TextField( verbose_name='주소')
    price = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='총액', default=0)
    down_pay = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='계약금', default=0)
    balance = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='잔금', default=0)
    manager = models.ForeignKey('manager.Manager', on_delete=models.SET_NULL, null=True, verbose_name='작성 담당자')
    writer = models.CharField(max_length=100, blank=True, null=True, verbose_name='작성자')
    writer_phone = models.CharField(max_length=20, verbose_name='작성자_전화번호')
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='주문 일자')
    updated_at  = models.DateTimeField(auto_now=True, verbose_name='마지막 수정일')
    const_date = models.DateTimeField(verbose_name='시공일', null=True, blank=True)
    CONST_TIME_CHOICES = [
        ('morning', '오전 (09:00 ~ 12:00)'),
        ('afternoon', '오후 (13:00 ~ 18:00)'),
        ('evening', '저녁 (19:00 이후)'),
        ('specific', '특정 시간'),
    ]
    const_preferred_time = models.CharField(
        max_length=10,
        verbose_name="시공 희망 시간대",
        choices=CONST_TIME_CHOICES,
        null=True,
        blank=True
    )
    specific_const_time = models.TimeField(
        verbose_name="특정 시공 시간",
        null=True,
        blank=True
    )
    complete = models.BooleanField(verbose_name='완료 여부', default=False)

    def __str__(self):
        return f"{self.id} - {self.customer or '고객 정보 없음'}"

    def clean(self):
        super().clean()
        if self.const_date and self.create_at and self.const_date < self.create_at:
            raise ValidationError({'const_date': '시공일은 계약일보다 이전일 수 없습니다.'})

    def save(self, *args, **kwargs):
        if self.custom_id:
            self.customer = self.custom_id.name
            self.phone = self.custom_id.phone
            self.address = self.custom_id.address
        # 잔금 계산 및 저장
        self.balance = self.price - self.down_pay
        super().save(*args, **kwargs)

    def update_price(self):
        """연결된 품목들의 총 가격을 합산하여 업데이트합니다."""
        inner_curtain_total = self.inner_curtains.aggregate(Sum('total_price'))['total_price__sum'] or 0
        outer_curtain_total = self.outer_curtains.aggregate(Sum('total_price'))['total_price__sum'] or 0
        blind_total = self.blinds.aggregate(Sum('total_price'))['total_price__sum'] or 0
        etc_total = self.etc.aggregate(Sum('total_price'))['total_price__sum'] or 0
        self.price = inner_curtain_total + outer_curtain_total + blind_total + etc_total
        super().save()

    class Meta:
        db_table            = 'contract'
        verbose_name        = '계약'
        verbose_name_plural = '계약'

class InnerCurtain(models.Model):   # 속 커튼
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='inner_curtains')
    name = models.CharField(max_length=100, verbose_name='속 커튼 이름')
    size = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='치수')
    width = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='폭', null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='높이', null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='단가')
    quantity = models.IntegerField(verbose_name='수량', default=1)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='총 가격', null=True, blank=True)

    def calculate_total_price(self):
        return calculate_item_total_price(self.size, self.unit_price, self.quantity)

    def save(self, *args, **kwargs):
        self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)
        self.contract.update_price()

    class Meta:
        unique_together = ('contract', 'name', 'size')

class OuterCurtain(models.Model): # 겉 커튼
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='outer_curtains')
    name = models.CharField(max_length=100, verbose_name='속 커튼 이름')
    size = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='치수')
    width = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='폭', null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='높이', null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='단가')
    quantity = models.IntegerField(verbose_name='수량', default=1)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='총 가격', null=True, blank=True)

    def calculate_total_price(self):
        return calculate_item_total_price(self.size, self.unit_price, self.quantity)

    def save(self, *args, **kwargs):
        self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)
        self.contract.update_price()

    class Meta:
        unique_together = ('contract', 'name', 'size')

class Blind(models.Model): # 블라인드
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='blinds')
    name = models.CharField(max_length=100, verbose_name='속 커튼 이름')
    size = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='치수')
    width = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='폭', null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='높이', null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='단가')
    quantity = models.IntegerField(verbose_name='수량', default=1)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='총 가격', null=True, blank=True)

    def calculate_total_price(self):
        return calculate_item_total_price(self.size, self.unit_price, self.quantity)

    def save(self, *args, **kwargs):
        self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)
        self.contract.update_price()

    class Meta:
        unique_together = ('contract', 'name', 'size')

class Etc(models.Model): # 기타
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='etc')
    name = models.CharField(max_length=100, verbose_name='속 커튼 이름')
    size = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='치수')
    width = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='폭', null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='높이', null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='단가')
    quantity = models.IntegerField(verbose_name='수량', default=1)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='총 가격', null=True, blank=True)

    def calculate_total_price(self):
        return calculate_item_total_price(self.size, self.unit_price, self.quantity)

    def save(self, *args, **kwargs):
        self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)
        self.contract.update_price()

    class Meta:
        unique_together = ('contract', 'name', 'size')

