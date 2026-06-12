from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .models import *
import datetime

# Helper functions to check authentication and authorization
def check_admin(request):
    return request.session.get('usertype') == 'admin'

def check_artisan(request):
    return request.session.get('usertype') == 'artisan' and 'artisan_id' in request.session

# Admin Views
def homeadmin(request):
    if not check_admin(request):
        messages.error(request, "Please log in as Administrator.")
        return redirect('/log')
        
    artisan_count = artisan.objects.count()
    customer_count = customer.objects.count()
    category_count = category.objects.count()
    complaint_count = complaint.objects.filter(reply='pending').count()
    
    context = {
        'artisan_count': artisan_count,
        'customer_count': customer_count,
        'category_count': category_count,
        'complaint_count': complaint_count,
    }
    return render(request, 'admin/Adminhome.html', context)

# Login Views
def log(request):
    return render(request, 'login.html')

def log_post(request):
    u = request.POST.get('textfield')
    p = request.POST.get('textfield2')
    
    user_list = login.objects.filter(username=u, password=p)
    if user_list.exists():
        user = user_list.first()
        if user.usertype == 'admin':
            request.session['login_id'] = user.id
            request.session['usertype'] = 'admin'
            messages.success(request, "Welcome, Administrator!")
            return redirect('/')
        elif user.usertype == 'artisan':
            try:
                artisan_obj = artisan.objects.get(LOGIN=user)
                request.session['login_id'] = user.id
                request.session['usertype'] = 'artisan'
                request.session['artisan_id'] = artisan_obj.id
                messages.success(request, f"Welcome back, {artisan_obj.name}!")
                return redirect('/artisan_home')
            except artisan.DoesNotExist:
                messages.error(request, "Artisan profile not found.")
                return redirect('/log')
        elif user.usertype == 'customer':
            try:
                customer_obj = customer.objects.get(LOGIN=user)
                request.session['login_id'] = user.id
                request.session['usertype'] = 'customer'
                request.session['customer_id'] = customer_obj.id
                messages.success(request, f"Welcome back, {customer_obj.name}!")
                return redirect('/customer_home')
            except customer.DoesNotExist:
                messages.error(request, "Customer profile not found.")
                return redirect('/log')
        elif user.usertype == 'blocked':
            messages.error(request, "Your account has been blocked by the Administrator.")
            return redirect('/log')
        else:
            messages.error(request, "Invalid account type.")
            return redirect('/log')
    else:
        messages.error(request, "Invalid username or password.")
        return redirect('/log')

def logout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect('/log')

def changepass(request):
    if 'login_id' not in request.session:
        messages.error(request, "Please log in to change password.")
        return redirect('/log')
    return render(request, 'admin/change_pass.html')

def changepass_post(request):
    if 'login_id' not in request.session:
        messages.error(request, "Unauthorized request.")
        return redirect('/log')
        
    current_pass = request.POST.get('textfield')
    new_pass = request.POST.get('textfield2')
    confirm_pass = request.POST.get('textfield3')
    
    try:
        user = login.objects.get(id=request.session['login_id'])
        if user.password != current_pass:
            messages.error(request, "Current password does not match.")
            return redirect('/changepass')
        if new_pass != confirm_pass:
            messages.error(request, "New passwords do not match.")
            return redirect('/changepass')
            
        user.password = new_pass
        user.save()
        messages.success(request, "Password updated successfully.")
        
        # Redirect based on usertype
        if user.usertype == 'admin':
            return redirect('/')
        else:
            return redirect('/artisan_home')
            
    except login.DoesNotExist:
        messages.error(request, "User account not found.")
        return redirect('/log')

# Category Management (Admin)
def addcategory(request):
    if not check_admin(request):
        messages.error(request, "Access denied.")
        return redirect('/log')
    return render(request, 'admin/add_category.html')

def addcategory_post(request):
    if not check_admin(request):
        messages.error(request, "Access denied.")
        return redirect('/log')
        
    cat_name = request.POST.get('textfield')
    if category.objects.filter(category__iexact=cat_name).exists():
        messages.error(request, "Category already exists.")
        return redirect('/addcategory')
        
    obj = category(category=cat_name)
    obj.save()
    messages.success(request, "Category added successfully.")
    return redirect('/viewcategory')

