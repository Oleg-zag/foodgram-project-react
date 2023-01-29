from django.db.models import Q
from django_filters import rest_framework as filters
from recept.models import Ingredient, Recept, Tag

RECEPT_CHOICES = (
    (0, "нет в списке"),
    (1, "в списке"),
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
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=RECEPT_CHOICES,
        # по спецификации QUERY PARAMETERS integer Enum 0 1
        method='get_favorite'
    )
    is_favorited = filters.ChoiceFilter(
        choices=RECEPT_CHOICES,
        # по спецификации QUERY PARAMETERS integer Enum 0 1
        method='get_favorite'
    )

    def get_favorite(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value == '1':
                if name == 'is_favorited':
                    return queryset.filter(favoriet__user=user)
                if name == 'is_in_shopping_cart':
                    return queryset.filter(cart__user=user)
        # return queryset

    class Meta:
        model = Recept
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
