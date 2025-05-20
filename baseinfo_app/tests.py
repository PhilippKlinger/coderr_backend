from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from accounts_app.models import Profile
from reviews_app.models import Review
from offers_app.models import Offer
from django.contrib.auth.models import User

class BaseInfoViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        user1 = User.objects.create_user(username="test1", password="pw", email="t1@ex.com")
        user2 = User.objects.create_user(username="test2", password="pw", email="t2@ex.com")
        Profile.objects.create(user=user1, type="business")
        Profile.objects.create(user=user2, type="customer")
        offer = Offer.objects.create(user=user1, title="Logo", description="desc")
        Review.objects.create(business_user=user1, reviewer=user2, rating=4, description="Nice!")

    def test_baseinfo_returns_counts_and_average(self):
        response = self.client.get("/api/base-info/")
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn("review_count", data)
        self.assertIn("average_rating", data)
        self.assertIn("business_profile_count", data)
        self.assertIn("offer_count", data)
        self.assertEqual(data["review_count"], 1)
        self.assertEqual(data["average_rating"], 4.0)
        self.assertEqual(data["business_profile_count"], 1)
        self.assertEqual(data["offer_count"], 1)

    def test_baseinfo_no_data(self):

        Review.objects.all().delete()
        Offer.objects.all().delete()
        Profile.objects.all().delete()
        response = self.client.get("/api/base-info/")
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data["review_count"], 0)
        self.assertEqual(data["average_rating"], 0)
        self.assertEqual(data["business_profile_count"], 0)
        self.assertEqual(data["offer_count"], 0)
