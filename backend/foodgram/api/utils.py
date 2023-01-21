def shopping_list(cart):
    '''
        функция сортирует список, в цикле проверяет совпадение
        элементов списка по первому эелементу подсписков,
        если совпадение есть, cуммирует вторые элементы подсписка
        сраниваемых элементов списка в исходном элемнте, а срвниваемый
        элемент удаляет
    '''
    cart.sort()
    for object in range(len(cart)):
        compr = object
        while compr < len(cart)-1 and cart[compr][0] == cart[compr+1][0]:
            cart[compr+1][2] += cart[compr][2]
            cart.pop(compr)
    return cart


def fav_cart_queryset(qs, queryset):
    '''
        функция возвращает отфильтрованный  QS
        рецептов,  если в запросе есть фильтр по
        рецептам в корзине, либо по рецептам в избранном,
        либо по рецептам и в избранном и в корзине
    '''
    receptid = []
    for obj in qs:
        receptid.append(obj['recepet_id'])
    return queryset.filter(id__in=receptid)
