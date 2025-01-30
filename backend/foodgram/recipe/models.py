from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Название ингридиента'
    )
    measurement_unit = models.CharField(
        max_length=200, verbose_name='Еденицы измерения'
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Название тэга'
    )
    color = models.TextField(
        verbose_name="Цвет тэга",
        validators=[
            RegexValidator(
                regex=r"^#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$",
                message='Неправильный Hex цвет',
            ),
        ],
    )
    slug = models.SlugField(verbose_name="Ссылка тэга")

    class Meta:
        unique_together = ("name", "color", "slug")
        verbose_name = "тэг"
        verbose_name_plural = "тэги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Пользователь',
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    image = image = models.ImageField(
        upload_to='recipe/images/',
        null=True,
        default=None,
        verbose_name='Изображение',
    )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag, through='RecipeTag', related_name='recipes', verbose_name='Тэги'
    )
    cooking_time = models.IntegerField(
        blank=False,
        validators=[MinValueValidator(1)],
        verbose_name='Время готовки',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=(
            MinValueValidator(1, message='Мин. количество ингридиентов 1'),
        ),
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Рецепт с ингридиентами'
        verbose_name_plural = 'Рецепты с ингредиентами'

    def __str__(self) -> str:
        return f'{self.recipe} {self.ingredient}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tag',
        verbose_name='Рецепт',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipe_tag',
        verbose_name='Тэг',
    )

    class Meta:
        verbose_name = 'Рецепт с тэгами'
        verbose_name_plural = 'Рецепты с тэгами'

    def __str__(self) -> str:
        return f'{self.recipe} {self.tag}'


class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favourite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Корзину покупок'
