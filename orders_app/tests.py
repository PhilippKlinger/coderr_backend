from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from accounts_app.models import Profile


class OrdersTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # User & Profile Setup
        self.customer = User.objects.create_user(
            username="customer", password="pass", email="cust@test.com"
        )
        Profile.objects.create(user=self.customer, type="customer")
        self.business = User.objects.create_user(
            username="business", password="pass", email="biz@test.com"
        )
        Profile.objects.create(user=self.business, type="business")

        # Offer & OfferDetail for Order
        self.offer = Offer.objects.create(
            user=self.business, title="Logo", description="desc"
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Logo Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["A", "B"],
            offer_type="basic",
        )

        # Auth Token Setup
        self.client.force_authenticate(self.customer)

    # Helper Token change
    def switch_to_business(self):
        self.client.force_authenticate(self.business)

    def switch_to_customer(self):
        self.client.force_authenticate(self.customer)

    def test_order_list_as_customer_and_business(self):
        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["A", "B"],
            offer_type="basic",
        )
        self.switch_to_customer()
        response = self.client.get(reverse("order-list-create"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.switch_to_business()
        response = self.client.get(reverse("order-list-create"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_order_as_customer(self):
        self.switch_to_customer()
        url = reverse("order-list-create")
        data = {"offer_detail_id": self.offer_detail.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], self.offer_detail.title)
        self.assertEqual(response.data["customer_user"], self.customer.id)
        self.assertEqual(response.data["business_user"], self.business.id)

    def test_create_order_as_business_forbidden(self):
        self.switch_to_business()
        url = reverse("order-list-create")
        data = {"offer_detail_id": self.offer_detail.id}
        response = self.client.post(url, data)
        self.assertIn(
            response.status_code, [403, 401]
        )  # Forbidden no Customer!

    def test_create_order_missing_offer_detail(self):
        self.switch_to_customer()
        url = reverse("order-list-create")
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_create_order_invalid_offer_detail(self):
        self.switch_to_customer()
        url = reverse("order-list-create")
        data = {"offer_detail_id": 99999}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)

    def test_retrieve_order_as_involved_users(self):
        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["A", "B"],
            offer_type="basic",
        )
        url = reverse("order-detail", args=[order.id])
        self.switch_to_customer()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.switch_to_business()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_patch_order_as_business(self):
        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["A", "B"],
            offer_type="basic",
        )
        url = reverse("order-detail", args=[order.id])
        self.switch_to_business()
        data = {"status": "completed"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "completed")

    def test_patch_order_as_customer_forbidden(self):
        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["A", "B"],
            offer_type="basic",
        )
        url = reverse("order-detail", args=[order.id])
        self.switch_to_customer()
        data = {"status": "completed"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 403)

    def test_delete_order_as_admin(self):
        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["A", "B"],
            offer_type="basic",
        )
        url = reverse("order-detail", args=[order.id])
        admin = User.objects.create_superuser(username="admin", password="admin")
        self.client.force_authenticate(admin)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_delete_order_as_normal_user_forbidden(self):
        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["A", "B"],
            offer_type="basic",
        )
        url = reverse("order-detail", args=[order.id])
        self.switch_to_customer()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_order_count(self):
        Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["A", "B"],
            offer_type="basic",
        )
        url = reverse("order-count", args=[self.business.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("order_count", response.data)

    def test_completed_order_count(self):
        Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["A", "B"],
            offer_type="basic",
            status="completed",
        )
        url = reverse("completed-order-count", args=[self.business.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("completed_order_count", response.data)
