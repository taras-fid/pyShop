from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Product, CartItem, Order, Cart, OrderItem
from django.contrib.auth import get_user_model, authenticate, login as Dlogin, logout as Dlogout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
# TODO delete logging
import logging
logger = logging.getLogger('django')


def home(request):
    products = Product.objects.all()
    user_id = request.user.id
    context = {'title': 'pyShop', 'description': 'Buy needs online!', 'products': products, 'user_id': user_id}
    return render(request, 'home.html', context)


def view_cart(request):
    cart = CartItem.objects.all()
    total = sum([item.product.price * item.quantity for item in cart])
    context = {'title': 'Shopping Cart', 'cart': cart, 'total': total}
    return render(request, 'cart.html', context)


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


# User views
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                Dlogin(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            Dlogin(request, user)
            Cart(user=user).save()
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def logout(request):
    user = User.objects.get(id=request.user.id)
    cart = Cart.objects.filter(user=user)
    CartItem.objects.filter(cart=cart.first()).delete()
    Dlogout(request)
    return redirect('home')


User = get_user_model()


@login_required
def users(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})


@login_required
def user_detail(request, user_id):
    orders_info = []
    user = User.objects.get(id=user_id)
    orders = Order.objects.filter(user=user)
    for order in orders:
        order_items = OrderItem.objects.filter(order=order)
        orders_info.append([order.id, [str(order_item) for order_item in order_items], order.total])
    return render(request, 'user_detail.html', {'orders': orders_info})


@login_required
@user_passes_test(lambda u: u.role == User.ADMIN_ROLE)
def set_user_role(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        user.role = request.POST['role']
        user.save()
        return redirect(reverse('user_detail', args=[user_id]))
    else:
        return render(request, 'set_user_role.html', {'user': user})