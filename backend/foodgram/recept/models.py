from django.db import models

from users.models import User

from django.core.validators import MinValueValidator


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
                models.UniqueConstraint(
                    fields=('name', 'measurement_unit'),
                    name='unique ingredients')]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Наименование тэга',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет',
    )
    slug = models.SlugField(max_length=200,  unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tэги'
        verbose_name_plural = 'Тэги'


class Recept(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recept',
        verbose_name='Тэг',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recept',
        verbose_name='Автор',
    )
    time_create = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    time_update = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )

    image = models.ImageField(
        upload_to='image/',
        blank=True,
        verbose_name='Фото',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.IntegerField(
        validators=[
            MinValueValidator(1)
        ],
        verbose_name='Время приготовления',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        null=False,
        through="IngredientReceptlink",
        verbose_name='Ингредиенты',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепты'
        verbose_name_plural = 'Рецепты'


class IngredientReceptlink(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recept = models.ForeignKey(
        Recept,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingrrec',
    )
    amount = models.FloatField(
        verbose_name='Кол-во',
        validators=[
            MinValueValidator(0.1)
        ]
        )

    class Meta:
        verbose_name = 'Кол-во ингридиента в рецепте'
        verbose_name_plural = 'Кол-во ингридиента в рецепте'
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=('recept', 'ingredient'),
        #         name='unique ingredient')]


class Favoriete(models.Model):
    recepet = models.ForeignKey(
        Recept,
        unique=False,
        on_delete=models.CASCADE,
        related_name='favoriet',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favoriet',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class Cart(models.Model):
    recepet = models.ForeignKey(
        Recept,
        unique=True,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт',)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Автор',

    )

    def __str__(self):
        return f'{self.user} {self.recepet}'

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
