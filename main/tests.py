from django.test import TestCase


# Create your tests here.
from construction.models import Construction

places = Construction.objects.all()

for place in places:
    if not place.latitude or not place.longitude:
        place.save()
        print(f"{place.place}의 좌표가 업데이트되었습니다.")
