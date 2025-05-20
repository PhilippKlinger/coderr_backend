from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import Profile
from rest_framework.authtoken.models import Token

class AccountsTests(APITestCase):
    def setUp(self):
        # Customer user
        self.customer = User.objects.create_user(username="kunde", password="pw1", email="kunde@test.de", first_name="Cust", last_name="Omer")
        self.customer_profile = Profile.objects.create(user=self.customer, type="customer")
        self.customer_token = Token.objects.create(user=self.customer)

        # Business user
        self.business = User.objects.create_user(username="business", password="pw2", email="business@test.de", first_name="Biz", last_name="Ness")
        self.business_profile = Profile.objects.create(user=self.business, type="business")
        self.business_token = Token.objects.create(user=self.business)

    # --- Register ---
    def test_registration_success(self):
        url = reverse("register")
        data = {
            "username": "newuser",
            "email": "newuser@mail.com",
            "password": "Newuser1234",
            "repeated_password": "Newuser1234",
            "type": "customer",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_registration_passwords_do_not_match(self):
        url = reverse("register")
        data = {
            "username": "failuser",
            "email": "fail@mail.com",
            "password": "pw1",
            "repeated_password": "pw2",
            "type": "business",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", str(response.data).lower())

    def test_registration_duplicate_username(self):
        url = reverse("register")
        data = {
            "username": "kunde", 
            "email": "neu@mail.com",
            "password": "Pw123456!",
            "repeated_password": "Pw123456!",
            "type": "customer",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", str(response.data).lower())

    def test_registration_duplicate_email(self):
        url = reverse("register")
        data = {
            "username": "uniqueusername",
            "email": "kunde@test.de",  
            "password": "Pw123456!",
            "repeated_password": "Pw123456!",
            "type": "customer",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", str(response.data).lower())

    # --- LOGIN ---
    def test_login_success(self):
        url = reverse("login")
        data = {"username": "kunde", "password": "pw1"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)

    def test_login_wrong_password(self):
        url = reverse("login")
        data = {"username": "kunde", "password": "falsch"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_login_missing_fields(self):
        url = reverse("login")
        data = {"username": "kunde"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    # --- USER-PROFILE VIEW ---
    def test_get_own_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        url = reverse("user-profile", args=[self.customer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "kunde")
        self.assertEqual(response.data["type"], "customer")
        self.assertNotIn("location", response.data)

    def test_get_other_profile_no_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        url = reverse("user-profile", args=[self.business.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_patch_own_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        url = reverse("user-profile", args=[self.customer.id])
        data = {"first_name": "NeuerName"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        # Fetch updated user
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.first_name, "NeuerName")

    def test_patch_other_profile_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        url = reverse("user-profile", args=[self.business.id])
        data = {"first_name": "KeinZugriff"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 403)

    # --- BUSINESS PROFILES LIST ---
    def test_business_profiles_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        url = reverse("business-profile-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) >= 1)
        self.assertIn("user", response.data[0])
        self.assertEqual(response.data[0]["type"], "business")

    def test_business_profiles_requires_auth(self):
        url = reverse("business-profile-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    # --- CUSTOMER PROFILES LIST ---
    def test_customer_profiles_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        url = reverse("customer-profile-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) >= 1)
        self.assertIn("user", response.data[0])
        self.assertEqual(response.data[0]["type"], "customer")

    def test_customer_profiles_requires_auth(self):
        url = reverse("customer-profile-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