def editcategory(request, id):
    if not check_admin(request):
        messages.error(request, "Access denied.")
        return redirect('/log')
    try:
        data = category.objects.get(id=id)
        return render(request, 'admin/edit_category.html', {"data": data, "id": id})
    except category.DoesNotExist:
        messages.error(request, "Category not found.")
        return redirect('/viewcategory')

def editcategory_post(request, id):
    if not check_admin(request):
        messages.error(request, "Access denied.")
        return redirect('/log')
        
    cat_name = request.POST.get('textfield')
    category.objects.filter(id=id).update(category=cat_name)
    messages.success(request, "Category updated successfully.")
    return redirect('/viewcategory')

def deletecategory(request, id):
    if not check_admin(request):
        messages.error(request, "Access denied.")
        return redirect('/log')
    try:
        category.objects.get(id=id).delete()
        messages.success(request, "Category deleted successfully.")
    except category.DoesNotExist:
        messages.error(request, "Category not found.")
    return redirect('/viewcategory')

def viewcategory(request):
    if not check_admin(request):
        messages.error(request, "Access denied.")
        return redirect('/log')
    data = category.objects.all()
    return render(request, 'admin/view_category.html', {"data": data})

# User Moderation & Views (Admin)
def viewartisan(request):
    if not check_admin(request):
        messages.error(request, "Access denied.")
        return redirect('/log')
    data = artisan.objects.all()
    return render(request, 'admin/view_artisan.html', {"data": data})

def blockartisan(request, id):
    if not check_admin(request):
        messages.error(request, "Access denied.")
        return redirect('/log')
    try:
        art = artisan.objects.get(id=id)
        art.LOGIN.usertype = 'blocked'
        art.LOGIN.save()
        messages.success(request, f"Artisan {art.name} has been blocked.")
    except artisan.DoesNotExist:
        messages.error(request, "Artisan not found.")
    return redirect('/viewartisan')

def unblockartisan(request, id):
    if not check_admin(request):
        messages.error(request, "Access denied.")
        return redirect('/log')
    try:
        art = artisan.objects.get(id=id)
        art.LOGIN.usertype = 'artisan'
        art.LOGIN.save()
        messages.success(request, f"Artisan {art.name} has been unblocked.")
    except artisan.DoesNotExist:
        messages.error(request, "Artisan not found.")
    return redirect('/viewartisan')

def viewcustomer(request):
    if not check_admin(request):
        messages.error(request, "Access denied.")
        return redirect('/log')
    data = customer.objects.all()
    return render(request, 'admin/view_customer.html', {"data": data})

# Complaints & Feedback (Admin)
def viewcomplaint(request):
    if not check_admin(request):
        messages.error(request, "Access denied.")
        return redirect('/log')
    data = complaint.objects.all()
    return render(request, 'admin/view_complaint.html', {"data": data})

def replycomplaint(request, id):
    if not check_admin(request):
        messages.error(request, "Access denied.")
        return redirect('/log')
    return render(request, 'admin/replycomplaint.html', {"id": id})

def replycomplaint_post(request, id):
    if not check_admin(request):
        messages.error(request, "Access denied.")
        return redirect('/log')
        
    rep = request.POST.get('textarea')
    today = datetime.date.today().strftime('%Y-%m-%d')
    
    complaint.objects.filter(id=id).update(reply=rep, replydate=today)
    messages.success(request, "Reply sent successfully.")
    return redirect('/viewcomplaint')

def viewfeedback(request):
    if not check_admin(request):
        messages.error(request, "Access denied.")
        return redirect('/log')
    data = feedback.objects.all()
    return render(request, 'admin/view_feedback.html', {"data": data})


# ----------------------------------------------------
# Artisan Module Views
# ----------------------------------------------------

def artisan_signup(request):
    return render(request, 'artisan/artisan_register.html')

def artisan_signup_post(request):
    name = request.POST.get('name')
    phone = request.POST.get('phone')
    email = request.POST.get('email')
    place = request.POST.get('place')
    gender = request.POST.get('gender')
    username = request.POST.get('username')
    passw = request.POST.get('password')
    conf_pass = request.POST.get('confirm_password')
    
    if passw != conf_pass:
        messages.error(request, "Passwords do not match.")
        return redirect('/artisan_signup')
        
    if login.objects.filter(username=username).exists():
        messages.error(request, "Username already taken.")
        return redirect('/artisan_signup')
        
    # Create login credentials
    log_obj = login(username=username, password=passw, usertype='artisan')
    log_obj.save()
    
    # Create artisan profile linked to the login credentials
    art_obj = artisan(name=name, phone=phone, email=email, place=place, gender=gender, LOGIN=log_obj)
    art_obj.save()
    
    messages.success(request, "Registration successful! You can now log in.")
    return redirect('/log')

