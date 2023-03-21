from decimal import Decimal
from django.conf import settings
from .models import Product


class Cart(object):
    def __init__(self, request):
        # init cart session
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save cart to the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    # adds products to the cart or update the quantity
    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    # saves session data
    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        # indicate that session was modified
        self.session.modified = True

    # removes product from the cart
    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    # products iterator
    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    # returns amount of products in the cart
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    # returns total price of the cart
    def get_total_price(self):
        return sum(Decimal(item['price'])*item['quantity'] for item in self.cart.values())

    # deletes cart session
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def change_product_quantity(self, product_id, quantity_change):
        self.cart[product_id]['quantity'] += int(quantity_change)
        self.save()
