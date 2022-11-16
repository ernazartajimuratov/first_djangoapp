from django.shortcuts import render, redirect
from . import models
import telebot

bot = telebot.TeleBot('5445263065:AAFZA9U9i8KDHB4gXT7dFyhS4R-Mmf5e9H8')

# Create your views here.
def index_page(request):
    #если отправляет отзыв
    if request.method == 'POST':
        mail = request.POST.get('mail')
        feedback = request.POST.get('message')

        models.Feedback.objects.create(user_mail=mail, feedback_meesage=feedback)
    connect = requests.get(url='https://cbu.uz/ru/arkhiv-kursov-valyut/json/').json()

    products = models.Product.objects.all()
    categories = models.Category.objects.all()
    sales = models.Sale.objects.all()
    currency_rate =connect[0]['Rate']
    weather = '+32 C'
    
    return render(request, 'index.html', {'products':products, 
                                          'categories':categories,
                                          'sales':sales,
                                          'rate': currency_rate})


# Function of searching
def search_product(request):
    if request.method == 'POST':
        user_search_product = request.POST.get('search')
        try:
            result_product = models.Product.objects.get(product_name=user_search_product)
            
            return render(request, 'current_product.html', {'result_product': result_product})
        
        except:
            return redirect('/')
        

#Get certain product
def current_product(request, name, pk):
    product = models.Product.objects.get(product_name=name, id=pk)
    
    return render(request, 'current_product.html', {'result_product':product})

# Getting all products from certain category
def current_category(request, pk):
    category = models.Category.objects.get(id=pk)
    category_part = models.Product.objects.filter(product_category=category)

    
    return render(request, 'current_category.html', {'category_part':category_part})
    
# Adding to cart 
def add_product_to_user_cart(request, pk):
    if request.method == 'POST':
        product = models.Product.objects.get(id=pk)
        product_count = float(request.POST.get('count'))
        
        user = models.Cart(user_id=request.user.id, 
                           user_product = product, 
                           product_quantity = product_count,
                           total_for_current_product = product_count * product.product_price)
        
        product.product_quantity -= product_count
        product.save()
        user.save()
        
        return redirect(f'/product/{product.product_name}/{pk}')
        
def show_cart(request):
    cart_product = models.Cart.objects.filter(id=request.user.id)
    
    return render(request, 'cart.html', {'user_product': cart_product})

#отображение корзины
def get_user_cart(request):
    cart_user = models.Cart.objects.filter(user_id=request.user.id)

    #itog summa
    total = sum([i.total_for_current_product for i in cart_user])

    return render(request, 'cart_user.html', {"cart_user": cart_user,"total":total})


def delete_product_from_cart(request, pk):
    if request.method == 'POST':
        product_to_delete = models.Cart.objects.get(id=pk, user_id=request.user_id)
        product = models.Product.objects.get(product_name=product_to_delete.user.id)
        product = models.Product.objects.get(product_name=product_to_delete.user_product)
        product.product_quantity += product_to_delete.product_quantity

        product.save()
        product_to_delete.delete()

        return redirect('/cart')

#oform zakaza
def confirm_order(request):
    if request.method == "POST":
        current_user_cart = models.Cart.objects.filter(user_id=request.user.id)


        client_name = request.POST.get('client_name')
        client_address = request.POST.get('client_address')
        client_number= request.POST.get('client_number')
        client_comment = request.POST.get('client_comment')

        #formulirovka soobsh dlya admina v tg
        full_message = f'новый заказ(от сайта)\n\nимя: {client_name}' \
                       f'\nадрес: {client_address}' \
                       f'\nномер телефона: {client_number}' \
                       f'\nкомментарии к заказу: {client_comment}\n\n'

        for i in current_user_cart:
            full_message += f'продукт: {i.user_product}' \
                            f'\nколичество: {i.product_quantity} шт'\
                            f'\nсумма: {i.total_for_current_product} сум\n--------\n'
        bot.send_message(646893300, full_message)

        return redirect('/')