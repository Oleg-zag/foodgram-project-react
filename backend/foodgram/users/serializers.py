from djoser.serializers import UserSerializer
from rest_framework import serializers

from recept.models import Recept

from .models import Subscriptions, User


class ReceptMinified(serializers.ModelSerializer):

    class Meta:
        model = Recept
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class MyUserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ['email', 'id', 'username',
                  'first_name', 'last_name',
                  'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def to_representation(self, obj):
        user = self.context['request'].user
        representation = super().to_representation(obj)
        representation['is_subscribed'] = Subscriptions.objects.filter(
            subscriber=user, subscription=obj
        ).exists()
        return representation


class SubscriptionSerializer(serializers.ModelSerializer):

    email = serializers.ReadOnlyField(source='subscription.email')
    id = serializers.ReadOnlyField(source='subscription.id')
    username = serializers.ReadOnlyField(source='subscription.username')
    first_name = serializers.ReadOnlyField(source='subscription.first_name')
    last_name = serializers.ReadOnlyField(source='subscription.last_name')
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes_count', 'recipes',
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes_count(self, obj):
        return obj.subscription.recept.count()

    def get_recipes(self, obj):
        recepts = obj.subscription.recept.all()[:3]
        return ReceptMinified(recepts, many=True).data
