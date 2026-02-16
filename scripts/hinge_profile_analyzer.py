#!/usr/bin/env python3
"""
Hinge Profile Analyzer
Analyzes profile photos and bios to score matches based on Ross's preferences
"""

import json
import re
import os
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WORKSPACE = Path("/Users/clawdbot/clawd")
PREFS_FILE = WORKSPACE / "data" / "hinge_preferences.json"


class HingeProfileAnalyzer:
    def __init__(self):
        self.prefs = self.load_preferences()
        
    def load_preferences(self) -> Dict:
        """Load user preferences from config"""
        with open(PREFS_FILE) as f:
            return json.load(f)
    
    def analyze_profile(self, profile_data: Dict) -> Dict:
        """
        Analyze a profile and return scoring breakdown
        
        Args:
            profile_data: {
                'name': str,
                'age': int,
                'bio': str,
                'photos': [base64_encoded_images],
                'height': str (optional, e.g., "5'7\""),
                'distance': float (miles)
            }
        
        Returns:
            {
                'score': int (1-10),
                'breakdown': {
                    'age': score,
                    'height': score,
                    'hair': score,
                    'body': score,
                    'bio': score,
                    'distance': score
                },
                'reasoning': str,
                'decision': 'LIKE' | 'SKIP',
                'red_flags': [str],
                'green_flags': [str]
            }
        """
        breakdown = {}
        red_flags = []
        green_flags = []
        reasoning_parts = []
        
        # Age analysis
        age = profile_data.get('age')
        age_min, age_max = self.prefs['preferences']['age_range']
        if age and age_min <= age <= age_max:
            breakdown['age'] = 2
            reasoning_parts.append(f"Age {age} ✓")
        elif age:
            breakdown['age'] = 0
            reasoning_parts.append(f"Age {age} ✗ (want {age_min}-{age_max})")
        else:
            breakdown['age'] = 1
            reasoning_parts.append("Age unknown")
        
        # Height analysis
        height_score, height_reason = self.analyze_height(profile_data.get('height'))
        breakdown['height'] = height_score
        reasoning_parts.append(height_reason)
        
        # Distance analysis
        distance = profile_data.get('distance', 0)
        max_distance = self.prefs['preferences']['distance_max_miles']
        if distance <= max_distance:
            breakdown['distance'] = 1
            reasoning_parts.append(f"{distance:.1f}mi ✓")
        else:
            breakdown['distance'] = 0
            reasoning_parts.append(f"{distance:.1f}mi ✗ (want ≤{max_distance}mi)")
        
        # Bio analysis
        bio = profile_data.get('bio', '')
        bio_score, bio_flags = self.analyze_bio(bio)
        breakdown['bio'] = bio_score
        red_flags.extend(bio_flags['red'])
        green_flags.extend(bio_flags['green'])
        if bio_flags['red']:
            reasoning_parts.append(f"🚩 {', '.join(bio_flags['red'])}")
        if bio_flags['green']:
            reasoning_parts.append(f"✨ {', '.join(bio_flags['green'])}")
        
        # Photo analysis (vision-based)
        # This will be called separately with vision model
        # For now, placeholder
        breakdown['hair'] = 0  # Will be filled by vision analysis
        breakdown['body'] = 0  # Will be filled by vision analysis
        
        # Calculate total score
        total_score = sum(breakdown.values())
        max_score = 10  # 2 age + 2 height + 1 distance + 2 bio + 2 hair + 1 body
        normalized_score = min(10, round((total_score / max_score) * 10))
        
        # Decision
        skip_threshold = self.prefs['scoring']['skip_threshold']
        decision = 'LIKE' if normalized_score >= skip_threshold else 'SKIP'
        
        # Override: red flags auto-skip
        if red_flags:
            decision = 'SKIP'
            reasoning_parts.append(f"Auto-skip due to red flags")
        
        return {
            'score': normalized_score,
            'breakdown': breakdown,
            'reasoning': ' | '.join(reasoning_parts),
            'decision': decision,
            'red_flags': red_flags,
            'green_flags': green_flags
        }
    
    def analyze_height(self, height_str: Optional[str]) -> Tuple[int, str]:
        """
        Parse height string and score it
        
        Args:
            height_str: e.g., "5'7\"" or "5'7" or "67 inches"
        
        Returns:
            (score, reasoning)
        """
        if not height_str:
            return (1, "Height unknown")
        
        # Parse height to inches
        inches = self.parse_height_to_inches(height_str)
        if inches is None:
            return (1, f"Height '{height_str}' (unclear)")
        
        min_height, max_height = self.prefs['preferences']['height_range']
        
        if min_height <= inches <= max_height:
            feet = inches // 12
            remaining_inches = inches % 12
            return (2, f"{feet}'{remaining_inches}\" ✓")
        else:
            feet = inches // 12
            remaining_inches = inches % 12
            min_feet = min_height // 12
            min_inches = min_height % 12
            max_feet = max_height // 12
            max_inches = max_height % 12
            return (0, f"{feet}'{remaining_inches}\" ✗ (want {min_feet}'{min_inches}\"-{max_feet}'{max_inches}\")")
    
    def parse_height_to_inches(self, height_str: str) -> Optional[int]:
        """Convert height string to inches"""
        height_str = height_str.strip().lower()
        
        # Match patterns like "5'7\"" or "5'7" or "5 ft 7 in"
        match = re.match(r"(\d+)'?\s*['\"]?\s*(\d+)", height_str)
        if match:
            feet = int(match.group(1))
            inches = int(match.group(2))
            return feet * 12 + inches
        
        # Match patterns like "67 inches" or "67in"
        match = re.match(r"(\d+)\s*(?:inches|in)", height_str)
        if match:
            return int(match.group(1))
        
        # Match patterns like "5 feet"
        match = re.match(r"(\d+)\s*(?:feet|ft)", height_str)
        if match:
            return int(match.group(1)) * 12
        
        return None
    
    def analyze_bio(self, bio: str) -> Tuple[int, Dict[str, List[str]]]:
        """
        Analyze bio text for red flags and green flags
        
        Returns:
            (score, {'red': [flags], 'green': [flags]})
        """
        bio_lower = bio.lower()
        
        red_flags_found = []
        for flag in self.prefs['preferences']['red_flags']:
            if flag.lower() in bio_lower:
                red_flags_found.append(flag)
        
        green_flags_found = []
        for flag in self.prefs['preferences']['green_flags']:
            if flag.lower() in bio_lower:
                green_flags_found.append(flag)
        
        # Scoring
        if red_flags_found:
            score = 0  # Red flags = instant fail
        elif green_flags_found:
            score = 2  # Green flags = bonus
        elif len(bio) > 20:
            score = 1  # Has bio = neutral
        else:
            score = 1  # Empty/short bio = neutral
        
        return (score, {'red': red_flags_found, 'green': green_flags_found})
    
    def analyze_photos_with_vision(self, photos: List[str]) -> Dict:
        """
        Analyze photos using vision model
        
        Args:
            photos: List of base64-encoded images (or data URLs)
        
        Returns:
            {
                'hair_score': int,
                'body_score': int,
                'hair_analysis': str,
                'body_analysis': str
            }
        """
        # This would call the vision model
        # For now, return placeholder
        # In practice, you'd use the image tool to analyze photos
        
        if not photos:
            return {
                'hair_score': 1,
                'body_score': 1,
                'hair_analysis': 'No photos to analyze',
                'body_analysis': 'No photos to analyze'
            }
        
        # Vision prompt for Hinge profile analysis
        vision_prompt = f"""
        Analyze this dating profile photo. Provide:
        
        1. **Hair color**: blonde, light brown, dark brown, black, red, or other
        2. **Body type**: athletic, fit, average, slim, curvy, or plus-size
        3. **Confidence level**: How clear is the photo for assessment? (clear/unclear/group photo/poor lighting)
        
        Respond in this format:
        Hair: [color]
        Body: [type]
        Clarity: [clear/unclear/other]
        """
        
        # This is a placeholder - actual implementation would call vision model
        # You would use subprocess or API call to image tool
        
        return {
            'hair_score': 0,  # Will be updated by vision call
            'body_score': 0,  # Will be updated by vision call
            'hair_analysis': 'Vision analysis needed',
            'body_analysis': 'Vision analysis needed'
        }


def test_analyzer():
    """Test the analyzer with sample data"""
    analyzer = HingeProfileAnalyzer()
    
    # Test profile
    test_profile = {
        'name': 'Sarah',
        'age': 27,
        'bio': 'Love volleyball and staying active! Looking for someone who enjoys hiking and fitness.',
        'height': "5'7\"",
        'distance': 5.2,
        'photos': []  # Would be base64 encoded images
    }
    
    result = analyzer.analyze_profile(test_profile)
    
    print("=" * 60)
    print(f"Profile: {test_profile['name']}, {test_profile['age']}")
    print(f"Score: {result['score']}/10")
    print(f"Decision: {result['decision']}")
    print(f"Reasoning: {result['reasoning']}")
    if result['green_flags']:
        print(f"Green flags: {', '.join(result['green_flags'])}")
    if result['red_flags']:
        print(f"Red flags: {', '.join(result['red_flags'])}")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    test_analyzer()
