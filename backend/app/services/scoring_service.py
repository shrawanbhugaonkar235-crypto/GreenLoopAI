import logging
from typing import List, Tuple
from app.config import settings
from app.schemas import (
    DetectedObject,
    OcrResult,
    AuthenticitySignal,
    ScoreBreakdown
)

logger = logging.getLogger("greenloopai.scoring")

class ScoringService:
    def calculate_score_and_reward(
        self,
        detected_objects: List[DetectedObject],
        ocr_result: OcrResult,
        authenticity: AuthenticitySignal
    ) -> Tuple[ScoreBreakdown, int, str, str, bool, str]:
        """
        Calculates verification score V using real evidence:
        V = 0.45 * D + 0.30 * B + 0.25 * A
        
        Returns:
            - breakdown: ScoreBreakdown
            - coins: int (GreenCoins awarded)
            - reward_tier: str ("PLATINUM", "GOLD", "SILVER", "None")
            - calculation_basis: str
            - is_verified: bool
            - explanation_message: str
        """
        # 1. Detection Component D (0 - 100)
        if detected_objects:
            avg_conf = sum(obj.confidence for obj in detected_objects) / len(detected_objects)
            detection_score = round(avg_conf * 100.0, 1)
        else:
            detection_score = 0.0

        # 2. Brand Verification Component B (0 - 100)
        if ocr_result.brand:
            brand_score = round(max(70.0, (ocr_result.confidence or 0.85) * 100.0), 1)
        elif ocr_result.barcode:
            brand_score = 75.0
        elif ocr_result.text and len(ocr_result.text) >= 3:
            brand_score = 60.0
        elif detected_objects:
            # Genuine unbranded recyclable material (cardboard, glass, scrap, etc.)
            brand_score = 55.0
        else:
            brand_score = 20.0

        # 3. Authenticity Component A (0 - 100)
        authenticity_score = round(authenticity.score * 100.0, 1)

        # 4. Composite Verification Score V
        composite = (detection_score * 0.45) + (brand_score * 0.30) + (authenticity_score * 0.25)
        composite_score = round(max(0.0, min(100.0, composite)), 1)

        breakdown = ScoreBreakdown(
            detection_score=detection_score,
            brand_score=brand_score,
            authenticity_score=authenticity_score,
            composite_score=composite_score
        )

        # Verification criterion: V >= 60 and at least one detected object
        has_waste = len(detected_objects) > 0
        is_verified = bool(has_waste and composite_score >= 60.0)

        # 5. GreenCoins Reward
        if is_verified:
            base_coins = int(composite_score * settings.GREENCOINS_PER_SCORE)
            if ocr_result.brand:
                base_coins += 15  # Brand traceability bonus

            if composite_score >= 85.0:
                reward_tier = "PLATINUM"
                base_coins += 10
            elif composite_score >= 75.0:
                reward_tier = "GOLD"
                base_coins += 5
            else:
                reward_tier = "SILVER"

            coins = max(10, base_coins)

            basis_parts = [
                f"Score V {composite_score}%",
                f"({detection_score}% detect + {brand_score}% brand + {authenticity_score}% auth)"
            ]
            if ocr_result.brand:
                basis_parts.append(f"+ Brand Bonus ({ocr_result.brand})")
            basis_parts.append(f"[{reward_tier} Tier]")

            calculation_basis = " ".join(basis_parts)
            explanation_message = (
                f"Successfully verified. Identified {len(detected_objects)} waste item(s) "
                f"with a composite verification score of {composite_score}/100."
            )
        else:
            coins = 0
            reward_tier = "None"
            calculation_basis = (
                f"Score V {composite_score}% ({detection_score}% detect + "
                f"{brand_score}% brand + {authenticity_score}% auth)"
            )
            if not has_waste:
                explanation_message = (
                    "No recognisable recyclable waste object was detected by the YOLO model."
                )
            else:
                explanation_message = (
                    f"Verification score {composite_score}/100 is below the passing threshold of 60."
                )

        return breakdown, coins, reward_tier, calculation_basis, is_verified, explanation_message

scoring_service = ScoringService()
