"""
RaithuSetu - AI Crop Disease Detection Service powered by Anthropic Claude Vision
With Strict Crop-Disease Validation and Resilient Indian Agronomy Fallback Engine
"""

import base64
import json
import logging
import re
import time
from decouple import config

logger = logging.getLogger(__name__)

# =====================================================================
# 1. COMPREHENSIVE 12-CROP AGRICULTURAL FALLBACK KNOWLEDGE BASE
# =====================================================================
INDIAN_AGRONOMY_FALLBACK_DB = {
    "rice": {
        "crop_name": "Rice / Paddy",
        "crop_scientific_name": "Oryza sativa",
        "crop_telugu": "వరి (Paddy)",
        "crop_hindi": "धान (Rice)",
        "allowed_diseases": [
            "rice blast", "bacterial leaf blight", "brown spot",
            "sheath blight", "sheath rot", "false smut", "tungro", "healthy"
        ],
        "diseases": {
            "bacterial_leaf_blight": {
                "name": "Bacterial Leaf Blight",
                "scientific_name": "Xanthomonas oryzae pv. oryzae",
                "category": "Bacterial Disease",
                "severity": "Moderate",
                "symptoms": [
                    "Water-soaked yellowish-green stripes along leaf margins progressing inward",
                    "Lesions enlarge, turn straw-yellow, and cause leaves to dry prematurely",
                    "Milky bacterial exudate droplets visible on infected leaf surfaces in early morning"
                ],
                "diagnosis_summary": "Bacterial leaf blight detected on paddy leaves with characteristic marginal yellowing and necrosis.",
                "organic_solution": "Foliar spray of Pseudomonas fluorescens @ 5g/liter or apply fresh cow dung slurry supernatant (10%) mixed with turmeric extract.",
                "chemical_treatment": "Spray Plantomycin / Streptomycin sulfate + Tetracycline @ 0.5g/liter combined with Copper Oxychloride 50% WP @ 2.5g/liter. Follow product label for exact spray volume.",
                "prevention": "Avoid excessive split application of nitrogen fertilizers. Maintain intermittent wetting and drying water management in the field.",
                "warning": "Do not enter or work in wet fields during early morning to prevent mechanical spreading of bacterial ooze."
            },
            "rice_blast": {
                "name": "Rice Blast",
                "scientific_name": "Magnaporthe oryzae",
                "category": "Fungal Disease",
                "severity": "Severe",
                "symptoms": [
                    "Elliptical / spindle-shaped leaf lesions with greyish-white centers and dark brown margins",
                    "Lesions coalesce causing complete drying and burning of foliage (leaf blast)",
                    "Brown to black rot at neck nodes (neck blast) causing panicle breakage"
                ],
                "diagnosis_summary": "Rice blast infection identified by characteristic diamond/spindle-shaped necrotic lesions on the leaf blade.",
                "organic_solution": "Apply Pseudomonas fluorescens (20g/kg seed treatment and 5g/L foliar spray) or Dashaparni Kashayam @ 30ml/liter to reinforce plant silica barriers.",
                "chemical_treatment": "Foliar spray of Tricyclazole 75% WP @ 0.6g/liter or Isoprothiolane 40% EC @ 1.5ml/liter at initial booting stage. Adhere strictly to the product label instructions.",
                "prevention": "Adopt blast-resistant rice cultivars (e.g. MTU 1010, BPT 5204 tolerant lines). Avoid dense planting and excessive urea application in night-dew conditions.",
                "warning": "High atmospheric humidity (>90%) with night temperatures between 18-24°C accelerates blast spore spread rapidly."
            },
            "brown_spot": {
                "name": "Brown Spot",
                "scientific_name": "Bipolaris oryzae",
                "category": "Fungal Disease",
                "severity": "Moderate",
                "symptoms": [
                    "Small circular to oval brown spots with prominent yellow halo on leaves",
                    "Spots can coalesce resulting in large dry patches on mature foliage"
                ],
                "diagnosis_summary": "Brown spot disease detected, typically associated with nutrient-deficient or water-stressed soil conditions.",
                "organic_solution": "Seed treatment with Trichoderma viride @ 5g/kg seed. Apply enriched FYM to correct potassium and silicon deficiencies.",
                "chemical_treatment": "Foliar spray of Mancozeb 75% WP @ 2g/liter or Propiconazole 25% EC @ 1ml/liter. Follow local agricultural extension guidance.",
                "prevention": "Ensure balanced N-P-K-Zn application. Avoid severe drought stress during active tillering stage.",
                "warning": "Brown spot indicates soil exhaustion; soil nutrient testing is recommended for long-term correction."
            },
            "sheath_blight": {
                "name": "Sheath Blight",
                "scientific_name": "Rhizoctonia solani",
                "category": "Fungal Disease",
                "severity": "Moderate",
                "symptoms": [
                    "Greenish-grey oval or irregular lesions on leaf sheaths near water line",
                    "Lesions expand up to upper leaves with brown margins (snakeskin pattern)"
                ],
                "diagnosis_summary": "Sheath blight identified with characteristic snakeskin-like blotches near the waterline.",
                "organic_solution": "Spray Trichoderma harzianum or Bacillus subtilis @ 5g/liter directly targeted at lower plant canopy.",
                "chemical_treatment": "Foliar spray of Hexaconazole 5% EC @ 2ml/liter or Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1ml/liter directed at the plant base.",
                "prevention": "Maintain wider row spacing (20cm x 15cm) to improve light penetration and air circulation. Drain excess standing water.",
                "warning": "Apply chemical sprays directed towards the lower stem and base rather than upper canopy."
            },
            "healthy": {
                "name": "Healthy Rice Crop",
                "scientific_name": "Oryza sativa",
                "category": "Healthy",
                "severity": "None",
                "symptoms": ["Uniformly vibrant green leaf blades with no visible lesions, yellowing, or insect chewing damage."],
                "diagnosis_summary": "The paddy leaf shows healthy vigorous vegetative growth with no active signs of pathology.",
                "organic_solution": "Continue regular bio-fertilizer application (Azospirillum & Phosphobacteria) and periodic neem oil repellent sprays.",
                "chemical_treatment": "No chemical fungicide or bactericide intervention is required.",
                "prevention": "Maintain clean field bunds and regular weekly scoutings for early pest/disease detection.",
                "warning": "Keep monitoring fields weekly during cloudy weather for early blast or BLB symptoms."
            }
        }
    },
    "tomato": {
        "crop_name": "Tomato",
        "crop_scientific_name": "Solanum lycopersicum",
        "crop_telugu": "టమాటా (Tomato)",
        "crop_hindi": "टमाटर (Tomato)",
        "allowed_diseases": [
            "early blight", "late blight", "bacterial spot",
            "septoria leaf spot", "leaf mold", "mosaic virus", "healthy"
        ],
        "diseases": {
            "early_blight": {
                "name": "Early Blight",
                "scientific_name": "Alternaria solani",
                "category": "Fungal Disease",
                "severity": "Moderate",
                "symptoms": [
                    "Dark brown to black necrotic circular spots with concentric target-board rings",
                    "Yellow chlorotic halos surrounding older lesions on lower leaves first",
                    "Progressive defoliation from ground level upwards"
                ],
                "diagnosis_summary": "Early blight identified by characteristic concentric target-board rings on lower tomato foliage.",
                "organic_solution": "Foliar spray of cold-pressed Neem Oil (10,000 ppm) @ 5ml/liter or Trichoderma viride @ 5g/liter on lower leaves every 7-10 days.",
                "chemical_treatment": "Foliar spray of Mancozeb 75% WP @ 2.5g/liter or Azoxystrobin 23% SC @ 1ml/liter during calm evening hours. Follow product label for safety intervals.",
                "prevention": "Prune bottom leaves touching wet soil, use silver-black mulch, and avoid overhead sprinkler irrigation.",
                "warning": "Burn or bury heavily infected lower pruned leaves away from the tomato crop area."
            },
            "late_blight": {
                "name": "Late Blight",
                "scientific_name": "Phytophthora infestans",
                "category": "Oomycete Disease",
                "severity": "Severe",
                "symptoms": [
                    "Large irregular water-soaked pale green lesions rapidly turning dark brown",
                    "White delicate fungal downy growth visible on leaf undersides in cool humid mornings"
                ],
                "diagnosis_summary": "Late blight detected; a fast-spreading destructive pathology favored by cool, foggy, or wet conditions.",
                "organic_solution": "Apply Copper Hydroxide or Bordeaux mixture (1%) as a protective foliar barrier before disease spreads.",
                "chemical_treatment": "Spray Cymoxanil 8% + Mancozeb 64% WP @ 3g/liter or Dimethomorph 50% WP @ 1g/liter. Follow local extension label guidance.",
                "prevention": "Ensure wide plant spacing and excellent row aeration. Avoid planting near potato crops.",
                "warning": "Late blight can decimate entire tomato fields within 72 hours under cool, wet weather."
            },
            "healthy": {
                "name": "Healthy Tomato Crop",
                "scientific_name": "Solanum lycopersicum",
                "category": "Healthy",
                "severity": "None",
                "symptoms": ["Dark green, well-expanded leaves free from leaf spots, curling, or chlorosis."],
                "diagnosis_summary": "Tomato foliage is healthy and showing normal vegetative vigor.",
                "organic_solution": "Maintain routine foliar sprays of Panchagavya (3%) or Seaweed extract for enhanced vigor.",
                "chemical_treatment": "No chemical intervention needed.",
                "prevention": "Stake plants properly to keep foliage elevated away from wet ground.",
                "warning": "Monitor lower foliage weekly for early signs of fungal spotting."
            }
        }
    },
    "chilli": {
        "crop_name": "Chilli",
        "crop_scientific_name": "Capsicum annuum",
        "crop_telugu": "మిరప (Chilli)",
        "crop_hindi": "मिर्च (Chilli)",
        "allowed_diseases": [
            "anthracnose", "powdery mildew", "leaf curl", "bacterial leaf spot", "healthy"
        ],
        "diseases": {
            "anthracnose": {
                "name": "Anthracnose / Fruit Rot",
                "scientific_name": "Colletotrichum capsici",
                "category": "Fungal Disease",
                "severity": "Moderate",
                "symptoms": [
                    "Sunken circular dark lesions with concentric rings on chilli pods and leaves",
                    "Die-back of twigs starting from the top tips moving downwards"
                ],
                "diagnosis_summary": "Anthracnose and die-back identified on chilli plant tissue.",
                "organic_solution": "Foliar spray of 5% Neem Seed Kernel Extract (NSKE) or Bacillus subtilis @ 5ml/liter.",
                "chemical_treatment": "Apply Difenoconazole 25% EC @ 0.5ml/liter or Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1ml/liter. Follow product label guidance.",
                "prevention": "Collect and destroy mummified pods from previous season. Treat seeds with Thiram @ 3g/kg seed.",
                "warning": "Ensure adequate field drainage; avoid stagnant irrigation water around root zones."
            },
            "leaf_curl": {
                "name": "Chilli Leaf Curl Virus",
                "scientific_name": "Begomovirus (Whitefly vector)",
                "category": "Viral Disease",
                "severity": "Moderate",
                "symptoms": [
                    "Upward curling, puckering, and crinkling of leaves with thickened veins",
                    "Stunted plant growth with reduced fruit setting"
                ],
                "diagnosis_summary": "Chilli leaf curl virus transmission identified, transmitted primarily by whiteflies (Bemisia tabaci).",
                "organic_solution": "Install 15 yellow sticky traps per acre. Spray 5% NSKE or Verticillium lecanii @ 5g/liter.",
                "chemical_treatment": "Control whitefly vectors by spraying Diafenthiuron 50% WP @ 1.25g/liter. Follow product label safety intervals.",
                "prevention": "Eradicate weed hosts around field borders. Plant barrier crops like maize or sorghum around the chilli field.",
                "warning": "Viral diseases cannot be cured once inside the plant; focus strictly on controlling vector insects."
            },
            "healthy": {
                "name": "Healthy Chilli Crop",
                "scientific_name": "Capsicum annuum",
                "category": "Healthy",
                "severity": "None",
                "symptoms": ["Glossy, deep green leaves with normal venation and active apical flowering."],
                "diagnosis_summary": "Chilli plant exhibits strong vegetative vigor with no signs of pest or fungal damage.",
                "organic_solution": "Apply periodic preventive neem oil sprays (3ml/L) to keep sucking pests away.",
                "chemical_treatment": "No chemical treatment required.",
                "prevention": "Maintain balanced micronutrient foliar sprays (Zinc & Boron).",
                "warning": "Scout weekly for thrips and mites during hot, dry spells."
            }
        }
    },
    "cotton": {
        "crop_name": "Cotton",
        "crop_scientific_name": "Gossypium hirsutum",
        "crop_telugu": "పత్తి (Cotton)",
        "crop_hindi": "कपास (Cotton)",
        "allowed_diseases": [
            "bacterial blight", "alternaria leaf spot", "grey mildew", "fusarium wilt", "healthy"
        ],
        "diseases": {
            "bacterial_blight": {
                "name": "Bacterial Blight / Angular Leaf Spot",
                "scientific_name": "Xanthomonas citri pv. malvacearum",
                "category": "Bacterial Disease",
                "severity": "Moderate",
                "symptoms": [
                    "Angular water-soaked spots bounded by leaf veinlets",
                    "Spots turn dark brown to black (black arm symptom on branches)"
                ],
                "diagnosis_summary": "Angular leaf spot / bacterial blight detected on cotton leaves.",
                "organic_solution": "Spray Copper Oxychloride 50% WP @ 2.5g/liter mixed with cow dung slurry supernatant (5%).",
                "chemical_treatment": "Foliar spray of Streptocycline @ 0.1g/liter + Copper Oxychloride @ 2.5g/liter. Follow extension label recommendations.",
                "prevention": "Acid delinting of cotton seeds before sowing. Deep summer ploughing to eradicate crop residues.",
                "warning": "Avoid excessive overhead irrigation that spreads bacterial drops between adjacent plants."
            },
            "healthy": {
                "name": "Healthy Cotton Crop",
                "scientific_name": "Gossypium hirsutum",
                "category": "Healthy",
                "severity": "None",
                "symptoms": ["Broad, palmately lobed green leaves with clear veins and healthy squares/bolls."],
                "diagnosis_summary": "Cotton plant shows healthy leaf development and good photosynthetic canopy.",
                "organic_solution": "Routine monitoring and installing pheromone traps for pink bollworm.",
                "chemical_treatment": "No chemical action required.",
                "prevention": "Maintain clean inter-row cultivation.",
                "warning": "Inspect leaf undersides periodically for early jassid/aphid nymph activity."
            }
        }
    },
    "maize": {
        "crop_name": "Maize / Corn",
        "crop_scientific_name": "Zea mays",
        "crop_telugu": "మొక్కజొన్న (Maize)",
        "crop_hindi": "मक्का (Maize)",
        "allowed_diseases": [
            "northern corn leaf blight", "common rust", "maydis leaf blight", "fall armyworm", "healthy"
        ],
        "diseases": {
            "northern_corn_leaf_blight": {
                "name": "Northern Corn Leaf Blight",
                "scientific_name": "Exserohilum turcicum",
                "category": "Fungal Disease",
                "severity": "Moderate",
                "symptoms": [
                    "Long, elliptical, grayish-green or tan lesions (cigar-shaped) on leaves",
                    "Lesions can extend 3 to 15 cm along the leaf blade"
                ],
                "diagnosis_summary": "Northern corn leaf blight (NCLB) identified by long cigar-shaped necrotic lesions on maize leaves.",
                "organic_solution": "Foliar application of Trichoderma harzianum @ 5g/liter or botanical neem formulation.",
                "chemical_treatment": "Foliar spray of Mancozeb 75% WP @ 2.5g/liter or Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1ml/liter. Follow label instructions.",
                "prevention": "Plant resistant hybrids and perform balanced N-P-K fertilizer application.",
                "warning": "Rotate maize with non-graminaceous crops (pulses/oilseeds) to break fungal spore cycle."
            },
            "healthy": {
                "name": "Healthy Maize Crop",
                "scientific_name": "Zea mays",
                "category": "Healthy",
                "severity": "None",
                "symptoms": ["Long arching dark green leaves with strong central midribs and intact whorls."],
                "diagnosis_summary": "Maize crop exhibits robust vegetative health with no signs of leaf blight or borer damage.",
                "organic_solution": "Maintain soil organic matter and timely nitrogen top-dressing.",
                "chemical_treatment": "No chemical application necessary.",
                "prevention": "Monitor central whorls for early fall armyworm pinholes.",
                "warning": "Avoid waterlogging in early seedling stages."
            }
        }
    },
    "groundnut": {
        "crop_name": "Groundnut / Peanut",
        "crop_scientific_name": "Arachis hypogaea",
        "crop_telugu": "వేరుశనగ (Groundnut)",
        "crop_hindi": "मूंगफली (Groundnut)",
        "allowed_diseases": ["early leaf spot", "late leaf spot", "rust", "healthy"],
        "diseases": {
            "late_leaf_spot": {
                "name": "Tikka / Late Leaf Spot",
                "scientific_name": "Phaeoisariopsis personata",
                "category": "Fungal Disease",
                "severity": "Moderate",
                "symptoms": [
                    "Nearly circular, dark brown to black spots mostly on lower leaf surface",
                    "Spots lack a distinct yellow halo and cause premature leaf drop"
                ],
                "diagnosis_summary": "Tikka disease (late leaf spot) identified on groundnut foliage.",
                "organic_solution": "Spray 3% Panchagavya or Trichoderma harzianum @ 5g/liter at 35 and 50 days after sowing.",
                "chemical_treatment": "Foliar spray of Carbendazim 12% + Mancozeb 63% WP @ 2g/liter or Hexaconazole 5% EC @ 2ml/liter. Follow product label instructions.",
                "prevention": "Crop rotation with pearl millet, maize, or sorghum. Remove and burn diseased plant debris.",
                "warning": "Leaf loss during peg development directly reduces pod yield; treat at earliest appearance."
            },
            "healthy": {
                "name": "Healthy Groundnut Crop",
                "scientific_name": "Arachis hypogaea",
                "category": "Healthy",
                "severity": "None",
                "symptoms": ["Uniformly green 4-foliolate leaves with active flowering and healthy peg formation."],
                "diagnosis_summary": "Groundnut crop shows healthy green foliage and normal growth.",
                "organic_solution": "Apply gypsum @ 200 kg/acre at flowering stage for strong pod development.",
                "chemical_treatment": "No chemical application needed.",
                "prevention": "Maintain optimum soil moisture without flooding.",
                "warning": "Scout leaves after humid spells for early tikka spots."
            }
        }
    },
    "potato": {
        "crop_name": "Potato",
        "crop_scientific_name": "Solanum tuberosum",
        "crop_telugu": "బంగాళాదుంప (Potato)",
        "crop_hindi": "आलू (Potato)",
        "allowed_diseases": ["early blight", "late blight", "healthy"],
        "diseases": {
            "late_blight": {
                "name": "Late Blight",
                "scientific_name": "Phytophthora infestans",
                "category": "Oomycete Disease",
                "severity": "Severe",
                "symptoms": [
                    "Water-soaked lesions on leaves rapidly expanding into large brown necrotic areas",
                    "White moldy growth on leaf undersides in wet morning hours"
                ],
                "diagnosis_summary": "Late blight detected on potato crop; highly contagious in cool wet weather.",
                "organic_solution": "Prophylactic spray of Copper Hydroxide @ 2g/liter or 1% Bordeaux mixture.",
                "chemical_treatment": "Foliar spray of Cymoxanil 8% + Mancozeb 64% WP @ 3g/liter or Metalaxyl-M 4% + Mancozeb 64% WP @ 2.5g/liter. Follow label instructions.",
                "prevention": "Plant certified disease-free seed tubers. High earthing-up to prevent spores washing into tubers.",
                "warning": "Do not harvest infected crops during rainy weather to prevent tuber contamination."
            },
            "healthy": {
                "name": "Healthy Potato Crop",
                "scientific_name": "Solanum tuberosum",
                "category": "Healthy",
                "severity": "None",
                "symptoms": ["Vigorous green compound leaves with sturdy stems and no foliage spotting."],
                "diagnosis_summary": "Potato foliage is healthy with no visible pathogen symptoms.",
                "organic_solution": "Maintain adequate earthing up and balanced organic nutrition.",
                "chemical_treatment": "No chemical treatment required.",
                "prevention": "Ensure good soil aeration and avoid over-irrigation.",
                "warning": "Keep watchful during foggy or overcast weather spells."
            }
        }
    },
    "brinjal": {
        "crop_name": "Brinjal / Eggplant",
        "crop_scientific_name": "Solanum melongena",
        "crop_telugu": "వంకాయ (Brinjal)",
        "crop_hindi": "बैंगन (Brinjal)",
        "allowed_diseases": ["phomopsis fruit rot", "bacterial wilt", "leaf spot", "healthy"],
        "diseases": {
            "phomopsis_fruit_rot": {
                "name": "Phomopsis Fruit Rot & Blight",
                "scientific_name": "Phomopsis vexans",
                "category": "Fungal Disease",
                "severity": "Moderate",
                "symptoms": [
                    "Circular brown spots with pale centers on leaves and fruits",
                    "Stem lesions causing seedling damping off or twig dieback"
                ],
                "diagnosis_summary": "Phomopsis blight identified on brinjal leaf and stem tissue.",
                "organic_solution": "Spray Trichoderma viride @ 5g/liter and treat seeds before sowing.",
                "chemical_treatment": "Spray Mancozeb 75% WP @ 2.5g/liter or Copper Oxychloride 50% WP @ 3g/liter. Follow product label guidance.",
                "prevention": "Remove infected fruits and crop debris from the field. Practice crop rotation with non-solanaceous crops.",
                "warning": "Avoid picking fruits when morning dew is still present on plants."
            },
            "healthy": {
                "name": "Healthy Brinjal Crop",
                "scientific_name": "Solanum melongena",
                "category": "Healthy",
                "severity": "None",
                "symptoms": ["Large, broad, healthy green leaves with no fruit rot or shoot bore entry holes."],
                "diagnosis_summary": "Brinjal crop is healthy with vigorous vegetative canopy.",
                "organic_solution": "Install pheromone traps for brinjal shoot and fruit borer.",
                "chemical_treatment": "No chemical action required.",
                "prevention": "Maintain weed-free field bunds.",
                "warning": "Monitor terminal shoot tips weekly for early wilting."
            }
        }
    },
    "onion": {
        "crop_name": "Onion",
        "crop_scientific_name": "Allium cepa",
        "crop_telugu": "ఉల్లిపాయ (Onion)",
        "crop_hindi": "प्याज (Onion)",
        "allowed_diseases": ["purple blotch", "downy mildew", "stemphylium blight", "healthy"],
        "diseases": {
            "purple_blotch": {
                "name": "Purple Blotch",
                "scientific_name": "Alternaria porri",
                "category": "Fungal Disease",
                "severity": "Moderate",
                "symptoms": [
                    "Small, sunken, whitish lesions turning purple at centers with yellow borders",
                    "Lesions girdle leaves causing leaf blades to fall over and dry up"
                ],
                "diagnosis_summary": "Purple blotch detected on tubular onion foliage.",
                "organic_solution": "Foliar spray of Garlic-Chilli botanical extract (20ml/L) with sticking agent or Ampelomyces bio-formulation.",
                "chemical_treatment": "Foliar spray of Tebuconazole 25.9% EC @ 1.25ml/liter or Mancozeb 75% WP @ 2.5g/liter with a surfactant/sticker.",
                "prevention": "Maintain proper plant spacing (15cm x 10cm). Avoid excess nitrogen in late crop stages.",
                "warning": "Always add an agricultural sticker/spreader agent (0.5ml/L) due to waxy tubular onion leaf surface."
            },
            "healthy": {
                "name": "Healthy Onion Crop",
                "scientific_name": "Allium cepa",
                "category": "Healthy",
                "severity": "None",
                "symptoms": ["Erect, cylindrical, dark blue-green leaves with healthy basal bulb swelling."],
                "diagnosis_summary": "Onion crop exhibits healthy foliage and good bulb enlargement.",
                "organic_solution": "Apply vermicompost and bio-potash around root zones.",
                "chemical_treatment": "No chemical intervention needed.",
                "prevention": "Ensure good drainage to prevent neck rot during bulbing.",
                "warning": "Inspect leaf tips after cloudy rains for early purple spots."
            }
        }
    },
    "banana": {
        "crop_name": "Banana",
        "crop_scientific_name": "Musa acuminata",
        "crop_telugu": "అరటి (Banana)",
        "crop_hindi": "केला (Banana)",
        "allowed_diseases": ["sigatoka", "panama disease", "bacterial wilt", "healthy"],
        "diseases": {
            "sigatoka": {
                "name": "Sigatoka Leaf Spot",
                "scientific_name": "Pseudocercospora musae",
                "category": "Fungal Disease",
                "severity": "Moderate",
                "symptoms": [
                    "Small chlorotic yellowish spots parallel to leaf veins turning dark brown",
                    "Centers of older spots become gray with dark brown ring halos"
                ],
                "diagnosis_summary": "Sigatoka leaf spot identified on banana leaf blade.",
                "organic_solution": "Spray mineral oil / petroleum spray oil @ 10ml/liter mixed with Trichoderma viride @ 5g/liter.",
                "chemical_treatment": "Foliar spray of Propiconazole 25% EC @ 1ml/liter or Carbendazim 50% WP @ 1g/liter with mineral oil sticker.",
                "prevention": "Prune and burn severely spotted lower dried leaves. Maintain proper drainage in banana groves.",
                "warning": "Unchecked Sigatoka causes premature fruit ripening and reduces bunch weight drastically."
            },
            "healthy": {
                "name": "Healthy Banana Crop",
                "scientific_name": "Musa acuminata",
                "category": "Healthy",
                "severity": "None",
                "symptoms": ["Large, broad, glossy green leaves with strong central pseudostem and no leaf edge necrosis."],
                "diagnosis_summary": "Banana plant shows healthy expansive foliage and strong pseudostem.",
                "organic_solution": "Apply regular potash and cow dung slurry mulching around the basin.",
                "chemical_treatment": "No chemical intervention required.",
                "prevention": "Desucker periodically to maintain 1 main plant + 1 follower sucker.",
                "warning": "De-leaf senescent lower leaves to maintain good airflow."
            }
        }
    },
    "sugarcane": {
        "crop_name": "Sugarcane",
        "crop_scientific_name": "Saccharum officinarum",
        "crop_telugu": "చెరకు (Sugarcane)",
        "crop_hindi": "गन्ना (Sugarcane)",
        "allowed_diseases": ["red rot", "smut", "wilt", "healthy"],
        "diseases": {
            "red_rot": {
                "name": "Red Rot",
                "scientific_name": "Colletotrichum falcatum",
                "category": "Fungal Disease",
                "severity": "Severe",
                "symptoms": [
                    "Yellowing and drying of crown leaves starting from outer leaves",
                    "Reddening of internal stalk pith tissue with crosswise white patches"
                ],
                "diagnosis_summary": "Red rot detected; a major fungal pathogen causing stalk internal decay.",
                "organic_solution": "Sett treatment with Trichoderma viride @ 10g/liter before planting. Apply bio-agents in furrow.",
                "chemical_treatment": "Sett dip treatment with Carbendazim 50% WP @ 1g/liter before planting. Follow extension safety norms.",
                "prevention": "Use red-rot resistant cane cultivars (e.g. Co 0238, Co 86032). Ensure zero water stagnation.",
                "warning": "Never use seed setts from infected fields; discard and burn diseased stools completely."
            },
            "healthy": {
                "name": "Healthy Sugarcane Crop",
                "scientific_name": "Saccharum officinarum",
                "category": "Healthy",
                "severity": "None",
                "symptoms": ["Tall, sturdy green canes with lush green spindle leaves and strong tillering."],
                "diagnosis_summary": "Sugarcane crop displays excellent vigor and healthy stalk growth.",
                "organic_solution": "Apply trash mulching between rows for moisture retention and weed suppression.",
                "chemical_treatment": "No chemical action required.",
                "prevention": "Earthing up at 90 and 120 days after planting to prevent lodging.",
                "warning": "Monitor spindle leaves for early top shoot borer attacks."
            }
        }
    },
    "mango": {
        "crop_name": "Mango",
        "crop_scientific_name": "Mangifera indica",
        "crop_telugu": "మామిడి (Mango)",
        "crop_hindi": "आम (Mango)",
        "allowed_diseases": ["powdery mildew", "anthracnose", "bacterial black spot", "healthy"],
        "diseases": {
            "anthracnose": {
                "name": "Anthracnose",
                "scientific_name": "Colletotrichum gloeosporioides",
                "category": "Fungal Disease",
                "severity": "Moderate",
                "symptoms": [
                    "Small dark brown necrotic angular spots on tender leaves and panicles",
                    "Blossom blight resulting in premature flower drop and black spots on young fruits"
                ],
                "diagnosis_summary": "Anthracnose identified on mango leaf and blossom tissue.",
                "organic_solution": "Foliar spray of 5% Neem Seed Kernel Extract (NSKE) or Pseudomonas fluorescens @ 5g/liter.",
                "chemical_treatment": "Foliar spray of Copper Oxychloride 50% WP @ 3g/liter or Carbendazim 50% WP @ 1g/liter before flowering. Follow product label guidance.",
                "prevention": "Prune dead criss-cross branches after harvest to allow sun penetration inside canopy.",
                "warning": "Spray before flower panicles open to prevent severe fruit-set loss."
            },
            "healthy": {
                "name": "Healthy Mango Tree",
                "scientific_name": "Mangifera indica",
                "category": "Healthy",
                "severity": "None",
                "symptoms": ["Lush dark green leathery leaves with clean margin and vigorous new bronze flushes."],
                "diagnosis_summary": "Mango tree shows healthy canopy with no signs of fungal spot or hopper damage.",
                "organic_solution": "Apply Farm Yard Manure and tree basin mulching before monsoon onset.",
                "chemical_treatment": "No chemical treatment required.",
                "prevention": "Maintain tree basin ring weed-free.",
                "warning": "Inspect emerging flower panicles during spring for powdery mildew white dust."
            }
        }
    }
}


