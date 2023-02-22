from django import template

register = template.Library()


@register.filter
# For cart multiplying product`s price and quantity
def multiply_price_quantity(price, quantity):
    return price * quantity
