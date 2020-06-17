from rest_framework import serializers
from users.serializers import UserSerializer
from .models import Room, Photo


class RoomSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Room
        fields = ("name", "price", "instant_book", "user")
