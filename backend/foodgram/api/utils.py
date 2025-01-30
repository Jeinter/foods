from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from recipe.models import Recipe


def generate_action(
    model,
    serializer_class,
    url: str,
    error_texts: dict[str, str],
):
    def action_func(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if model.objects.filter(user=user, recipe=recipe).exists():
                raise ValidationError(error_texts['POST'])
            model.objects.create(user=user, recipe=recipe)
            serializer = serializer_class(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not model.objects.filter(user=user, recipe=recipe).exists():
                raise ValidationError(error_texts['DELETE'])
            model.objects.filter(recipe=recipe, user=user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    action_func.__name__ = url
    return action(
        methods=['post', 'delete'],
        detail=True,
        serializer_class=serializer_class,
        url_path=url,
    )(action_func)
