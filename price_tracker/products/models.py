from django.db import models
from django.contrib.postgres.fields import ArrayField

from core.models import BaseModel


class Store(BaseModel):
    shortname = models.CharField(verbose_name='Short Name', max_length=100)
    base_url = models.URLField(verbose_name='Base URL')
    image = models.URLField(verbose_name='Image URL', blank=True)

    def __str__(self):
        return self.name
    

class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    categories = ArrayField(models.CharField(max_length=255), default=list, blank=True)
    supplier = models.CharField(verbose_name='Supplier Name', max_length=150, blank=True, default=None, null=True)
    name = models.CharField(verbose_name='Product Name', max_length=200)
    brand = models.CharField(verbose_name='Brand', max_length=100)
    model = models.CharField(verbose_name='Model', max_length=100, blank=True, default=None, null=True)
    sku = models.CharField(verbose_name='SKU', max_length=100)
    link = models.URLField(verbose_name='URL Product', max_length=500)
    image = models.URLField(verbose_name='URL Image', max_length=500)    
    
    def __str__(self):
        return f'{self.store.name}: {self.name}, {self.sku}'
    
    
class ProductHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField(verbose_name='Current Price')
    last_price = models.FloatField(verbose_name='Last Price')
    discount_rate = models.FloatField(verbose_name='Discount Rate', blank=True, null=True)
    date = models.DateTimeField(verbose_name='Date')
    
    def __str__(self):
        return f'{self.product.name}: {self.product.sku}, {self.price}'