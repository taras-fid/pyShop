from django.shortcuts import render, redirect
from django.urls import reverse
from .models import CartItem, Product, Cart, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def view_cart(request):
    cart = CartItem.objects.all()
    total = sum([item.product.price * item.quantity for item in cart])
    context = {'title': 'Shopping Cart', 'cart': cart, 'total': total}
    return render(request, 'cart.html', context)


@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(pk=product_id)
        quantity = int(request.POST.get('quantity', 1))
        cart = Cart.objects.get(user=request.user)
        try:
            # If these item is new for the cart.
            cart_item = CartItem.objects.get(product=product)
            cart_item.quantity = cart_item.quantity + quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            # If these item is already in the cart.
            item = CartItem(product=product, quantity=quantity, cart=cart)
            item.save()
    else:
        return redirect(reverse('home'))
    return redirect(reverse('view_cart'))


@login_required
def delete_cart_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id)
        # Check if the cart item belongs to the current user
        if cart_item.cart.user != request.user:
            raise CartItem.DoesNotExist
        cart_item.delete()
        messages.success(request, "Item deleted from cart.")
    except CartItem.DoesNotExist:
        messages.error(request, "Cart item not found.")
    return redirect('view_cart')


@login_required
def checkout(request):
    if request.method == 'POST':
        cart_obj = Cart.objects.filter(user=request.user.id)
        cart = CartItem.objects.filter(cart=cart_obj.first())
        total = sum([item.product.price * item.quantity for item in cart])
        order = Order(user=request.user, total=total)
        order.save()
        for item in cart:
            order_item = OrderItem(product=item.product, quantity=item.quantity, order=order)
            order_item.save()
        cart.delete()
        return render(request, 'checkout_success.html', {'title': 'Checkout Success'})
    else:
        return render(request, 'checkout.html', {'title': 'Checkout'})