from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from reviews_app.models import Review
from accounts_app.models import Profile

class ReviewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # User create
        self.customer_user = User.objects.create_user(username="kunde", password="test123", email="kunde@example.com")
        self.business_user = User.objects.create_user(username="business", password="test123", email="business@example.com")
        # Profile create
        Profile.objects.create(user=self.customer_user, type="customer")
        Profile.objects.create(user=self.business_user, type="business")

        self.token_customer = Token.objects.create(user=self.customer_user)
        self.token_business = Token.objects.create(user=self.business_user)

        self.review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=5,
            description="Super Service"
        )

    def auth_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_customer.key)

    def auth_business(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_business.key)

    def unauth(self):
        self.client.credentials()

    def test_review_list_authenticated(self):
        self.auth_customer()
        response = self.client.get("/api/reviews/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.data, list))

    def test_review_list_unauthenticated(self):
        self.unauth()
        response = self.client.get("/api/reviews/")
        self.assertEqual(response.status_code, 401)

    def test_create_review_as_customer(self):
        self.auth_customer()
        # additional Business for unique_together Error
        business2 = User.objects.create_user(username="biz2", password="pw", email="b2@ex.com")
        Profile.objects.create(user=business2, type="business")

        data = {
            "business_user": business2.id,
            "rating": 4,
            "description": "Gut, aber ausbaufähig."
        }
        response = self.client.post("/api/reviews/", data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["rating"], 4)

    def test_create_review_duplicate(self):
        self.auth_customer()
        data = {
            "business_user": self.business_user.id,
            "rating": 3,
            "description": "Noch eine Bewertung"
        }
        response = self.client.post("/api/reviews/", data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Du hast bereits eine Bewertung abgegeben.", str(response.data))

    def test_create_review_as_business_forbidden(self):
        self.auth_business()
        data = {
            "business_user": self.business_user.id,
            "rating": 5,
            "description": "Fake Bewertung"
        }
        response = self.client.post("/api/reviews/", data)
        self.assertEqual(response.status_code, 403)
        self.assertIn("permission", str(response.data).lower())

    def test_retrieve_review(self):
        self.auth_customer()
        url = f"/api/reviews/{self.review.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.review.id)

    def test_update_review_by_reviewer(self):
        self.auth_customer()
        url = f"/api/reviews/{self.review.id}/"
        data = {"rating": 2, "description": "Update!"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 2)
        self.assertEqual(self.review.description, "Update!")

    def test_update_review_by_non_reviewer_forbidden(self):
        self.auth_business()
        url = f"/api/reviews/{self.review.id}/"
        data = {"rating": 1}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 403)

    def test_delete_review_by_reviewer(self):
        self.auth_customer()
        url = f"/api/reviews/{self.review.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    def test_delete_review_by_non_reviewer_forbidden(self):
        self.auth_business()
        url = f"/api/reviews/{self.review.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_retrieve_review_unauthenticated(self):
        self.unauth()
        url = f"/api/reviews/{self.review.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_review_filter_by_business_user(self):
        self.auth_customer()
        response = self.client.get(f"/api/reviews/?business_user_id={self.business_user.id}")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_review_ordering(self):
        self.auth_customer()
        # two Reviews for Ordering
        business2 = User.objects.create_user(username="biz2", password="pw", email="b2@ex.com")
        Profile.objects.create(user=business2, type="business")

        Review.objects.create(business_user=business2, reviewer=self.customer_user, rating=3)
        response = self.client.get(f"/api/reviews/?ordering=-rating")
        self.assertEqual(response.status_code, 200)