def artisan_home(request):
    if not check_artisan(request):
        messages.error(request, "Please log in as an Artisan.")
        return redirect('/log')
        
    art_id = request.session['artisan_id']
    art_obj = artisan.objects.get(id=art_id)
    
    prod_count = product.objects.filter(ARTISAN=art_obj).count()
    orders = order.objects.filter(PRODUCT__ARTISAN=art_obj)
    order_count = orders.count()
    
    # Calculate Earnings
    earnings = 0
    for o in orders:
        if o.status.lower() in ['delivered', 'completed', 'paid']:
            try:
                earnings += float(o.price)
            except ValueError:
                pass
                
    context = {
        'artisan': art_obj,
        'prod_count': prod_count,
        'order_count': order_count,
        'earnings': f"{earnings:.2f}",
    }
    return render(request, 'artisan/Artisanhome.html', context)

def artisan_profile(request):
    if not check_artisan(request):
        messages.error(request, "Please log in as an Artisan.")
        return redirect('/log')
        
    art_obj = artisan.objects.get(id=request.session['artisan_id'])
    return render(request, 'artisan/view_profile.html', {'artisan': art_obj})

def artisan_profile_post(request):
    if not check_artisan(request):
        messages.error(request, "Unauthorized request.")
        return redirect('/log')
        
    art_obj = artisan.objects.get(id=request.session['artisan_id'])
    art_obj.name = request.POST.get('name')
    art_obj.phone = request.POST.get('phone')
    art_obj.email = request.POST.get('email')
    art_obj.place = request.POST.get('place')
    art_obj.gender = request.POST.get('gender')
    art_obj.save()
    
    messages.success(request, "Profile updated successfully.")
    return redirect('/artisan_profile')

# Artisan Products Management
def artisan_addproduct(request):
    if not check_artisan(request):
        messages.error(request, "Please log in as an Artisan.")
        return redirect('/log')
    return render(request, 'artisan/add_product.html')

def artisan_addproduct_post(request):
    if not check_artisan(request):
        messages.error(request, "Unauthorized request.")
        return redirect('/log')
        
    art_obj = artisan.objects.get(id=request.session['artisan_id'])
    pname = request.POST.get('name')
    qty = request.POST.get('quantity')
    price = request.POST.get('price')
    
    myfile = request.FILES.get('image')
    filename = 'no_image.png'
    if myfile:
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        
    prod = product(productname=pname, quantity=qty, price=price, image=filename, ARTISAN=art_obj)
    prod.save()
    
    messages.success(request, "Product added successfully.")
    return redirect('/artisan_viewproducts')

def artisan_viewproducts(request):
    if not check_artisan(request):
        messages.error(request, "Please log in as an Artisan.")
        return redirect('/log')
        
    art_obj = artisan.objects.get(id=request.session['artisan_id'])
    data = product.objects.filter(ARTISAN=art_obj)
    return render(request, 'artisan/view_products.html', {'data': data})

def artisan_editproduct(request, id):
    if not check_artisan(request):
        messages.error(request, "Please log in as an Artisan.")
        return redirect('/log')
    try:
        art_obj = artisan.objects.get(id=request.session['artisan_id'])
        prod = product.objects.get(id=id, ARTISAN=art_obj)
        return render(request, 'artisan/edit_product.html', {'data': prod, 'id': id})
    except product.DoesNotExist:
        messages.error(request, "Product not found or access denied.")
        return redirect('/artisan_viewproducts')

def artisan_editproduct_post(request, id):
    if not check_artisan(request):
        messages.error(request, "Unauthorized request.")
        return redirect('/log')
        
    try:
        art_obj = artisan.objects.get(id=request.session['artisan_id'])
        prod = product.objects.get(id=id, ARTISAN=art_obj)
        
        prod.productname = request.POST.get('name')
        prod.quantity = request.POST.get('quantity')
        prod.price = request.POST.get('price')
        
        myfile = request.FILES.get('image')
        if myfile:
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            prod.image = filename
            
        prod.save()
        messages.success(request, "Product updated successfully.")
    except product.DoesNotExist:
        messages.error(request, "Product not found.")
        
    return redirect('/artisan_viewproducts')

