from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from recipe.models import Favourite, Ingredient, Recipe, ShoppingCart, Tag

from .filters import IngredientFilter
from .permissions import IsAdminAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    RecipeMiniSerializer,
    TagSerializer,
)
from .utils import generate_action


class TagViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAdminAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeCreateSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = self.request.query_params
        is_favorited = query_params.get('is_favorited')
        if is_favorited == '1':
            queryset = queryset.filter(favorites__user=self.request.user)
        is_in_shopping_cart = query_params.get('is_in_shopping_cart')
        if is_in_shopping_cart == '1':
            queryset = queryset.filter(shopping_cart__user=self.request.user)
        tags = query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(
                recipe_tag__tag__slug__in=tags
            ).distinct()
        author = query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    shopping_cart = generate_action(
        model=ShoppingCart,
        serializer_class=RecipeMiniSerializer,
        url='shopping_cart',
        error_texts={
            'DELETE': 'Рецепта нет в козине',
            'POST': 'Рецепт уже находится в корзине',
        },
    )

    favorite = generate_action(
        model=Favourite,
        serializer_class=RecipeMiniSerializer,
        url='favorite',
        error_texts={
            'DELETE': 'Рецепта нет в списке избранных',
            'POST': 'Рецепт уже находится в списке избранных',
        },
    )

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        recipes_in_shopping_cart = ShoppingCart.objects.filter(
            user=request.user
        ).values('recipe__id')
        ingredients = Ingredient.objects.filter(
            recipes__id__in=recipes_in_shopping_cart
        ).annotate(amount=Sum('ingredient__amount'))
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=shopping_cart'
        response.writelines(
            f'{ingredient.name}: {ingredient.amount} '
            f'{ingredient.measurement_unit}\n'
            for ingredient in ingredients
        )
        return response
