from api import views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.ReceptViewSet)
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart', views.CartViewSet,
                basename='shoppingcart')
router.register(r'recipes/(?P<recipe_id>\d+)/favorite', views.FavoriteViewSet,
                basename='favorite')
urlpatterns = [
    path('', include(router.urls))
]
