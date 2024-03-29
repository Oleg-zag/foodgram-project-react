# Generated by Django 2.2.28 on 2023-01-03 13:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название ингредиента')),
                ('measurement_unit', models.CharField(max_length=200, verbose_name='Еденица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиенты',
                'verbose_name_plural': 'Ингредиенты',
            },
        ),
        migrations.CreateModel(
            name='IngredientReceptlink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField(verbose_name='Кол-во')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient', to='recept.Ingredient', verbose_name='Ингредиент')),
            ],
            options={
                'verbose_name': 'Кол-во ингридиента в рецепте',
                'verbose_name_plural': 'Кол-во ингридиента в рецепте',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Наименование тэга')),
                ('color', models.CharField(max_length=7, unique=True, verbose_name='Цвет')),
                ('slug', models.SlugField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name': 'Tэги',
                'verbose_name_plural': 'Тэги',
            },
        ),
        migrations.CreateModel(
            name='Recept',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название рецепта')),
                ('time_create', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('time_update', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('favorite_count', models.IntegerField(default=0)),
                ('cart_count', models.IntegerField(default=0)),
                ('image', models.ImageField(blank=True, upload_to='image/', verbose_name='Фото')),
                ('text', models.TextField(verbose_name='Описание')),
                ('cooking_time', models.IntegerField(verbose_name='Время приготовления')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recept', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('ingredient', models.ManyToManyField(through='recept.IngredientReceptlink', to='recept.Ingredient', verbose_name='Ингредиенты')),
                ('tags', models.ManyToManyField(related_name='recept', to='recept.Tag', verbose_name='Тэг')),
            ],
            options={
                'verbose_name': 'Рецепты',
                'verbose_name_plural': 'Рецепты',
            },
        ),
        migrations.AddField(
            model_name='ingredientreceptlink',
            name='recept',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recept.Recept', verbose_name='Рецепт'),
        ),
        migrations.CreateModel(
            name='Favoriete',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recepet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favoriet', to='recept.Recept', unique=True, verbose_name='Рецепт')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favoriet', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'Избранное',
                'verbose_name_plural': 'Избранное',
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recepet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='recept.Recept', unique=True, verbose_name='Рецепт')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'Корзина',
                'verbose_name_plural': 'Корзина',
            },
        ),
    ]
