"""
diet_planner.py — a simple, transparent diet planner. No AI API call needed
for the calculation itself (it's a real formula); the AI brain is only used
afterwards, optionally, to turn the numbers into a friendly meal suggestion
in Urdu/English.

Uses the Mifflin-St Jeor equation (a standard, widely-used BMR formula).
This is general wellness guidance, not medical advice — for any real
medical condition, diabetes, pregnancy, etc., a doctor/dietitian should
be consulted; this tool doesn't know about those factors.
"""

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,       # little/no exercise
    "light": 1.375,          # light exercise 1-3 days/week
    "moderate": 1.55,        # moderate exercise 3-5 days/week
    "active": 1.725,         # hard exercise 6-7 days/week
    "very_active": 1.9,      # very hard exercise + physical job
}

GOAL_ADJUSTMENT = {
    "lose": -500,     # ~0.5kg/week deficit
    "maintain": 0,
    "gain": 300,
}


def calculate_calories(weight_kg: float, height_cm: float, age: int, sex: str,
                        activity_level: str = "moderate", goal: str = "maintain") -> dict:
    sex = sex.lower()
    if sex.startswith("m"):
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    maintenance = bmr * multiplier
    target = maintenance + GOAL_ADJUSTMENT.get(goal, 0)

    protein_g = weight_kg * (1.8 if goal == "gain" else 1.6)  # g/kg, moderate-high for either goal
    fat_g = (target * 0.25) / 9
    carbs_g = (target - (protein_g * 4) - (fat_g * 9)) / 4

    return {
        "bmr": round(bmr),
        "maintenance_calories": round(maintenance),
        "target_calories": round(target),
        "protein_g": round(protein_g),
        "fat_g": round(fat_g),
        "carbs_g": round(max(carbs_g, 0)),
    }


def build_meal_plan_prompt(macros: dict, cuisine: str = "Pakistani") -> str:
    """Builds a prompt you can pass to brain.ask() to turn numbers into a real day's meals."""
    return (
        f"Suggest a full day's {cuisine} meal plan (breakfast, lunch, dinner, 1-2 snacks) "
        f"that totals approximately {macros['target_calories']} calories, "
        f"with about {macros['protein_g']}g protein, {macros['fat_g']}g fat, {macros['carbs_g']}g carbs. "
        f"Keep it practical and affordable. Reply in Urdu+English mix."
    )


if __name__ == "__main__":
    result = calculate_calories(70, 175, 25, "male", "moderate", "lose")
    print(result)
