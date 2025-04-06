from django.test import TestCase

# Create your tests here.
from placeBoard.models import PlaceBoard

places = PlaceBoard.objects.all()
for place in places:
    print(f"{place.place} - 위도: {place.latitude}, 경도: {place.longitude}")