def artisan_deleteproduct(request, id):
    if not check_artisan(request):
        messages.error(request, "Unauthorized request.")
        return redirect('/log')
        
    try:
        art_obj = artisan.objects.get(id=request.session['artisan_id'])
        product.objects.get(id=id, ARTISAN=art_obj).delete()
        messages.success(request, "Product deleted successfully.")
    except product.DoesNotExist:
        messages.error(request, "Product not found.")
        
    return redirect('/artisan_viewproducts')

# Artisan Orders, Payments, and Reviews
def artisan_vieworders(request):
    if not check_artisan(request):
        messages.error(request, "Please log in as an Artisan.")
        return redirect('/log')
        
    art_obj = artisan.objects.get(id=request.session['artisan_id'])
    data = order.objects.filter(PRODUCT__ARTISAN=art_obj)
    return render(request, 'artisan/view_orders.html', {'data': data})

def artisan_updateorderstatus(request, id):
    if not check_artisan(request):
        messages.error(request, "Unauthorized request.")
        return redirect('/log')
        
    try:
        art_obj = artisan.objects.get(id=request.session['artisan_id'])
        ord_obj = order.objects.get(id=id, PRODUCT__ARTISAN=art_obj)
        status = request.POST.get('status')
        ord_obj.status = status
        ord_obj.save()
        messages.success(request, "Order status updated successfully.")
    except order.DoesNotExist:
        messages.error(request, "Order not found.")
        
    return redirect('/artisan_vieworders')

def artisan_viewpayments(request):
    if not check_artisan(request):
        messages.error(request, "Please log in as an Artisan.")
        return redirect('/log')
        
    art_obj = artisan.objects.get(id=request.session['artisan_id'])
    data = payment.objects.filter(ORDER__PRODUCT__ARTISAN=art_obj)
    return render(request, 'artisan/view_payments.html', {'data': data})

def artisan_viewreviews(request):
    if not check_artisan(request):
        messages.error(request, "Please log in as an Artisan.")
        return redirect('/log')
        
    art_obj = artisan.objects.get(id=request.session['artisan_id'])
    reviews = review.objects.filter(PRODUCT__ARTISAN=art_obj)
    feedbacks = feedback.objects.filter(PRODUCT__ARTISAN=art_obj)
    
    return render(request, 'artisan/view_reviews.html', {
        'reviews': reviews,
        'feedbacks': feedbacks
    })

# Artisan Chat Management
def artisan_chat(request):
    if not check_artisan(request):
        messages.error(request, "Please log in as an Artisan.")
        return redirect('/log')
        
    art_obj = artisan.objects.get(id=request.session['artisan_id'])
    
    # Find unique customers who have chatted with this artisan
    chatted_customer_ids = chat.objects.filter(ARTISAN=art_obj).values_list('CUSTOMER_id', flat=True).distinct()
    recent_customers = customer.objects.filter(id__in=chatted_customer_ids)
    
    # Also get all other customers in case the artisan wants to start a new chat
    all_customers = customer.objects.exclude(id__in=chatted_customer_ids)
    
    return render(request, 'artisan/chat_list.html', {
        'recent_customers': recent_customers,
        'all_customers': all_customers
    })

def artisan_chatroom(request, customer_id):
    if not check_artisan(request):
        messages.error(request, "Please log in as an Artisan.")
        return redirect('/log')
        
    art_obj = artisan.objects.get(id=request.session['artisan_id'])
    try:
        cust = customer.objects.get(id=customer_id)
        messages_list = chat.objects.filter(ARTISAN=art_obj, CUSTOMER=cust).order_by('id')
        return render(request, 'artisan/chat_room.html', {
            'customer': cust,
            'chats': messages_list
        })
    except customer.DoesNotExist:
        messages.error(request, "Customer not found.")
        return redirect('/artisan_chat')

def artisan_chat_send(request, customer_id):
    if not check_artisan(request):
        messages.error(request, "Unauthorized request.")
        return redirect('/log')
        
    art_id = request.session['artisan_id']
    art_obj = artisan.objects.get(id=art_id)
    chat_text = request.POST.get('chat_text')
    today = datetime.date.today().strftime('%Y-%m-%d')
    
    if chat_text:
        # Since it is sent by artisan, we save it with the "Artisan:" prefix
        chat_obj = chat(chat=f"Artisan:{chat_text}", chatdate=today, CUSTOMER_id=customer_id, ARTISAN=art_obj)
        chat_obj.save()
        
    return redirect(f'/artisan_chatroom/{customer_id}')


