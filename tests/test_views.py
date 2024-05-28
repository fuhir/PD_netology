from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from backend.models import User, Shop, Order

class TestAccountDetails(APITestCase):
    """
    Test for getting and modifying account detail
    """
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', email='testuser@test.com', password='testpassword')

    def test_get_account_details_authenticated(self):
        # Log in the user
        self.client.force_login(self.user)

        # Send a GET request to the view
        url = reverse('user_details')
        response = self.client.get(url)

        # Assert the response status code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], 'testuser')  # Adjust this based on your serializer

    def test_get_account_details_unauthenticated(self):
        # Send a GET request to the view without authenticating
        url = reverse('user_details')
        response = self.client.get(url)

        # Assert the response status code and content
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'Status': False, 'Error': 'Log in required'})

    def test_update_account_details_authenticated(self):
        # Log in the user
        self.client.force_login(self.user)

        # Send a POST request to update account details
        data = {'email': 'newemail@example.com'}  # Adjust data as needed
        url = reverse('user_details')
        response = self.client.post(url, data, format='json')

        # Assert the response status code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'Status': True})

        # Refresh the user instance from the database
        self.user.refresh_from_db()

        # Assert that the user's details have been updated
        self.assertEqual(self.user.email, 'newemail@example.com')

    def test_update_account_details_unauthenticated(self):
        # Send a POST request to update account details without authenticating
        url = reverse('user_details')
        response = self.client.post(url, {'email': 'newemail@example.com'})

        # Assert the response status code and content
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'Status': False, 'Error': 'Log in required'})


class TestPartnerStateView(APITestCase):
    """
    Test for getting and modifying partner state
    """
    def setUp(self):
        # Create a user with type 'shop' for testing
        self.shop_user = User.objects.create_user(username='shopuser', email='shopuser@test.com',
                                                  password='testpassword', type='shop')
        # Create a shop associated with the shop user
        self.shop = Shop.objects.create(user=self.shop_user, name='Test Shop', state=True)

    def test_get_partner_state_authenticated_shop_user(self):
        # Log in the shop user
        self.client.force_login(self.shop_user)

        # Send a GET request to the PartnerState view
        url = reverse('partner_state')  # Adjust the URL based on your project's URL configuration
        response = self.client.get(url)

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'id': self.shop.id, 'name': 'Test Shop', 'user_id': self.shop.user_id, 'state': True})

    def test_get_partner_state_unauthenticated(self):
        # Send a GET request to the PartnerState view without authenticating
        url = reverse('partner_state')  # Adjust the URL based on your project's URL configuration
        response = self.client.get(url)

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'Status': False, 'Error': 'Log in required'})

    def test_get_partner_state_authenticated_non_shop_user(self):
        # Create a user with type other than 'shop'
        non_shop_user = User.objects.create_user(username='nonshopuser', email='nonshopuser@test.com', password='testpassword', type='customer')

        # Log in the non-shop user
        self.client.force_login(non_shop_user)

        # Send a GET request to the PartnerState view
        url = reverse('partner_state')  # Adjust the URL based on your project's URL configuration
        response = self.client.get(url)

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'Status': False, 'Error': 'Shops only'})

    def test_post_partner_state_authenticated_shop_user(self):
        # Log in the shop user
        self.client.force_login(self.shop_user)

        # Send a POST request to the PartnerState view
        url = reverse('partner_state')  # Adjust the URL based on your project's URL configuration
        data = {'state': 'false'}  # Adjust the data based on your view's requirements
        response = self.client.post(url, data, format='json')

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'Status': True})
        # Add more assertions based on your view's behavior

    def test_post_partner_state_unauthenticated(self):
        # Send a POST request to the PartnerState view without authenticating
        url = reverse('partner_state')  # Adjust the URL based on your project's URL configuration
        data = {'state': 'false'}  # Adjust the data based on your view's requirements
        response = self.client.post(url, data, format='json')

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'Status': False, 'Error': 'Log in required'})

    def test_post_partner_state_authenticated_non_shop_user(self):
        # Create a user with type other than 'shop'
        non_shop_user = User.objects.create_user(username='nonshopuser', email='nonshopuser@test.com', password='testpassword', type='customer')

        # Log in the non-shop user
        self.client.force_login(non_shop_user)

        # Send a POST request to the PartnerState view
        url = reverse('partner_state')  # Adjust the URL based on your project's URL configuration
        data = {'state': 'false'}  # Adjust the data based on your view's requirements
        response = self.client.post(url, data, format='json')

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'Status': False, 'Error': 'Shops only'})
        
