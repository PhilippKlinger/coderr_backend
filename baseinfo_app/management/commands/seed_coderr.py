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
from django.core.files.base import ContentFile

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import io
import textwrap

from accounts_app.models import Profile
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from reviews_app.models import Review

# Faker optional
try:
    from faker import Faker  
except Exception:
    Faker = None  # noqa: N816

UserModel = get_user_model()

SEED_MEDIA_DIR = Path(settings.BASE_DIR) / "seed_media"

# ---- Typing helpers (für Pylance) -----------------------------------------
if TYPE_CHECKING:
    from faker import Faker as FakerT  

    UserT = AbstractBaseUser
else:
    FakerT = Any  # Laufzeit egal
    UserT = AbstractBaseUser  # Platzhalter

# ---- Kuratierte Datenquellen ----------------------------------------------
CATEGORIES = [
    # Tech / Produkt
    "Webentwicklung",
    "App-Entwicklung",
    "UI/UX Design",
    "Datenanalyse",
    "DevOps & Cloud",
    "QA & Testing",
    "SEO/Content",
    "Automatisierung",
    "E-Commerce & CMS",
    "IT & Netzwerk",
    "Cybersecurity",
    "KI/ML & Data Science",
    "Game Development",
    "Produktmanagement",
    # Kreativ
    "Grafikdesign & Branding",
    "Video & Animation",
    "Audio & Musik",
    "Fotografie & Bildbearbeitung",
    # Business/Marketing
    "Schreiben & Übersetzen",
    "Digital Marketing",
    "Sales & Leadgen",
    "Social Media Management",
    "PR & Kommunikation",
    # Operations
    "Admin & Assistenz",
    "Projektmanagement",
    "Finanzen & Buchhaltung",
    "HR & Recruiting",
    # Spezial
    "Architektur & CAD",
    "E-Learning & Bildung",
    "Rechtsdokumente (allgemein)",
    "Research & Analyse",
]


