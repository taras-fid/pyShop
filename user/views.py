from django.shortcuts import render, redirect
from cart.models import Order, OrderItem
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse

User = get_user_model()


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def users(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users, 'is_admin': request.user.is_superuser})


@login_required
def user_detail(request, user_id):
    if request.user.id == user_id or request.user.is_staff or request.user.is_superuser:
        orders_info = []
        user = User.objects.get(id=user_id)
        orders = Order.objects.filter(user=user)
        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            orders_info.append([order.id, [order_item for order_item in order_items], order.total])
        return render(request, 'user_detail.html', {'orders': orders_info, 'user': user})
    else:
        return redirect('home')


@login_required
def change_user_info(request, user_id):
    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        user.first_name = request.POST['f_name']
        user.last_name = request.POST['l_name']
        user.email = request.POST['email']
        user.save()
    return redirect('user_detail', user_id=user_id)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def set_user_role(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        if request.POST['role'] == 'admin':
            user.is_superuser = 1
        elif request.POST['role'] == 'staff':
            user.is_superuser = 0
            user.is_staff = 1
        elif request.POST['role'] == 'user':
            user.is_superuser = 0
            user.is_staff = 0
            if request.user.id == user.id:
                user.save()
                return redirect('home')
        else:
            return JsonResponse({'error': 'Invalid request'}, status=400)
        user.save()
        return redirect('user_detail', user_id=user_id)
    else:
        return render(request, 'set_user_role.html', {'user': user})
