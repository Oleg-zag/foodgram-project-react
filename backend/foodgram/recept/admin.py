from django.contrib import admin

from .models import (Cart, Favoriete, Ingredient, IngredientReceptlink, Recept,
                     Tag)


class FavorieteAdmin(admin.ModelAdmin):
    pass


class IngredientAdmin(admin.ModelAdmin):
    search_fildes = ('name',)
    list_display = ('name', 'measurement_unit')


class TagAdmin(admin.ModelAdmin):
    pass


class IngredientReceptlinkAdminInline(admin.TabularInline):
    model = IngredientReceptlink
    extra = 1


class ReceptAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name', 'author__username', 'author__last_name',
                     'tags__name', 'tags_slug', 'author__first_name')
    inlines = (IngredientReceptlinkAdminInline,)

    fieldsets = (
        ('Данные', {
            'fields': (
                'name', 'author', 'image', 'tags',
                'text', 'cooking_time',
                'time_create', 'time_update',
            )
        }),
        ('Счетчик избранного и покупок', {
            'fields': (
                'favorite_count', 'cart_count'
            )
        }),
    )
    readonly_fields = ('favorite_count',
                       'cart_count', 'time_create', 'time_update')
    filter_horizontal = ('tags',)

    def favorite_count(self, obj):
        return obj.favorites.count()

    def cart_count(self, obj):
        return obj.cart.count()

    favorite_count.short_description = "Рецепт добавлен в избранное:"
    cart_count.short_description = "Рецепт добавлен в список покупок:"


class CartAdmin(admin.ModelAdmin):
    pass


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recept, ReceptAdmin)
admin.site.register(Favoriete, FavorieteAdmin)
admin.site.register(Cart, CartAdmin)
