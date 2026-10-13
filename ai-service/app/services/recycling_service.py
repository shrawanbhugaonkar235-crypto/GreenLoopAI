import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.recycling import (
    RecyclingCategory,
    RecyclabilityStatusEnum,
    WarningSeverityEnum,
    RuleTypeEnum
)
from app.repositories.recycling_repository import RecyclingRepository
from app.schemas.recycling import (
    RecyclingGuideResponse,
    RecyclingStepSchema,
    RecyclingWarningSchema,
    RecyclingRuleSchema,
    RecyclingDisposalMethodSchema,
    RecyclingCategorySummarySchema
)

logger = logging.getLogger("greenloopai.recycling")

# Mapping of YOLO labels and taxonomy categories to recycling category slugs
WASTE_TO_RECYCLING_SLUG_MAP: Dict[str, str] = {
    # Plastic
    "plastic": "plastic-bottles-containers",
    "bottle": "plastic-bottles-containers",
    "cup": "plastic-bottles-containers",
    "container": "plastic-bottles-containers",
    "bowl": "plastic-bottles-containers",
    "bag": "plastic-bottles-containers",
    # Paper & Cardboard
    "paper / cardboard": "paper-cardboard",
    "paper": "paper-cardboard",
    "cardboard": "paper-cardboard",
    "box": "paper-cardboard",
    "book": "paper-cardboard",
    # Glass
    "glass": "glass-bottles-jars",
    "wine glass": "glass-bottles-jars",
    "vase": "glass-bottles-jars",
    # Metal
    "metal": "metal-cans-packaging",
    "can": "metal-cans-packaging",
    "fork": "metal-cans-packaging",
    "knife": "metal-cans-packaging",
    "spoon": "metal-cans-packaging",
    "scissors": "metal-cans-packaging",
    # E-Waste
    "e-waste": "e-waste",
    "electronic": "e-waste",
    "phone": "e-waste",
    "cell phone": "e-waste",
    "laptop": "e-waste",
    "mouse": "e-waste",
    "keyboard": "e-waste",
    "remote": "e-waste",
    "tv": "e-waste",
    "clock": "e-waste",
    "toaster": "e-waste",
    "microwave": "e-waste",
    "oven": "e-waste",
    "refrigerator": "e-waste",
    # Batteries
    "battery": "batteries",
    "power bank": "batteries",
    # Organic / Compost
    "organic / compost": "organic-wet-waste",
    "organic": "organic-wet-waste",
    "compost": "organic-wet-waste",
    "banana": "organic-wet-waste",
    "apple": "organic-wet-waste",
    "orange": "organic-wet-waste",
    "sandwich": "organic-wet-waste",
    "broccoli": "organic-wet-waste",
    "carrot": "organic-wet-waste",
    "hot dog": "organic-wet-waste",
    "pizza": "organic-wet-waste",
    "donut": "organic-wet-waste",
    "cake": "organic-wet-waste",
    "potted plant": "organic-wet-waste",
    # Textiles
    "textile / fabric": "textiles-fabrics",
    "textile": "textiles-fabrics",
    "fabric": "textiles-fabrics",
    "backpack": "textiles-fabrics",
    "handbag": "textiles-fabrics",
    "suitcase": "textiles-fabrics",
    "umbrella": "textiles-fabrics",
    "tie": "textiles-fabrics",
    # Hazardous
    "hazardous": "hazardous-waste",
    "chemical": "hazardous-waste",
    "paint": "hazardous-waste",
    # Wood & Bulky Furniture
    "wood / bulky": "wood-bulky-furniture",
    "wood": "wood-bulky-furniture",
    "bulky": "wood-bulky-furniture",
    "furniture": "wood-bulky-furniture",
    "dining table": "wood-bulky-furniture",
    "table": "wood-bulky-furniture",
    "chair": "wood-bulky-furniture",
    "couch": "wood-bulky-furniture",
    "sofa": "wood-bulky-furniture",
    "bed": "wood-bulky-furniture",
    "bench": "wood-bulky-furniture",
    "desk": "wood-bulky-furniture"
}


