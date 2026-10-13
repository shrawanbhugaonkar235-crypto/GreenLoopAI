# GreenLoopAI — How to Recycle Guidance Engine

## 1. Overview & Vision
The **How to Recycle** module in GreenLoopAI extends the multi-modal verification pipeline into the complete circular waste lifecycle:

```text
SCAN ──► DETECT ──► VERIFY ──► RECYCLE ──► REWARD ──► EPR
```

This ensures citizens scanning waste at home receive immediate, accurate, step-by-step preparation, sorting, safety warnings, and disposal routes derived dynamically from the AI detection results or accessible via the interactive material directory.

---

## 2. Waste Stream Categorization & Knowledge Base
The knowledge base supports 9 comprehensive household waste streams:

1. **Plastics (`plastic-bottles-containers`, `flexible-plastic-film`)**
   - **Rigid Plastics (PET / HDPE #1, #2)**: Empty & rinse, crush to save bin space, reattach screw cap.
   - **Flexible Films & Wrappers (LDPE / PP #4, #5)**: Clean & dry, store bag-in-bag, separate from rigid curbside collection to avoid MRF optical sorting tangles.
2. **Paper & Cardboard (`paper-cardboard`)**
   - Flatten boxes to maximize bin capacity.
   - **Contamination Rule**: Remove greasy pizza box sections, wax coatings, and plastic tape.
3. **Glass (`glass-bottles-jars`)**
   - Rinse residue, remove metal lids/corks.
   - **Safety Callout**: Unbroken bottles & jars only in curbside bins. Broken glass must be wrapped in heavy paper/cardboard and disposed in general trash to protect municipal sanitation workers.
4. **Metals & Cans (`metals-aluminum-cans`)**
   - Aluminum beverage cans, tin food cans, foil trays.
   - Clean grease/food before baling. Never place pressurized aerosol cans in general recycling bins without depressurization.
5. **E-Waste & Electronics (`electronic-waste`)**
   - Laptops, smartphones, chargers, cords, small appliances.
   - **Data Privacy**: Mandatory factory reset / cryptographic storage wipe before handover.
   - Channel via authorized municipal e-waste collection drives or brand take-back schemes.
6. **Batteries & Energy Storage (`batteries-accumulators`)**
   - Alkaline (AA/AAA), Lithium-Ion, button cells.
   - **Hazard Severity High**: High fire and explosion risk. Never put in general waste or curbside recycling bins.
   - Terminal insulation: Tape both positive and negative terminals with non-conductive electrical or scotch tape before drop-off at designated battery bins.
7. **Organic & Compost (`organic-wet-waste`)**
   - Fruit peels, vegetable scraps, coffee grounds, garden clippings.
   - Keep free of stickers, plastic twist ties, and treated wood.
8. **Textiles & Footwear (`textiles-clothing`)**
   - Waste hierarchy applied: **Reuse → Repair → Donate → Textile Recycling**.
   - Clean and dry before donation. Stained/torn textiles directed to industrial shredding/insulation recycling.
9. **Hazardous & Chemicals (`hazardous-household-waste`)**
   - Paint, motor oil, solvents, pesticides, bleach, fluorescent tubes.
   - **Safety Rules**: Keep in original labeled containers. Never mix chemicals. Never pour down sinks, storm drains, or toilets.

---

## 3. Data Schema & Relational Models
The module uses normalized relational structures:

- **`RecyclingCategory`**:
  - `name`, `slug`, `material_type`, `description`, `recyclability_status`, `badge_color`, `general_bin`, `co2_savings_kg_per_unit`.
- **`RecyclingStep`**:
  - `step_number`, `title`, `instruction`, `why_it_matters`, `icon_name`.
- **`RecyclingWarning`**:
  - `title`, `warning_message`, `severity` (`INFO`, `CAUTION`, `WARNING`, `DANGER`), `icon_name`.
- **`RecyclingRule`**:
  - `rule_type` (`DO`, `DONT`), `rule_text`, `explanation`.
- **`RecyclingDisposalMethod`**:
  - `method_type` (`CURBSIDE_BIN`, `DROP_OFF_POINT`, `RETAIL_TAKEBACK`, `SPECIAL_FACILITY`, `COMPOST_BIN`, `MUNICIPAL_DEPOT`), `name`, `instructions`, `is_preferred`.

---

## 4. API Endpoints
All endpoints are exposed under `/api/v1/recycling`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/recycling/categories` | List all available recycling categories with summary facts |
| `GET` | `/api/v1/recycling/categories/{slug}` | Get full detailed recycling guide by category slug |
| `GET` | `/api/v1/recycling/guide/{waste_type}` | Get recycling guide mapped dynamically from YOLO label |
| `POST` | `/api/v1/recycling/recommendation` | Dynamic recommendation with confidence weighting and preparation checklist |

---

## 5. Vision AI to Recycling Mapping Engine
The YOLO waste detector classes map seamlessly to verified recycling guides:

```python
WASTE_TO_RECYCLING_SLUG_MAP = {
    "plastic": "plastic-bottles-containers",
    "plastic_bottle": "plastic-bottles-containers",
    "plastic_container": "plastic-bottles-containers",
    "plastic_bag": "flexible-plastic-film",
    "plastic_film": "flexible-plastic-film",
    "wrapper": "flexible-plastic-film",
    "paper": "paper-cardboard",
    "cardboard": "paper-cardboard",
    "glass": "glass-bottles-jars",
    "glass_bottle": "glass-bottles-jars",
    "metal": "metals-aluminum-cans",
    "can": "metals-aluminum-cans",
    "aluminum_can": "metals-aluminum-cans",
    "tin_can": "metals-aluminum-cans",
    "e-waste": "electronic-waste",
    "electronics": "electronic-waste",
    "battery": "batteries-accumulators",
    "organic": "organic-wet-waste",
    "food_waste": "organic-wet-waste",
    "textile": "textiles-clothing",
    "clothes": "textiles-clothing",
    "hazardous": "hazardous-household-waste"
}
```

---

## 6. Municipal Variability & Honest Disclaimers
When exact municipal geographical metadata is unavailable:
- Standard international recycling best practices are rendered.
- An explicit disclaimer is attached to every guide: *"Recycling rules and bin colors vary by municipality and waste facility capabilities. Check your local municipal guidelines for specific curbside rules."*