# ----------------------------------------------------
# Customer (User) Module Views
# ----------------------------------------------------

def check_customer(request):
    return request.session.get('usertype') == 'customer' and 'customer_id' in request.session

def customer_signup(request):
    return render(request, 'customer/customer_register.html')

def customer_signup_post(request):
    name = request.POST.get('name')
    phone = request.POST.get('phone')
    email = request.POST.get('email')
    place = request.POST.get('place')
    username = request.POST.get('username')
    passw = request.POST.get('password')
    conf_pass = request.POST.get('confirm_password')
    
    if passw != conf_pass:
        messages.error(request, "Passwords do not match.")
        return redirect('/customer_signup')
        
    if login.objects.filter(username=username).exists():
        messages.error(request, "Username already taken.")
        return redirect('/customer_signup')
        
    log_obj = login(username=username, password=passw, usertype='customer')
    log_obj.save()
    
    cust_obj = customer(name=name, phone=phone, email=email, place=place, LOGIN=log_obj)
    cust_obj.save()
    
    messages.success(request, "Registration successful! You can now log in.")
    return redirect('/log')

def customer_home(request):
    if not check_customer(request):
        messages.error(request, "Please log in as a Customer.")
        return redirect('/log')
        
    cust_id = request.session['customer_id']
    cust_obj = customer.objects.get(id=cust_id)
    
    cart_count = cart.objects.filter(CUSTOMER=cust_obj).count()
    order_count = order.objects.filter(CUSTOMER=cust_obj).count()
    
    context = {
        'customer': cust_obj,
        'cart_count': cart_count,
        'order_count': order_count,
    }
    return render(request, 'customer/customer_home.html', context)

def customer_viewproducts(request):
    if not check_customer(request):
        messages.error(request, "Please log in as a Customer.")
        return redirect('/log')
        
    cust_id = request.session['customer_id']
    cust_obj = customer.objects.get(id=cust_id)
    
    # Filter by category if category parameter is passed
    cat_filter = request.GET.get('category')
    if cat_filter:
        # Since product doesn't link to category directly, we can filter by productname containing the category,
        # or list all products if not applicable. Since the schema doesn't link product to category,
        # we can show all products but display the category search filter.
        # Let's search by product name matching query if they search, or category name.
        # To make it fully functional and useful, let's search if productname contains the filter term:
        prods = product.objects.filter(productname__icontains=cat_filter)
    else:
        prods = product.objects.all()
        
    categories = category.objects.all()
    
    # Get list of followed artisans
    followed_art_ids = followers.objects.filter(CUSTOMER=cust_obj).values_list('ARTISAN_id', flat=True)
    
    context = {
        'data': prods,
        'categories': categories,
        'followed_art_ids': followed_art_ids,
        'selected_category': cat_filter
    }
    return render(request, 'customer/customer_viewproducts.html', context)

def customer_follow_artisan(request, artisan_id):
    if not check_customer(request):
        messages.error(request, "Unauthorized request.")
        return redirect('/log')
        
    cust_id = request.session['customer_id']
    cust_obj = customer.objects.get(id=cust_id)
    
    try:
        art_obj = artisan.objects.get(id=artisan_id)
        follow_rel = followers.objects.filter(CUSTOMER=cust_obj, ARTISAN=art_obj)
        
        if follow_rel.exists():
            follow_rel.delete()
            messages.success(request, f"Unfollowed {art_obj.name}.")
        else:
            today = datetime.date.today().strftime('%Y-%m-%d')
            followers.objects.create(followdate=today, CUSTOMER=cust_obj, ARTISAN=art_obj)
            messages.success(request, f"Now following {art_obj.name}!")
            
    except artisan.DoesNotExist:
        messages.error(request, "Artisan not found.")
        
    return redirect('/customer_viewproducts')

def customer_addto_cart(request, product_id):
    if not check_customer(request):
        messages.error(request, "Unauthorized request.")
        return redirect('/log')
        
    cust_id = request.session['customer_id']
    cust_obj = customer.objects.get(id=cust_id)
    
    try:
        prod_obj = product.objects.get(id=product_id)
        
        # Check if already in cart
        if cart.objects.filter(CUSTOMER=cust_obj, PRODUCT=prod_obj).exists():
            messages.info(request, "Item is already in your cart.")
        else:
            cart.objects.create(CUSTOMER=cust_obj, PRODUCT=prod_obj)
            messages.success(request, f"Added {prod_obj.productname} to cart.")
            
    except product.DoesNotExist:
        messages.error(request, "Product not found.")
        
    return redirect('/customer_viewproducts')

