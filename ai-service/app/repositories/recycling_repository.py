from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.recycling import (
    RecyclingCategory,
    RecyclingStep,
    RecyclingWarning,
    RecyclingRule,
    RecyclingDisposalMethod,
    RecyclabilityStatusEnum,
    WarningSeverityEnum,
    RuleTypeEnum
)

# Comprehensive, authoritative circular economy recycling knowledge base
DEFAULT_RECYCLING_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "name": "Plastic Bottles & Rigid Containers",
        "slug": "plastic-bottles-containers",
        "icon": "🧴",
        "description": "Rigid plastic bottles, jars, tubs, and jugs made of PET (1), HDPE (2), or PP (5).",
        "recyclability_status": RecyclabilityStatusEnum.RECYCLABLE,
        "preparation": [
            "Empty liquids and residues completely",
            "Lightly rinse with greywater if food or sugary residue remains",
            "Crush or flatten bottle to save bin space",
            "Leave plastic caps on (most modern optical MRFs sort attached caps)"
        ],
        "steps": [
            {"step_number": 1, "title": "Identify & Empty", "description": "Verify the item is rigid plastic (e.g. water bottle, shampoo container). Empty all liquid or contents completely."},
            {"step_number": 2, "title": "Rinse Clean", "description": "Give a quick rinse if food, oil, or sugar remains. It does not need to be sterilized, just free of excess residue."},
            {"step_number": 3, "title": "Separate Non-Plastic Parts", "description": "Remove foil seals, pump dispensers with metal springs, and non-recyclable tamper bands."},
            {"step_number": 4, "title": "Flatten & Keep Dry", "description": "Crush plastic bottles vertically or horizontally to conserve collection volume and prevent rolling."},
            {"step_number": 5, "title": "Segregate to Dry Bin", "description": "Place directly into your designated Blue / Dry Recyclables bin. Do not bag recyclables in black trash bags."}
        ],
        "warnings": [
            {"title": "No Soft Plastic / Film Mixing", "description": "Do not mix soft plastic bags, chip wrappers, or multi-layer pouches into rigid plastic bins as they jam sorting machinery.", "severity": WarningSeverityEnum.CAUTION},
            {"title": "No Chemical Residues", "description": "Containers previously holding motor oil, pesticides, or industrial solvents require hazardous waste processing and must never go in standard recycling.", "severity": WarningSeverityEnum.WARNING}
        ],
        "rules": [
            {"rule_type": RuleTypeEnum.DO, "title": "Keep it Clean & Dry", "description": "Ensure containers are empty and reasonably dry before binning.", "priority": 1},
            {"rule_type": RuleTypeEnum.DO_NOT, "title": "Do Not Bag Recyclables", "description": "Keep items loose in your recycling container unless your local municipality specifically requests clear bags.", "priority": 2},
            {"rule_type": RuleTypeEnum.DO_NOT, "title": "Do Not Recycle Dirty Styrofoam", "description": "Expanded polystyrene (Styrofoam) is generally not accepted in curbside blue bins.", "priority": 3}
        ],
        "disposal": {
            "primary_route": "Curbside Dry Recycling / Blue Bin",
            "stream_name": "Dry Recyclables (Rigid Polymers)",
            "bin_color": "Blue Bin",
            "special_notes": "PET & HDPE have highest domestic circular value and generate official EPR credits.",
            "local_guidance_notes": "Local municipal collection rules may vary by region. Please consult your local municipal authority."
        }
    },
    {
        "name": "Paper & Cardboard Packaging",
        "slug": "paper-cardboard",
        "icon": "📦",
        "description": "Cardboard boxes, corrugated cartons, office paper, notebooks, examination boards, and clean paperboard.",
        "recyclability_status": RecyclabilityStatusEnum.RECYCLABLE,
        "preparation": [
            "Keep clean and dry at all times",
            "Flatten all cardboard boxes",
            "Remove plastic tape, bubble wrap, and thermocol inserts",
            "Separate heavily soiled, oily, or food-stained sections"
        ],
        "steps": [
            {"step_number": 1, "title": "Inspect for Cleanliness", "description": "Ensure paper is dry and uncontaminated. Food grease, oil, and liquid break down paper pulp fibers permanently."},
            {"step_number": 2, "title": "Remove Non-Paper Elements", "description": "Strip heavy plastic packing tape, metal clips, spiral bindings, and plastic window films where possible."},
            {"step_number": 3, "title": "Flatten & Bundle", "description": "Break down cardboard cartons flat to optimize storage and transport efficiency."},
            {"step_number": 4, "title": "Segregate to Dry Bin", "description": "Keep alongside clean dry recyclables in a covered area protected from rain and moisture."}
        ],
        "warnings": [
            {"title": "Greasy & Food-Stained Paper is Not Recyclable", "description": "Greasy pizza box bottoms, used paper towels, and oil-soaked tissues cannot be recycled as paper; divert them to organic composting.", "severity": WarningSeverityEnum.CAUTION},
            {"title": "Avoid Wetting Cardboard", "description": "Wet paper degrades pulp yield and molds quickly, causing entire bales to be rejected at recycling mills.", "severity": WarningSeverityEnum.INFO}
        ],
        "rules": [
            {"rule_type": RuleTypeEnum.DO, "title": "Flatten Corrugated Boxes", "description": "Always collapse delivery boxes flat before disposal.", "priority": 1},
            {"rule_type": RuleTypeEnum.DO_NOT, "title": "Do Not Recycle Waxed / Thermal Paper", "description": "Receipts (thermal BPA paper) and wax-coated beverage cartons require specialized hydropulping facilities.", "priority": 2}
        ],
        "disposal": {
            "primary_route": "Dry Paper & Packaging Stream",
            "stream_name": "Paper & Fiber Recovery",
            "bin_color": "Blue / Dry Bin",
            "special_notes": "High circularity; recyclable up to 5-7 times into fresh paperboard.",
            "local_guidance_notes": "Local municipal collection rules may vary by region. Please consult your local municipal authority."
        }
    },
    {
        "name": "Glass Bottles & Jars",
        "slug": "glass-bottles-jars",
        "icon": "🍾",
        "description": "Clear, green, and amber glass bottles, condiment jars, and beverage containers.",
        "recyclability_status": RecyclabilityStatusEnum.RECYCLABLE,
        "preparation": [
            "Empty liquids and rinse out residual food/drink",
            "Remove metal or plastic caps and lids",
            "Inspect for cracks or breakages before handling"
        ],
        "steps": [
            {"step_number": 1, "title": "Empty & Rinse", "description": "Pour out all liquid contents and rinse food jars with water."},
            {"step_number": 2, "title": "Separate Caps & Corks", "description": "Remove metal twist caps, corks, and foil necks (metal caps can be recycled with metals)."},
            {"step_number": 3, "title": "Keep Intact & Unbroken", "description": "Place whole glass containers into the recycling stream gently to avoid shattering."},
            {"step_number": 4, "title": "Segregate into Glass / Dry Stream", "description": "Deposit into designated glass drop-off bin or municipal dry recyclable stream."}
        ],
        "warnings": [
            {"title": "Handle Broken Glass With Extreme Care", "description": "Never handle broken glass with bare hands. Wrap shattered pieces securely in newspaper and label clearly before disposal to protect sanitation workers.", "severity": WarningSeverityEnum.WARNING},
            {"title": "Do Not Mix Ceramics or Window Glass", "description": "Mirrors, cookware (Pyrex), light bulbs, and window panes have different melting temperatures and ruin container glass cullet batches.", "severity": WarningSeverityEnum.CAUTION}
        ],
        "rules": [
            {"rule_type": RuleTypeEnum.DO, "title": "Rinse Jars Thoroughly", "description": "Eliminate organic traces to prevent odors and insect attraction.", "priority": 1},
            {"rule_type": RuleTypeEnum.DO_NOT, "title": "Do Not Mix Pyrex / Oven Glass", "description": "Borosilicate cookware cannot be remelted with soda-lime packaging glass.", "priority": 2}
        ],
        "disposal": {
            "primary_route": "Glass Container Recycling Stream",
            "stream_name": "Inorganic Glass Packaging",
            "bin_color": "Glass Bin / Blue Dry Bin",
            "special_notes": "100% infinitely recyclable without any loss in purity or quality.",
            "local_guidance_notes": "Local municipal collection rules may vary by region. Please consult your local municipal authority."
        }
    },
    {
        "name": "Metal Cans & Aluminium Packaging",
        "slug": "metal-cans-packaging",
        "icon": "🥫",
        "description": "Aluminium beverage cans, food tin cans, metal jar lids, and clean aluminum foil.",
        "recyclability_status": RecyclabilityStatusEnum.RECYCLABLE,
        "preparation": [
            "Empty drink or food contents completely",
            "Rinse out food tins",
            "Crush aluminium cans to save bin volume",
            "Do not remove pop tabs from beverage cans"
        ],
        "steps": [
            {"step_number": 1, "title": "Empty & Light Rinse", "description": "Ensure no food residue or liquid remains inside cans or tins."},
            {"step_number": 2, "title": "Crush Aluminium", "description": "Crush soda cans to save collection space."},
            {"step_number": 3, "title": "Include Metal Lids", "description": "Metal lids can be placed inside tin cans or crimped closed."},
            {"step_number": 4, "title": "Deposit in Dry / Metal Bin", "description": "Place with dry recyclables for magnetic and eddy-current metal sorting."}
        ],
        "warnings": [
            {"title": "Aerosol Cans Must Be Completely Empty", "description": "Pressurized spray cans (deodorants, spray paint) can explode under compaction. Ensure they are completely depressurized before recycling.", "severity": WarningSeverityEnum.CAUTION},
            {"title": "Beware of Sharp Edges", "description": "Opened food cans can have razor-sharp lids. Push lids inside the can to prevent cuts.", "severity": WarningSeverityEnum.INFO}
        ],
        "rules": [
            {"rule_type": RuleTypeEnum.DO, "title": "Recycle Clean Aluminium", "description": "Aluminium requires 95% less energy to recycle than primary smelting from bauxite.", "priority": 1},
            {"rule_type": RuleTypeEnum.DO_NOT, "title": "Do Not Recycle Dirty Foil", "description": "Foil covered in burnt food or heavy grease should be wiped clean or discarded.", "priority": 2}
        ],
        "disposal": {
            "primary_route": "Metal Recycling & Smelting Stream",
            "stream_name": "Ferrous & Non-Ferrous Metals",
            "bin_color": "Blue / Metal Bin",
            "special_notes": "Extremely high circular value; aluminum cans return to shelves in under 60 days.",
            "local_guidance_notes": "Local municipal collection rules may vary by region. Please consult your local municipal authority."
        }
    },
    {
        "name": "Electronic Waste (E-Waste)",
        "slug": "e-waste",
        "icon": "💻",
        "description": "Smartphones, laptops, cables, chargers, earphones, remotes, clocks, keyboards, and consumer electronics.",
        "recyclability_status": RecyclabilityStatusEnum.SPECIAL_HANDLING,
        "preparation": [
            "Back up personal data and cloud storage",
            "Sign out of digital accounts (Apple ID, Google, Banking)",
            "Perform factory reset to wipe device memory",
            "Detach external batteries if removable",
            "Bundle charging cables neatly"
        ],
        "steps": [
            {"step_number": 1, "title": "Data Safety & Backup", "description": "Back up your personal photos, files, and contacts. Sign out of all accounts and perform a secure factory reset."},
            {"step_number": 2, "title": "Remove SIM & Memory Cards", "description": "Eject SIM trays and remove micro-SD memory cards before handover."},
            {"step_number": 3, "title": "Separate Removable Batteries", "description": "If the device has a detachable lithium battery, remove it and store separately."},
            {"step_number": 4, "title": "Keep Device Intact", "description": "Do not dismantle circuits, crush screens, or burn casing. Keep devices intact for component recovery."},
            {"step_number": 5, "title": "Hand Over to Authorized E-Waste Collector", "description": "Drop off at authorized municipal e-waste collection bins, producer take-back kiosks, or licensed recycler drop points."}
        ],
        "warnings": [
            {"title": "Never Throw in General Trash", "description": "Electronics contain toxic heavy metals (lead, mercury, cadmium) that leach into groundwater if landfilled.", "severity": WarningSeverityEnum.WARNING},
            {"title": "Do Not Puncture Lithium Batteries", "description": "Puncturing internal lithium polymer batteries causes thermal runaway fires.", "severity": WarningSeverityEnum.DANGER}
        ],
        "rules": [
            {"rule_type": RuleTypeEnum.DATA_SAFETY, "title": "Protect Personal Privacy", "description": "Always perform device wiping and factory reset prior to recycling.", "priority": 1},
            {"rule_type": RuleTypeEnum.SPECIAL_HANDLING, "title": "Use Authorized Channels Only", "description": "Deliver to certified E-Waste Management Rule (EPR) authorized collection centers.", "priority": 2},
            {"rule_type": RuleTypeEnum.DO_NOT, "title": "Never Burn or Incinerate", "description": "Burning circuit boards and cables releases deadly dioxins and furans.", "priority": 3}
        ],
        "disposal": {
            "primary_route": "Authorized E-Waste Takeback & Kiosks",
            "stream_name": "Electronic Waste Recovery Stream",
            "bin_color": "Designated E-Waste Drop Box",
            "special_notes": "Valuable precious metals (gold, copper, silver) recovered under strict environmental controls.",
            "local_guidance_notes": "Local municipal collection rules may vary by region. Please consult your local municipal authority."
        }
    },
    {
        "name": "Household Batteries & Power Cells",
        "slug": "batteries",
        "icon": "🔋",
        "description": "Alkaline AA/AAA, Lithium-ion (Li-ion), Button cells, rechargeable power banks, and lead batteries.",
        "recyclability_status": RecyclabilityStatusEnum.SPECIAL_HANDLING,
        "preparation": [
            "Tape terminal ends with non-conductive electrical/clear tape",
            "Inspect for swelling, leaks, corrosion, or overheating",
            "Store in a cool, dry, non-metallic container"
        ],
        "steps": [
            {"step_number": 1, "title": "Terminal Taping", "description": "Apply a strip of tape over exposed positive/negative terminals of 9V and lithium batteries to prevent short-circuit sparks."},
            {"step_number": 2, "title": "Isolate Damaged Cells", "description": "If a battery is swollen or leaking, place in sand or baking soda in a sealed container immediately."},
            {"step_number": 3, "title": "Do Not Puncture or Crush", "description": "Never attempt to open, hammer, or incinerate any battery cell."},
            {"step_number": 4, "title": "Take to Battery Collection Kiosk", "description": "Drop off at dedicated battery recycling boxes located in electronics stores, supermarkets, or municipal centers."}
        ],
        "warnings": [
            {"title": "High Fire & Explosion Hazard", "description": "Lithium batteries crushed in garbage trucks or landfill compactors cause severe facility fires.", "severity": WarningSeverityEnum.DANGER},
            {"title": "Corrosive Chemical Leakage", "description": "Avoid touching leaking battery acid with bare skin. Use protective gloves.", "severity": WarningSeverityEnum.WARNING}
        ],
        "rules": [
            {"rule_type": RuleTypeEnum.SPECIAL_HANDLING, "title": "Tape Terminals Before Storing", "description": "Prevents accidental discharge and electrical friction fires.", "priority": 1},
            {"rule_type": RuleTypeEnum.DO_NOT, "title": "Never Dispose in Regular Bins", "description": "Batteries are classified as hazardous waste in municipal bylaws.", "priority": 2}
        ],
        "disposal": {
            "primary_route": "Specialized Battery Recycling Drop Points",
            "stream_name": "Hazardous Battery Reclamation",
            "bin_color": "Battery Drop Kiosk",
            "special_notes": "Critical minerals (Lithium, Cobalt, Nickel, Zinc) recovered for circular battery production.",
            "local_guidance_notes": "Local municipal collection rules may vary by region. Please consult your local municipal authority."
        }
    },
    {
        "name": "Organic & Kitchen Wet Waste",
        "slug": "organic-wet-waste",
        "icon": "🍎",
        "description": "Vegetable peels, fruit scraps, leftover food, tea leaves, coffee grounds, garden clippings, and eggshells.",
        "recyclability_status": RecyclabilityStatusEnum.RECYCLABLE,
        "preparation": [
            "Keep separate from all plastics, wrappers, and packaging",
            "Drain excess free liquid and gravy",
            "Do not include plastic bags or rubber bands"
        ],
        "steps": [
            {"step_number": 1, "title": "Segregate from Packaging", "description": "Remove fruit stickers, plastic wraps, rubber bands, and staples from tea bags."},
            {"step_number": 2, "title": "Drain Liquids", "description": "Drain excess broth/gravy to minimize odors and ease processing."},
            {"step_number": 3, "title": "Home Composting / Wet Bin", "description": "Deposit into home aerobic compost bin, vermicompost bin, or municipal Green Wet Waste Bin."},
            {"step_number": 4, "title": "Collect Daily", "description": "Cover wet waste container tightly and empty daily to maintain household hygiene."}
        ],
        "warnings": [
            {"title": "Never Mix with Dry Recyclables", "description": "Wet organic waste contaminates paper, cardboard, and plastics, rendering them unrecyclable.", "severity": WarningSeverityEnum.CAUTION},
            {"title": "No Plastic Liners in Compost", "description": "Ordinary plastic grocery bags will not decompose and ruin finished compost batches.", "severity": WarningSeverityEnum.INFO}
        ],
        "rules": [
            {"rule_type": RuleTypeEnum.DO, "title": "Compost at Source", "description": "Home composting reduces landfill methane emissions by over 80%.", "priority": 1},
            {"rule_type": RuleTypeEnum.DO_NOT, "title": "Do Not Add Meat / Dairy to Open Piles", "description": "In simple backyard composters, avoid heavy dairy or animal bones to prevent pests.", "priority": 2}
        ],
        "disposal": {
            "primary_route": "Home Composter / Municipal Green Bin",
            "stream_name": "Biodegradable Organic Stream",
            "bin_color": "Green Bin",
            "special_notes": "Converts naturally into nutrient-rich soil humus and biogas.",
            "local_guidance_notes": "Local municipal collection rules may vary by region. Please consult your local municipal authority."
        }
    },
    {
        "name": "Textiles, Clothing & Fabrics",
        "slug": "textiles-fabrics",
        "icon": "👕",
        "description": "Worn apparel, bed linens, towels, fabric scraps, shoes, backpacks, and household curtains.",
        "recyclability_status": RecyclabilityStatusEnum.CONDITIONALLY_RECYCLABLE,
        "preparation": [
            "Wash and dry cleanly before donation",
            "Mend small tears or loose buttons if usable",
            "Separate wearable clothes from shreddable rags"
        ],
        "steps": [
            {"step_number": 1, "title": "Evaluate Condition (Hierarchy)", "description": "Prioritize: 1. Reuse/Wear → 2. Repair → 3. Donate → 4. Repurpose/Rags → 5. Textile Fiber Recycling."},
            {"step_number": 2, "title": "Clean & Dry", "description": "Ensure garments are freshly washed and completely dry to prevent mold during storage."},
            {"step_number": 3, "title": "Donate Usable Clothing", "description": "Give wearable garments to local charity drives, community shelters, or thrift programs."},
            {"step_number": 4, "title": "Textile Drop-off for Worn Items", "description": "Drop unwearable or stained fabrics at brand take-back programs or municipal textile recovery centers."}
        ],
        "warnings": [
            {"title": "Keep Textiles Dry", "description": "Damp clothing stored in collection bins will mildew and rot adjacent fabrics.", "severity": WarningSeverityEnum.INFO}
        ],
        "rules": [
            {"rule_type": RuleTypeEnum.DO, "title": "Pair Shoes Together", "description": "Tie shoelaces together so pairs do not get separated during sorting.", "priority": 1},
            {"rule_type": RuleTypeEnum.DO_NOT, "title": "Do Not Trash Wearable Clothes", "description": "Extend garment lifespans through donation or upcycling before considering disposal.", "priority": 2}
        ],
        "disposal": {
            "primary_route": "Charity Donation / Brand Take-Back Kiosk",
            "stream_name": "Textile Circularity Stream",
            "bin_color": "Textile Drop Bin",
            "special_notes": "Synthetics like polyester and blended fibers are shredded into insulation and industrial wiping rags.",
            "local_guidance_notes": "Local municipal collection rules may vary by region. Please consult your local municipal authority."
        }
    },
    {
        "name": "Household Hazardous Waste & Chemicals",
        "slug": "hazardous-waste",
        "icon": "☣",
        "description": "Paints, thinners, chemical cleaners, pesticides, motor oil, medical waste, and fluorescent tubes.",
        "recyclability_status": RecyclabilityStatusEnum.SPECIAL_HANDLING,
        "preparation": [
            "Keep in original container with legible warning labels",
            "Ensure lids and caps are tightly sealed",
            "Never mix different chemical products together"
        ],
        "steps": [
            {"step_number": 1, "title": "Retain Original Packaging", "description": "Keep chemicals in their original containers with hazard labels visible so handlers know the chemical composition."},
            {"step_number": 2, "title": "Secure Container Caps", "description": "Tighten caps securely to avoid volatile fumes and liquid spills during storage."},
            {"step_number": 3, "title": "Store Safely Away from Children", "description": "Keep in a ventilated, secure area out of reach of pets and children."},
            {"step_number": 4, "title": "Deliver to Hazardous Waste Depot", "description": "Transport carefully to an authorized municipal Hazardous Household Waste (HHW) collection event or depot."}
        ],
        "warnings": [
            {"title": "Never Pour Down Sinks or Drains", "description": "Chemicals poured into storm drains poison rivers, destroy septic bacteria, and contaminate drinking water.", "severity": WarningSeverityEnum.DANGER},
            {"title": "Never Mix Cleaning Products", "description": "Mixing bleach with ammonia or acids generates lethal chloramine/chlorine gases.", "severity": WarningSeverityEnum.DANGER}
        ],
        "rules": [
            {"rule_type": RuleTypeEnum.SPECIAL_HANDLING, "title": "Dedicated Hazardous Depot Handover", "description": "Must never enter standard residential municipal bins.", "priority": 1},
            {"rule_type": RuleTypeEnum.DO_NOT, "title": "Do Not Incinerate or Burn", "description": "Chemical containers release toxic carcinogenic gases upon combustion.", "priority": 2}
        ],
        "disposal": {
            "primary_route": "Municipal Hazardous Waste Drop-Off Center",
            "stream_name": "Regulated Hazardous Household Waste (HHW)",
            "bin_color": "Red / Hazardous Storage",
            "special_notes": "Requires specialized neutralization, high-temperature incineration, or safe chemical reclamation.",
            "local_guidance_notes": "Local municipal collection rules may vary by region. Please consult your local municipal authority."
        }
    },
    {
        "name": "Wood, Bulky Items & Furniture",
        "slug": "wood-bulky-furniture",
        "icon": "🪵",
        "description": "Wooden furniture, chairs, tables, desks, bookshelves, cabinetry, pallets, and solid bulky timber items.",
        "recyclability_status": RecyclabilityStatusEnum.CONDITIONALLY_RECYCLABLE,
        "preparation": [
            "Assess structural condition for donation, resale, or refurbishment",
            "Disassemble large items to remove non-wood hardware (screws, nails, glass, cushions)",
            "Keep unpainted and untreated wood separate from treated/varnished timber",
            "Keep dry to prevent rotting and fungal decay prior to collection"
        ],
        "steps": [
            {"step_number": 1, "title": "Check Reuse Viability", "description": "If furniture is intact or easily repairable, prioritize donation, charity collection, or local reuse platforms before recycling."},
            {"step_number": 2, "title": "Dismantle & Remove Hardware", "description": "Unscrew metal hinges, brackets, glass tabletops, and fabric cushions to isolate clean timber."},
            {"step_number": 3, "title": "Sort by Wood Type", "description": "Distinguish untreated solid wood (high circular value for chipping/mulch/pellets) from treated wood, MDF, and particle board."},
            {"step_number": 4, "title": "Schedule Bulky Pickup or Depot Drop-Off", "description": "Book a scheduled municipal bulky waste collection or deliver directly to a municipal civic amenity / recycling center."}
        ],
        "warnings": [
            {"title": "Do Not Place in Standard Curbside Bins", "description": "Bulky wooden items and furniture cannot be compacted by standard residential collection trucks and will damage bin lifters.", "severity": WarningSeverityEnum.WARNING},
            {"title": "Treated Wood is Not for Home Burning", "description": "Pressure-treated, creosote, or painted wood releases toxic arsenic and chemical fumes if burned in fireplaces or open fires.", "severity": WarningSeverityEnum.DANGER}
        ],
        "rules": [
            {"rule_type": RuleTypeEnum.DO, "title": "Prioritize Repair & Upcycling", "description": "Restoring, sanding, or re-staining wooden furniture dramatically extends lifecycle.", "priority": 1},
            {"rule_type": RuleTypeEnum.DO_NOT, "title": "Do Not Dump on Public Roadsides", "description": "Illegal fly-tipping incurs heavy municipal penalties and damages local ecosystems.", "priority": 2}
        ],
        "disposal": {
            "primary_route": "Municipal Bulky Waste Collection / Civic Amenity Site",
            "stream_name": "Timber & Bulky Household Goods",
            "bin_color": "Bulky Waste Collection / Wood Depot",
            "special_notes": "Untreated solid wood is chipped into landscape mulch, animal bedding, or particleboard furnish.",
            "local_guidance_notes": "Local municipal collection rules may vary by region. Please consult your local municipal authority."
        }
    }
]


