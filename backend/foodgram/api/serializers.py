import base64

from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipe.models import (
    Favourite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.serializers import ListUserSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class FollowUserSerializer(ListUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        fields = ListUserSerializer.Meta.fields + ('recipes', 'recipes_count')
        model = ListUserSerializer.Meta.model

    def get_recipes(self, user):
        recipes = user.recipes.all()
        limit = self.context['request'].query_params.get('recipes_limit', 0)
        try:
            limit_int = int(limit)
        except ValueError:
            raise ValidationError('limit должен быть числом')
        if limit_int > 0:
            recipes = recipes[:limit_int]
        serializer = RecipeMiniSerializer(recipes, many=True)
        return serializer.data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, required=True, source='recipe'
    )
    author = ListUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        model = Recipe
        read_only_fields = ('__all__',)

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and Favourite.objects.filter(user=user, recipe=recipe).exists()
        )

    def get_image(self, obj):
        return obj.image.url

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(user=user, recipe=recipe).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(required=True)

    class Meta:
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        model = Recipe

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError('Укажите ингрединты.')
        unique_ingredients = set(
            ingredient['id'] for ingredient in ingredients
        )
        if len(ingredients) != len(unique_ingredients):
            raise serializers.ValidationError(
                'Ингридиенты должны быть уникальными.'
            )
        return ingredients

    def create_ingredient(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            (
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient['id'],
                    amount=ingredient['amount'],
                )
                for ingredient in ingredients
            ),
            batch_size=100,
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredient(recipe, ingredients_data)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().update(recipe, validated_data)
        if ingredients_data:
            recipe.ingredients.clear()
            self.create_ingredient(recipe, ingredients_data)
        if tags:
            recipe.tags.set(tags)
        recipe.save()
        return recipe

    def to_representation(self, instance):
        context = {'request': self.context['request']}
        return RecipeListSerializer(instance, context=context).data
