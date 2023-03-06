from django.contrib import admin
from cart.models import Product, Order, Category


class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(Category)
