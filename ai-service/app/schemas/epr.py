from typing import Optional
from pydantic import BaseModel, Field


class EprProcessingRequest(BaseModel):
    verification_id: str = Field(..., description="ID from a verified scan result")
    waste_category: str = Field(..., description="Category: Plastic, Paper, Metal, Glass, E-Waste")
    material_type: str = Field(..., description="Material designation e.g. PET (Type 1), HDPE (Type 2)")
    weight_kg: float = Field(default=1.0, ge=0.01, le=10000.0, description="Estimated weight in kg")
    brand: Optional[str] = Field(None, description="Identified producer brand if known")
    verification_score: float = Field(..., ge=0.0, le=100.0, description="Score calculated by verification engine")


class EprProcessingResponse(BaseModel):
    evidence_id: str = Field(..., description="Generated EPR evidence tracking ID")
    verification_id: str = Field(..., description="Referenced verification ID")
    compliance_status: str = Field(..., description="COMPLIANT, PENDING_AUDIT, or REJECTED")
    epr_credits_generated: float = Field(..., description="Calculated EPR credit quantity")
    target_category: str = Field(..., description="Regulatory EPR category")
    recyclability_tier: str = Field(..., description="TIER_1_HIGH, TIER_2_MEDIUM, TIER_3_LOW")
    timestamp: str = Field(..., description="ISO 8601 evaluation timestamp")
    regulatory_standard: str = Field(..., description="Governing EPR compliance standard")
    calculation_summary: str = Field(..., description="Formula and multiplier details")
