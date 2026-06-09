from django.db import models

# Create your models here.

class login(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    usertype = models.CharField(max_length=100)

class category(models.Model):
    category = models.CharField(max_length=100)

class artisan(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    LOGIN = models.ForeignKey(login,on_delete=models.CASCADE,default=1)

class customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    LOGIN = models.ForeignKey(login, on_delete=models.CASCADE, default=1)

class complaint(models.Model):
    complaint =models.CharField(max_length=100)
    complaintdate=models.CharField(max_length=100)
    reply =models.CharField(max_length=100)
    replydate =models.CharField(max_length=100)
    CUSTOMER = models.ForeignKey(customer,on_delete=models.CASCADE,default=1)

class product(models.Model):
    productname = models.CharField(max_length=100)
    quantity = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    image = models.CharField(max_length=100)
    ARTISAN = models.ForeignKey(artisan,on_delete=models.CASCADE,default=1)

class feedback(models.Model):
    feedback = models.CharField(max_length=100)
    feedbackdate = models.CharField(max_length=100)
    CUSTOMER = models.ForeignKey(customer, on_delete=models.CASCADE, default=1)
    PRODUCT = models.ForeignKey(product, on_delete=models.CASCADE, default=1)

class followers(models.Model):
    followdate = models.CharField(max_length=100)
    ARTISAN = models.ForeignKey(artisan, on_delete=models.CASCADE, default=1)
    CUSTOMER = models.ForeignKey(customer, on_delete=models.CASCADE, default=1)

class chat(models.Model):
    chat = models.CharField(max_length=100)
    chatdate = models.CharField(max_length=100)
    CUSTOMER = models.ForeignKey(customer, on_delete=models.CASCADE, default=1)
    ARTISAN = models.ForeignKey(artisan, on_delete=models.CASCADE, default=1)

class order(models.Model):
    date = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    CUSTOMER = models.ForeignKey(customer, on_delete=models.CASCADE, default=1)
    PRODUCT = models.ForeignKey(product, on_delete=models.CASCADE, default=1)

class ordersub(models.Model):
    price = models.CharField(max_length=100)
    PRODUCT = models.ForeignKey(product, on_delete=models.CASCADE, default=1)
    ORDER = models.ForeignKey(order, on_delete=models.CASCADE, default=1)

class payment(models.Model):
    paymentmethods = models.CharField(max_length=100)
    ORDER = models.ForeignKey(order, on_delete=models.CASCADE, default=1)

class review(models.Model):
    review = models.CharField(max_length=100)
    reviewdate = models.CharField(max_length=100)
    CUSTOMER = models.ForeignKey(customer, on_delete=models.CASCADE, default=1)
    PRODUCT = models.ForeignKey(product, on_delete=models.CASCADE, default=1)

class cart(models.Model):
    CUSTOMER = models.ForeignKey(customer, on_delete=models.CASCADE, default=1)
    PRODUCT = models.ForeignKey(product, on_delete=models.CASCADE, default=1)




