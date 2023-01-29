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

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'id', 'username',
                  'first_name', 'last_name',
                  'password', 'is_subscribed' ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_is_subscribed(self, username):
        user = self.context["request"].user
        return (not user.is_anonymous
                and Subscriptions.objects.filter(
                    subscriber=user,
                    subscription=username
                ).exists())


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