OFFER_TEMPLATES = {
    "Webentwicklung": [
        (
            "Landingpage in Next.js",
            "SEO-freundliche Landingpage inkl. Deployment & Tracking.",
        ),
        ("Django REST API", "Saubere REST API inkl. Auth, Swagger und Tests."),
        ("React App Refactor", "Refactoring, State-Management und Performance-Tuning."),
    ],
    "App-Entwicklung": [
        ("Flutter MVP", "Cross-platform MVP inkl. State-Management & CI."),
        ("React Native App Setup", "RN App mit Navigation, Auth und OTA Updates."),
        ("Store-Submission", "Vorbereitung & Einreichung in App/Play Store."),
    ],
    "UI/UX Design": [
        ("Design System (Figma)", "Komponentenbasiertes Design-System mit Doku."),
        ("UX-Audit", "Heuristisches Audit + klickbarer Prototyp."),
        ("User Flow & Wireframes", "Low-/Mid-Fi Wireframes inkl. Feedback-Runden."),
    ],
    "Datenanalyse": [
        ("ETL Pipeline", "Daten-Pipeline (Airflow/Pandas) + Reports."),
        ("Dashboard (Plotly/Dash)", "Interaktives Dashboard inkl. Auth & Export."),
        ("SQL-Reporting", "Wiederverwendbare SQL-Views & Kennzahlen."),
    ],
    "DevOps & Cloud": [
        ("Dockerize & CI", "Dockerisierung + CI/CD (GitHub Actions)."),
        ("Kubernetes Basics", "K8s-Deployment (Ingress, HPA) für bestehende App."),
        ("Monitoring Setup", "Prometheus/Grafana inkl. Alerts."),
    ],
    "QA & Testing": [
        ("Test Suite Aufbau", "Pytest/DRF Tests, Coverage und Reporting."),
        ("E2E Setup", "Playwright/Cypress E2E inkl. Seeds und Mocks."),
        ("Load/Stress Test", "k6/JMeter Lasttests mit Auswertung."),
    ],
    "SEO/Content": [
        ("Techn. SEO", "Core Web Vitals, Sitemap, Meta, strukturierte Daten."),
        ("Content Landing", "Keyword-Landingpage inkl. CMS-Hook."),
        ("SEO-Audit", "On-/Off-Page Analyse mit Maßnahmenplan."),
    ],
    "Automatisierung": [
        ("Scripting Bundle", "Automationen (Python) für Workflows."),
        ("RPA Light", "Browser/Desktop-Automationen für wiederkehrende Tasks."),
        ("Zapier/Make Flows", "No-Code Automations inkl. Fehlertoleranz."),
    ],
    "E-Commerce & CMS": [
        ("Shopify Setup", "Theme-Anpassung, Produkte, Zahlungen, Apps."),
        ("WooCommerce Fix", "Bugfixes, Payment/Versand-Integration."),
        ("Headless CMS", "Strapi/Contentful Setup + Frontend-Hook."),
    ],
    "IT & Netzwerk": [
        ("VPN/Firewall Setup", "Sichere Site-to-Site/Remote VPN-Konfiguration."),
        ("Server Härtung", "SSH-Hardening, Fail2ban, Updates, Backup."),
    ],
    "Cybersecurity": [
        ("Sec-Audit Light", "OWASP-Checkliste, Security-Headers, Secrets-Scan."),
        ("Pentest Basic", "Black/Gray-Box Kurztest + Report."),
    ],
    "KI/ML & Data Science": [
        ("Feature Engineering", "Vorbereitung & Feature-Pipelines für ML."),
        ("ML Modell Quickstart", "Baseline-Modelle + Evaluation."),
        ("LLM Integration", "Prompt-Flows, Vektorsuche, Guardrails."),
    ],
    "Game Development": [
        ("Unity Prototype", "Gameplay-Prototype inkl. Input & UI."),
        ("Asset Integration", "Level, Audio, FX in bestehendem Projekt."),
    ],
    "Produktmanagement": [
        ("Produkt Discovery", "Hypothesen, JTBD, Value Proposition Canvas."),
        ("Backlog Setup", "Epics/Stories, Priorisierung, Roadmap Light."),
    ],
    "Grafikdesign & Branding": [
        ("Logo & Mini-CI", "Logo, Farbwelt, Typo + Brand-Sheet."),
        ("Social Assets", "Templates für Posts/Stories/Banner."),
        ("Brand Guidelines", "Kompaktes Styleguide-Dokument."),
    ],
    "Video & Animation": [
        ("Short-Form Edits", "TikTok/Reels/Shorts inkl. Captions."),
        ("Explainer (2D)", "Kurz-Erklärvideo mit Voiceover."),
        ("Motion Graphics", "Intro/Lower Thirds/Transitions Paket."),
    ],
    "Audio & Musik": [
        ("Podcast Schnitt", "Rauschreduzierung, Mastering, Kapitelmarken."),
        ("Jingle/Intro", "Kurzer Marken-Jingle (royalty-free)."),
    ],
    "Fotografie & Bildbearbeitung": [
        ("Retusche Paket", "Skin, Licht, Farblook, Export-Presets."),
        ("Produktfreisteller", "E-Com-ready PNG/JPG, konsistenter Schatten."),
    ],
    "Schreiben & Übersetzen": [
        ("Blog-Artikel", "Strukturierter Fachartikel inkl. Quellen."),
        ("Übersetzung DE↔EN", "Kontextgetreu, leichte Lokalisierung."),
        ("UX-Microcopy", "Buttons, Leermeldungen, Onboarding-Texte."),
    ],
    "Digital Marketing": [
        ("SEA Kampagne", "Google Ads Setup + Tracking + A/B."),
        ("Newsletter Setup", "Template, Automationen, List Hygiene."),
        ("Analytics", "GA4/Matomo Events, Funnels, Dashboards."),
    ],
    "Sales & Leadgen": [
        ("B2B Leadlist", "ICP-basierte Liste inkl. Kontaktdaten."),
        ("Outbound Sequenzen", "E-Mail/LinkedIn Copy + Rhythmus."),
    ],
    "Social Media Management": [
        ("Content-Plan", "30-Tage Plan mit Themen/Visuals."),
        ("Community Mgmt", "Antworten, Moderation, KPI-Report."),
    ],
    "PR & Kommunikation": [
        ("Pressemitteilung", "Struktur, Zitate, Verteiler-Tipps."),
        ("Case Study", "Use-Case Story inkl. Grafiken."),
    ],
    "Admin & Assistenz": [
        ("Research Paket", "Vergleiche, Shortlists, Quellen-Doku."),
        ("Datenpflege", "CRM/Sheets Aufbereitung & Bereinigung."),
    ],
    "Projektmanagement": [
        ("Projekt Kickoff", "Scope, Risiken, Stakeholder-Map."),
        ("Agile Coaching", "Scrum/Kanban Setup + Routinen."),
    ],
    "Finanzen & Buchhaltung": [
        ("Rechnungsworkflow", "Vorlagen, Kategorien, Export."),
        ("Kostenanalyse", "Fix/Variabel, Quick-Savings, Visuals."),
    ],
    "HR & Recruiting": [
        ("Stellenprofil", "Anforderungsprofil, Scorecards."),
        ("Screening Paket", "Vorselektion, Interview-Leitfaden."),
    ],
    "Architektur & CAD": [
        ("Grundriss-Redraw", "Saubere CAD-Dateien aus Skizzen."),
        ("3D Visualisierung", "Schnelle Interior/Exterior-Renders."),
    ],
    "E-Learning & Bildung": [
        ("Kurskonzept", "Lernziele, Module, Quiz-Ideen."),
        ("LMS Setup", "Moodle/Teachable Grundsetup."),
    ],
    "Rechtsdokumente (allgemein)": [
        ("AGB/Privacy Vorlage", "Allg. Muster + Hinweise (keine Rechtsberatung)."),
        ("Vertrags-Template", "Basis-Vorlage zur internen Verwendung."),
    ],
    "Research & Analyse": [
        ("Wettbewerbsanalyse", "Mit Stärken/Schwächen & Positionierung."),
        ("Kunden-Interviews", "Leitfaden, Auswertung, Insights."),
    ],
}


