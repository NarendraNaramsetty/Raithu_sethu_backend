"""
RaithuSetu - Verified Government Agricultural Schemes Dataset (2025-2026)
Contains accurate monetary subsidies, eligibility requirements, required documents,
and direct links to official Central & State Government portals.
"""

GOVT_SCHEMES_DATA = [
    {
        "title": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "subtitle": "Direct income support of ₹6,000 per year paid in three 4-monthly installments of ₹2,000 directly into farmers' Aadhaar-seeded bank accounts.",
        "category": "Central Scheme",
        "benefit_amount": "₹6,000 / Year (₹2,000 × 3 Installments via DBT)",
        "eligibility": "All landholding small and marginal farmer families with cultivable land in their names. Excludes institutional landholders and tax-paying professionals.",
        "required_documents": [
            "Aadhaar Card (Mandatory eKYC)",
            "Land Record (Pattadar Passbook / RoR 1-B)",
            "Bank Account (NPCI / Aadhaar Seeded)",
            "Mobile Number Linked to Aadhaar"
        ],
        "application_status": "Active (19th Installment 2026)",
        "official_portal_url": "https://pmkisan.gov.in"
    },
    {
        "title": "PMFBY (Pradhan Mantri Fasal Bima Yojana)",
        "subtitle": "Comprehensive crop insurance shield against natural calamities, pests & localized extreme weather from pre-sowing to post-harvest.",
        "category": "Crop Insurance",
        "benefit_amount": "Up to 100% Sum Insured (Farmers pay only 1.5% - 2% Premium)",
        "eligibility": "All farmers including sharecroppers and tenant farmers growing notified Kharif & Rabi crops in notified areas.",
        "required_documents": [
            "Aadhaar Card",
            "Land Revenue Record / Tenant Agreement",
            "Crop Sowing Declaration / Adangal / Pahani",
            "Cancelled Cheque or Bank Passbook Copy"
        ],
        "application_status": "Kharif & Rabi 2026 Applications Open",
        "official_portal_url": "https://pmfby.gov.in"
    },
    {
        "title": "PM-KUSUM Component-B (Solar Agri Pumps)",
        "subtitle": "60% to 70% direct government subsidy for replacing diesel pumps with standalone high-efficiency 3HP to 10HP DC/AC Solar Water Pumps.",
        "category": "Solar",
        "benefit_amount": "60% to 70% Subsidy (Up to ₹1,80,000 financial support)",
        "eligibility": "Individual farmers, groups of farmers, water user associations with farmland having boring/open well water source but no grid electricity.",
        "required_documents": [
            "Aadhaar Card",
            "Land Title Deed / 1-B Records",
            "Borewell / Open Well Certificate",
            "Bank Account Details",
            "Passport Size Photograph"
        ],
        "application_status": "State Portals Open for 2026 Subsidies",
        "official_portal_url": "https://pmkusum.mnre.gov.in"
    },
    {
        "title": "Kisan Credit Card (KCC) Low-Interest Crop Loan",
        "subtitle": "Flexible institutional working capital credit for crop cultivation, fertilizer, pesticide purchase, and post-harvest maintenance at heavily subsidized interest.",
        "category": "Low Interest Loan",
        "benefit_amount": "Up to ₹3,00,000 Loan @ 4% Effective Interest Rate",
        "eligibility": "All farmers, individual or joint borrowers, tenant farmers, oral lessees, and Self Help Groups (SHGs). Collateral-free loan up to ₹1.60 Lakh.",
        "required_documents": [
            "Duly filled KCC Bank Application Form",
            "Identity & Address Proof (Aadhaar / Voter ID)",
            "Land Title / Revenue Record (Pahani / Chitta / 1-B)",
            "Crop Sowing Certificate"
        ],
        "application_status": "Applications Open across all Nationalized & RRBs",
        "official_portal_url": "https://agricoop.nic.in"
    },
    {
        "title": "YSR Rythu Bharosa / PM-KISAN State Combined Scheme",
        "subtitle": "Input financial assistance provided to farmer families including SC, ST, BC, Minorities, and RoFR forest cultivators in Andhra Pradesh.",
        "category": "Central Scheme",
        "benefit_amount": "₹13,500 / Year per family (₹7,500 + ₹4,000 + ₹2,000)",
        "eligibility": "All landowning farmer families and eligible tenant farmers cultivating land in Andhra Pradesh.",
        "required_documents": [
            "Aadhaar Card",
            "Pattadar Passbook / CCRC Card (for tenant farmers)",
            "Aadhaar Linked Bank Passbook",
            "e-Crop Booking Registration"
        ],
        "application_status": "Active 2026 Disbursal Cycle",
        "official_portal_url": "https://ysrrythubharosa.ap.gov.in"
    },
    {
        "title": "SMAM - Sub-Mission on Agricultural Mechanization",
        "subtitle": "Direct financial subsidy on purchase of modern farm machinery including Tractors, Power Tillers, Drone Sprayers, Rotavators & Custom Hiring Centers.",
        "category": "Central Scheme",
        "benefit_amount": "40% to 50% Subsidy (Up to ₹5,00,000 on Machinery)",
        "eligibility": "Small, marginal, SC/ST, and women farmers given top priority. Available for individual farmers, FPOs, and village cooperatives.",
        "required_documents": [
            "Aadhaar Card",
            "Land Ownership Proof / RoR Record",
            "Bank Passbook Copy",
            "Caste Certificate (for SC/ST quota subsidy)",
            "Quotation from Authorized Dealer"
        ],
        "application_status": "Direct Benefit Transfer Portal Active 2026",
        "official_portal_url": "https://agrimachinery.nic.in"
    },
    {
        "title": "PMKSY - Per Drop More Crop (Micro Irrigation Subsidy)",
        "subtitle": "Promoting water use efficiency through subsidized installation of Drip Irrigation and Sprinkler Irrigation systems on farm fields.",
        "category": "Central Scheme",
        "benefit_amount": "55% Subsidy for Small/Marginal & 45% for Other Farmers",
        "eligibility": "Farmers holding valid agricultural land with an assured water source (borewell, river lift, or farm pond).",
        "required_documents": [
            "Aadhaar Card",
            "Land Title / 1-B Record",
            "Water & Electricity Connection Certificate",
            "Field Sketch Map & Soil / Water Test Report",
            "Bank Passbook"
        ],
        "application_status": "State Horticulture Departments Enrolling",
        "official_portal_url": "https://pmksy.gov.in"
    },
    {
        "title": "Paramparagat Krishi Vikas Yojana (PKVY Organic Farming)",
        "subtitle": "Financial and technical assistance for cluster-based organic farming adoption, chemical-free bio-inputs production, and PGS-India green certification.",
        "category": "Central Scheme",
        "benefit_amount": "₹50,000 / Hectare for 3 years (₹31,000 for Bio-inputs via DBT)",
        "eligibility": "Farmer clusters/groups having minimum 20 hectares or 50 farmers adopting organic farming standards.",
        "required_documents": [
            "Aadhaar Card",
            "Land Record (ROR/Passbook)",
            "Group Registration / Self Help Group MoU",
            "Soil Organic Carbon Baseline Test",
            "Bank Account"
        ],
        "application_status": "Cluster Enrollment Active 2026",
        "official_portal_url": "https://pgsindia-ncof.gov.in"
    },
    {
        "title": "PM-KUSUM Component-C (Feeder Level Solarization)",
        "subtitle": "Solarizing existing grid-connected agricultural pumps with up to 60% capital subsidy and earning extra steady income by selling surplus power to DISCOMs.",
        "category": "Solar",
        "benefit_amount": "60% Subsidy + ₹3.10 / kWh Earned on Surplus Solar Feed-in",
        "eligibility": "Farmers and groups of farmers connected to dedicated agricultural distribution feeders.",
        "required_documents": [
            "Aadhaar Card",
            "Electricity Consumer Number / Service Connection Bill",
            "Land Ownership Document",
            "Bank Account linked to Aadhaar"
        ],
        "application_status": "DISCOM State Windows Active 2026",
        "official_portal_url": "https://mnre.gov.in"
    },
    {
        "title": "Agriculture Infrastructure Fund (AIF)",
        "subtitle": "Medium-long term debt financing facility with attractive 3% annual interest subvention and CGTMSE guarantee for setting up cold storage, packhouses & silos.",
        "category": "Low Interest Loan",
        "benefit_amount": "Up to ₹2 Crore Loan with 3% Interest Subvention for 7 Years",
        "eligibility": "Primary Agricultural Credit Societies (PACS), FPOs, Agri-entrepreneurs, Startups, and individual progressive farmers.",
        "required_documents": [
            "Detailed Project Report (DPR)",
            "Aadhaar & PAN Card",
            "Land Ownership / Long Lease Document (Minimum 10 Years)",
            "Bank Statements of past 6 months",
            "FPO / Entity Registration (if applicable)"
        ],
        "application_status": "Portal Open & Approving Applications",
        "official_portal_url": "https://agriinfra.dac.gov.in"
    },
    {
        "title": "Restructured Weather Based Crop Insurance Scheme (RWBCIS)",
        "subtitle": "Parametric index-based risk mitigation scheme providing quick automated claims for adverse weather triggers such as rainfall deficit, heatwave, and frost.",
        "category": "Crop Insurance",
        "benefit_amount": "Automatic Weather-Triggered Payouts up to ₹65,000 / Acre",
        "eligibility": "Cultivators of notified horticultural and fruit crops (Chilli, Mango, Banana, Tomato, Cotton, Turmeric) in notified automatic weather station zones.",
        "required_documents": [
            "Aadhaar Card",
            "Land Revenue Record / e-Pahani",
            "Crop Sowing Certificate issued by Village Revenue Officer",
            "Bank Account Passbook"
        ],
        "application_status": "2026 Weather Season Active",
        "official_portal_url": "https://pmfby.gov.in"
    }
]
