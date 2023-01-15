def shopping_list(cart):
    cart.sort()
    for obj in cart:
        print(obj)
    for i in range(len(cart)):
        j = i
        while j < len(cart)-1 and cart[j][0] == cart[j+1][0]:
            cart[j+1][2] += cart[j][2]
            cart.pop(j)
    return cart
