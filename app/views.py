from django.shortcuts import render, redirect
from cart.models import Product
from django.contrib.auth import get_user_model, authenticate, login as Dlogin, logout as Dlogout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
# TODO delete logging
import logging
logger = logging.getLogger('django')
User = get_user_model()


def home(request):
    products = Product.objects.order_by('category__weight')
    user_id = request.user.id
    context = {'title': 'pyShop', 'description': 'Buy needs online!', 'products': products, 'user_id': user_id}
    return render(request, 'home.html', context)


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
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def logout(request):
    Dlogout(request)
    return redirect('home')