class ClaudeDiseaseService:
    @classmethod
    def get_api_key(cls):
        """Retrieve Anthropic Claude API Key from environment variables safely."""
        return (
            config('Anthropic_Claude_API_Key', default='') or
            config('ANTHROPIC_API_KEY', default='')
        ).strip()

    @classmethod
    def analyze_crop_leaf(cls, image_file=None, language='en'):
        """
        Primary AI Diagnosis via Anthropic Claude Vision API.
        Sequential evaluation:
        Image Quality -> Plant Check -> Crop ID -> Symptom ID -> Disease ID -> Compatibility Validation -> Treatment.
        
        If Claude is unavailable (timeout, rate limit 429, 500, 529, depleted key),
        gracefully delivers verified agronomy fallback clearly labeled as 'Reference Guidance'.
        """
        api_key = cls.get_api_key()

        if not image_file:
            return {
                "status": "invalid_image",
                "source": "validation",
                "message": "Please upload a clear photograph of a crop leaf, stem, fruit, or affected plant."
            }

        # Validate file size (max 10MB)
        if hasattr(image_file, 'size') and image_file.size > 10 * 1024 * 1024:
            return {
                "status": "invalid_image",
                "source": "validation",
                "message": "Image size exceeds 10MB limit. Please upload a smaller image."
            }

        # Attempt Claude Vision Analysis if API key is present
        if api_key:
            claude_result = cls._call_claude_vision_with_retry(api_key, image_file)
            if claude_result:
                # Run strict Crop-Disease Validation Layer
                validated_result = cls._validate_and_sanitize_claude_response(claude_result)
                if validated_result:
                    return validated_result

        # If Claude failed or key not configured, deliver honest reference fallback
        logger.info("Claude Vision API unavailable or returned uncertain result. Activating Reference Guidance Fallback.")
        return cls._generate_reference_fallback()

    @classmethod
    def _call_claude_vision_with_retry(cls, api_key, image_file, max_retries=2):
        """Calls Claude 3.5 Sonnet / Claude 3 with exponential backoff on transient errors."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            logger.error("Failed to initialize Anthropic client: %s", e)
            return None

        # Prepare base64 image data
        try:
            image_file.seek(0)
            image_bytes = image_file.read()
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            image_file.seek(0)

            content_type = getattr(image_file, 'content_type', 'image/jpeg') or 'image/jpeg'
            if 'png' in content_type:
                media_type = 'image/png'
            elif 'webp' in content_type:
                media_type = 'image/webp'
            elif 'gif' in content_type:
                media_type = 'image/gif'
            else:
                media_type = 'image/jpeg'
        except Exception as e:
            logger.error("Failed to read image bytes: %s", e)
            return None

        system_prompt = (
            "You are RaithuSetu Agricultural Vision Assistant, an expert plant pathologist for Indian agriculture.\n"
            "Analyze the actual uploaded agricultural image carefully.\n\n"
            "CRITICAL ANALYSIS SEQUENCE:\n"
            "1. IMAGE QUALITY: Check if the image is clear, adequately lit, and focused. If blurry/dark/unusable, set status to 'insufficient_image'.\n"
            "2. PLANT CHECK: Determine if a real crop, plant leaf, stem, or fruit is visible. If not a plant (e.g. human face, car, document, pet), set status to 'invalid_image'.\n"
            "3. CROP IDENTIFICATION: Identify what crop/plant is actually visible (e.g. Rice, Tomato, Chilli, Cotton, Maize, Groundnut, Potato, Brinjal, Onion, Banana, Sugarcane, Mango, or Other).\n"
            "   DO NOT assume the crop from filenames or previous inputs.\n"
            "4. SYMPTOM IDENTIFICATION: Look for specific visual lesions, spots, blights, rusts, molds, or insect damage.\n"
            "5. DISEASE DIAGNOSIS: Diagnose the disease ONLY if symptoms match and the disease is biologically compatible with the detected crop.\n"
            "   (Example: Rice leaf showing lesions -> Rice Blast or Bacterial Leaf Blight. NEVER diagnose Tomato Early Blight on Rice!).\n"
            "   If the crop is healthy with no disease, specify 'Healthy [Crop Name]'.\n"
            "6. CONFIDENCE: Set confidence level strictly to 'high', 'medium', or 'low'. Do NOT fabricate percentage decimals.\n"
            "7. SEVERITY: Set severity strictly to 'mild', 'moderate', 'severe', or 'unknown'.\n"
            "8. TREATMENT SAFETY: Provide practical, crop-specific organic and chemical recommendations. Instruct the farmer to follow the product label and local agricultural extension guidance. Do NOT invent pesticide dosages.\n\n"
            "OUTPUT FORMAT:\n"
            "Return ONLY valid JSON (no markdown formatting, no code fences, no conversational text) matching this schema:\n"
            "{\n"
            '  "status": "success" | "uncertain" | "invalid_image" | "insufficient_image",\n'
            '  "image_analysis": {\n'
            '    "is_plant_image": true | false,\n'
            '    "image_quality": "good" | "poor"\n'
            "  },\n"
            '  "crop": {\n'
            '    "name": "Crop Name (e.g. Rice, Tomato, Chilli, Cotton, etc.)",\n'
            '    "scientific_name": "Botanical Binomial Name"\n'
            "  },\n"
            '  "disease": {\n'
            '    "name": "Disease Name (or Healthy Crop)",\n'
            '    "scientific_name": "Pathogen Binomial Name",\n'
            '    "category": "Fungal disease" | "Bacterial disease" | "Viral disease" | "Pest damage" | "Healthy" | "Nutrient deficiency"\n'
            "  },\n"
            '  "confidence": {\n'
            '    "level": "high" | "medium" | "low"\n'
            "  },\n"
            '  "severity": {\n'
            '    "level": "mild" | "moderate" | "severe" | "unknown"\n'
            "  },\n"
            '  "symptoms": ["Symptom 1", "Symptom 2"],\n'
            '  "diagnosis_summary": "Short 1-2 sentence farmer-friendly diagnosis explanation.",\n'
            '  "organic_remedy": {\n'
            '    "recommendations": ["Organic remedy 1", "Organic remedy 2"]\n'
            "  },\n"
            '  "chemical_treatment": {\n'
            '    "recommendations": ["Chemical remedy 1 (follow product label)", "Chemical remedy 2"]\n'
            "  },\n"
            '  "prevention": ["Prevention tip 1", "Prevention tip 2"],\n'
            '  "warning": "Advisory warning message regarding safe application and weather precautions."\n'
            "}"
        )

        user_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_b64
                }
            },
            {
                "type": "text",
                "text": "Please analyze this uploaded agricultural image following the system instructions and return the structured JSON diagnosis."
            }
        ]

        # Model selection: Claude 3.5 Sonnet / Claude 3 Haiku
        models_to_try = [
            "claude-3-5-sonnet-20241022",
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229"
        ]

        for attempt in range(max_retries + 1):
            model_name = models_to_try[min(attempt, len(models_to_try) - 1)]
            try:
                logger.info("Calling Claude Vision API (model: %s, attempt: %d)...", model_name, attempt + 1)
                response = client.messages.create(
                    model=model_name,
                    max_tokens=1200,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_content}]
                )
                response_text = response.content[0].text.strip()
                
                # Parse JSON
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    parsed["source"] = "claude_vision"
                    return parsed
                else:
                    logger.warning("Claude response did not contain valid JSON: %s", response_text[:200])

            except Exception as err:
                err_str = str(err).lower()
                logger.warning("Claude API attempt %d failed: %s", attempt + 1, err)

                # If Authentication or Credit Balance Error, do not retry
                if any(k in err_str for k in ["401", "authentication", "invalid_api_key", "credit balance", "plans & billing", "permission"]):
                    logger.error("Claude API non-retryable account/auth error: %s", err)
                    return None

                # Transient rate-limit / server errors: backoff & retry
                if attempt < max_retries:
                    backoff = 0.5 * (2 ** attempt)
                    time.sleep(backoff)
                else:
                    return None

        return None

    @classmethod
    def _validate_and_sanitize_claude_response(cls, data):
        """
        Crop-Disease Validation Layer:
        Validates whether the detected disease is biologically compatible with the detected crop.
        Rejects incompatible pairings (e.g. Rice + Early Blight) to eliminate misdiagnoses.
        """
        if not isinstance(data, dict):
            return None

        status_val = data.get("status", "success")
        if status_val in ["invalid_image", "insufficient_image"]:
            return {
                "status": status_val,
                "source": "claude_vision",
                "message": (
                    "Please upload a clear photograph of a crop leaf, stem, fruit, or affected plant."
                    if status_val == "invalid_image" else
                    "The image is not clear enough for reliable diagnosis. Please upload a closer photograph in natural daylight."
                )
            }

        crop_info = data.get("crop", {})
        disease_info = data.get("disease", {})
        crop_name = crop_info.get("name", "").strip() if isinstance(crop_info, dict) else str(crop_info)
        disease_name = disease_info.get("name", "").strip() if isinstance(disease_info, dict) else str(disease_info)

        crop_key = cls._match_crop_key(crop_name)
        disease_lower = disease_name.lower()

        # Check compatibility if crop is recognized
        if crop_key and crop_key in INDIAN_AGRONOMY_FALLBACK_DB:
            allowed = INDIAN_AGRONOMY_FALLBACK_DB[crop_key]["allowed_diseases"]
            is_compatible = any(allow in disease_lower for allow in allowed)
            
            # If Claude paired an incompatible disease (e.g. Rice + Tomato Early Blight)
            if not is_compatible and "healthy" not in disease_lower:
                logger.warning(
                    "Crop-Disease Incompatibility Detected: Crop '%s' paired with incompatible disease '%s'. Rejecting.",
                    crop_name, disease_name
                )
                return {
                    "status": "uncertain",
                    "source": "claude_vision",
                    "crop": {
                        "name": crop_name or INDIAN_AGRONOMY_FALLBACK_DB[crop_key]["crop_name"],
                        "scientific_name": crop_info.get("scientific_name") or INDIAN_AGRONOMY_FALLBACK_DB[crop_key]["crop_scientific_name"]
                    },
                    "disease": {
                        "name": "Uncertain / Unconfirmed Pathology",
                        "scientific_name": "Pathogen undetermined",
                        "category": "Uncertain"
                    },
                    "confidence": {"level": "low"},
                    "severity": {"level": "unknown"},
                    "symptoms": data.get("symptoms") or ["Atypical foliar symptoms not definitively matching standard profiles."],
                    "diagnosis_summary": f"The plant was identified as {crop_name}, but visual symptoms do not reliably match known diseases for this crop. Please consult an agricultural extension officer.",
                    "organic_remedy": {
                        "recommendations": ["Apply preventive Neem Oil (3-5 ml/L) or Trichoderma bio-fungicide while monitoring progress."]
                    },
                    "chemical_treatment": {
                        "recommendations": ["Avoid unverified chemical spraying until the symptom is confirmed by a qualified agronomist."]
                    },
                    "prevention": [
                        "Maintain balanced plant nutrition and regular field sanitation.",
                        "Inspect new foliage weekly for emerging distinct symptoms."
                    ],
                    "warning": "AI diagnosis is advisory. Do not apply heavy chemical sprays without expert confirmation."
                }

        # Normalize structured fields
        confidence_level = data.get("confidence", {}).get("level", "high") if isinstance(data.get("confidence"), dict) else "high"
        if confidence_level not in ["high", "medium", "low"]:
            confidence_level = "medium"

        severity_level = data.get("severity", {}).get("level", "moderate") if isinstance(data.get("severity"), dict) else "moderate"
        if severity_level not in ["mild", "moderate", "severe", "unknown"]:
            severity_level = "moderate"

        organic_recs = []
        if isinstance(data.get("organic_remedy"), dict):
            organic_recs = data.get("organic_remedy", {}).get("recommendations", [])
        elif isinstance(data.get("organic_remedy"), list):
            organic_recs = data.get("organic_remedy")
        elif isinstance(data.get("organicSolution"), str):
            organic_recs = [data.get("organicSolution")]

        chemical_recs = []
        if isinstance(data.get("chemical_treatment"), dict):
            chemical_recs = data.get("chemical_treatment", {}).get("recommendations", [])
        elif isinstance(data.get("chemical_treatment"), list):
            chemical_recs = data.get("chemical_treatment")
        elif isinstance(data.get("chemicalSolution"), str):
            chemical_recs = [data.get("chemicalSolution")]

        prevention_recs = data.get("prevention") or []
        if isinstance(prevention_recs, str):
            prevention_recs = [prevention_recs]

        symptoms_list = data.get("symptoms") or []
        if isinstance(symptoms_list, str):
            symptoms_list = [symptoms_list]

        return {
            "status": "success",
            "source": "claude_vision",
            "crop": {
                "name": crop_name or "Detected Crop",
                "scientific_name": crop_info.get("scientific_name", "") if isinstance(crop_info, dict) else ""
            },
            "disease": {
                "name": disease_name or "Plant Condition",
                "scientific_name": disease_info.get("scientific_name", "") if isinstance(disease_info, dict) else "",
                "category": disease_info.get("category", "Foliar Pathology") if isinstance(disease_info, dict) else "Foliar Pathology"
            },
            "confidence": {
                "level": confidence_level
            },
            "severity": {
                "level": severity_level
            },
            "symptoms": symptoms_list,
            "diagnosis_summary": data.get("diagnosis_summary", f"{disease_name} observed on {crop_name} foliage."),
            "organic_remedy": {
                "recommendations": organic_recs or ["Apply cold-pressed Neem Oil (5ml/L) as a bio-protective measure."]
            },
            "chemical_treatment": {
                "recommendations": chemical_recs or ["Follow product label and local agricultural extension guidance for approved fungicides/insecticides."]
            },
            "prevention": prevention_recs or ["Maintain proper field spacing, balanced irrigation, and crop rotation."],
            "warning": data.get("warning") or "AI-based diagnosis is advisory. Always follow product labels and wear protective gear when applying agricultural inputs."
        }

    @classmethod
    def _match_crop_key(cls, text):
        """Matches crop name string to internal crop key."""
        t = text.lower()
        if any(w in t for w in ["rice", "paddy", "oryza", "వరి", "धान"]):
            return "rice"
        if any(w in t for w in ["tomato", "lycopersicon", "టమాటా", "टमाटर"]):
            return "tomato"
        if any(w in t for w in ["chilli", "chili", "pepper", "capsicum", "మిరప", "మిర్చి", "मिर्च"]):
            return "chilli"
        if any(w in t for w in ["cotton", "gossypium", "పత్తి", "కపాస్", "कपास"]):
            return "cotton"
        if any(w in t for w in ["maize", "corn", "zea", "మొక్కజొన్న", "మక్కా", "मक्का"]):
            return "maize"
        if any(w in t for w in ["groundnut", "peanut", "arachis", "వేరుశనగ", "मूंगफली"]):
            return "groundnut"
        if any(w in t for w in ["potato", "బంగాళాదుంప", "आलू"]):
            return "potato"
        if any(w in t for w in ["brinjal", "eggplant", "aubergine", "వంకాయ", "बैंगन"]):
            return "brinjal"
        if any(w in t for w in ["onion", "allium", "ఉల్లిపాయ", "प्याज"]):
            return "onion"
        if any(w in t for w in ["banana", "musa", "అరటి", "केला"]):
            return "banana"
        if any(w in t for w in ["sugarcane", "saccharum", "చెరకు", "गन्ना"]):
            return "sugarcane"
        if any(w in t for w in ["mango", "mangifera", "మామిడి", "आम"]):
            return "mango"
        return None

    @classmethod
    def _generate_reference_fallback(cls):
        """
        Delivers clean, honest agricultural reference guidance when Claude is unavailable.
        Clearly labels source as 'reference_knowledge_base' and status as 'fallback'.
        NEVER fakes a visual diagnosis or confidence percentage.
        """
        # Default reference to Rice / Paddy (the primary staple crop for RaithuSetu)
        ref_crop = INDIAN_AGRONOMY_FALLBACK_DB["rice"]
        ref_disease = ref_crop["diseases"]["bacterial_leaf_blight"]

        return {
            "status": "fallback",
            "source": "reference_knowledge_base",
            "message": "AI image analysis is temporarily unavailable. Showing agricultural reference guidance.",
            "crop": {
                "name": ref_crop["crop_name"],
                "scientific_name": ref_crop["crop_scientific_name"]
            },
            "disease": {
                "name": ref_disease["name"],
                "scientific_name": ref_disease["scientific_name"],
                "category": ref_disease["category"]
            },
            "confidence": {
                "level": "low"
            },
            "severity": {
                "level": ref_disease["severity"].lower()
            },
            "symptoms": ref_disease["symptoms"],
            "diagnosis_summary": ref_disease["diagnosis_summary"],
            "organic_remedy": {
                "recommendations": [ref_disease["organic_solution"]]
            },
            "chemical_treatment": {
                "recommendations": [ref_disease["chemical_treatment"]]
            },
            "prevention": [ref_disease["prevention"]],
            "warning": "Reference guidance only. AI image analysis was unavailable for this scan. Please consult your local Krishi Vigyan Kendra (KVK) or extension officer."
        }
