from app.models.models import ConditionEnum

CONDITION_MULTIPLIER = {
    ConditionEnum.new: 0.85,
    ConditionEnum.like_new: 0.75,
    ConditionEnum.good: 0.62,
    ConditionEnum.fair: 0.48,
    ConditionEnum.poor: 0.32,
}


def recommend_price(retail_price: float, condition: ConditionEnum) -> tuple[float, str]:
    multiplier = CONDITION_MULTIPLIER[condition]
    recommended = round(retail_price * multiplier, 2)
    rationale = f"Retail x condition multiplier ({retail_price:.2f} x {multiplier:.2f})"
    return recommended, rationale
