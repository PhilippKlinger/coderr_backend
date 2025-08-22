from __future__ import annotations
import random
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, Any
from pathlib import Path
from datetime import timedelta

from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db import transaction
from django.conf import settings
from django.core.files import File

from accounts_app.models import Profile
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from reviews_app.models import Review
from .data import (
    CATEGORIES,
    OFFER_TEMPLATES,
    CATEGORY_IMAGE_MAP,
    FEATURE_POOL,
    FIRST_NAMES,
    LAST_NAMES,
    REVIEW_SENTENCES,
    TIER_SCHEMES,
)

try:
    from faker import Faker
except Exception:
    Faker = None

if TYPE_CHECKING:
    from faker import Faker as FakerT
else:
    FakerT = Any


UserModel = get_user_model()
SEED_MEDIA_DIR = Path(settings.BASE_DIR) / "seed_media"

if TYPE_CHECKING:
    from faker import Faker as FakerT

    UserT = AbstractBaseUser
else:
    FakerT = Any
    UserT = AbstractBaseUser


# ---- Utils ----------------------------------------------------------------
def _rand_username() -> str:
    base = f"{random.choice(FIRST_NAMES)}.{random.choice(LAST_NAMES)}".lower()
    return f"{base}{random.randint(1,999)}"


def _maybe_faker() -> Optional["FakerT"]:
    try:
        from faker import Faker as _Faker

        return _Faker()
    except Exception:
        return None


def _list_images(dirpath: Path) -> list[Path]:
    imgs: list[Path] = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
        imgs += list(dirpath.glob(ext))
    return imgs


def _attach_file(instance, field_name: str, src: Path, dst_name: str):
    with src.open("rb") as fh:
        getattr(instance, field_name).save(dst_name, File(fh), save=True)


def _resolve_category_image(cat: str) -> Path | None:
    base = SEED_MEDIA_DIR / "offer_images"
    # 1) Mapping
    fname = CATEGORY_IMAGE_MAP.get(cat)
    if fname:
        p = base / fname
        if p.exists():
            return p
        stem = Path(fname).stem
        candidates = [q for q in _list_images(base) if q.stem.startswith(stem)]
        if candidates:
            return random.choice(candidates)
    # 2) Slug-Varianten
    s = cat.lower()
    for a, b in (
        ("ä", "ae"),
        ("ö", "oe"),
        ("ü", "ue"),
        ("ß", "ss"),
        (" & ", "-"),
        (" / ", "-"),
        ("/", "-"),
        (" ", "-"),
    ):
        s = s.replace(a, b)
    variants = [f"{s}.jpg", f"{s}.png", f"{s}.webp"]
    simple = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in s).strip("-_")
    if simple != s:
        variants += [f"{simple}.jpg", f"{simple}.png", f"{simple}.webp"]
    for name in variants:
        p = base / name
        if p.exists():
            return p
    # 3) Fallback: irgend eins
    candidates = _list_images(base)
    return random.choice(candidates) if candidates else None


def _random_avatar_path() -> Path | None:
    base = SEED_MEDIA_DIR / "profile_pictures"
    choices = _list_images(base)
    return random.choice(choices) if choices else None


def _choose_tier_days() -> tuple[int, int, int]:
    names, days, weights = zip(*TIER_SCHEMES)
    return random.choices(list(days), weights=weights, k=1)[0]


def _random_past_datetime(max_days: int = 45) -> "timezone.datetime":
    """
    Datum in den letzten max_days, bias zu 'kürzlich' (triangular).
    """
    now = timezone.now()
    d = int(random.triangular(0, max_days, 5))  # viele jüngere
    s = random.randint(0, 23 * 3600 + 59 * 60 + 59)  # zufällige Tageszeit
    return now - timedelta(days=d, seconds=s)


