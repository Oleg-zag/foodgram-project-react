from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recept.models import (Cart, Favoriete, Ingredient, IngredientReceptlink,
                           Recept, Tag)

from .filters import IngredientFilter, ReceptFilter
from .permissions import IsOwnerOrReadOnly
from .serializers import (CartSerializer, FavoriteSerializer,
                          IngredientReceptlinkSerializer, IngredientSerializer,
                          ReceptCreateUpdateSerializer, ReceptSerializer,
                          TagSerializer)


class CreateDeleteViewset(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    pass


class CartViewSet(CreateDeleteViewset):
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recepet_id'] = self.kwargs.get('recipe_id')
        return context

    def perform_create(self, serializer):
        id = self.kwargs.get('recipe_id')
        serializer.save(
            user=self.request.user,
            recepet=get_object_or_404(
               Recept,
               id=id
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id, pk=None):
        user = request.user
        model = user.cart.filter(
                    recepet_id=recipe_id)
        error = {'errors': 'Рецепта нет в корзине'}
        return cart_fav_delete(model, error)


class FavoriteViewSet(CartViewSet):
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        user = self.request.user
        return Favoriete.objects.filter(user=user)

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id, pk=None):
        user = self.request.user
        model = user.favoriet.filter(
            recepet_id=recipe_id, user_id=user.id)
        error = {'errors': 'Рецепта нет в избранном'}
        return cart_fav_delete(model, error)


def cart_fav_delete(model, error):
    if model.exists() is False:
        return Response(error,
                        status=status.HTTP_400_BAD_REQUEST)
    model.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientReceptlinkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IngredientReceptlink.objects.all()
    serializer_class = IngredientReceptlinkSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = IngredientFilter
    filterset_fields = ('name', )


class ReceptViewSet(viewsets.ModelViewSet):
    queryset = Recept.objects.all()
    serializer_class = ReceptSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    search_fields = ['author__username']
    ordering_fields = ['-time_update']
    serializer_class = (ReceptSerializer)
    filterset_class = ReceptFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReceptSerializer
        else:
            return ReceptCreateUpdateSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = (AllowAny,)
        elif self.action in ('update', 'destroy', 'partial_update'):
            permission_classes = (IsOwnerOrReadOnly,)
        else:
            permission_classes = (IsAuthenticated,)
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        pagination_class=None)
    def download_file(self, request):
        user = request.user
        if Cart.objects.filter(user_id=user.id).exists() is False:
            return Response(
                'В корзине нет товаров', status=status.HTTP_400_BAD_REQUEST)
        text = 'Список покупок:\n\n'
        cart = IngredientReceptlink.objects.filter(
            recept__cart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            Sum('quantity')
        ).order_by('ingredient')
        for element in cart:
            print(element)
            list = []
            for subelemet in element:
                list.append(element[subelemet])
            text += (f'{list}\n')
        response = HttpResponse(text, content_type='text/plain')
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
