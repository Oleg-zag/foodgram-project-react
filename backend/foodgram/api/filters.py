from django.db.models import Q
from django_filters import rest_framework as filters

from recept.models import Cart, Favoriete, Ingredient, Recept, Tag

from .utils import fav_cart_queryset

RECEPT_CHOICES = (
    (0, 'нет'),
    (1, 'да'),
)


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ['name', ]

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value))


class ReceptFilter(filters.FilterSet):
    author = filters.NumberFilter(
        field_name='author__id',
        lookup_expr='exact'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_in_shopping_cart = filters.BooleanFilter(
        # choices=RECEPT_CHOICES,
        # по спецификации QUERY PARAMETERS integer Enum 0 1
        method='get_favorite'
    )
    is_favorited = filters.BooleanFilter(
        # choices=RECEPT_CHOICES,
        # по спецификации QUERY PARAMETERS integer Enum 0 1
        method='get_cart'
    )

    def get_favorite(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value is True:
                qs = Favoriete.objects.filter(
                    user_id=user.id).values('recepet_id')
                return fav_cart_queryset(qs, queryset)
        return queryset

    def get_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value is True:
                qs = Cart.objects.filter(
                    user_id=user.id).values('recepet_id')
                return fav_cart_queryset(qs, queryset)
        return queryset

    class Meta:
        model = Recept
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