class RecyclingGuidanceService:
    def get_categories_list(self, db: Session) -> List[RecyclingCategorySummarySchema]:
        repo = RecyclingRepository(db)
        categories = repo.get_all_categories()
        return [
            RecyclingCategorySummarySchema(
                id=c.id,
                name=c.name,
                slug=c.slug,
                icon=c.icon,
                description=c.description,
                recyclability_status=c.recyclability_status.value if hasattr(c.recyclability_status, "value") else str(c.recyclability_status)
            )
            for c in categories
        ]

    def get_guide_by_slug(self, slug: str, db: Session) -> RecyclingGuideResponse:
        repo = RecyclingRepository(db)
        category = repo.get_category_by_slug(slug)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recycling category '{slug}' not found."
            )
        return self._format_category_guide(category, waste_type=category.name)

    def get_guide_for_waste_item(
        self,
        waste_category: Optional[str],
        detected_label: Optional[str],
        confidence: Optional[float],
        db: Session
    ) -> RecyclingGuideResponse:
        """
        Determines appropriate recycling guidance based on AI detection results.
        Handles low-confidence and unknown items with safety-first fallbacks.
        """
        repo = RecyclingRepository(db)
        repo.seed_default_knowledge_if_empty()

        # 1. Low Confidence / Unknown Waste Handling
        if confidence is not None and confidence < 0.15:
            return self._build_unknown_waste_fallback(
                title="Low-Confidence Detection",
                summary="Waste type could not be identified with high confidence. Please verify the category before disposal."
            )

        # 2. Resolve matching category slug
        target_slug = None
        search_terms = []
        if detected_label:
            search_terms.append(detected_label.lower().strip())
            search_terms.append(detected_label.lower().replace("/", " ").replace("-", " ").strip())
        if waste_category:
            search_terms.append(waste_category.lower().strip())
            search_terms.append(waste_category.lower().replace("/", " ").replace("-", " ").strip())

        for term in search_terms:
            if not term:
                continue
            if term in WASTE_TO_RECYCLING_SLUG_MAP:
                target_slug = WASTE_TO_RECYCLING_SLUG_MAP[term]
                break
            for key, slug_val in WASTE_TO_RECYCLING_SLUG_MAP.items():
                if key in term or term in key:
                    target_slug = slug_val
                    break
            if target_slug:
                break

        # Default to plastic/general if not matched
        if not target_slug:
            target_slug = "wood-bulky-furniture" if "wood" in str(waste_category).lower() else "plastic-bottles-containers"

        category = repo.get_category_by_slug(target_slug)
        if not category:
            # Fallback to first available category
            cats = repo.get_all_categories()
            if cats:
                category = cats[0]
            else:
                return self._build_unknown_waste_fallback(
                    title="Guidance Temporarily Unavailable",
                    summary="Recycling knowledge base is initializing."
                )

        item_label = detected_label or waste_category or category.name
        return self._format_category_guide(category, waste_type=item_label)

    def _format_category_guide(self, category: RecyclingCategory, waste_type: str) -> RecyclingGuideResponse:
        steps = [
            RecyclingStepSchema(
                step_number=s.step_number,
                title=s.title,
                description=s.description,
                is_mandatory=s.is_mandatory
            )
            for s in sorted(category.steps, key=lambda x: x.step_number)
        ]

        warnings = [
            RecyclingWarningSchema(
                title=w.title,
                description=w.description,
                severity=w.severity.value if hasattr(w.severity, "value") else str(w.severity)
            )
            for w in category.warnings
        ]

        rules = [
            RecyclingRuleSchema(
                rule_type=r.rule_type.value if hasattr(r.rule_type, "value") else str(r.rule_type),
                title=r.title,
                description=r.description,
                priority=r.priority
            )
            for r in category.rules
        ]

        disp = category.disposal_method
        disposal_schema = RecyclingDisposalMethodSchema(
            primary_route=disp.primary_route if disp else "Municipal Recyclable Stream",
            stream_name=disp.stream_name if disp else "Dry Recyclables",
            bin_color=disp.bin_color if disp else "Blue Bin",
            special_notes=disp.special_notes if disp else None,
            local_guidance_notes=disp.local_guidance_notes if disp else None
        )

        status_str = (
            category.recyclability_status.value
            if hasattr(category.recyclability_status, "value")
            else str(category.recyclability_status)
        )

        # Build dynamic preparation bullet points
        prep_bullets = [
            "Empty all remaining contents and liquids",
            "Rinse lightly if food, sugar, or chemical residue remains",
            "Separate non-compatible attachments (lids, batteries, caps)",
            "Deposit in the designated dry/specialized collection stream"
        ]

        return RecyclingGuideResponse(
            success=True,
            waste_type=waste_type,
            category_name=category.name,
            category_slug=category.slug,
            icon=category.icon or "♻",
            recyclability_status=status_str,
            title=f"How to Recycle {waste_type.capitalize()}",
            summary=category.description,
            preparation_summary=prep_bullets,
            steps=steps,
            warnings=warnings,
            rules=rules,
            disposal_method=disposal_schema,
            local_guidance_available=False,
            local_guidance_message=(
                "General recycling standards are displayed. "
                "Local municipal collection schedules and drop-off locations may vary by region."
            )
        )

    def _build_unknown_waste_fallback(self, title: str, summary: str) -> RecyclingGuideResponse:
        return RecyclingGuideResponse(
            success=True,
            waste_type="Unidentified Waste Item",
            category_name="General Waste",
            category_slug="unidentified",
            icon="❓",
            recyclability_status=RecyclabilityStatusEnum.UNKNOWN.value,
            title=title,
            summary=summary,
            preparation_summary=[
                "Inspect the item for recycling identification symbols (e.g. Resin Code 1-7)",
                "Separate organic wet parts from dry parts if mixed",
                "Do not place unknown chemicals or pressurized items in regular bins"
            ],
            steps=[
                RecyclingStepSchema(
                    step_number=1,
                    title="Manual Verification",
                    description="Check the packaging for triangular recycling numbers or material stamps.",
                    is_mandatory=True
                ),
                RecyclingStepSchema(
                    step_number=2,
                    title="Segregate Dry vs Wet",
                    description="If the material is dry plastic, paper, glass, or metal, place with dry recyclables. If food-stained or wet, divert to wet waste.",
                    is_mandatory=True
                )
            ],
            warnings=[
                RecyclingWarningSchema(
                    title="Safety Caution",
                    description="If the item is electronic or contains batteries or chemicals, do not dispose in ordinary household bins.",
                    severity=WarningSeverityEnum.WARNING.value
                )
            ],
            rules=[
                RecyclingRuleSchema(
                    rule_type=RuleTypeEnum.DO_NOT.value,
                    title="Avoid Wish-cycling",
                    description="Placing non-recyclable materials in recycling bins causes contamination and machinery breakdowns.",
                    priority=1
                )
            ],
            disposal_method=RecyclingDisposalMethodSchema(
                primary_route="Manual Verification Required",
                stream_name="General / Dry Stream Pending Verification",
                bin_color="Pending Verification",
                special_notes="Check with your local waste management service if unsure.",
                local_guidance_notes="Local municipal collection rules may vary."
            ),
            local_guidance_available=False,
            local_guidance_message="Local collection information is not currently available."
        )


recycling_service = RecyclingGuidanceService()
