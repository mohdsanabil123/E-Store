from django.shortcuts import render, redirect
from .models.product import Product
from .models.category import Category
from .models.customer import Customer
from .models.orders import Order
from django.views import View
# Handling middleware
from store.middleware.auth import auth_middleware
from django.utils.decorators import method_decorator

# Create your views here.

class Index(View):
    
    def post(self, request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        # print(product)
        
        cart = request.session.get('cart')
        # print(cart)
        if cart:
            cart[product] = 1
        else:
            cart = {}
            cart[product] = 1
        
        request.session['cart'] = cart
        # print(cart)
        return redirect('home')
        
        
    
    def get(self, request):
        search = request.GET.get('search')
        if search:
            products = Product.objects.filter(name__icontains=search) 
            return render( request, 'index.html', {'products':products} )
        
        cart = request.session.get('cart')
        if not cart:
            request.session['cart'] = {}
        products = None
        categories = Category.get_all_categories()
        categoryID = request.GET.get('category')
    
        if categoryID:
            products = Product.get_all_products_by_category_id(categoryID)
        else:
            products = Product.get_all_products()
        data = {
            'products':products,
            'categories':categories,
        }
        
        # print('Your email from seesion:', request.session.get('customer_email'))
        
        return render( request, 'index.html', data )


class SignUP(View):
    def get(self, request):
        return render(request, 'signup.html')
    
    def post(self, request):
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        phone = request.POST['phone']
        email = request.POST['email']
        password = request.POST['password']
        
        # Validation
        value = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email,
        }
        error_message = None
        
        customer = Customer(first_name=first_name, last_name=last_name, phone=phone, email=email, password=password)
        
        if len(first_name) < 4:
            error_message = 'First name is too short!'
        elif len(password) < 4:
            error_message = 'Password must contain 8 characters!'
        elif len(phone) < 8:
            error_message = 'Phone no. is incorrect!'
        elif Customer.objects.filter(email=email):
            error_message = 'Email is already taken!'
        
        
        if not error_message:
            customer.save()
            return redirect('login')
        else:
            data = {
                'values': value,
                'error':error_message,
            }
            return render(request, 'signup.html', data)
        
        
class Login(View):
    def get(self, request):
        return render(request, 'login.html')
    
    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        customer = Customer.get_customer_by_email(email)
        error_message = None
        # print(customer)
        if customer:
            if password == customer.password:
                request.session['customer'] = customer.id
                # request.session['customer_email'] = customer.email
                return redirect('/')
            else:
                error_message = 'Email or Password Invalid !'
        error_message = 'Email or Password Invalid !'
    
        return render(request, 'login.html', {'error': error_message} )


def logout(request):
    request.session.clear()
    return redirect('login')


class Cart(View):
    def get(self, request):
        ids = list(request.session.get('cart').keys())
        products = Product.get_products_by_id(ids)
        # print(products)
        return render(request, 'cart.html', {'products':products})
    
    def post(self, request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart')
        # print(cart)
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity == 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity - 1
                else:
                    cart[product] = quantity + 1
            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1
        
        request.session['cart'] = cart
        # print(cart)
        return redirect('cart')


class Checkout(View):
    
    # @method_decorator(auth_middleware)
    def post(self, request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        customer = request.session.get('customer')
        cart = request.session.get('cart')
        products = Product.get_products_by_id(list(cart.keys()))
        # print(customer, address, phone, cart, products)
        
        for product in products:
            order = Order(customer = Customer(id=customer),
                          product = product,
                          price=product.price,
                          address = address,
                          phone = phone,
                          quantity=cart.get(str(product.id)))
            order.placeOrder()
            
        request.session['cart'] = {}
        
        return redirect('cart')


class OrderView(View):
    
    def get(self, request):
        customer = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer)
        # print(orders)
        
        return render(request, 'orders.html', {'orders': orders})
