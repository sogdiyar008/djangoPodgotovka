from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from .permision import *
from rest_framework.status import (HTTP_200_OK,
                                   HTTP_201_CREATED,
                                   HTTP_403_FORBIDDEN,
                                   HTTP_404_NOT_FOUND,
                                   HTTP_422_UNPROCESSABLE_ENTITY)


@api_view(['GET'])
def productsView(request):
    products = Product.objects.all()
    prod_ser = ProductSerializer(products, many=True)
    return Response({'data': prod_ser.data}, status=HTTP_200_OK)

@api_view(['GET'])
def logout(request):
    request.user.auth_token.delete()
    return Response({'data',{'message':'logout'}}, status=HTTP_200_OK)




@api_view(["POST"])
def loginView(request):
    user_ser = LoginSerializer(data=request.data)
    if user_ser.is_valid():
        try:
            user = User.objects.get(email=user_ser.validated_data['email'])
        except:
            return Response({'error':{'code': 401, 'message': 'Authentication failed'}}, status=401)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'data':{'user_token':token.key}}, status=HTTP_200_OK)
    else:
        return Response({'error':{
                                    'code':422,
                                    'message':'Validation error',
                                    'errors': user_ser.errors}},
                    status=HTTP_422_UNPROCESSABLE_ENTITY)

@api_view(['POST'])
def register_ser(request):
    user_ser = RegisterSerializer(data=request.data)
    if user_ser.is_valid():
        user = user_ser.save()
        token = Token.objects.create(user=user)
        return Response({'data':{'user_token': token.key}}, status=HTTP_200_OK)
    else:
        return Response({'error':{
                                    'code':422,
                                    'message':'Validation error',
                                    'errors': user_ser.errors}},
                    status=HTTP_422_UNPROCESSABLE_ENTITY)


@api_view(["post"])
@permission_classes([IsAdminUser])
def createProduct(request):
    prod_ser = ProductSerializer(data=request.data)
    if prod_ser.is_valid():
        prod_ser.save()
        return Response({'data':{'id': prod_ser.data['id'], 'message': 'Product added'}}, status=HTTP_200_OK)
    else:
        return Response({'error':{
                                    'code':422,
                                    'message':'Validation error',
                                    'errors': prod_ser.errors}},
                    status=HTTP_422_UNPROCESSABLE_ENTITY)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
def changeproduct(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except:
        return Response({'error':{'code': 404, 'message': 'Not found'}}, status=HTTP_404_NOT_FOUND)
    if request.method == 'DELETE':
        product.delete()
        return Response({'data': {'message':'Item removed from cart'}})
    elif request.method == 'PATCH':
        prod_ser = ProductSerializer(data=request.data, instance=product, partial=True)
        if prod_ser.is_valid():
            prod_ser.save()
            return Response({'data': prod_ser.data}, status=HTTP_200_OK)
        return Response({'error':
                             {'code': 422, 'message': 'alidation error', 'errors':prod_ser.errors}}, status=HTTP_422_UNPROCESSABLE_ENTITY)

@api_view(['GET'])
@permission_classes([IsClient])
def cartView(request):
    carts = Carts.objects.filter(user=request.user)
    cart_ser = CartsSerializer(carts, many=True)
    carts = []
    for cart in cart_ser.data:
        newcart ={
            'id': cart['id'],
            'product_id': cart['product']['id'],
            'name':cart['product']['name'],
            'description':cart['product']['description'],
            'price':cart['product']['price']
        }
        carts.append(newcart)
    return Response({'data':carts}, status=HTTP_200_OK)


@api_view(["DELETE",'POST'])
@permission_classes([IsClient])
def changeCart(request, pk):
    if request.method == "DELETE":
        try:
            cart = Carts.objects.get(pk=pk)
        except:
            return Response({'error': {'code': 404, 'message': 'not found'}}, status=HTTP_404_NOT_FOUND)
        cart.delete()
        return Response({'data':{'message': 'Item removed from cart'}}, status=HTTP_200_OK)
    elif request.method == 'POST':
        try:
            product = Product.objects.get(pk=pk)
        except:
            return Response({'error':{'code':404, 'message':"Not found"}}, status=HTTP_404_NOT_FOUND)
        Carts.objects.create(user=request.user, product=product)


@api_view(['GET','POST'])
@permission_classes([IsClient])
def orderView(request):
    if request.method == 'GET':
        orders = Order.objects.filter(user=request.user)
        order_ser = OrderSerializer(orders, many=True)
        return Response({'data':order_ser.data}, status=HTTP_200_OK)
    elif request.method == "POST":
        carts = Carts.objects.filter(user=request.user)
        if len(carts) == 0:
            return Response({'data':{'code': 404,'message': "Cart is not empty", }}, status=HTTP_404_NOT_FOUND)
        order = Order.objects.create(user=request.user, order_price=0)
        order_price = 0

        for cart in carts:
            print(cart.product.price)
            order.product.add(cart.product)
            order_price += cart.product.price
            cart.delete()
        order.order_price = order_price
        order.save()
        order_ser = OrderSerializer(order)
        return Response({'data':order_ser.data})
