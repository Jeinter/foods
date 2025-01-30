import re

from rest_framework.serializers import ValidationError


def validate_username(value):
    """Убедитесь, что имя пользователя не равно зарезервированным никам."""
    if value == 'me':
        raise ValidationError(f"Имя пользователя '{value}' недопустимо.")
    return value


def validate_username_bad_sign(value):
    """Валидация запрета недопустимых символов в имени пользователя"""
    invalid_chars = re.findall(r'[^\w.@+-]', value)
    if invalid_chars:
        raise ValidationError(
            f"Имя пользователя содержит недопустимые символы: "
            f"{''.join(set(invalid_chars))}"
        )
    return value
