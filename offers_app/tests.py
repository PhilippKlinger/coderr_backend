from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from accounts_app.models import Profile
from offers_app.models import Offer, OfferDetail

class OffersTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # User/Profiles: business und customer
        self.business = User.objects.create_user(username="biz", password="pw", email="b@t.de")
        Profile.objects.create(user=self.business, type="business")
        self.customer = User.objects.create_user(username="cus", password="pw", email="c@t.de")
        Profile.objects.create(user=self.customer, type="customer")

        # Offer + Details for business
        self.offer = Offer.objects.create(user=self.business, title="Logo Design", description="desc")
        self.detail1 = OfferDetail.objects.create(offer=self.offer, title="Basic", revisions=1, delivery_time_in_days=3, price=100, features=["A"], offer_type="basic")
        self.detail2 = OfferDetail.objects.create(offer=self.offer, title="Standard", revisions=2, delivery_time_in_days=5, price=200, features=["B"], offer_type="standard")
        self.detail3 = OfferDetail.objects.create(offer=self.offer, title="Premium", revisions=3, delivery_time_in_days=7, price=300, features=["C"], offer_type="premium")

    def switch_to_business(self):
        self.client.force_authenticate(self.business)

    def switch_to_customer(self):
        self.client.force_authenticate(self.customer)

    def switch_to_anon(self):
        self.client.force_authenticate(None)

    def test_list_offers_anonymous(self):
        self.switch_to_anon()
        url = reverse("offers")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["results"]) >= 1)

    def test_list_offers_search(self):
        self.switch_to_anon()
        url = reverse("offers") + "?search=Logo"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("Logo" in offer["title"] for offer in response.data["results"]))

    def test_list_offers_filter_creator_id(self):
        self.switch_to_anon()
        url = reverse("offers") + f"?creator_id={self.business.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for offer in response.data["results"]:
            self.assertEqual(offer["user"], self.business.id)

    def test_create_offer_business(self):
        self.switch_to_business()
        url = reverse("offers")
        data = {
            "title": "New Offer",
            "description": "desc",
            "details": [
                {"title": "B1", "revisions": 1, "delivery_time_in_days": 1, "price": 10, "features": ["A"], "offer_type": "basic"},
                {"title": "B2", "revisions": 2, "delivery_time_in_days": 2, "price": 20, "features": ["B"], "offer_type": "standard"},
                {"title": "B3", "revisions": 3, "delivery_time_in_days": 3, "price": 30, "features": ["C"], "offer_type": "premium"},
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "New Offer")

    def test_create_offer_customer_forbidden(self):
        self.switch_to_customer()
        url = reverse("offers")
        data = {
            "title": "ShouldNotWork",
            "description": "desc",
            "details": [
                {"title": "B1", "revisions": 1, "delivery_time_in_days": 1, "price": 10, "features": ["A"], "offer_type": "basic"},
                {"title": "B2", "revisions": 2, "delivery_time_in_days": 2, "price": 20, "features": ["B"], "offer_type": "standard"},
                {"title": "B3", "revisions": 3, "delivery_time_in_days": 3, "price": 30, "features": ["C"], "offer_type": "premium"},
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertIn(response.status_code, [403, 401])

    def test_create_offer_too_few_details(self):
        self.switch_to_business()
        url = reverse("offers")
        data = {
            "title": "NotEnoughDetails",
            "description": "desc",
            "details": [
                {"title": "B1", "revisions": 1, "delivery_time_in_days": 1, "price": 10, "features": ["A"], "offer_type": "basic"},
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_retrieve_offer(self):
        self.switch_to_anon()
        url = reverse("offer-detail", args=[self.offer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)

    def test_patch_offer_as_owner(self):
        self.switch_to_business()
        url = reverse("offer-detail", args=[self.offer.id])
        data = {"title": "Changed"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Changed")

    def test_patch_offer_as_not_owner_forbidden(self):
        self.switch_to_customer()
        url = reverse("offer-detail", args=[self.offer.id])
        data = {"title": "NoPerm"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 403)

    def test_delete_offer_as_owner(self):
        self.switch_to_business()
        url = reverse("offer-detail", args=[self.offer.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_delete_offer_as_not_owner_forbidden(self):
        self.switch_to_customer()
        url = reverse("offer-detail", args=[self.offer.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_retrieve_offerdetail_anonymous(self):
        self.switch_to_anon()
        url = reverse("offerdetail-retrieve", args=[self.detail1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)
