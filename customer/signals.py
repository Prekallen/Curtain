from django.db.models.signals import post_save
from django.dispatch import receiver
from customer.models import Customer
from contract.models import Contract  # Contract 모델은 contract 앱에 있다고 가정

@receiver(post_save, sender=Customer)
def update_related_contracts_on_customer_update(sender, instance, **kwargs):
    """Customer 정보가 저장된 후 연결된 Contract 모델의 고객 정보를 업데이트합니다."""
    if not kwargs['created']:  # Customer가 새로 생성된 경우가 아니라 업데이트된 경우에만 실행
        contracts = Contract.objects.filter(custom_id=instance)
        for contract in contracts:
            contract.customer = instance.name
            contract.phone = instance.phone
            contract.address = instance.address
            contract.save()