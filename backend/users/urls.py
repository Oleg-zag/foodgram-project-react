from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import APISubscription, MyUserViewSet

router = DefaultRouter()
router.register('users', MyUserViewSet, basename='users')
urlpatterns = [
    path('subscriptions/', APISubscription.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('drf-auth/', include('rest_framework.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
