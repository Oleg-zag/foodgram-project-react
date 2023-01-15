from django.db.models import Q
from django_filters import rest_framework as filters

from recept.models import Cart, Favoriete, Ingredient, Recept, Tag

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
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=RECEPT_CHOICES,
        method='get_favorite_cart'
    )
    is_favorited = filters.ChoiceFilter(
        choices=RECEPT_CHOICES,
        method='get_favorite_cart'
    )

    def get_favorite_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value == '1':
                if name == 'is_favorited':
                    receptid = []
                    fav = Favoriete.objects.filter(
                        user_id=user.id).values('recepet_id')
                    for obj in fav:
                        receptid.append(obj['recepet_id'])
                    return queryset.filter(id__in=receptid)
                if name == 'is_in_shopping_cart':
                    receptid = []
                    cart = Cart.objects.filter(
                        user_id=user.id).values('recepet_id')
                    for obj in cart:
                        receptid.append(obj['recepet_id'])
                    return queryset.filter(id__in=receptid)
        return queryset

    class Meta:
        model = Recept
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
