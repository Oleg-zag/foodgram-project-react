from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """ Кастомная модель пользователя. """

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        blank=False,
        null=False,
        max_length=254,
        unique=True)
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False,
        null=False,
        )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False,
        null=False,
        )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
        )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
        )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', ]

    class Meta:
        ordering = ['-pk']
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    subscription = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='Пользователь',
    )

    class Meta:
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['subscriber', 'subscription'],
        #         name='unique_subscriber',
        #     ),
        #     models.CheckConstraint(
        #         check=~models.Q(subscriber=models.F('subscription')),
        #         name='subscriber_not_equals_subscription',
        #     ),
        # ]
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.subscriber} - {self.subscription}'
