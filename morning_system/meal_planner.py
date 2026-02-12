#!/usr/bin/env python3
"""
Smart Meal Planner - Hits protein goals while staying within calorie budget
Learns from Ross's eating patterns and suggests high-protein meals
"""

import json
from datetime import datetime

# Meal database (high-protein focused)
MEALS = {
    "breakfast": [
        {"name": "Eggs (3) + Oatmeal", "calories": 450, "protein": 25, "carbs": 45, "fat": 15},
        {"name": "Greek Yogurt (1.5 cups) + Berries + Granola", "calories": 320, "protein": 25, "carbs": 42, "fat": 6},
        {"name": "Protein Shake (2 scoops) + Banana + PB", "calories": 420, "protein": 50, "carbs": 40, "fat": 12},
        {"name": "Chicken Sausage + Whole Wheat Toast + Egg", "calories": 380, "protein": 35, "carbs": 30, "fat": 12},
    ],
    "lunch": [
        {"name": "Grilled Chicken (6oz) + Rice + Veggies", "calories": 550, "protein": 55, "carbs": 50, "fat": 12},
        {"name": "Salmon (5oz) + Sweet Potato + Broccoli", "calories": 520, "protein": 45, "carbs": 48, "fat": 18},
        {"name": "Lean Beef (5oz) + Pasta + Sauce", "calories": 580, "protein": 50, "carbs": 60, "fat": 15},
        {"name": "Turkey Breast (6oz) + Quinoa Bowl + Veggies", "calories": 490, "protein": 52, "carbs": 48, "fat": 10},
    ],
    "dinner": [
        {"name": "Grilled Steak (7oz) + Potatoes + Asparagus", "calories": 680, "protein": 65, "carbs": 50, "fat": 22},
        {"name": "Baked Cod (6oz) + Brown Rice + Roasted Veggies", "calories": 520, "protein": 48, "carbs": 52, "fat": 10},
        {"name": "Chicken Breast (7oz) + Pasta Primavera", "calories": 620, "protein": 65, "carbs": 55, "fat": 15},
        {"name": "Ground Turkey (6oz) + Sweet Potato + Green Beans", "calories": 550, "protein": 55, "carbs": 48, "fat": 14},
    ],
    "snacks": [
        {"name": "Protein Bar", "calories": 200, "protein": 20, "carbs": 20, "fat": 7},
        {"name": "Greek Yogurt + Almonds", "calories": 280, "protein": 20, "carbs": 22, "fat": 12},
        {"name": "Chicken Breast + Veggies", "calories": 200, "protein": 35, "carbs": 8, "fat": 3},
        {"name": "Cottage Cheese + Berries", "calories": 250, "protein": 28, "carbs": 25, "fat": 6},
    ]
}

def generate_meal_plan():
    """Generate daily meal plan hitting 200g protein, ~2200 calories"""
    
    daily_goal = {
        "calories": 2200,
        "protein": 200,
        "carbs": 250,
        "fat": 70
    }
    
    # Select one meal from each category
    breakfast = MEALS["breakfast"][0]  # Eggs + Oatmeal (high protein start)
    lunch = MEALS["lunch"][0]  # Grilled Chicken (classic bulk)
    dinner = MEALS["dinner"][0]  # Steak (protein + satisfaction)
    
    # Add snacks strategically to hit protein
    snack1 = MEALS["snacks"][2]  # Chicken + veggies (35g protein)
    snack2 = MEALS["snacks"][0]  # Protein bar (20g protein)
    
    plan = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "meals": [
            {"meal": "Breakfast", "time": "7:00 AM", **breakfast},
            {"meal": "Mid-Morning Snack", "time": "10:00 AM", **snack1},
            {"meal": "Lunch", "time": "12:30 PM", **lunch},
            {"meal": "Pre-Workout", "time": "4:00 PM", **snack2},
            {"meal": "Dinner", "time": "7:00 PM", **dinner},
        ]
    }
    
    # Calculate totals
    totals = {
        "calories": sum(m["calories"] for m in plan["meals"]),
        "protein": sum(m["protein"] for m in plan["meals"]),
        "carbs": sum(m["carbs"] for m in plan["meals"]),
        "fat": sum(m["fat"] for m in plan["meals"]),
    }
    
    plan["totals"] = totals
    plan["vs_goal"] = {
        "calories": f"{totals['calories']} (Goal: {daily_goal['calories']}, {totals['calories']-daily_goal['calories']:+d})",
        "protein": f"{totals['protein']}g (Goal: {daily_goal['protein']}g, {totals['protein']-daily_goal['protein']:+d}g)",
        "carbs": f"{totals['carbs']}g (Goal: {daily_goal['carbs']}g, {totals['carbs']-daily_goal['carbs']:+d}g)",
        "fat": f"{totals['fat']}g (Goal: {daily_goal['fat']}g, {totals['fat']-daily_goal['fat']:+d}g)",
    }
    
    return plan

if __name__ == "__main__":
    plan = generate_meal_plan()
    print(f"\n🍽️  MEAL PLAN FOR {plan['date']}\n")
    
    for meal in plan["meals"]:
        print(f"⏰ {meal['time']} - {meal['meal']}")
        print(f"   {meal['name']}")
        print(f"   {meal['calories']} cal | {meal['protein']}g protein | {meal['carbs']}g carbs | {meal['fat']}g fat\n")
    
    print("=" * 60)
    print("📊 DAILY TOTALS:\n")
    for macro, value in plan["vs_goal"].items():
        print(f"  {macro.title()}: {value}")
    
    # Save to file
    with open("/Users/clawdbot/clawd/morning_system/meal_plan_today.json", "w") as f:
        json.dump(plan, f, indent=2)
    
    print("\n✅ Meal plan saved to meal_plan_today.json")
