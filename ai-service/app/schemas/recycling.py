from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class RecyclingStepSchema(BaseModel):
    step_number: int
    title: str
    description: str
    is_mandatory: bool = True

    model_config = ConfigDict(from_attributes=True)


class RecyclingWarningSchema(BaseModel):
    title: str
    description: str
    severity: str  # INFO, CAUTION, WARNING, DANGER

    model_config = ConfigDict(from_attributes=True)


class RecyclingRuleSchema(BaseModel):
    rule_type: str  # DO, DO_NOT, SPECIAL_HANDLING, DATA_SAFETY
    title: str
    description: str
    priority: int = 1

    model_config = ConfigDict(from_attributes=True)


class RecyclingDisposalMethodSchema(BaseModel):
    primary_route: str
    stream_name: str
    bin_color: Optional[str] = None
    special_notes: Optional[str] = None
    local_guidance_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RecyclingCategorySummarySchema(BaseModel):
    id: str
    name: str
    slug: str
    icon: Optional[str] = None
    description: str
    recyclability_status: str

    model_config = ConfigDict(from_attributes=True)


class RecyclingGuideResponse(BaseModel):
    success: bool = True
    waste_type: str
    category_name: str
    category_slug: str
    icon: Optional[str] = "♻"
    recyclability_status: str
    title: str
    summary: str
    preparation_summary: List[str]
    steps: List[RecyclingStepSchema]
    warnings: List[RecyclingWarningSchema]
    rules: List[RecyclingRuleSchema]
    disposal_method: RecyclingDisposalMethodSchema
    local_guidance_available: bool = False
    local_guidance_message: str

    model_config = ConfigDict(from_attributes=True)


class RecyclingCategoriesListResponse(BaseModel):
    success: bool = True
    total: int
    categories: List[RecyclingCategorySummarySchema]


class RecyclingRecommendationRequest(BaseModel):
    verification_id: Optional[str] = None
    waste_category: Optional[str] = None
    detected_label: Optional[str] = None
    confidence: Optional[float] = None
