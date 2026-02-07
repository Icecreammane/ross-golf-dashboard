#!/usr/bin/env python3
"""
Food Logging Helper - Process food images and log to fitness tracker
Usage: python3 food-logger.py <image_path> [--analyze-only]
"""

import sys
import os
import requests
import json
from datetime import datetime

FITNESS_API = "http://localhost:3000/api/log-food"

# Common food estimates (calories per serving)
FOOD_DB = {
    "chicken breast": {"calories": 165, "protein": 31, "serving": "4oz"},
    "rice": {"calories": 206, "protein": 4, "serving": "1 cup cooked"},
    "broccoli": {"calories": 55, "protein": 4, "serving": "1 cup"},
    "salmon": {"calories": 206, "protein": 22, "serving": "4oz"},
    "steak": {"calories": 280, "protein": 26, "serving": "4oz"},
    "eggs": {"calories": 70, "protein": 6, "serving": "1 large"},
    "oatmeal": {"calories": 150, "protein": 5, "serving": "1 cup cooked"},
    "banana": {"calories": 105, "protein": 1, "serving": "1 medium"},
    "apple": {"calories": 95, "protein": 0, "serving": "1 medium"},
    "protein shake": {"calories": 120, "protein": 24, "serving": "1 scoop"},
    "peanut butter": {"calories": 190, "protein": 8, "serving": "2 tbsp"},
    "bread": {"calories": 80, "protein": 4, "serving": "1 slice"},
    "pasta": {"calories": 220, "protein": 8, "serving": "1 cup cooked"},
    "potato": {"calories": 163, "protein": 4, "serving": "1 medium"},
    "sweet potato": {"calories": 112, "protein": 2, "serving": "1 medium"}
}

def analyze_food_image(image_path):
    """
    Placeholder for AI vision analysis
    In production, this would use Claude Vision or similar to identify foods
    """
    # For now, return a template that needs manual input
    return {
        "identified_foods": [],
        "estimated_total": 0,
        "confidence": "manual_entry_required",
        "note": "Image analysis requires AI vision API - manual entry for now"
    }

def log_food_entry(description, calories):
    """Log food to fitness tracker"""
    try:
        response = requests.post(
            FITNESS_API,
            json={"description": description, "calories": int(calories)},
            timeout=5
        )
        if response.status_code == 200:
            return True, "✅ Logged successfully"
        else:
            return False, f"❌ API error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "❌ Fitness tracker not running (start on port 3000)"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def quick_log(food_name, servings=1.0):
    """Quick log from common foods database"""
    food_name = food_name.lower()
    
    # Find closest match
    matches = [f for f in FOOD_DB.keys() if food_name in f or f in food_name]
    
    if not matches:
        print(f"❌ '{food_name}' not in database")
        print("\n📚 Available foods:")
        for food in sorted(FOOD_DB.keys()):
            print(f"  - {food}")
        return False
    
    food = matches[0]
    info = FOOD_DB[food]
    total_cals = int(info["calories"] * servings)
    
    description = f"{food.title()} ({servings}x {info['serving']})"
    success, message = log_food_entry(description, total_cals)
    
    if success:
        print(f"✅ Logged: {description}")
        print(f"   Calories: {total_cals}")
        print(f"   Protein: ~{int(info['protein'] * servings)}g")
    else:
        print(message)
    
    return success

def interactive_log():
    """Interactive food logging"""
    print("\n🍽️  FOOD LOGGER")
    print("━" * 50)
    print("\nOptions:")
    print("  1. Quick log (from database)")
    print("  2. Custom entry")
    print("  3. List common foods")
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == "1":
        food = input("Food name: ").strip()
        servings = input("Servings (default 1.0): ").strip() or "1.0"
        quick_log(food, float(servings))
    
    elif choice == "2":
        desc = input("Description: ").strip()
        cals = input("Calories: ").strip()
        if desc and cals.isdigit():
            success, message = log_food_entry(desc, int(cals))
            print(message)
    
    elif choice == "3":
        print("\n📚 Common Foods Database:")
        for food, info in sorted(FOOD_DB.items()):
            print(f"  {food:20s} - {info['calories']} cal ({info['serving']})")

def main():
    if len(sys.argv) < 2:
        interactive_log()
        return
    
    arg = sys.argv[1]
    
    # Check if it's an image file
    if os.path.isfile(arg) and arg.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')):
        print(f"📸 Analyzing image: {arg}")
        result = analyze_food_image(arg)
        print(json.dumps(result, indent=2))
        print("\n⚠️  AI vision not yet configured - use manual entry for now")
    
    # Quick log mode
    elif len(sys.argv) >= 2:
        food = sys.argv[1]
        servings = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
        quick_log(food, servings)

if __name__ == "__main__":
    main()