FEATURE_POOL = [
    # Tech
    "Responsive",
    "Dark Mode",
    "i18n",
    "CI/CD",
    "Unit Tests",
    "E2E Tests",
    "Dokumentation",
    "Monitoring",
    "Caching",
    "Auth",
    "Rollen & Rechte",
    "SEO-Basics",
    "Analytics",
    "Export (CSV/Excel)",
    "Accessibility A11y",
    "Offline-Support",
    "HLS-Streaming",
    "Image-Optimierung",
    "Rate-Limiting",
    "Security-Headers",
    "Env-Switch (Dev/Prod)",
    "Docker Support",
    # Kreativ & Content
    "Brand-Sheet",
    "Source Files",
    "Social-Templates",
    "Storyboard",
    "Untertitel/Caption",
    "Color Grading",
    "Audio Mastering",
    # Business/Marketing
    "Keyword-Recherche",
    "Redaktionsplan",
    "A/B-Test-Plan",
    "Lead-Tracking",
    "UTM-Konzept",
    "Consent-Banner",
    # Ops
    "Runbook",
    "SLA Light",
    "Backup-Plan",
    "Kostenübersicht",
    # Service
    "Express-Option",
    "2 Feedback-Runden",
    "Onboarding-Call",
    "Abschluss-Report",
]


FIRST_NAMES = [
    "Lena",
    "Jonas",
    "Mara",
    "Paul",
    "Sofia",
    "Felix",
    "Mira",
    "Lukas",
    "Ella",
    "Noah",
    "Emma",
    "Ben",
    "Lea",
    "Max",
    "Milan",
    "Mia",
    "Emil",
    "Clara",
    "Theo",
    "Nina",
    "Julius",
    "Hanna",
    "Tom",
    "Leonie",
    "Sam",
    "Ida",
    "Oskar",
    "Maja",
    "Anton",
    "Eva",
]

LAST_NAMES = [
    "Klein",
    "Meyer",
    "Schmidt",
    "Wagner",
    "Becker",
    "Hoffmann",
    "Koch",
    "Bauer",
    "Sommer",
    "Kaiser",
    "Vogel",
    "Jung",
    "Keller",
    "Schneider",
    "Fischer",
    "Weber",
    "Schulz",
    "Krüger",
    "Wolf",
    "Zimmermann",
    "Braun",
    "Hartmann",
    "Schreiber",
    "Neumann",
    "Lorenz",
    "Franke",
    "Seidel",
    "Schuster",
    "Kuhn",
    "Ott",
]

REVIEW_SENTENCES = [
    "Schnelle Lieferung und saubere Code-Basis.",
    "Sehr gute Kommunikation, klare Struktur.",
    "Top Ergebnis, jederzeit wieder.",
    "Gute Qualität, kleine Nachbesserung nötig.",
    "Abstimmung hätte schneller sein können, Ergebnis passt.",
    "Über den Erwartungen, strukturiertes Vorgehen.",
    "Tolle Ideen und professionelle Umsetzung.",
    "Termine gehalten, proaktive Updates.",
    "Preis-Leistung absolut fair.",
    "Flexibel auf Änderungen reagiert.",
    "Analyse fundiert und nachvollziehbar.",
    "Design modern, Markenfit stimmt.",
    "Technische Umsetzung stabil und performant.",
    "Storytelling gelungen und kurzweilig.",
    "Sehr gründliche Recherche, gute Quellen.",
    "Einrichtung verständlich dokumentiert.",
    "Messbare Verbesserungen nach dem Go-Live.",
    "Konstruktives Feedback, angenehme Zusammenarbeit.",
    "Wir empfehlen definitiv weiter.",
    "Gerne wieder bei zukünftigen Projekten.",
]

