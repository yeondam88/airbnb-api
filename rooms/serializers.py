from rest_framework import serializers
from users.serializers import RelatedUserSerializer
from .models import Room, Photo


class RoomSerializer(serializers.ModelSerializer):

    user = RelatedUserSerializer(read_only=True)
    is_fav = serializers.SerializerMethodField()

    def get_is_fav(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            if user.is_authenticated:
                return obj in user.favs.all()
        return False

    class Meta:
        model = Room
        exclude = (
            "modified",
        )
        read_only_fields = ('user', 'id', 'created', 'updated',)

    def validate(self, data):
        if self.instance:
            check_in = data.get('check_in', self.instance.check_in)
            check_out = data.get('check_out', self.instance.check_out)
        else:
            check_in = data.get('check_in')
            check_out = data.get('check_out')

        if check_in == check_out:
            raise serializers.ValidationError(
                "Not enough time between changes")
        return data
