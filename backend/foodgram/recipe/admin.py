from django.contrib import admin
from django.forms import BaseInlineFormSet, ValidationError

from .models import (
    Favourite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShoppingCart,
    Tag,
)

admin.site.register(ShoppingCart)
admin.site.register(Favourite)


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class RecipeIngredientInlineFormeset(BaseInlineFormSet):
    def clean(self) -> None:
        super().clean()
        if not any(self.errors) and not any(
            obj and not obj['DELETE'] for obj in self.cleaned_data
        ):
            raise ValidationError('Укажите хотя бы один ингредиент')


class RecipeTagInlineFormeset(BaseInlineFormSet):
    def clean(self) -> None:
        super().clean()
        if not any(self.errors) and not any(
            obj and not obj['DELETE'] for obj in self.cleaned_data
        ):
            raise ValidationError('Укажите хотя бы один тэг')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    formset = RecipeIngredientInlineFormeset
    extra = 1


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    formset = RecipeTagInlineFormeset
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author')
    list_editable = ('name',)
    list_filter = ('author', 'name')
    inlines = (RecipeIngredientInline, RecipeTagInline)
