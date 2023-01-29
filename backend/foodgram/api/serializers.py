import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recept.models import (Cart, Favoriete, Ingredient, IngredientReceptlink,
                           Recept, Tag)
from users.serializers import MyUserSerializer


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
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        )
    name = serializers.ReadOnlyField(required=False, source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        required=False,
        source='ingredient.measurement_unit',
       )
    # amount = serializers.FloatField(source='quantity')

    class Meta:
        model = IngredientReceptlink
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ReceptSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = MyUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientReceptlinkSerializer(   
        many=True,
        source='ingrrec',
    )
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recept
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'image', 'name',
                  'text', 'cooking_time',)

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
        source='ingrrec',
    )
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recept
        fields = ('tags', 'ingredients', 'image',
                  'name',
                  'text', 'cooking_time',)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingrrec')
        tags = validated_data.pop('tags')
        recept = Recept.objects.create(**validated_data)
        recept.tags.set(tags)
        self.get_ingredients(recept, ingredients)
        return recept

    @staticmethod
    def get_ingredients(recept, ingredients):
        ingredient_list = []
        for ingredient_data in ingredients:
            print(ingredient_data)
            ingredient_list.append(
                IngredientReceptlink(
                    ingredient=ingredient_data.pop('id'),
                    amount=ingredient_data.pop('amount'),
                    recept=recept,
                )
            )
        IngredientReceptlink.objects.bulk_create(ingredient_list)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = (
            validated_data.get('cooking_time', instance.cooking_time)
        )
        instance.tags.set(validated_data.get('tags', instance.tags))
        instance.ingredients.clear()
        instance.save()
        ingredients = validated_data.pop('ingrrec')
        self.get_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

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
