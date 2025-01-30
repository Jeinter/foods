from djoser import serializers as djoser_serializer
from rest_framework import serializers

from users.models import Follow, User


class ListUserSerializer(djoser_serializer.UserSerializer):
    is_subscribed = serializers.SerializerMethodField('check_subscribed')

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        model = User

    def check_subscribed(self, author):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and Follow.objects.filter(author=author, user=user).exists()
        )


class CreateUserSerializer(djoser_serializer.UserCreateSerializer):
    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        model = User
