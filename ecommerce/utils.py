import json
from .models import *

def cookieCart(request):
	#Create empty cart for now for non-logged in user
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    print('CART:', cart)
    items = []
    orden = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
    items_carrito = orden['get_cart_items']
    for i in cart:
        try:
            items_carrito += cart[i]['cantidad']
            producto = Producto.objects.get(id=i)
            total = (producto.precio * cart[i]['cantidad'])
            orden['get_cart_total'] += total
            orden['get_cart_items'] += cart[i]['cantidad']
            item = {
                'producto':{
                    'categoria':producto.categoria,
                    'id':producto.id,
                    'nombre':producto.nombre, 
                    'precio':producto.precio, 
                    'URLimagen':producto.URLimagen
                }, 
                'cantidad':cart[i]['cantidad'],
                'get_total':total,
                }
            items.append(item)
            if producto.digital == False:
                shipping = True
        except:
            pass
        if shipping:
            orden['shipping'] = shipping 
    context = {'items':items, 'orden':orden, 'items_carrito':items_carrito}
    return context

def cartData(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
        orden, created = Orden.objects.get_or_create(cliente=cliente, completada=False)
        items = orden.itemorden_set.all()
        items_carrito = orden.get_cart_items
    else:
        #Create empty cart for now for non-logged in user
        cookieData = cookieCart(request)
        items_carrito = cookieData['items_carrito']
        orden = cookieData['orden']
        items = cookieData['items']
    context = {'items':items, 'orden':orden, 'items_carrito':items_carrito}
    return context

def guestOrder(request, data):
    print('User is not logged in')
    print('COOKIES: ', request.COOKIES)
    nombre = data['form']['nombre']
    correo = data['form']['correo']
    cookieData = cookieCart(request)
    items = cookieData['items']
    cliente, created = Cliente.objects.get_or_create(correo=correo,)
    cliente.nombre = nombre
    cliente.save()
    orden = Orden.objects.create(cliente=cliente, completada=False,)
    for item in items:
        producto = Producto.objects.get(id = item['producto']['id'])
        item_orden = ItemOrden.objects.create(producto=producto, 
        orden=orden, cantidad=item['cantidad'],)
    return cliente, orden
    