def customer_viewcart(request):
    if not check_customer(request):
        messages.error(request, "Please log in as a Customer.")
        return redirect('/log')
        
    cust_id = request.session['customer_id']
    cust_obj = customer.objects.get(id=cust_id)
    
    cart_items = cart.objects.filter(CUSTOMER=cust_obj)
    
    # Calculate total price
    total_price = 0
    for item in cart_items:
        try:
            total_price += float(item.PRODUCT.price)
        except ValueError:
            pass
            
    context = {
        'data': cart_items,
        'total_price': f"{total_price:.2f}",
    }
    return render(request, 'customer/customer_viewcart.html', context)

def customer_remove_cart(request, cart_id):
    if not check_customer(request):
        messages.error(request, "Unauthorized request.")
        return redirect('/log')
        
    cust_id = request.session['customer_id']
    cust_obj = customer.objects.get(id=cust_id)
    
    try:
        cart.objects.get(id=cart_id, CUSTOMER=cust_obj).delete()
        messages.success(request, "Item removed from cart.")
    except cart.DoesNotExist:
        messages.error(request, "Cart item not found.")
        
    return redirect('/customer_viewcart')

def customer_checkout(request):
    if not check_customer(request):
        messages.error(request, "Please log in as a Customer.")
        return redirect('/log')
        
    cust_id = request.session['customer_id']
    cust_obj = customer.objects.get(id=cust_id)
    
    cart_items = cart.objects.filter(CUSTOMER=cust_obj)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('/customer_viewcart')
        
    total_price = 0
    for item in cart_items:
        try:
            total_price += float(item.PRODUCT.price)
        except ValueError:
            pass
            
    context = {
        'data': cart_items,
        'total_price': f"{total_price:.2f}",
    }
    return render(request, 'customer/customer_checkout.html', context)

def customer_place_order(request):
    if not check_customer(request):
        messages.error(request, "Unauthorized request.")
        return redirect('/log')
        
    cust_id = request.session['customer_id']
    cust_obj = customer.objects.get(id=cust_id)
    
    cart_items = cart.objects.filter(CUSTOMER=cust_obj)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('/customer_viewcart')
        
    payment_method = request.POST.get('payment_method', 'Cash on Delivery')
    today = datetime.date.today().strftime('%Y-%m-%d')
    
    for item in cart_items:
        # 1. Create order
        new_order = order(
            date=today,
            price=item.PRODUCT.price,
            status='pending',
            CUSTOMER=cust_obj,
            PRODUCT=item.PRODUCT
        )
        new_order.save()
        
        # 2. Create sub-order (ordersub)
        new_sub = ordersub(
            price=item.PRODUCT.price,
            PRODUCT=item.PRODUCT,
            ORDER=new_order
        )
        new_sub.save()
        
        # 3. Create payment transaction
        new_payment = payment(
            paymentmethods=payment_method,
            ORDER=new_order
        )
        new_payment.save()
        
        # Deduct quantity if it is numeric
        try:
            qty = int(item.PRODUCT.quantity)
            if qty > 0:
                item.PRODUCT.quantity = str(qty - 1)
                item.PRODUCT.save()
        except ValueError:
            pass
            
        # 4. Remove item from cart
        item.delete()
        
    messages.success(request, "Order placed successfully! Thank you for purchasing.")
    return redirect('/customer_vieworders')

def customer_vieworders(request):
    if not check_customer(request):
        messages.error(request, "Please log in as a Customer.")
        return redirect('/log')
        
    cust_id = request.session['customer_id']
    cust_obj = customer.objects.get(id=cust_id)
    
    orders = order.objects.filter(CUSTOMER=cust_obj).order_by('-id')
    return render(request, 'customer/customer_vieworders.html', {'data': orders})

def customer_addfeedback(request, product_id):
    if not check_customer(request):
        messages.error(request, "Please log in as a Customer.")
        return redirect('/log')
        
    try:
        prod = product.objects.get(id=product_id)
        return render(request, 'customer/customer_addfeedback.html', {'product': prod})
    except product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('/customer_viewproducts')

