from django.core.management.base import BaseCommand
from authentication.models import FarmerProfile
from disease_detection.models import CropDiseaseKnowledge
from mandi_prices.models import MandiCommodityPrice
from govt_schemes.models import GovtScheme
from weather_advisory.models import WeatherReport, DailyForecast
from community.models import ForumPost, PostReply

class Command(BaseCommand):
    help = 'Seeds realistic Indian agricultural data for RaithuSetu backend'

    def handle(self, *args, **options):
        self.stdout.write("Seeding RaithuSetu initial data...")

        # 1. Farmer Profile
        FarmerProfile.objects.get_or_create(
            phone='9876543210',
            defaults={
                'name': 'Ramesh Patel',
                'name_native': 'రమేష్ పటేల్',
                'village': 'Pedakakani',
                'district': 'Guntur',
                'state': 'Andhra Pradesh',
                'total_land': '6.5 Acres',
                'soil_type': 'Black Clay Loam (నల్లరేగడి నేల)',
                'irrigation_source': 'Borewell + Canal',
                'active_crops': ['Paddy (BPT 5204)', 'Chilli (Teja Variety)']
            }
        )

        # 2. Disease Knowledge Base
        diseases = [
            {
                'crop_name': 'Tomato (టమాటా / टमाटर)',
                'crop_name_native': 'టమాట',
                'disease_name': 'Early Blight (Alternaria solani)',
                'scientific_name': 'Alternaria solani',
                'severity': 'Moderate',
                'confidence_default': 96.4,
                'symptoms': 'Concentric dark brown rings on older lower leaves resembling a target board.',
                'organic_solution': 'Spray Neem Oil (5ml/liter) or Trichoderma viride bio-fungicide once every 7 days.',
                'chemical_solution': 'Apply Mancozeb 75% WP @ 2.5g/liter or Azoxystrobin 23% SC @ 1ml/liter in the evening.',
                'prevention_advice': 'Avoid overhead irrigation, prune infected lower leaves, and maintain proper crop spacing.'
            },
            {
                'crop_name': 'Paddy / Rice (వరి / धान)',
                'crop_name_native': 'వరి',
                'disease_name': 'Leaf Blast (Pyricularia oryzae)',
                'scientific_name': 'Magnaporthe oryzae',
                'severity': 'High',
                'confidence_default': 94.8,
                'symptoms': 'Spindle-shaped elliptical lesions with greyish center and brownish margins on leaf blades.',
                'organic_solution': 'Spray Pseudomonas fluorescens @ 10g/liter or fermented butter milk spray.',
                'chemical_solution': 'Spray Tricyclazole 75% WP @ 0.6g/liter or Isoprothiolane 40% EC @ 1.5ml/liter.',
                'prevention_advice': 'Avoid excessive nitrogen fertilizer application during cloudy and high humidity weather.'
            },
            {
                'crop_name': 'Cotton (పత్తి / कपास)',
                'crop_name_native': 'పత్తి',
                'disease_name': 'Cotton Leaf Curl Disease (CLCuD)',
                'scientific_name': 'Begomovirus',
                'severity': 'High',
                'confidence_default': 95.2,
                'symptoms': 'Upward or downward leaf curling, thickened veins, and enation on undersides.',
                'organic_solution': 'Apply yellow sticky traps (10/acre) and spray 5% NSKE (Neem Seed Kernel Extract).',
                'chemical_solution': 'Control whitefly vector with Diafenthiuron 50% WP @ 1.2g/L or Flonicamid 50% WG @ 0.3g/L.',
                'prevention_advice': 'Eradicate weed hosts like Abutilon and Parthenium near field borders.'
            }
        ]
        for d in diseases:
            CropDiseaseKnowledge.objects.get_or_create(disease_name=d['disease_name'], defaults=d)

        # 3. Mandi Prices
        mandi_records = [
            { 'crop_name': 'Wheat (గోధుమ / गेहूं)', 'crop_name_native': 'గోధుమ', 'mandi_name': 'Guntur APMC, AP', 'district': 'Guntur', 'modal_price': 2380, 'previous_price': 2320, 'price_change_percent': '+2.5%', 'msp_rate': 2275, 'daily_arrival': '450 Quintals' },
            { 'crop_name': 'Paddy / Rice (వరి / धान)', 'crop_name_native': 'వరి', 'mandi_name': 'Warangal Mandi, TS', 'district': 'Warangal', 'modal_price': 2240, 'previous_price': 2260, 'price_change_percent': '-0.8%', 'msp_rate': 2203, 'daily_arrival': '820 Quintals' },
            { 'crop_name': 'Cotton (పత్తి / कपास)', 'crop_name_native': 'పత్తి', 'mandi_name': 'Adilabad APMC, TS', 'district': 'Adilabad', 'modal_price': 7450, 'previous_price': 7200, 'price_change_percent': '+3.4%', 'msp_rate': 7020, 'daily_arrival': '310 Quintals' },
            { 'crop_name': 'Chilli (మిరప / मिर्च)', 'crop_name_native': 'మిరప', 'mandi_name': 'Khammam Yard, TS', 'district': 'Khammam', 'modal_price': 14500, 'previous_price': 14200, 'price_change_percent': '+2.1%', 'msp_rate': 13800, 'daily_arrival': '190 Quintals' },
            { 'crop_name': 'Tomato (టమాట / टमाटर)', 'crop_name_native': 'టమాట', 'mandi_name': 'Madanapalle, AP', 'district': 'Annamayya', 'modal_price': 1800, 'previous_price': 2100, 'price_change_percent': '-14.2%', 'msp_rate': 1500, 'daily_arrival': '1400 Crates' },
            { 'crop_name': 'Onion (ఉల్లిపాయ / प्याज)', 'crop_name_native': 'ఉల్లిపాయ', 'mandi_name': 'Lasalgaon / Kurnool', 'district': 'Kurnool', 'modal_price': 2150, 'previous_price': 2050, 'price_change_percent': '+4.8%', 'msp_rate': 1900, 'daily_arrival': '680 Quintals' },
        ]
        for m in mandi_records:
            MandiCommodityPrice.objects.get_or_create(crop_name=m['crop_name'], mandi_name=m['mandi_name'], defaults=m)

        # 4. Govt Schemes
        schemes = [
            {
                'title': 'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
                'subtitle': 'Direct income support of ₹6,000/year in 3 equal installments.',
                'category': 'Central Scheme',
                'benefit_amount': '₹6,000 / Year',
                'eligibility': 'All small & marginal landholder farmer families with cultivable land.',
                'application_status': 'Applications Open',
                'required_documents': ['Aadhaar Card', 'Land Ownership Records (Pattadar Passbook)', 'Bank Account Details'],
                'official_portal_url': 'https://pmkisan.gov.in'
            },
            {
                'title': 'PMFBY (Pradhan Mantri Fasal Bima Yojana)',
                'subtitle': 'Comprehensive crop insurance against drought, floods, pests & unseasonal rains.',
                'category': 'Crop Insurance',
                'benefit_amount': 'Up to 100% Crop Loss Cover',
                'eligibility': 'All farmers growing notified crops in notified areas (loanee & non-loanee).',
                'application_status': 'Kharif Window Active',
                'required_documents': ['Sowing Certificate', 'Land Record', 'Bank Passbook'],
                'official_portal_url': 'https://pmfby.gov.in'
            },
            {
                'title': 'Kisan Credit Card (KCC) Scheme',
                'subtitle': 'Low-interest short term agriculture credit up to ₹3,00,000 at 4% subsidized interest rate.',
                'category': 'Low Interest Loan',
                'benefit_amount': 'Up to ₹3 Lakh at 4% Interest',
                'eligibility': 'Individual/joint farmers, tenant farmers, self-help groups (SHGs).',
                'application_status': 'Available at all National Banks',
                'required_documents': ['Land Records', 'ID Proof', 'Recent Passport Photos'],
                'official_portal_url': 'https://myscheme.gov.in'
            },
            {
                'title': 'PM-KUSUM Solar Agriculture Pump Subsidy',
                'subtitle': 'Up to 60% financial subsidy for installing standalone solar irrigation pumps.',
                'category': 'Solar & Irrigation',
                'benefit_amount': '60% Govt Subsidy on Solar Pumps',
                'eligibility': 'Farmers, farmer producer organizations (FPOs), cooperatives.',
                'application_status': 'State Quota Open',
                'required_documents': ['Land ownership copy', 'Electricity clearance', 'Aadhaar'],
                'official_portal_url': 'https://pmkusum.mnre.gov.in'
            }
        ]
        for s in schemes:
            GovtScheme.objects.get_or_create(title=s['title'], defaults=s)

        # 5. Weather Advisory
        report, _ = WeatherReport.objects.get_or_create(
            location_name='Guntur District, AP',
            defaults={
                'temperature': '32°C',
                'feels_like': '36°C',
                'condition': 'Partly Cloudy',
                'humidity': '68%',
                'wind_speed': '14 km/h',
                'rain_probability': '20%',
                'uv_index': 'High',
                'advisory_headline': 'Agro-Advisory: Moderate Rain expected Sunday & Monday',
                'advisory_detail': 'Hold pesticide/fertilizer spraying until Tuesday to avoid chemical wash-off. Ensure field drainage channels are clear for standing cotton & chilli crops.'
            }
        )

        forecasts = [
            { 'day': 'Today (Sat)', 'temp': '32°C / 24°C', 'condition': 'Partly Cloudy', 'rain': '20%', 'icon': 'CloudSun' },
            { 'day': 'Sun', 'temp': '30°C / 23°C', 'condition': 'Scattered Showers', 'rain': '65%', 'icon': 'CloudRain' },
            { 'day': 'Mon', 'temp': '29°C / 22°C', 'condition': 'Moderate Rain', 'rain': '80%', 'icon': 'CloudRain' },
            { 'day': 'Tue', 'temp': '31°C / 23°C', 'condition': 'Sunny & Humid', 'rain': '10%', 'icon': 'Sun' },
            { 'day': 'Wed', 'temp': '33°C / 24°C', 'condition': 'Clear Sky', 'rain': '5%', 'icon': 'Sun' },
            { 'day': 'Thu', 'temp': '34°C / 25°C', 'condition': 'Hot & Clear', 'rain': '0%', 'icon': 'Sun' },
        ]
        for f in forecasts:
            DailyForecast.objects.get_or_create(weather_report=report, day=f['day'], defaults=f)

        # 6. Community Posts
        posts = [
            {
                'author': 'Venkat Rao',
                'location': 'Tenali, Andhra Pradesh',
                'crop': 'Paddy / BPT 5204',
                'time_ago': '2 hours ago',
                'content': 'Has anyone started harvesting Samba Mahsuri in Guntur delta? What moisture percentage are the millers accepting this week at the yard?',
                'likes': 18,
                'replies_count': 2,
                'is_verified': True
            },
            {
                'author': 'Suresh Reddy',
                'location': 'Suryapet, Telangana',
                'crop': 'Cotton & Chilli',
                'time_ago': '5 hours ago',
                'content': 'John Deere 5050D (50 HP) Tractor available with Rotavator & MB Plough for rent @ ₹750/hour in Suryapet mandal. Contact me on WhatsApp.',
                'likes': 24,
                'replies_count': 1,
                'is_rental': True
            },
            {
                'author': 'Dr. Ananya Sharma (Agri Scientist)',
                'location': 'ANGRAU Research Station',
                'crop': 'All Crops',
                'time_ago': '1 day ago',
                'content': 'Farmer advisory: High humidity this week increases risk of False Smut in late-sown paddy. Spray Copper Oxychloride (2.5g/L) during boot leaf stage.',
                'likes': 56,
                'replies_count': 3,
                'is_official': True
            }
        ]
        for p in posts:
            post_obj, created = ForumPost.objects.get_or_create(author=p['author'], content=p['content'], defaults=p)
            if created:
                PostReply.objects.create(
                    post=post_obj,
                    author='Ramesh Patel',
                    content='Thank you for sharing this crucial advisory for our Guntur cluster!'
                )

        self.stdout.write(self.style.SUCCESS("RaithuSetu seed data inserted successfully!"))