class RecyclingRepository:
    def __init__(self, db: Session):
        self.db = db

    def seed_default_knowledge_if_empty(self):
        """
        Seeds the database with verified recycling categories, steps, warnings, and rules if missing.
        """
        for item in DEFAULT_RECYCLING_KNOWLEDGE_BASE:
            existing = self.db.query(RecyclingCategory).filter(RecyclingCategory.slug == item["slug"]).first()
            if existing:
                continue

            cat = RecyclingCategory(
                name=item["name"],
                slug=item["slug"],
                icon=item["icon"],
                description=item["description"],
                recyclability_status=item["recyclability_status"]
            )
            self.db.add(cat)
            self.db.flush()

            for s in item.get("steps", []):
                step = RecyclingStep(
                    category_id=cat.id,
                    step_number=s["step_number"],
                    title=s["title"],
                    description=s["description"]
                )
                self.db.add(step)

            for w in item.get("warnings", []):
                warn = RecyclingWarning(
                    category_id=cat.id,
                    title=w["title"],
                    description=w["description"],
                    severity=w["severity"]
                )
                self.db.add(warn)

            for r in item.get("rules", []):
                rule = RecyclingRule(
                    category_id=cat.id,
                    rule_type=r["rule_type"],
                    title=r["title"],
                    description=r["description"],
                    priority=r.get("priority", 1)
                )
                self.db.add(rule)

            disp = item.get("disposal", {})
            if disp:
                method = RecyclingDisposalMethod(
                    category_id=cat.id,
                    primary_route=disp.get("primary_route", "Municipal Bin"),
                    stream_name=disp.get("stream_name", "Dry Recycling"),
                    bin_color=disp.get("bin_color", "Blue Bin"),
                    special_notes=disp.get("special_notes"),
                    local_guidance_notes=disp.get("local_guidance_notes")
                )
                self.db.add(method)

        self.db.commit()

    def get_all_categories(self) -> List[RecyclingCategory]:
        self.seed_default_knowledge_if_empty()
        return self.db.query(RecyclingCategory).order_by(RecyclingCategory.name).all()

    def get_category_by_slug(self, slug: str) -> Optional[RecyclingCategory]:
        self.seed_default_knowledge_if_empty()
        return self.db.query(RecyclingCategory).filter(RecyclingCategory.slug == slug.lower().strip()).first()

    def get_category_by_id(self, category_id: str) -> Optional[RecyclingCategory]:
        self.seed_default_knowledge_if_empty()
        return self.db.query(RecyclingCategory).filter(RecyclingCategory.id == category_id).first()
