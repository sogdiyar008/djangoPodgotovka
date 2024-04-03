from django.urls import path
from .views import *


urlpatterns = [
    path('products', productsView),
    path('login', loginView),
    path('signup',register_ser),
    path('product', createProduct),
    path('product/<int:pk>', changeproduct),
    path('logout', logout),
    path('carts', cartView),
    path('order', orderView)
]