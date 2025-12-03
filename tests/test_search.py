"""
Test Suite for Search Functionality
Maps to Requirements: REQ-18, REQ-19, REQ-27, REQ-28, REQ-29, REQ-30, REQ-31, REQ-32, REQ-33
User Stories: As per GitHub issues - product search and filtering
"""

import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Product, Category, Tags
from decimal import Decimal

User = get_user_model()


@pytest.mark.django_db
class TestSearchFunctionality:
    """Test cases for product search and filtering functionality"""

    @pytest.fixture
    def client(self):
        """Fixture to provide a test client"""
        return Client()

    @pytest.fixture
    def test_user(self):
        """Create a test vendor user"""
        user = User.objects.create_user(
            username='testvendor',
            email='testvendor@example.com',
            password='VendorPass123'
        )
        return user

    @pytest.fixture
    def test_category(self):
        """Create test category for products"""
        return Category.objects.create(
            title='Graphics Cards',
            image=None
        )

    @pytest.fixture
    def test_tags(self):
        """
        Create test tags for filtering
        Maps to: REQ-27 (Must only list items that have one or more tags that apply to the filter)
        """
        # Use get_or_create with slug only to handle existing tags from production DB
        tag1, _ = Tags.objects.get_or_create(slug='nvidia', defaults={'name': 'NVIDIA'})
        tag2, _ = Tags.objects.get_or_create(slug='gaming', defaults={'name': 'Gaming'})
        tag3, _ = Tags.objects.get_or_create(slug='rtx', defaults={'name': 'RTX'})
        return [tag1, tag2, tag3]

    @pytest.fixture
    def sample_products(self, test_user, test_category, test_tags):
        """
        Create sample published products for testing
        Maps to: REQ-18, REQ-19 (Users must be able to view listings)
        """
        # Product 1: RTX 3080
        product1 = Product.objects.create(
            title='NVIDIA RTX 3080 Graphics Card',
            description='High-performance gaming GPU',
            price=Decimal('699.99'),
            user=test_user,
            category=test_category,
            product_status='published',
            in_stock=True
        )
        product1.tags.set([test_tags[0], test_tags[1], test_tags[2]])
        
        # Product 2: RTX 4090
        product2 = Product.objects.create(
            title='NVIDIA RTX 4090 Graphics Card',
            description='Top-tier gaming and professional GPU',
            price=Decimal('1599.99'),
            user=test_user,
            category=test_category,
            product_status='published',
            in_stock=True
        )
        product2.tags.set([test_tags[0], test_tags[1], test_tags[2]])
        
        # Product 3: Gaming Motherboard (different category, different tags)
        product3 = Product.objects.create(
            title='ASUS Gaming Motherboard',
            description='ATX gaming motherboard',
            price=Decimal('299.99'),
            user=test_user,
            category=test_category,
            product_status='published',
            in_stock=True
        )
        product3.tags.set([test_tags[1]])  # Only gaming tag
        
        # Product 4: Unpublished (should not appear in search)
        product4 = Product.objects.create(
            title='Pending Review GPU',
            description='Should not appear in search',
            price=Decimal('499.99'),
            user=test_user,
            category=test_category,
            product_status='in_review',
            in_stock=True
        )
        
        return [product1, product2, product3, product4]

    def test_search_by_product_name(self, client, sample_products):
        """
        Test Case 1: Search returns products matching keyword in title
        
        Expected: Only published products matching "RTX" are returned
        """
        search_url = reverse('core:search')
        response = client.get(search_url, {'q': 'RTX'})
        
        assert response.status_code == 200
        products = response.context['products']
        
        # Should return 2 published products with RTX in title
        assert products.count() == 2
        
        # Verify both RTX products are in results
        product_titles = [p.title for p in products]
        assert any('3080' in title for title in product_titles)
        assert any('4090' in title for title in product_titles)
        
        # Verify unpublished product is not in results
        assert not any('Pending Review' in title for title in product_titles)

    def test_search_displays_all_listings_when_no_query(self, client, sample_products):
        """
        Test Case 2: Empty search displays all published listings
        
        Expected: All published products displayed, unpublished excluded
        """
        search_url = reverse('core:search')
        response = client.get(search_url)
        
        assert response.status_code == 200
        products = response.context['products']
        
        # Should return at least 3 published products from our fixtures
        # (may be more from production database)
        assert products.count() >= 3
        
        # Verify our test products are included
        test_product_titles = [p.title for p in sample_products[:3]]  # First 3 are published
        response_titles = [p.title for p in products]
        for title in test_product_titles:
            assert title in response_titles, f"Test product '{title}' should be in search results"
        
        # Verify only published products
        for product in products:
            assert product.product_status == 'published'
        
        # Verify our unpublished product is NOT included
        assert 'Pending Review GPU' not in response_titles

    def test_tag_filter_shows_only_matching_products(self, client, sample_products, test_tags):
        """
        Test Case 3: Tag filtering shows only products with selected tags
        
        Expected: Only products tagged with NVIDIA are displayed
        """
        search_url = reverse('core:search')
        # Filter by NVIDIA tag
        response = client.get(search_url, {'tag': 'nvidia'})
        
        assert response.status_code == 200
        products = response.context['products']
        
        # Should return 2 products with NVIDIA tag (RTX 3080 and 4090)
        assert products.count() == 2
        
        # Verify all returned products have the NVIDIA tag
        for product in products:
            tag_names = [tag.slug for tag in product.tags.all()]
            assert 'nvidia' in tag_names

    def test_reset_filter_shows_all_products(self, client, sample_products):
        """
        Test Case 4: Reset button clears filter and shows all products
        
        Expected: All published products displayed, no active filters
        """
        search_url = reverse('core:search')
        
        # First apply a filter
        filtered_response = client.get(search_url, {'tag': 'nvidia'})
        filtered_products = filtered_response.context['products']
        assert filtered_products.count() == 2
        
        # Now reset (visit search without parameters)
        reset_response = client.get(search_url)
        reset_products = reset_response.context['products']
        
        # Should show more products than filtered (at least 3 from our fixtures)
        assert reset_products.count() > filtered_products.count()
        assert reset_products.count() >= 3
        
        # Verify context shows no active tag filter
        active_tag = reset_response.context.get('selected_tag', None)
        assert active_tag is None or active_tag == ''

    def test_search_case_insensitive_matching(self, client, sample_products):
        """
        Test Case 5: Search is case-insensitive and finds partial matches
        
        Expected: Case-insensitive search finds relevant products quickly
        """
        search_url = reverse('core:search')
        
        # Test lowercase search for NVIDIA
        response = client.get(search_url, {'q': 'nvidia'})
        assert response.status_code == 200
        products = response.context['products']
        assert products.count() >= 2
        
        # Test partial match
        response2 = client.get(search_url, {'q': 'gaming'})
        assert response2.status_code == 200
        products2 = response2.context['products']
        
        # Should find at least the Gaming Motherboard and possibly others with gaming tag
        assert products2.count() >= 1
        
        # Verify one of them is the ASUS Gaming Motherboard
        product_titles = [p.title for p in products2]
        assert any('ASUS' in title or 'Gaming' in title for title in product_titles)


# Additional configuration
@pytest.fixture(scope='session')
def django_db_setup():
    """Setup test database"""
    pass
