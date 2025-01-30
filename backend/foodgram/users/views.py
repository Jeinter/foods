from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import FollowUserSerializer

from .models import Follow, User


class FollowPagination(PageNumberPagination):
    page_size = 6


class UserViewSet(UserViewSet):
    http_method_names = ['get', 'post']
    pagination_class = FollowPagination

    @action(
        detail=False,
        methods=['GET'],
        serializer_class=FollowUserSerializer,
    )
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=self.request.user)
        b = []
        for follow in queryset:
            b.append(follow.author.id)
        users_queryset = User.objects.filter(id__in=b)
        page = self.paginate_queryset(users_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class FollowApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def post(self, request, author_id):
        author = User.objects.get(id=author_id)
        if author.id == request.user.id:
            raise ValidationError('Нельзя подписаться на самого себя')
        if Follow.objects.filter(author=author, user=request.user).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя')
        Follow.objects.create(author=author, user=request.user)
        context = {'request': request}
        serialiser = FollowUserSerializer(author, context=context)
        return Response(serialiser.data, status=status.HTTP_201_CREATED)

    def delete(self, request, author_id):
        author = User.objects.get(id=author_id)
        if not Follow.objects.filter(
            author=author, user=request.user
        ).exists():
            raise ValidationError(
                'Вы не можете отписаться от этого пользователя,'
                'так как вы не подписаны на него'
            )
        Follow.objects.get(author=author, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
