from django.test import TestCase
from Artstore.models import login, artisan, category, customer, product

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
