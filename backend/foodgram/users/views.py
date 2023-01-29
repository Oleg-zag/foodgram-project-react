
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscriptions, User
from .serializers import SubscriptionSerializer


class MyUserViewSet(UserViewSet):

    queryset = User.objects.all()
    pagination_class = PageNumberPagination
    #permission_classes=[permissions.IsAuthenticatedOrReadOnly]
    
    @action(
        detail=True, methods=['POST', 'DELETE'],
        url_path='subscribe',
        permission_classes=[permissions.IsAuthenticatedOrReadOnly],
    )
    def subscribe(self, request, id=None):
        user = get_object_or_404(User, id=id)
        subscription = Subscriptions.objects.filter(
            subscriber=request.user,
            subscription=user
        )
        if request.method == 'POST':
            if user == request.user:
                error = {
                    'error': 'вы не можете подписаться на себя'
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            obj, created = Subscriptions.objects.get_or_create(
                subscriber=request.user,
                subscription=user
            )
            if not created:
                error = {
                    'error': 'вы уже подписаны на пользователя'
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscriptionSerializer(
                                                obj,
                                                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not subscription.exists():
            error = {
                'error': 'Вы не подписаны на пользователя'
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['GET'],
        url_path='subscriptions',
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        pages = self.paginate_queryset(
            Subscriptions.objects.filter(subscriber_id=request.user)
        )
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class APISubscription(APIView):
    '''почемуто во фронтэнде url /subscriptions отличается от спецификации
        user/subscriptions. API написан на всякий случай.
        Подписчики на странице во фронте все равно не отображаются(
    '''
    def get(self, request):
        pages = Subscriptions.objects.filter(subscriber_id=request.user)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request}
        )
        return Response(serializer.data)
