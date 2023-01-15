import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recept.models import (Cart, Favoriete, Ingredient, IngredientReceptlink,
                           Recept, Tag,)
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
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        )
    amount = serializers.FloatField(source='quantity')

    class Meta:
        model = IngredientReceptlink
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ReceptSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = MyUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientReceptlinkSerializer(
        read_only=True,
        many=True,
        source='ingrrec',
    )
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recept
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'image', 'name',
                  'text', 'cooking_time',)

    def get_is_favorited(self, obj):
        if Favoriete.objects.filter(recepet_id=obj.id).count() == 0:
            return False
        return True

    def get_is_in_shopping_cart(self, obj):
        if Cart.objects.filter(recepet_id=obj.id).count() == 0:
            return False
        return True


class Recept_Create_Update_Serializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())
    ingredients = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recept
        fields = ('tags', 'ingredients', 'image',
                  'name',
                  'text', 'cooking_time',)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recept = Recept.objects.create(**validated_data)
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient)
            IngredientReceptlink.objects.create(
                ingredient=current_ingredient, recept=recept
            )
        return recept


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
