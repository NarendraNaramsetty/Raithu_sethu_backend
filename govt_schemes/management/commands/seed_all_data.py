"""
Management command to seed all realistic agricultural datasets:
- Government Schemes & Subsidies (2025-2026 accurate)
- Crop Disease Knowledge Base (Paddy, Cotton, Chilli, Tomato, Wheat, Maize, etc.)
- Mandi Commodity Prices with MSP
- Farmer Community Discussions & Equipment Rental Listings
- Weather Reports & Agricultural Advisories
"""

from django.core.management.base import BaseCommand
from govt_schemes.models import GovtScheme
from govt_schemes.fixtures_data import GOVT_SCHEMES_DATA
from disease_detection.models import CropDiseaseKnowledge
from disease_detection.services import EXPERT_AGRONOMY_DATABASE
from mandi_prices.models import MandiCommodityPrice
from community.models import ForumPost, PostReply
from weather_advisory.models import WeatherReport, DailyForecast


class Command(BaseCommand):
    help = 'Seeds realistic, up-to-date Indian agricultural data across all modules'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding RaithuSetu Database with realistic 2026 agricultural data..."))

        # 1. Seed Government Schemes
        GovtScheme.objects.all().delete()
        schemes = [
            GovtScheme(
                title=item["title"],
                subtitle=item["subtitle"],
                category=item["category"],
                benefit_amount=item["benefit_amount"],
                eligibility=item["eligibility"],
                required_documents=item["required_documents"],
                application_status=item["application_status"],
                official_portal_url=item["official_portal_url"],
            )
            for item in GOVT_SCHEMES_DATA
        ]
        GovtScheme.objects.bulk_create(schemes)
        self.stdout.write(self.style.SUCCESS(f"[OK] Seeded {len(schemes)} Government Schemes & Subsidies"))

        # 2. Seed Disease Knowledge Base
        CropDiseaseKnowledge.objects.all().delete()
        diseases = [
            CropDiseaseKnowledge(
                crop_name=item["crop"],
                disease_name=item["disease"],
                scientific_name=item["scientific_name"],
                severity=item["severity"],
                confidence_default=item["confidence"],
                symptoms=item.get("symptoms", "Visible foliar lesions, discoloration, and leaf curling symptoms."),
                organic_solution=item["organicSolution"],
                chemical_solution=item["chemicalSolution"],
                prevention_advice=item["prevention"],
            )
            for item in EXPERT_AGRONOMY_DATABASE.values()
        ]
        CropDiseaseKnowledge.objects.bulk_create(diseases)
        self.stdout.write(self.style.SUCCESS(f"[OK] Seeded {len(diseases)} Crop Disease Profiles"))

        # 3. Seed Mandi Commodity Prices
        MandiCommodityPrice.objects.all().delete()
        mandi_records = [
            MandiCommodityPrice(
                crop_name="Paddy / Rice (Common)",
                crop_name_native="వరి / धान",
                mandi_name="Warangal Mandi",
                district="Warangal",
                state="Telangana",
                modal_price=2340,
                previous_price=2310,
                price_change_percent="+1.3%",
                msp_rate=2300,
                daily_arrival="850 Quintals"
            ),
            MandiCommodityPrice(
                crop_name="Cotton (Medium Staple)",
                crop_name_native="పత్తి / कपास",
                mandi_name="Adilabad APMC",
                district="Adilabad",
                state="Telangana",
                modal_price=7480,
                previous_price=7250,
                price_change_percent="+3.1%",
                msp_rate=7121,
                daily_arrival="420 Quintals"
            ),
            MandiCommodityPrice(
                crop_name="Chilli Red (Teja / Super 10)",
                crop_name_native="మిరప / मिर्च",
                mandi_name="Guntur Mirchi Yard",
                district="Guntur",
                state="Andhra Pradesh",
                modal_price=14600,
                previous_price=14200,
                price_change_percent="+2.8%",
                msp_rate=13800,
                daily_arrival="620 Quintals"
            ),
            MandiCommodityPrice(
                crop_name="Tomato (Hybrid Local)",
                crop_name_native="టమాట / टमाटर",
                mandi_name="Madanapalle APMC",
                district="Annamayya",
                state="Andhra Pradesh",
                modal_price=1850,
                previous_price=1950,
                price_change_percent="-5.1%",
                msp_rate=1600,
                daily_arrival="1,800 Crates"
            ),
            MandiCommodityPrice(
                crop_name="Onion (Red Nasik)",
                crop_name_native="ఉల్లిపాయ / प्याज",
                mandi_name="Kurnool Market Yard",
                district="Kurnool",
                state="Andhra Pradesh",
                modal_price=2180,
                previous_price=2080,
                price_change_percent="+4.8%",
                msp_rate=1900,
                daily_arrival="720 Quintals"
            ),
            MandiCommodityPrice(
                crop_name="Wheat (Lokwan FAQ)",
                crop_name_native="గోధుమ / गेहूं",
                mandi_name="Khanna Mandi",
                district="Ludhiana",
                state="Punjab",
                modal_price=2420,
                previous_price=2380,
                price_change_percent="+1.7%",
                msp_rate=2275,
                daily_arrival="1,200 Quintals"
            ),
            MandiCommodityPrice(
                crop_name="Maize (Yellow Hybrid)",
                crop_name_native="మొక్కజొన్న / मक्का",
                mandi_name="Nizamabad Market",
                district="Nizamabad",
                state="Telangana",
                modal_price=2210,
                previous_price=2150,
                price_change_percent="+2.8%",
                msp_rate=2090,
                daily_arrival="510 Quintals"
            ),
            MandiCommodityPrice(
                crop_name="Groundnut (Pod Bold)",
                crop_name_native="వేరుశనగ / मूंगफली",
                mandi_name="Anantapur Yard",
                district="Anantapur",
                state="Andhra Pradesh",
                modal_price=7020,
                previous_price=6850,
                price_change_percent="+2.5%",
                msp_rate=6783,
                daily_arrival="340 Quintals"
            ),
            MandiCommodityPrice(
                crop_name="Turmeric (Finger Nizamabad)",
                crop_name_native="పసుపు / हल्दी",
                mandi_name="Duggirala APMC",
                district="Guntur",
                state="Andhra Pradesh",
                modal_price=13800,
                previous_price=13200,
                price_change_percent="+4.5%",
                msp_rate=8500,
                daily_arrival="260 Quintals"
            ),
            MandiCommodityPrice(
                crop_name="Soyabean (Yellow)",
                crop_name_native="సోయాబీన్ / सोयाबीन",
                mandi_name="Latur APMC",
                district="Latur",
                state="Maharashtra",
                modal_price=4980,
                previous_price=4890,
                price_change_percent="+1.8%",
                msp_rate=4892,
                daily_arrival="980 Quintals"
            ),
            MandiCommodityPrice(
                crop_name="Potato (Jyoti / Kufri)",
                crop_name_native="బంగాళాదుంప / आलू",
                mandi_name="Agra Mandi",
                district="Agra",
                state="Uttar Pradesh",
                modal_price=1680,
                previous_price=1620,
                price_change_percent="+3.7%",
                msp_rate=1400,
                daily_arrival="1,450 Quintals"
            ),
        ]
        MandiCommodityPrice.objects.bulk_create(mandi_records)
        self.stdout.write(self.style.SUCCESS(f"[OK] Seeded {len(mandi_records)} Mandi APMC Commodity Prices"))

        # 4. Seed Community Forum & Equipment Rentals
        ForumPost.objects.all().delete()
        PostReply.objects.all().delete()

        post1 = ForumPost.objects.create(
            author="Ramesh Patel",
            location="Guntur, Andhra Pradesh",
            crop="Chilli & Cotton",
            content="Heavy rainfall in Guntur region over the weekend. What is the recommended bio-fungicide spray to prevent root rot and anthracnose in 45-day chilli crop?",
            likes=14,
            replies_count=2,
            is_rental=False,
            time_ago="2 hours ago"
        )
        PostReply.objects.create(
            post=post1,
            author="Dr. Venkat Rao (Agronomist)",
            content="Brother, do a soil drench with Trichoderma viride @ 5g/L mixed with 1kg jaggery fermented water. Avoid chemical nitrogen for next 5 days."
        )
        PostReply.objects.create(
            post=post1,
            author="Srinivas Reddy",
            content="I used SAAF (Mancozeb + Carbendazim) @ 2g/L and got very fast leaf recovery."
        )

        post2 = ForumPost.objects.create(
            author="Anji Reddy Farm Equipments",
            location="Warangal, Telangana",
            crop="Paddy & Maize",
            content="John Deere 5050 D (50 HP Tractor) with Rotavator and MB Plough available for rent. Hourly rate: Rs.850/hr including diesel and operator. Call/WhatsApp: 9848012345.",
            likes=28,
            replies_count=1,
            is_rental=True,
            time_ago="4 hours ago"
        )
        PostReply.objects.create(
            post=post2,
            author="Koteswara Rao",
            content="Is it available for 4 acres field preparation tomorrow near Narsampet?"
        )

        post3 = ForumPost.objects.create(
            author="Kisan Drone Sprayers Co-op",
            location="Khammam, Telangana",
            crop="Cotton, Chilli, Paddy",
            content="DGCA-certified Agri Drone Spraying service available! Covers 1 acre in 7 minutes with uniform micron droplet coverage. Charges: Rs.450 per acre. Saves 30% chemical and 90% water.",
            likes=42,
            replies_count=3,
            is_rental=True,
            time_ago="1 day ago"
        )
        PostReply.objects.create(
            post=post3,
            author="Mallesh Goud",
            content="Used their drone service last week for cotton pink bollworm spray. Very neat work and zero crop trampling."
        )

        post4 = ForumPost.objects.create(
            author="Venkateswarlu Farmer",
            location="Kurnool, Andhra Pradesh",
            crop="Groundnut & Onion",
            content="PM-KISAN 19th installment e-KYC status update: Make sure your bank account is linked to NPCI Aadhaar bridge before the end of the month to receive the Rs.2,000 credit smoothly.",
            likes=35,
            replies_count=1,
            is_rental=False,
            time_ago="1 day ago"
        )

        self.stdout.write(self.style.SUCCESS("[OK] Seeded Farmer Community Forum & Rental Posts with Replies"))

        # 5. Seed Weather & Advisories
        WeatherReport.objects.all().delete()
        DailyForecast.objects.all().delete()

        w_report = WeatherReport.objects.create(
            location_name="Guntur, Andhra Pradesh",
            temperature="31°C",
            feels_like="35°C",
            condition="Partly Cloudy",
            humidity="70%",
            wind_speed="12 km/h",
            rain_probability="20%",
            uv_index="High (7/10)",
            advisory_headline="Favorable Weather for Kharif Foliar Nutrient Sprays",
            advisory_detail="Dry conditions expected for the next 48 hours. Ideal window for micronutrient sprays (Zinc + Boron) and pest scouting in cotton & chilli."
        )

        forecasts = [
            DailyForecast(weather_report=w_report, day="Mon", temp="24°C - 33°C", condition="Partly Cloudy", rain="15%", icon="CloudSun"),
            DailyForecast(weather_report=w_report, day="Tue", temp="25°C - 34°C", condition="Sunny & Clear", rain="10%", icon="Sun"),
            DailyForecast(weather_report=w_report, day="Wed", temp="24°C - 32°C", condition="Scattered Clouds", rain="25%", icon="CloudSun"),
            DailyForecast(weather_report=w_report, day="Thu", temp="23°C - 31°C", condition="Light Showers", rain="45%", icon="CloudRain"),
            DailyForecast(weather_report=w_report, day="Fri", temp="23°C - 30°C", condition="Thunderstorms", rain="60%", icon="CloudLightning"),
            DailyForecast(weather_report=w_report, day="Sat", temp="24°C - 32°C", condition="Passing Showers", rain="35%", icon="CloudDrizzle"),
            DailyForecast(weather_report=w_report, day="Sun", temp="25°C - 33°C", condition="Partly Cloudy", rain="20%", icon="CloudSun"),
        ]
        DailyForecast.objects.bulk_create(forecasts)
        self.stdout.write(self.style.SUCCESS("[OK] Seeded Weather Agro-Advisory and 7-Day Forecasts"))

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] All Realistic 2026 Agricultural Datasets Seeded Successfully!"))
