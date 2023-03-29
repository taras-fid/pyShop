from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_cart, name='view_cart'),
    path('add-to-cart/(<product_id>)/', views.add_to_cart, name='add_to_cart'),
    path('delete/(<product_id>)/', views.delete_cart_item, name='delete_cart_item'),
    path('change_quantity/(<product_id>)/(<quantity_change>)', views.change_quantity_item, name='change_quantity_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment, name='payment')
]