class TestOrderView(APITestCase):
    def setUp(self):
        # Create a shop user
        self.shop_user = User.objects.create_user(username='shopuser', email='shopuser@test.com', password='testpassword', type='shop')

        # Create a customer user
        self.customer_user = User.objects.create_user(username='customeruser', email='customeruser@test.com', password='testpassword', type='customer')

        # Create an order for the customer
        self.order = Order.objects.create(user=self.customer_user, state='new')

    def test_get_order_authenticated_customer_user(self):
        # Log in the customer user
        self.client.force_login(self.customer_user)

        # Send a GET request to the OrderView view
        url = reverse('order')  # Adjust the URL based on your project's URL configuration
        response = self.client.get(url)

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'id': self.order.id, 'state': 'new', 'user_id': self.customer_user.id})

    def test_get_order_unauthenticated(self):
        # Send a GET request to the OrderView view without authenticating
        url = reverse('order')  # Adjust the URL based on your project's URL configuration
        response = self.client.get(url)

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'Status': False, 'Error': 'Log in required'})
        
    def test_get_order_authenticated_non_customer_user(self):
        # Create a user with type other than 'customer'
        non_customer_user = User.objects.create_user(username='noncustomeruser', email='noncustomeruser@test.com', password='testpassword', type='shop')

        # Log in the non-customer user
        self.client.force_login(non_customer_user)

        # Send a GET request to the OrderView view
        url = reverse('order')  # Adjust the URL based on your project's URL configuration
        response = self.client.get(url)

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'Status': False, 'Error': 'Customers only'})
        
class ContactView(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', email='testuser@test.com', password='testpassword')

    def test_get_contact_authenticated(self):
        # Log in the user
        self.client.force_login(self.user)

        # Send a GET request to the ContactView view
        url = reverse('user-contact')  # Adjust the URL based on your project's URL configuration
        response = self.client.get(url)

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])
        
    def test_get_contact_unauthenticated(self):
        # Send a GET request to the ContactView view without authenticating
        url = reverse('user-contact')  # Adjust the URL based on your project's URL configuration
        response = self.client.get(url)

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'Status': False, 'Error': 'Log in required'})
        
    def test_get_contact_authenticated_non_user(self):
        # Create a user with type other than 'user'
        non_user = User.objects.create_user(username='nonuser', email='nonuser@test.com', password='testpassword', type='shop')

        # Log in the non-user
        self.client.force_login(non_user)

        # Send a GET request to the ContactView view
        
        url = reverse('user-contact')  # Adjust the URL based on your project's URL configuration
        response = self.client.get(url)

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'Status': False, 'Error': 'Users only'})
        
    def test_post_contact_authenticated(self):
        # Log in the user
        self.client.force_login(self.user)

        # Send a POST request to the ContactView view
        url = reverse('user-contact')  # Adjust the URL based on your project's URL configuration
        data = {'city': 'Test City', 'street': 'Test Street', 'phone': '1234567890'}
        response = self.client.post(url, data)

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), {'Status': True, 'Message': 'Contact information saved successfully'})
        
    def test_post_contact_unauthenticated(self):
        # Send a POST request to the ContactView view without authenticating
        url = reverse('user-contact')  # Adjust the URL based on your project's URL configuration
        data = {'city': 'Test City', 'street': 'Test Street', 'phone': '1234567890'}
        response = self.client.post(url, data)

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'Status': False, 'Error': 'Log in required'})
        
    def test_post_contact_authenticated_non_user(self):
        # Create a user with type other than 'user'
        non_user = User.objects.create_user(username='nonuser', email='nonuser@test.com', password='testpassword', type='shop')

        # Log in the non-user
        self.client.force_login(non_user)

        # Send a POST request to the ContactView view
        url = reverse('user-contact')  # Adjust the URL based on your project's URL configuration
        data = {'city': 'Test City', 'street': 'Test Street', 'phone': '1234567890'}
        response = self.client.post(url, data)

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'Status': False, 'Error': 'Users only'})
        
    def test_delete_contact_authenticated(self):
        # Log in the user
        self.client.force_login(self.user)

        # Send a DELETE request to the ContactView view
        url = reverse('user-contact')  # Adjust the URL based on your project's URL configuration
        response = self.client.delete(url)

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.json(), {'Status': True, 'Message': 'Contact information deleted successfully'})
        
    def test_delete_contact_unauthenticated(self):
        # Send a DELETE request to the ContactView view without authenticating
        url = reverse('user-contact')  # Adjust the URL based on your project's URL configuration
        response = self.client.delete(url)

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'Status': False, 'Error': 'Log in required'})