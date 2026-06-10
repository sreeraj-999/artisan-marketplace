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
        elif user.usertype == 'blocked':
            messages.error(request, "Your account has been blocked by the Administrator.")
            return redirect('/log')
        else:
            messages.error(request, "Access restricted. Customers must log in via the mobile application.")
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
        
    art_obj = artisan.objects.get(id=request.session['artisan_id'])
    chat_text = request.POST.get('chat_text')
    today = datetime.date.today().strftime('%Y-%m-%d')
    
    if chat_text:
        prefixed_text = f"Artisan: {chat_text}"
        chat_obj = chat(chat=prefixed_text, chatdate=today, ARTISAN=art_obj, CUSTOMER_id=customer_id)
        chat_obj.save()
        
    return redirect(f'/artisan_chatroom/{customer_id}')
