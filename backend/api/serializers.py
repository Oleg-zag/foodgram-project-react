import base64

from django.db.models import F

from django.core.files.base import ContentFile
from rest_framework.fields import IntegerField
from recept.models import (Cart, Favoriete, Ingredient, IngredientReceptlink,
                           Recept, Tag)
from rest_framework import serializers
from users.serializers import MyUserSerializer
from rest_framework.exceptions import ValidationError


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('__all__')


class IngredientReceptlinkSerializer(serializers.ModelSerializer):
    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientReceptlink
        fields = ('id', 'amount')


class ReceptSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = MyUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recept
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'image', 'name',
                  'text', 'cooking_time',)

    def get_ingredients(self, obj):
        recept = obj
        ingredients = recept.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientreceptlink__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (not user.is_anonymous
                and obj.favoriet.filter(user=user).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (not user.is_anonymous
                and obj.cart.filter(user=user).exists())


class ReceptCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientReceptlinkSerializer(
        many=True,
    )
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recept
        fields = ('tags', 'ingredients', 'image',
                  'name',
                  'text', 'cooking_time',)

    def validate_name(self, value):
        name = self.context.get('name')
        user = self.context.get('request').user
        if Recept.objects.filter(author=user, name=name).exists() is True:
            raise ValidationError({
                'У Вас уже есть рецепт с таким именем'
            })
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recept = Recept.objects.create(**validated_data)
        recept.tags.set(tags)
        self.get_ingredients(recept, ingredients)
        return recept

    @staticmethod
    def get_ingredients(recept, ingredients):
        IngredientReceptlink.objects.bulk_create(
            [IngredientReceptlink(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recept=recept,
                amount=ingredient['amount']
            )for ingredient in ingredients]
        )

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.get_ingredients(recept=instance, ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, recept):
        return ReceptSerializer(recept, context={
            'request': self.context.get('request')
        }).data


class ReceptCartFavSerializers(serializers.ModelSerializer):

    class Meta:
        model = Recept
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class CartSerializer(serializers.ModelSerializer):
    recepet = ReceptCartFavSerializers(read_only=True)

    class Meta:
        model = Cart
        fields = ('recepet',)

    def validate(self, data):
        user = self.context.get('request').user
        recept = self.context.get('recepet_id')
        if Cart.objects.filter(
                user=user, recepet=recept).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже добавлен в список покупок'})
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    recepet = ReceptCartFavSerializers(read_only=True)

    class Meta:
        model = Favoriete
        fields = ('recepet',)

    def validate(self, data):
        user = self.context.get('request').user
        recept = self.context.get('recepet_id')
        if Favoriete.objects.filter(
                user=user, recepet=recept).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже добавлен в список избранного'})
        return data
