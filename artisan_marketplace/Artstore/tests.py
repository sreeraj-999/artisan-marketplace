from django.test import TestCase
from Artstore.models import login, artisan, category, customer, product, cart, order, ordersub, payment, feedback, review, complaint

class ArtisanMarketplaceTests(TestCase):
    
    def setUp(self):
        # Create default admin credentials
        login.objects.create(username='admin', password='admin', usertype='admin')
        
    def test_admin_created(self):
        admin_user = login.objects.filter(username='admin', usertype='admin')
        self.assertTrue(admin_user.exists())
        self.assertEqual(admin_user.first().password, 'admin')
        
    def test_category_management(self):
        # Add category
        cat = category.objects.create(category='Handmade Pottery')
        self.assertEqual(cat.category, 'Handmade Pottery')
        
        # Update category
        category.objects.filter(id=cat.id).update(category='Pottery')
        cat.refresh_from_db()
        self.assertEqual(cat.category, 'Pottery')
        
        # Delete category
        category.objects.get(id=cat.id).delete()
        self.assertFalse(category.objects.filter(category='Pottery').exists())
        
    def test_artisan_registration_and_moderation(self):
        # Register artisan
        log_obj = login.objects.create(username='john_artisan', password='securepass', usertype='artisan')
        art_obj = artisan.objects.create(
            name='John Doe', 
            phone='1234567890', 
            email='john@example.com', 
            place='New York', 
            gender='Male', 
            LOGIN=log_obj
        )
        
        self.assertEqual(art_obj.name, 'John Doe')
        self.assertEqual(art_obj.LOGIN.username, 'john_artisan')
        self.assertEqual(art_obj.LOGIN.usertype, 'artisan')
        
        # Block artisan
        art_obj.LOGIN.usertype = 'blocked'
        art_obj.LOGIN.save()
        
        # Refresh login object
        log_obj.refresh_from_db()
        self.assertEqual(log_obj.usertype, 'blocked')
        
        # Unblock artisan
        log_obj.usertype = 'artisan'
        log_obj.save()
        log_obj.refresh_from_db()
        self.assertEqual(log_obj.usertype, 'artisan')
        
    def test_product_addition(self):
        log_obj = login.objects.create(username='jane_artisan', password='securepass', usertype='artisan')
        art_obj = artisan.objects.create(
            name='Jane Doe', 
            phone='0987654321', 
            email='jane@example.com', 
            place='Boston', 
            gender='Female', 
            LOGIN=log_obj
        )
        
        # Add product
        prod = product.objects.create(
            productname='Clay Cup',
            quantity='15',
            price='20.00',
            image='cup.png',
            ARTISAN=art_obj
        )
        
        self.assertEqual(prod.productname, 'Clay Cup')
        self.assertEqual(prod.ARTISAN, art_obj)
        self.assertEqual(product.objects.filter(ARTISAN=art_obj).count(), 1)

    def test_customer_flows(self):
        # 1. Customer registration / login creation
        log_obj = login.objects.create(username='alice_cust', password='password123', usertype='customer')
        cust_obj = customer.objects.create(
            name='Alice Smith',
            phone='9876543210',
            email='alice@example.com',
            place='Seattle',
            LOGIN=log_obj
        )
        self.assertEqual(cust_obj.name, 'Alice Smith')
        self.assertEqual(cust_obj.LOGIN.username, 'alice_cust')
        
        # Create an artisan and a product for testing cart/orders
        art_log = login.objects.create(username='artisan_bob', password='bobspassword', usertype='artisan')
        art_obj = artisan.objects.create(
            name='Bob Builder',
            phone='5551234567',
            email='bob@example.com',
            place='Portland',
            gender='Male',
            LOGIN=art_log
        )
        prod = product.objects.create(
            productname='Wooden Spoon',
            quantity='10',
            price='15.50',
            image='spoon.jpg',
            ARTISAN=art_obj
        )
        
        # 2. Cart Additions
        cart_item = cart.objects.create(CUSTOMER=cust_obj, PRODUCT=prod)
        self.assertEqual(cart.objects.filter(CUSTOMER=cust_obj).count(), 1)
        self.assertEqual(cart_item.PRODUCT, prod)
        
        # 3. Order Placement and Checkout logic
        # Simulate customer_place_order logic
        new_order = order.objects.create(
            date='2026-06-12',
            price=prod.price,
            status='pending',
            CUSTOMER=cust_obj,
            PRODUCT=prod
        )
        new_sub = ordersub.objects.create(
            price=prod.price,
            PRODUCT=prod,
            ORDER=new_order
        )
        new_payment = payment.objects.create(
            paymentmethods='Credit Card',
            ORDER=new_order
        )
        
        # Verify order tables
        self.assertEqual(order.objects.filter(CUSTOMER=cust_obj).count(), 1)
        self.assertEqual(ordersub.objects.filter(ORDER=new_order).count(), 1)
        self.assertEqual(payment.objects.filter(ORDER=new_order).count(), 1)
        self.assertEqual(new_order.status, 'pending')
        
        # 4. Feedback & Review submission
        feed_obj = feedback.objects.create(
            feedback='Excellent craftsmanship!',
            feedbackdate='2026-06-12',
            CUSTOMER=cust_obj,
            PRODUCT=prod
        )
        rev_obj = review.objects.create(
            review='Excellent craftsmanship!',
            reviewdate='2026-06-12',
            CUSTOMER=cust_obj,
            PRODUCT=prod
        )
        self.assertEqual(feedback.objects.filter(CUSTOMER=cust_obj).count(), 1)
        self.assertEqual(review.objects.filter(CUSTOMER=cust_obj).count(), 1)
        
        # 5. Complaint submission
        comp_obj = complaint.objects.create(
            complaint='Shipping took longer than expected.',
            complaintdate='2026-06-12',
            reply='pending',
            replydate='',
            CUSTOMER=cust_obj
        )
        self.assertEqual(complaint.objects.filter(CUSTOMER=cust_obj).count(), 1)
        self.assertEqual(comp_obj.reply, 'pending')
