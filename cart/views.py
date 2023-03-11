from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], update_quantity=cd['update'])
    return redirect('view_cart')


def delete_cart_item(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('view_cart')


def view_cart(request):
    cart = Cart(request)
    context = {'title': 'Shopping Cart', 'cart': cart, 'total': cart.get_total_price()}
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
                                        initial={
                                            'quantity': item['quantity'],
                                            'update': True
                                        })
    return render(request, 'cart.html', context)


@login_required
def checkout(request):
    if request.method == 'POST':
        cart = Cart(request)
        total = cart.get_total_price()
        order = Order(user=request.user, total=total)
        order.save()
        for item in cart:
            order_item = OrderItem(product=item.product, quantity=item.quantity, order=order)
            order_item.save()
        cart.clear()
        return render(request, 'checkout_success.html', {'title': 'Checkout Success'})
    else:
        return render(request, 'checkout.html', {'title': 'Checkout'})