PALETTES = [
    ((99, 102, 241), (192, 132, 252)),  # indigo -> violet
    ((16, 185, 129), (59, 130, 246)),  # teal -> blue
    ((251, 146, 60), (244, 63, 94)),  # orange -> rose
    ((14, 165, 233), (99, 102, 241)),  # sky -> indigo
    ((20, 184, 166), (34, 197, 94)),  # teal -> green
]

TIER_SCHEMES = [
    ("express", (1, 2, 3), 0.15),  # zeigt im Listing "Express 24 h"
    ("bis3", (2, 3, 5), 0.30),  # "bis zu 3 Tage"
    ("bis7", (3, 5, 7), 0.35),  # "bis zu 7 Tage"
    ("extended", (7, 14, 21), 0.20),  # längere Projekte
]

def _choose_tier_days() -> tuple[int, int, int]:
    _, days, weights = zip(*TIER_SCHEMES)
    return random.choices(list(days), weights=weights, k=1)[0]

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


def _choose_tier_days() -> tuple[int, int, int]:
    names, days, weights = zip(*TIER_SCHEMES)
    scheme = random.choices(list(days), weights=weights, k=1)[0]
    return scheme  # (basic_days, standard_days, premium_days)


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
        parser.add_argument(
            "--images",
            choices=["none", "placeholders", "bundle"],
            default="placeholders",
            help="Bilder füllen: none | placeholders (Pillow) | bundle (aus seed_media/*)",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        fresh = opts["fresh"]
        keep_su = opts["keep_superuser"]

        mode = opts["images"]
        self._image_mode = mode  # für helpers verfügbar

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

                # Bild (dein bestehender Code bleibt)
                mode = getattr(self, "_image_mode", "placeholders")
                if not offer.image:
                    if mode == "bundle":
                        candidates = _list_seed_images("offer_images")
                        if candidates:
                            src = random.choice(candidates)
                            _attach_file(
                                offer, "image", src, f"offer-{offer.id}-{src.name}"
                            )
                        else:
                            _attach_placeholder(offer, "image", title, "offer")
                    elif mode == "placeholders":
                        _attach_placeholder(offer, "image", title, "offer")

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

    def _ensure_user(self, username: str, email: str, password: str) -> "UserT":
        u, created = UserModel.objects.get_or_create(
            username=username, defaults={"email": email}
        )
        if created:
            u.set_password(password)
            u.save()
        return u

    def _ensure_profile(self, user: "UserT", kind: str, *, desc: str | None = None):
        defaults = {
            "type": kind,
            "location": "München" if kind == "business" else "Berlin",
            "tel": "0151 2345678",
            "description": (desc or "Demo Profil")[:150],
            "working_hours": "9-17",
        }
        profile, _created = Profile.objects.get_or_create(user=user, defaults=defaults)

        # --- Bild anfügen (falls leer) ---
        mode = getattr(self, "_image_mode", "placeholders")  # wird in handle gesetzt
        if not profile.file:
            if mode == "bundle":
                candidates = _list_seed_images("profile_pictures")
                if candidates:
                    src = random.choice(candidates)
                    _attach_file(profile, "file", src, f"profile-{user.id}-{src.name}")
                else:
                    _attach_placeholder(
                        profile,
                        "file",
                        f"{user.first_name or user.username}",
                        "profile",
                    )
            elif mode == "placeholders":
                initials = (user.first_name or user.username or "User").split()[0]
                _attach_placeholder(profile, "file", initials, "profile")
            # mode == "none": nichts tun

    def _create_business_users(self, n: int) -> list["UserT"]:
        users: list["UserT"] = []
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

    def _create_customer_users(self, n: int) -> list["UserT"]:
        users: list["UserT"] = []
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
                ("basic",    Decimal("1.0"), b_days, 1),
                ("standard", Decimal("1.6"), s_days, 2),
                ("premium",  Decimal("2.3"), p_days, 3),
            ]
            tiers = []
            for name, mult, days, rev in data:
                tiers.append(OfferDetail.objects.create(
                    offer=offer,
                    title=f"{name.title()} Paket",
                    price=(Decimal(base) * mult).quantize(Decimal("1.00")),
                    delivery_time_in_days=days,
                    revisions=rev,
                    features=random.sample(features, k=min(4, len(features))),
                    offer_type=name,
                ))
            return tiers


def _slug(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in s).strip("-")


def _list_seed_images(kind: str) -> list[Path]:
    d = SEED_MEDIA_DIR / kind
    if not d.exists():
        return []
    imgs: list[Path] = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
        imgs += list(d.glob(ext))
    return imgs


