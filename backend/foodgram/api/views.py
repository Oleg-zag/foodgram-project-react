from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import viewsets, status
from recept.models import Favoriete
from recept.models import Tag, Ingredient, Recept, IngredientReceptlink, Cart
from .serializers import (TagSerializer,
                          IngredientSerializer, FavoriteSerializer)
from .serializers import Recept_Create_Update_Serializer, CartSerializer
from .serializers import ReceptSerializer, IngredientReceptlinkSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework import filters
from .filters import ReceptFilter, IngredientFilter
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly
                                        )
from .permissions import IsOwnerOrReadOnly
from .utils import shopping_list


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
        print(context)
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
        print(f'perform_create{serializer.data}')

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id, pk=None):
        print(request)
        user = request.user
        if not user.cart.filter(
                    recepet_id=recipe_id).exists():
            return Response({'errors': 'Рецепта нет в корзине'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            Cart,
            user_id=request.user.id,
            recepet_id=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(CartViewSet):
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        user = self.request.user
        return Favoriete.objects.filter(user=user)

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id, pk=None):
        user = request.user
        if not user.favoriet.filter(
                    recepet_id=recipe_id).exists():
            return Response({'errors': 'Рецепта нет в корзине'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            Favoriete,
            user_id=request.user.id,
            recepet_id=recipe_id).delete()
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
            return Recept_Create_Update_Serializer

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
        cart = user.cart.select_related(
            'recepet').values(
                'recepet_id__ingredients__name',
                'recepet_id__ingredients__measurement_unit',
                'recepet_id__ingredients__ingrrec__quantity')
        cart_set = []
        for obj in cart:
            cart_set.append(list(obj.values()))
        for obj in cart_set:
            print(f'тест{obj}')
        cart = shopping_list(cart_set)
        for element in range(len(cart)):
            text += (f'{cart[element]}\n')
        response = HttpResponse(text, content_type='text/plain')
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
