from typing import List
from app.schemas.verification import (
    DetectedObject,
    OcrResult,
    AuthenticitySignal,
    VerificationScoreBreakdown,
    RewardCalculation
)


class ScoringService:
    def calculate_score_and_reward(
        self,
        detected_objects: List[DetectedObject],
        ocr_result: OcrResult,
        authenticity: AuthenticitySignal
    ) -> tuple[VerificationScoreBreakdown, RewardCalculation, bool]:
        """
        Calculates composite verification score and GreenCoins reward dynamically.
        Never outputs hardcoded mock numbers.
        
        Formula:
        Composite Score = (Detection Score * 0.45) + (Brand Score * 0.30) + (Authenticity Score * 0.25)
        """
        # 1. Detection Component (0 - 100)
        if detected_objects:
            # Average confidence of detected objects weighted by presence
            avg_conf = sum(obj.confidence for obj in detected_objects) / len(detected_objects)
            detection_score = avg_conf * 100.0
        else:
            detection_score = 0.0

        # 2. Brand Recognition Component (0 - 100)
        if ocr_result.brand:
            brand_score = (ocr_result.confidence or 0.85) * 100.0
        elif ocr_result.barcode:
            brand_score = 75.0  # Recognized 1D/2D Barcode or QR code on packaging
        elif ocr_result.text:
            brand_score = 60.0  # Packaging text detected
        elif detected_objects:
            brand_score = 55.0  # Genuine unbranded recyclable material (cardboard, paper, scrap metal, glass, etc.)
        else:
            brand_score = 20.0  # Unidentified item without brand or clear category

        # 3. Authenticity Component (0 - 100)
        authenticity_score = authenticity.score * 100.0

        # Composite Score Calculation
        composite = (detection_score * 0.45) + (brand_score * 0.30) + (authenticity_score * 0.25)
        composite_score = round(max(0.0, min(100.0, composite)), 2)

        breakdown = VerificationScoreBreakdown(
            detection_score=round(detection_score, 2),
            brand_score=round(brand_score, 2),
            authenticity_score=round(authenticity_score, 2),
            composite_score=composite_score
        )

        # Verification threshold: minimum 60% composite score and at least one detected object
        verified = bool(detected_objects and composite_score >= 60.0)

        # 4. GreenCoins Reward Calculation
        # Base coins scaled by composite score
        base_coins = int(composite_score * 0.5)  # 60 score -> 30 coins, 90 score -> 45 coins
        
        # Brand bonus for EPR traceable items
        if ocr_result.brand:
            base_coins += 15

        if composite_score >= 85.0:
            reward_tier = "PLATINUM"
            base_coins += 10
        elif composite_score >= 75.0:
            reward_tier = "GOLD"
            base_coins += 5
        elif composite_score >= 60.0:
            reward_tier = "SILVER"
        else:
            reward_tier = "BRONZE"
            base_coins = 0 if not verified else 10

        calculation_basis = (
            f"Score {composite_score}% ({detection_score:.1f}% detect + "
            f"{brand_score:.1f}% brand + {authenticity_score:.1f}% auth)"
        )
        if ocr_result.brand:
            calculation_basis += f" + EPR Brand Bonus ({ocr_result.brand})"

        reward = RewardCalculation(
            greencoins_awarded=base_coins,
            reward_tier=reward_tier,
            calculation_basis=calculation_basis
        )

        return breakdown, reward, verified


scoring_service = ScoringService()
