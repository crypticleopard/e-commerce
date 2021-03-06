from django.shortcuts import render
from django.http import JsonResponse
from .models import *
import json
import datetime


def store(request):
    products=Product.objects.all()
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        cartItems=order.get_cart_items
    else:
        items=[]
        order={'get_cart_total':0,'get_cart_items':0,'shipping':False}
        cartItems=order['get_cart_items']
    context={'products':products,'cartItems':cartItems}
    return render(request,"store/store.html",context)

def cart(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        items=[]
        order={'get_cart_total':0,'get_cart_items':0,'shipping':False}
        cartItems=order['get_cart_items']
    context={'items':items,'order':order,'cartItems':cartItems}
    return render(request,"store/cart.html",context)

def checkout(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        items=[]
        order={'get_cart_total':0,'get_cart_items':0,'shipping':False}
        cartItems=order['get_cart_items']
    context={'items':items,'order':order,'cartItems':cartItems}
    return render(request,"store/checkout.html",context)

def updateItem(request):
    data=json.loads(request.body)
    productId=data['productId']
    action=data['action']
    customer=request.user.customer
    product=Product.objects.get(id=productId)
    order,created=Order.objects.get_or_create(customer=customer,complete=False)
    orderitem,created=OrderItem.objects.get_or_create(order=order,product=product)
    if action=='add':
        orderitem.quantity=(orderitem.quantity+1)
    elif action=='remove':
        orderitem.quantity=(orderitem.quantity-1)
    orderitem.save()
    if orderitem.quantity<=0:
        orderitem.delete()        
    return JsonResponse('Item was added',safe=False)

def processOrder(request):
    transaction_id=datetime.datetime.now().timestamp()
    data=json.loads(request.body)
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        total=float(data['form']['total'])
        order.transaction_id=transaction_id
        if total==order.get_cart_total:
            order.complete=True
        order.save()

        if order.shipping==True:
            print('shipping')
            ShipppingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                pincode=data['shipping']['zipcode'],
            )
            

    else:
        print('User is not logged in.......')
    return JsonResponse('Payment completed',safe=False)
