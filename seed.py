import os
import django
import random
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  # ggf. anpassen
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile
from offers.models import Offer, OfferDetail
from orders.models import Order
from reviews.models import Review

fake = Faker()

NUM_USERS = 10
NUM_OFFERS_PER_BUSINESS = 3
NUM_ORDERS = 15
NUM_REVIEWS = 10


def run():
    print("🔁 Resetting DB...")
    User.objects.all().delete()
    Profile.objects.all().delete()
    Offer.objects.all().delete()
    OfferDetail.objects.all().delete()
    Order.objects.all().delete()
    Review.objects.all().delete()

    print("👥 Creating users...")
    users = []
    for _ in range(NUM_USERS):
        is_business = random.choice([True, False])
        user = User.objects.create_user(
            username=fake.user_name(),
            email=fake.email(),
            password="1234",
            first_name=fake.first_name(),
            last_name=fake.last_name()
        )
        Profile.objects.create(user=user, type="business" if is_business else "customer")
        users.append(user)

    business_users = [u for u in users if u.profile.type == "business"]
    customer_users = [u for u in users if u.profile.type == "customer"]

    print("🛍 Creating offers...")
    for user in business_users:
        for _ in range(NUM_OFFERS_PER_BUSINESS):
            offer = Offer.objects.create(
                user=user,
                title=fake.catch_phrase(),
                description=fake.text(max_nb_chars=100),
            )
            for offer_type in ["basic", "standard", "premium"]:
                OfferDetail.objects.create(
                    offer=offer,
                    title=f"{offer_type.title()} Paket",
                    price=random.randint(100, 1000),
                    delivery_time_in_days=random.randint(1, 30),
                    revisions=random.randint(1, 5),
                    features=[fake.word(), fake.word()],
                    offer_type=offer_type,
                )

    print("📦 Creating orders...")
    offer_details = OfferDetail.objects.all()
    for _ in range(NUM_ORDERS):
        detail = random.choice(offer_details)
        customer = random.choice(customer_users)
        Order.objects.create(
            customer_user=customer,
            business_user=detail.offer.user,
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=detail.features,
            offer_type=detail.offer_type,
        )

    print("📝 Creating reviews...")
    for _ in range(NUM_REVIEWS):
        reviewer = random.choice(customer_users)
        business = random.choice(business_users)
        if not Review.objects.filter(business_user=business, reviewer=reviewer).exists():
            Review.objects.create(
                business_user=business,
                reviewer=reviewer,
                rating=random.randint(1, 5),
                description=fake.sentence(),
            )

    print("✅ Done!")


if __name__ == "__main__":
    run()
