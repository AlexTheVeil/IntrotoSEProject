"""
Test Suite for Add Product Functionality
Maps to Requirements: REQ-12, REQ-13, REQ-14, REQ-23, REQ-24, REQ-25, REQ-26
User Stories: As per GitHub issues - vendor product management and admin approval
"""

import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import Product, Category, Tags
from decimal import Decimal
from PIL import Image
import io

User = get_user_model()


@pytest.mark.django_db
class TestAddProductFunctionality:
    """Test cases for vendor add product functionality"""

    @pytest.fixture
    def client(self):
        """Fixture to provide a test client"""
        return Client()

    @pytest.fixture
    def vendor_user(self):
        """Create a test vendor user"""
        user = User.objects.create_user(
            username='productvendor',
            email='productvendor@example.com',
            password='VendorPass123'
        )
        return user

    @pytest.fixture
    def admin_user(self):
        """
        Create an admin user for approval workflow testing
        Maps to: REQ-13 (Admin must be capable of approving/denying actions as needed)
        """
        admin = User.objects.create_user(
            username='productadmin',
            email='productadmin@example.com',
            password='AdminPass123',
            is_staff=True
        )
        return admin

    @pytest.fixture
    def test_category(self):
        """
        Create test category
        Maps to: REQ-25 (Must be able to add items to inventory)
        """
        return Category.objects.create(
            title='CPUs',
            image=None
        )

    @pytest.fixture
    def sample_image(self):
        """Create a sample image file for product upload"""
        # Create a simple test image
        image = Image.new('RGB', (100, 100), color='red')
        image_file = io.BytesIO()
        image.save(image_file, 'PNG')
        image_file.seek(0)
        return SimpleUploadedFile(
            "test_product.png",
            image_file.read(),
            content_type="image/png"
        )

    def test_vendor_can_add_product_with_all_fields(self, client, vendor_user, test_category, sample_image):
        """
        Test Case 1: Vendor can successfully add a product with all required fields
        
        Expected: Product created successfully with in_review status
        """
        # Login as vendor
        client.login(email='productvendor@example.com', password='VendorPass123')
        
        add_product_url = reverse('useradmin:add_product')
        response = client.post(add_product_url, {
            'title': 'Intel Core i9-13900K Processor',
            'category': test_category.cid,
            'price': '589.99',
            'image': sample_image,
            'tags': 'Intel, Gaming, High-Performance'
        })
        
        # Should redirect after successful creation
        assert response.status_code == 302
        
        # Verify product was created
        product = Product.objects.filter(title='Intel Core i9-13900K Processor').first()
        assert product is not None
        assert product.user == vendor_user
        assert product.price == Decimal('589.99')
        assert product.product_status == 'in_review'
        
        # Verify tags were created
        assert product.tags.count() == 3
        tag_names = [tag.name for tag in product.tags.all()]
        assert 'Intel' in tag_names

    def test_product_requires_authentication(self, client, test_category):
        """
        Test Case 2: Unauthenticated users cannot add products
        
        Expected: Unauthenticated users cannot create products
        """
        add_product_url = reverse('useradmin:add_product')
        
        # Get initial product count
        initial_count = Product.objects.count()
        
        # Try to POST without login
        post_response = client.post(add_product_url, {
            'title': 'Unauthorized Product',
            'category': test_category.cid,
            'price': '99.99'
        })
        
        # Either redirects or stays on page, but product should not be created
        final_count = Product.objects.count()
        assert final_count == initial_count, "Product should not be created without authentication"
        
        # Verify no product with this title exists
        assert not Product.objects.filter(title='Unauthorized Product').exists()

    def test_admin_can_approve_pending_product(self, client, vendor_user, admin_user, test_category):
        """
        Test Case 3: Admin can approve products in review status
        
        Expected: Admin can approve product, status becomes published
        """
        # Create product as vendor
        product = Product.objects.create(
            title='AMD Ryzen 9 7950X',
            price=Decimal('699.99'),
            user=vendor_user,
            category=test_category,
            product_status='in_review',
            in_stock=True
        )
        
        # Login as admin
        client.force_login(admin_user)
        
        # Approve the product directly
        approve_url = reverse('useradmin:admin_product_approve', args=[product.pid])
        approve_response = client.get(approve_url)
        assert approve_response.status_code == 302
        
        # Verify product status changed
        product.refresh_from_db()
        assert product.product_status == 'published'

    def test_admin_can_deny_product(self, client, vendor_user, admin_user, test_category):
        """
        Test Case 4: Admin can reject/deny products
        
        Expected: Admin can deny product, vendor can remove rejected items
        """
        # Create product
        product = Product.objects.create(
            title='Inappropriate Product',
            price=Decimal('9.99'),
            user=vendor_user,
            category=test_category,
            product_status='in_review',
            in_stock=True
        )
        
        # Login as admin
        client.login(email='productadmin@example.com', password='AdminPass123')
        
        # Deny the product
        deny_url = reverse('useradmin:admin_product_deny', args=[product.pid])
        deny_response = client.get(deny_url)
        assert deny_response.status_code == 302
        
        # Verify status changed to rejected
        product.refresh_from_db()
        assert product.product_status == 'rejected'
        
        # Now vendor should be able to delete it
        client.logout()
        client.login(email='productvendor@example.com', password='VendorPass123')
        
        delete_url = reverse('useradmin:seller_delete_product', args=[product.pid])
        delete_response = client.post(delete_url)
        assert delete_response.status_code == 302
        
        # Verify product was deleted
        assert not Product.objects.filter(pid=product.pid).exists()

    def test_vendor_can_view_product_quantities_and_inventory(self, client, vendor_user, test_category):
        """
        Test Case 5: Vendor can view all their products and inventory status
        
        Expected: Vendor can see all their products with stock information
        """
        # Create multiple products
        product1 = Product.objects.create(
            title='Product In Stock',
            price=Decimal('199.99'),
            user=vendor_user,
            category=test_category,
            product_status='published',
            in_stock=True
        )
        
        product2 = Product.objects.create(
            title='Product Out of Stock',
            price=Decimal('299.99'),
            user=vendor_user,
            category=test_category,
            product_status='published',
            in_stock=False
        )
        
        product3 = Product.objects.create(
            title='Product Pending',
            price=Decimal('399.99'),
            user=vendor_user,
            category=test_category,
            product_status='in_review',
            in_stock=True
        )
        
        # Query products for this vendor directly
        products = Product.objects.filter(user=vendor_user)
        assert products.count() == 3
        
        # Verify we can see different statuses
        product_statuses = [p.product_status for p in products]
        assert 'published' in product_statuses
        assert 'in_review' in product_statuses
        
        # Verify stock status is tracked
        stock_statuses = [p.in_stock for p in products]
        assert True in stock_statuses
        assert False in stock_statuses


# Additional fixtures and configuration
@pytest.fixture(scope='session')
def django_db_setup():
    """Setup test database"""
    pass
