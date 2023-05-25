from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import get_language
from SPARQLWrapper import SPARQLWrapper, JSON
from requests import get as get_request
from re import split


class Category(models.Model):
    name = models.CharField(max_length=30)
    weight = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='app/static/images/products_img',
                              default='static/images/products_img/default.jpg')

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if not self.description:
            description = self.get_description_from_dbpedia()
            self.description = ''.join(split(r'(?<=[.;])\s', description)[:3])  # first 3 sentences from str.
            # TODO: upload database with new data of this field

        if not self.image:
            self.image = self.get_image_from_dbpedia()
            # TODO: upload database with new data of this field

    def get_description_from_dbpedia(self):
        name = str(self.name).replace(' ', '-').title()  # converting name for searching param in dbpedia.
        eng_desc = None
        sparql = SPARQLWrapper('https://dbpedia.org/sparql')  # connection.
        sparql.setQuery(f'SELECT ?object WHERE {{ dbr:{name} dbo:abstract ?object .}}')
        sparql.setReturnFormat(JSON)
        obj = sparql.query().convert()
        for i in obj['results']['bindings']:   # getting elements from results.
            if i['object']['xml:lang'] == get_language():
                return i['object']['value']  # returning user`s lang description
            elif i['object']['xml:lang'] == 'en':
                eng_desc = i['object']['value']
        if eng_desc:
            return eng_desc  # returning en lang description
        else:
            return 'we don`t have description for this one, so sorry <3'  # if there is no result in dbpedia.

    def get_image_from_dbpedia(self):
        name = str(self.name).replace(' ', '-').title()  # converting name for searching param in dbpedia.
        sparql = SPARQLWrapper('https://dbpedia.org/sparql')  # connection.
        sparql.setQuery(f'SELECT ?image WHERE {{dbr:{name} dbo:thumbnail ?image .}}')
        sparql.setReturnFormat(JSON)
        obj = sparql.query().convert()['results']['bindings']  # getting result array from JSON.
        if obj:
            result = obj[0]  # getting first el of array if there is one.
            image_url = result['image']['value']
            if get_request(image_url).status_code != 200:
                return '/static/images/products_img/default.jpg'  # if there is no img in dbpedia return default img.
            return get_request(image_url)
        else:
            return '/static/images/products_img/default.jpg'  # if there is no result in dbpedia return default img.


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return str(self.product.name) + '-' + str(self.quantity)
