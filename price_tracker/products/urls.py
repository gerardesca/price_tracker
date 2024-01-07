from django.urls import path
from . import views


app_name = 'product'
urlpatterns = [
    path("", views.home, name="home"),
    path("<int:pk>", views.product_details, name="product"),
]