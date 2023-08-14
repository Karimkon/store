from django.db import IntegrityError
from django.contrib.auth.models import User
from store.models import Address, Cart, Category, Order, Product, Wishlist, ContactMessage, BlogPost, Subscription
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm, CheckoutForm, ProductReviewForm, SubscriptionForm
from django.contrib import messages
from django.views import View
import decimal
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator # for Class Based Views
from django.core.paginator import Paginator




# Create your views here.

def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    
    wishlist_count = 0
    form = SubscriptionForm(request.POST)
    
    if request.method == 'POST':  # Check if the form was submitted
        if form.is_valid():
            # Process the form data (e.g., save the email to your database)
            email = form.cleaned_data['email']
            # Redirect to a success page or display a success message
            return redirect('store:index')  # Redirect back to the index page
            
    # If the form was not submitted or if it's not valid, create a new empty form
    else:
        form = SubscriptionForm()
    
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            products = wishlist.products.all()
            wishlist_count = products.count()

    context = {
        'categories': categories,
        'products': products,
        'wishlist_count': wishlist_count,
        'form': form,  # Include the form in the context
    }
    
    return render(request, 'store/index.html', context)

def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all()
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            products = wishlist.products.all()
            wishlist_count = products.count()
    if request.method == 'POST':
        review_form = ProductReviewForm(request.POST)
        if review_form.is_valid():
            # Save the review with the current product and logged-in user
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
    else:
        review_form = ProductReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'star_range': range(5),
        'related_products': related_products,
        'wishlist_count': wishlist_count,

    }
    return render(request, 'store/detail.html', context)



def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories':categories})


def category_products(request, slug):
    
    # Get the sorting parameter from the request
    sort_by = request.GET.get('sort', 'default')

    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    categories = Category.objects.filter(is_active=True)

# Implement sorting based on the 'sort_by' parameter
    if sort_by == 'popularity':
        products = products.order_by('-popularity')
    elif sort_by == 'low-high':
        products = products.order_by('price')
    elif sort_by == 'high-low':
        products = products.order_by('-price')

    
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'products': products,
        'categories': categories,
        'page_obj': page_obj,
    }
    return render(request, 'store/category_products.html', context)


# Authentication Starts Here

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations! Registration Successful!")
            form.save()
        return render(request, 'account/register.html', {'form': form})
        

@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses':addresses, 'orders':orders})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()
    
    return redirect('store:cart')


@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount

    # Customer Addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
    }
    return render(request, 'store/cart.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('store:cart')


@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('store:cart')


@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:cart')


@login_required
def checkout(request):
    user = request.user
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Get the selected address ID from the form data
            address_id = form.cleaned_data['address']
            address = get_object_or_404(Address, id=address_id)

            # Get all the products of the user in the cart
            cart_items = Cart.objects.filter(user=user)

            # Calculate the total amount
            total_amount = sum(item.product.price * item.quantity for item in cart_items)

            # Save all the products from the cart to orders
            for cart_item in cart_items:
                Order.objects.create(user=user, address=address, product=cart_item.product, quantity=cart_item.quantity)

                # You can also update the inventory or perform other necessary actions here

                # Delete the item from the cart after creating the order
                cart_item.delete()

            # Redirect to the 'store:orders' URL after processing the checkout
            return redirect('store:orders')

    else:
        form = CheckoutForm()

        # Get all the products of the user in the cart
        cart_items = Cart.objects.filter(user=user)

        # Calculate the total amount
        total_amount = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'store/checkout.html', {'form': form, 'total_amount': total_amount, 'cart_items': cart_items})

@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': all_orders})



def shop(request):
    return render(request, 'store/shop.html')





def test(request):
    return render(request, 'store/test.html')

@login_required
def view_wishlist(request):
    wishlist = Wishlist.objects.get(user=request.user)
    products = wishlist.products.all()
    return render(request, 'store/wishlist.html', {'wishlist': wishlist, 'products': products})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.products.add(product)
    # Increment the popularity of the product when added to the wishlist
    product.popularity += 1
    product.save()
    return redirect('store:view_wishlist')

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = Wishlist.objects.get(user=request.user)
    wishlist.products.remove(product)
    return redirect('store:view_wishlist')

def blog(request):
    blog_posts = BlogPost.objects.all()
    return render(request, 'store/blog.html', {'blog_posts': blog_posts})

def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Save the data to the database
        contact_message = ContactMessage(name=name, email=email, message=message)
        contact_message.save()
        
        return redirect('store:contact_success')
        
    return render(request, 'store/contact_us.html')

def contact_success(request):
    return render(request, 'store/contact_success.html')


def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                Subscription.objects.create(email=email)
                return redirect('store:success_page')
            except IntegrityError:
                # Handle case where email already exists
                form.add_error('email', 'This email address is already subscribed.')
    else:
        form = SubscriptionForm()

    return render(request, 'store/index.html', {'form': form})

def success_page(request):
    return render(request, 'store/success.html')