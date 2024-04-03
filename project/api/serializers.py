from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['fio', 'email', 'password']

    def save(self, **kwargs):
        user = User(
            email = self.validated_data['email'],
            username = self.validated_data['email'],
            fio = self.validated_data['fio'],
        )
        user.set_password(self.validated_data['password'])
        user.save()
        return user

class CartsSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = Carts
        fields = ['id', 'product']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'