def _attach_file(instance, field_name: str, src: Path, dst_name: str):
    with src.open("rb") as fh:
        getattr(instance, field_name).save(dst_name, File(fh), save=True)


def _pick_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """
    Versucht eine echte TTF mit Umlaut-Support zu laden (DejaVu/Noto/FreeSans),
    fällt ansonsten auf den Pillow-Default zurück.
    """
    candidates = [
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _placeholder_image_bytes(text: str, size=(1200, 800)) -> bytes:
    from PIL import Image, ImageDraw, ImageOps, ImageFilter 

    w, h = size
    margin = 36
    radius = 32
    bar_h = 16

    # Palette deterministisch wählen
    idx = sum(ord(c) for c in text) % len(PALETTES)
    c0, c1 = PALETTES[idx]
    accent = c1

    # --- Schatten-Layer ---
    base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shadow = Image.new("L", (w, h), 0)
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [margin, margin + 6, w - margin, h - margin + 6], radius=radius, fill=160
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    base.paste((0, 0, 0, 90), mask=shadow)

    # --- Kartenmask + Verlauf ---
    mask = Image.new("L", (w, h), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle(
        [margin, margin, w - margin, h - margin], radius=radius, fill=255
    )

    try:
        grad = Image.linear_gradient("L").rotate(90).resize((w, h))
    except Exception:
        grad = Image.new("L", (1, h))
        for y in range(h):
            grad.putpixel((0, y), int(255 * y / max(1, h - 1)))
        grad = grad.resize((w, h))

    card = ImageOps.colorize(grad, black=c0, white=c1).convert("RGBA")
    card_bg = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    card_bg.paste(card, (0, 0), mask)
    base = Image.alpha_composite(base, card_bg)

    # zarte Card-Border
    border = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(border)
    bdraw.rounded_rectangle(
        [margin, margin, w - margin, h - margin],
        radius=radius,
        outline=(255, 255, 255, 60),
        width=2,
    )
    base = Image.alpha_composite(base, border)

    # Accent-Bar unten
    bar = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    b = ImageDraw.Draw(bar)
    b.rounded_rectangle(
        [margin + 24, h - margin - bar_h - 16, w - margin - 24, h - margin - 16],
        radius=12,
        fill=accent,
    )
    base = Image.alpha_composite(base, bar)

    # --- Titel mittig (größer) ---
    draw = ImageDraw.Draw(base)
    # mehr „Punch“: größere Startschrift, weniger Wrap
    target_width_chars = 20
    lines = textwrap.wrap(text, width=target_width_chars)[:2]
    title = "\n".join(lines)

    # Safe-Area: innerhalb der Karte, oberhalb der Bar
    safe_left = margin + 24
    safe_right = w - margin - 24
    safe_top = margin + 48
    safe_bottom = h - margin - (bar_h + 32)
    safe_w = max(1, safe_right - safe_left)
    safe_h = max(1, safe_bottom - safe_top)

    # dynamisch passende Schriftgröße
    font_size = 54  # größer als vorher
    while font_size >= 28:
        font = _pick_font(font_size)
        try:
            bbox = draw.multiline_textbbox(
                (0, 0), title, font=font, spacing=8, align="center"
            )
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            # Fallback: per Zeile messen
            tw = 0
            th = 0
            for i, line in enumerate(lines):
                bb = draw.textbbox((0, 0), line, font=font)
                tw = max(tw, bb[2] - bb[0])
                th += (bb[3] - bb[1]) + (8 if i else 0)
        if tw <= safe_w - 32 and th <= safe_h - 24:
            break
        font_size -= 2

    # zentrieren
    x = safe_left + (safe_w - tw) // 2
    y = safe_top + (safe_h - th) // 2

    # Lesbarkeitsplatte
    draw.rounded_rectangle(
        [x - 24, y - 16, x + tw + 24, y + th + 16], radius=16, fill=(255, 255, 255, 110)
    )
    draw.multiline_text(
        (x, y), title, font=font, fill=(32, 37, 43), spacing=8, align="center"
    )

    # Export
    out = Image.new("RGB", (w, h), (255, 255, 255))
    out.paste(base, (0, 0), base)
    buf = io.BytesIO()
    out.save(buf, format="JPEG", quality=90, subsampling=1)
    return buf.getvalue()


def _attach_placeholder(instance, field_name: str, text: str, prefix: str):
    data = _placeholder_image_bytes(text)
    name = f"{prefix}-{_slug(text)}.jpg"
    getattr(instance, field_name).save(name, ContentFile(data), save=True)