# ---- Command ---------------------------------------------------------------
class Command(BaseCommand):
    help = "Seed Coderr mit kuratierten, realistischeren Demo-Daten (optional mit Faker auffüllen)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fresh",
            action="store_true",
            help="Alle relevanten Tabellen leeren (User/Profiles/Offers/Orders/Reviews).",
        )
        parser.add_argument(
            "--keep-superuser",
            action="store_true",
            help="Existierende Superuser NICHT löschen (empfohlen).",
        )
        parser.add_argument(
            "--lite",
            action="store_true",
            help="Kleine Demomenge (ca. 10 Business / 12 Customer).",
        )
        parser.add_argument(
            "--full",
            action="store_true",
            help="Größere Demomenge (ca. 35 Business / 35 Customer).",
        )
        parser.add_argument(
            "--fake-extra",
            type=int,
            default=0,
            help="Zusätzliche zufällige Offers mit Faker hinzufügen (0 = aus).",
        )
        parser.add_argument(
            "--biz",
            type=int,
            default=None,
            help="Anzahl Business-Accounts (überschreibt Presets).",
        )
        parser.add_argument(
            "--cust",
            type=int,
            default=None,
            help="Anzahl Customer-Accounts (überschreibt Presets).",
        )
        parser.add_argument("--orders", type=int, default=40, help="Anzahl Orders.")
        parser.add_argument("--reviews", type=int, default=80, help="Anzahl Reviews.")

    @transaction.atomic
    def handle(self, *args, **opts):
        fresh = opts["fresh"]
        keep_su = opts["keep_superuser"]

        # Mengen
        if opts["full"]:
            num_biz, num_cust = 35, 35
        elif opts["lite"]:
            num_biz, num_cust = 10, 12
        else:
            num_biz, num_cust = 20, 20

        if opts["biz"] is not None:
            num_biz = max(0, opts["biz"])
        if opts["cust"] is not None:
            num_cust = max(0, opts["cust"])
        fake_extra = max(0, int(opts["fake_extra"]))
        num_orders = max(0, int(opts["orders"]))
        num_reviews = max(0, int(opts["reviews"]))

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding Coderr…"))
        if fresh:
            self._flush(keep_superuser=keep_su)

        # Zwei Demo-Logins
        demo_business = self._ensure_user(
            "demo_business", "demo_business@example.com", "demo"
        )
        self._ensure_profile(
            demo_business, "business", desc="Demo Business – kann Angebote erstellen."
        )
        demo_customer = self._ensure_user(
            "demo_customer", "demo_customer@example.com", "demo"
        )
        self._ensure_profile(
            demo_customer,
            "customer",
            desc="Demo Customer – kann Bestellungen & Bewertungen erstellen.",
        )

        # Benutzer
        self.stdout.write("Erzeuge Benutzer…")
        business_users = self._create_business_users(num_biz)
        customer_users = self._create_customer_users(num_cust)

        # Offers + Tiers
        self.stdout.write("Erzeuge Offers…")
        all_details: list[OfferDetail] = []
        seen_for_user: dict[int, set[str]] = {}

        for user in business_users + [demo_business]:
            cat = random.choice(CATEGORIES)
            templates = OFFER_TEMPLATES.get(cat, [])
            qty = random.randint(2, 3)
            chosen = (
                random.sample(templates, k=min(qty, len(templates)))
                if templates
                else [("Individuelles Angebot", "Maßgeschneiderte Leistung.")] * qty
            )

            uid = user.id
            seen_for_user.setdefault(uid, set())

            for title, desc in chosen:
                if title in seen_for_user[uid]:
                    continue  # doppelte Titel pro User vermeiden
                seen_for_user[uid].add(title)

                offer = Offer.objects.create(user=user, title=title, description=desc)

                # Bild (nur "bundle" – echte Dateien; keine Placeholder mehr)
                imgpath = _resolve_category_image(cat)
                if imgpath:
                    _attach_file(
                        offer, "image", imgpath, f"offer-{offer.id}-{imgpath.name}"
                    )

                # Lieferzeiten-Schema für diese Offer bestimmen
                days_triplet = _choose_tier_days()
                all_details += self._create_tiers(offer, days_triplet)

                # Erstellungszeitpunkt realistisch verteilen (letzte 45 Tage)
                ts = _random_past_datetime(45)
                # effizient aktualisieren ohne Signals/auto_now:
                Offer.objects.filter(pk=offer.pk).update(created_at=ts, updated_at=ts)

        # Faker-Extras
        fk = _maybe_faker()
        if fake_extra and fk:
            for _ in range(fake_extra):
                user = random.choice(business_users)
                uid = user.id
                seen_for_user.setdefault(uid, set())

                for _attempt in range(10):
                    t = fk.catch_phrase()
                    if t not in seen_for_user[uid]:
                        seen_for_user[uid].add(t)
                        break
                else:
                    t = f"Individuelle Leistung #{len(seen_for_user[uid]) + 1}"
                    seen_for_user[uid].add(t)

                offer = Offer.objects.create(
                    user=user,
                    title=t,
                    description=fk.paragraph(nb_sentences=2),
                )
                days_triplet = _choose_tier_days()
                all_details += self._create_tiers(offer, days_triplet)

        # Orders
        self.stdout.write("Erzeuge Orders…")
        for _ in range(num_orders):
            detail = random.choice(all_details)
            customer = random.choice(customer_users + [demo_customer])
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

        # Reviews (pro Customer->Business max 1)
        self.stdout.write("Erzeuge Reviews…")
        seen: set[tuple[int, int]] = set()
        for _ in range(num_reviews):
            reviewer = random.choice(customer_users + [demo_customer])
            business = random.choice(business_users + [demo_business])
            key = (reviewer.id, business.id)
            if reviewer.id == business.id or key in seen:
                continue
            seen.add(key)
            Review.objects.create(
                business_user=business,
                reviewer=reviewer,
                rating=random.choices([5, 4, 3, 2, 1], weights=[35, 30, 20, 10, 5])[0],
                description=random.choice(REVIEW_SENTENCES),
            )

        self.stdout.write(self.style.SUCCESS("✔ Seed fertig."))

    # ---- Helpers -----------------------------------------------------------
    def _flush(self, keep_superuser: bool):
        self.stdout.write(
            self.style.WARNING("Flush: lösche Users/Profiles/Offers/Orders/Reviews …")
        )
        su_ids: set[int] = (
            set(
                UserModel.objects.filter(is_superuser=True).values_list("id", flat=True)
            )
            if keep_superuser
            else set()
        )

        Order.objects.all().delete()
        Review.objects.all().delete()
        OfferDetail.objects.all().delete()
        Offer.objects.all().delete()
        Profile.objects.all().delete()

        if keep_superuser:
            UserModel.objects.exclude(id__in=su_ids).delete()
        else:
            UserModel.objects.all().delete()

    def _ensure_user(self, username: str, email: str, password: str):
        u, created = UserModel.objects.get_or_create(
            username=username, defaults={"email": email}
        )
        if created:
            u.set_password(password)
            u.save()
        return u

    def _ensure_profile(self, user, kind: str, *, desc: str | None = None):
        defaults = {
            "type": kind,
            "location": "München" if kind == "business" else "Berlin",
            "tel": "0151 2345678",
            "description": (desc or "Demo Profil")[:150],
            "working_hours": "9-17",
        }
        profile, _created = Profile.objects.get_or_create(user=user, defaults=defaults)

        # Avatar aus seed_media anhängen (zufällig), aber nur wenn noch keins gesetzt ist
        if not profile.file:
            apath = _random_avatar_path()
            if apath:
                _attach_file(profile, "file", apath, f"profile-{user.id}-{apath.name}")

    def _create_business_users(self, n: int) -> list:
        users: list = []
        for _ in range(n):
            un = _rand_username()
            u = UserModel.objects.create_user(
                username=un,
                email=f"{un}@example.com",
                password="demo1234",
                first_name=random.choice(FIRST_NAMES),
                last_name=random.choice(LAST_NAMES),
            )
            self._ensure_profile(
                u, "business", desc="Agentur/Einzelunternehmen – nimmt Aufträge an."
            )
            users.append(u)
        return users

    def _create_customer_users(self, n: int) -> list:
        users: list = []
        for _ in range(n):
            un = _rand_username()
            u = UserModel.objects.create_user(
                username=un,
                email=f"{un}@example.com",
                password="demo1234",
                first_name=random.choice(FIRST_NAMES),
                last_name=random.choice(LAST_NAMES),
            )
            self._ensure_profile(
                u, "customer", desc="Kunde – erstellt Bestellungen und Bewertungen."
            )
            users.append(u)
        return users

    def _create_tiers(self, offer, days_triplet=None):
        if days_triplet is None:
            days_triplet = _choose_tier_days()
        b_days, s_days, p_days = days_triplet

        base = random.randint(200, 1200)
        features = random.sample(FEATURE_POOL, k=4)
        data = [
            ("basic", Decimal("1.0"), b_days, 1),
            ("standard", Decimal("1.6"), s_days, 2),
            ("premium", Decimal("2.3"), p_days, 3),
        ]
        tiers = []
        for name, mult, days, rev in data:
            tiers.append(
                OfferDetail.objects.create(
                    offer=offer,
                    title=f"{name.title()} Paket",
                    price=(Decimal(base) * mult).quantize(Decimal("1.00")),
                    delivery_time_in_days=days,
                    revisions=rev,
                    features=random.sample(features, k=min(4, len(features))),
                    offer_type=name,
                )
            )
        return tiers


def _slug(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in s).strip("-")
