from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username, validate_username_bad_sign

MAX_CHAR_LENGTH = 150
MAX_EMAIL_LENGTH = 254


class User(AbstractUser):
    username = models.CharField(
        max_length=MAX_CHAR_LENGTH,
        unique=True,
        blank=False,
        validators=[validate_username, validate_username_bad_sign],
        verbose_name='Никнэйм'
    )
    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        blank=False,
        verbose_name='Почта'
    )
    first_name = models.CharField(
        max_length=MAX_CHAR_LENGTH,
        blank=False,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=MAX_CHAR_LENGTH,
        blank=False,
        verbose_name='Фамилия',
    )
    password = models.CharField(
        max_length=MAX_CHAR_LENGTH,
        blank=False,
        verbose_name='Пароль',
    )

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'{self.username} - {self.first_name} {self.last_name}'


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_following'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
