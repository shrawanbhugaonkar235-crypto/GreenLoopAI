import uuid
from datetime import datetime, timezone
from app.schemas.epr import EprProcessingRequest, EprProcessingResponse

# Multipliers based on material recyclability category under EPR standards
RECYCLABILITY_MULTIPLIERS = {
    "PET": {"multiplier": 1.2, "tier": "TIER_1_HIGH", "standard": "CPCB EPR Guidelines (Category I - Rigid Plastic)"},
    "HDPE": {"multiplier": 1.1, "tier": "TIER_1_HIGH", "standard": "CPCB EPR Guidelines (Category I - Rigid Plastic)"},
    "LDPE": {"multiplier": 0.9, "tier": "TIER_2_MEDIUM", "standard": "CPCB EPR Guidelines (Category II - Flexible Plastic)"},
    "PP": {"multiplier": 1.0, "tier": "TIER_2_MEDIUM", "standard": "CPCB EPR Guidelines (Category I - Rigid Plastic)"},
    "PLASTIC": {"multiplier": 1.0, "tier": "TIER_2_MEDIUM", "standard": "CPCB EPR Guidelines (Plastic Waste Management)"},
    "ALUMINUM": {"multiplier": 1.5, "tier": "TIER_1_HIGH", "standard": "Metal Recycling & EPR Norms"},
    "METAL": {"multiplier": 1.4, "tier": "TIER_1_HIGH", "standard": "Industrial Metal Recovery Standard"},
    "CARDBOARD": {"multiplier": 0.85, "tier": "TIER_2_MEDIUM", "standard": "Paper & Cardboard Circularity Standard"},
    "PAPER": {"multiplier": 0.80, "tier": "TIER_2_MEDIUM", "standard": "Paper & Pulp Circularity Standard"},
    "GLASS": {"multiplier": 1.1, "tier": "TIER_1_HIGH", "standard": "Glass Packaging Circularity Norms"},
    "E-WASTE": {"multiplier": 2.0, "tier": "TIER_1_HIGH", "standard": "E-Waste Management Rules"},
    "TEXTILE": {"multiplier": 0.75, "tier": "TIER_3_STANDARD", "standard": "Textile Recycling & Circular Economy"},
    "WOOD": {"multiplier": 0.60, "tier": "TIER_3_STANDARD", "standard": "Biomass & Timber Circularity Standard"},
    "ORGANIC": {"multiplier": 0.50, "tier": "TIER_3_STANDARD", "standard": "Organic Composting Standards"}
}


class EprComplianceService:
    def process_compliance_record(self, request: EprProcessingRequest) -> EprProcessingResponse:
        """
        Calculates official EPR credits and compliance certification for a verified item.
        Does not use a database for persistence; returns deterministic structured compliance evidence.
        """
        # Match material type key
        mat_key = "PET"
        req_mat = request.material_type.upper()
        for key in RECYCLABILITY_MULTIPLIERS:
            if key in req_mat:
                mat_key = key
                break

        mat_info = RECYCLABILITY_MULTIPLIERS.get(mat_key, {
            "multiplier": 1.0,
            "tier": "TIER_2_MEDIUM",
            "standard": "General Waste Circularity Standard"
        })

        # Base credits = weight * material multiplier * (verification_score / 100)
        quality_factor = request.verification_score / 100.0
        credits_generated = round(request.weight_kg * mat_info["multiplier"] * quality_factor, 3)

        compliance_status = "COMPLIANT" if request.verification_score >= 60.0 else "PENDING_AUDIT"
        if request.verification_score < 40.0:
            compliance_status = "REJECTED"

        evidence_id = f"EPR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

        return EprProcessingResponse(
            evidence_id=evidence_id,
            verification_id=request.verification_id,
            compliance_status=compliance_status,
            epr_credits_generated=credits_generated,
            target_category=request.waste_category,
            recyclability_tier=mat_info["tier"],
            timestamp=datetime.now(timezone.utc).isoformat(),
            regulatory_standard=mat_info["standard"],
            calculation_summary=(
                f"{request.weight_kg:.2f} kg × {mat_info['multiplier']} (Material factor) "
                f"× {quality_factor:.2f} (Quality score) = {credits_generated:.3f} Credits"
            )
        )


epr_service = EprComplianceService()