def customer_addfeedback_post(request, product_id):
    if not check_customer(request):
        messages.error(request, "Unauthorized request.")
        return redirect('/log')
        
    cust_id = request.session['customer_id']
    cust_obj = customer.objects.get(id=cust_id)
    
    try:
        prod = product.objects.get(id=product_id)
        feedback_text = request.POST.get('feedback')
        today = datetime.date.today().strftime('%Y-%m-%d')
        
        # 1. Add to feedback table
        feed_obj = feedback(
            feedback=feedback_text,
            feedbackdate=today,
            CUSTOMER=cust_obj,
            PRODUCT=prod
        )
        feed_obj.save()
        
        # 2. Add to review table
        rev_obj = review(
            review=feedback_text,
            reviewdate=today,
            CUSTOMER=cust_obj,
            PRODUCT=prod
        )
        rev_obj.save()
        
        messages.success(request, "Thank you! Feedback and Review submitted successfully.")
    except product.DoesNotExist:
        messages.error(request, "Product not found.")
        
    return redirect('/customer_viewproducts')

def customer_addcomplaint(request):
    if not check_customer(request):
        messages.error(request, "Please log in as a Customer.")
        return redirect('/log')
    return render(request, 'customer/customer_addcomplaint.html')

def customer_addcomplaint_post(request):
    if not check_customer(request):
        messages.error(request, "Unauthorized request.")
        return redirect('/log')
        
    cust_id = request.session['customer_id']
    cust_obj = customer.objects.get(id=cust_id)
    
    comp_text = request.POST.get('complaint')
    today = datetime.date.today().strftime('%Y-%m-%d')
    
    comp_obj = complaint(
        complaint=comp_text,
        complaintdate=today,
        reply='pending',
        replydate='',
        CUSTOMER=cust_obj
    )
    comp_obj.save()
    
    messages.success(request, "Complaint submitted successfully.")
    return redirect('/customer_viewcomplaints')

def customer_viewcomplaints(request):
    if not check_customer(request):
        messages.error(request, "Please log in as a Customer.")
        return redirect('/log')
        
    cust_id = request.session['customer_id']
    cust_obj = customer.objects.get(id=cust_id)
    
    data = complaint.objects.filter(CUSTOMER=cust_obj).order_by('-id')
    return render(request, 'customer/customer_viewcomplaints.html', {'data': data})

def customer_chat(request):
    if not check_customer(request):
        messages.error(request, "Please log in as a Customer.")
        return redirect('/log')
        
    cust_id = request.session['customer_id']
    cust_obj = customer.objects.get(id=cust_id)
    
    # Get unique list of artisans they have chatted with
    chatted_art_ids = chat.objects.filter(CUSTOMER=cust_obj).values_list('ARTISAN_id', flat=True).distinct()
    recent_artisans = artisan.objects.filter(id__in=chatted_art_ids)
    
    # Other artisans in the system
    all_artisans = artisan.objects.exclude(id__in=chatted_art_ids)
    
    return render(request, 'customer/chat_list.html', {
        'recent_artisans': recent_artisans,
        'all_artisans': all_artisans
    })

def customer_chatroom(request, artisan_id):
    if not check_customer(request):
        messages.error(request, "Please log in as a Customer.")
        return redirect('/log')
        
    cust_id = request.session['customer_id']
    cust_obj = customer.objects.get(id=cust_id)
    
    try:
        art_obj = artisan.objects.get(id=artisan_id)
        messages_list = chat.objects.filter(CUSTOMER=cust_obj, ARTISAN=art_obj).order_by('id')
        return render(request, 'customer/chat_room.html', {
            'artisan': art_obj,
            'chats': messages_list
        })
    except artisan.DoesNotExist:
        messages.error(request, "Artisan not found.")
        return redirect('/customer_chat')

def customer_chat_send(request, artisan_id):
    if not check_customer(request):
        messages.error(request, "Unauthorized request.")
        return redirect('/log')
        
    cust_id = request.session['customer_id']
    cust_obj = customer.objects.get(id=cust_id)
    chat_text = request.POST.get('chat_text')
    today = datetime.date.today().strftime('%Y-%m-%d')
    
    if chat_text:
        # Since it is sent by customer, we save it directly (without prefix)
        chat_obj = chat(chat=chat_text, chatdate=today, CUSTOMER=cust_obj, ARTISAN_id=artisan_id)
        chat_obj.save()
        
    return redirect(f'/customer_chatroom/{artisan_id}')

