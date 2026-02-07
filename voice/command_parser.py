#!/usr/bin/env python3
"""
Voice Command Parser - Natural speech to structured commands
Handles "Jarvis" wake word and various command patterns
"""

import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

@dataclass
class ParsedCommand:
    """Structured command representation"""
    category: str  # status, action, logging, guidance
    intent: str  # get_mrr, find_leads, log_workout, etc.
    parameters: Dict[str, Any]
    confidence: float
    raw_input: str

class VoiceCommandParser:
    def __init__(self):
        # Command patterns (intent -> list of regex patterns)
        self.patterns = {
            # Status queries
            "get_mrr": [
                r"what'?s? (?:my|the) mrr",
                r"(?:show|tell) (?:me )?(?:my|the) mrr",
                r"mrr status",
                r"monthly recurring revenue"
            ],
            "get_revenue": [
                r"what'?s? (?:my|the) revenue",
                r"how much (?:am i|have i) (?:making|made)",
                r"revenue status"
            ],
            "get_progress": [
                r"am i on track",
                r"(?:how'?s?|what'?s?) (?:my )?progress",
                r"(?:show|check) progress",
                r"where am i at"
            ],
            "get_next_task": [
                r"what should i (?:work on|do|build)",
                r"what'?s? next",
                r"(?:give me|suggest) (?:a )?task",
                r"what'?s? (?:my )?next (?:task|priority)"
            ],
            "check_launch": [
                r"how'?s? (?:the )?launch (?:going|status)",
                r"launch status",
                r"(?:show|check) launch"
            ],
            
            # Mode activation
            "activate_sales_mode": [
                r"(?:activate|start|enable) sales (?:mode)?",
                r"find (?:me )?(\d+) leads?",
                r"sales mode(?: with (\d+) leads)?",
                r"let'?s? sell",
                r"outreach time"
            ],
            "activate_build_mode": [
                r"(?:activate|start|enable) build (?:mode)?",
                r"let'?s? build",
                r"time to build"
            ],
            "activate_research_mode": [
                r"(?:activate|start|enable) research (?:mode)?",
                r"research mode",
                r"find competitors"
            ],
            
            # Data logging
            "log_workout": [
                r"log workout (.+)",
                r"track workout (.+)",
                r"(?:i )(?:did|completed) (.+) workout"
            ],
            "log_food": [
                r"log (?:food|meal) (.+)",
                r"ate (.+)",
                r"(?:i )?consumed (.+)"
            ],
            "log_win": [
                r"log win (.+)",
                r"(?:i )?(?:got|achieved|completed) (.+)",
                r"win:? (.+)"
            ],
            
            # Guidance
            "get_advice": [
                r"what (?:do you|should i) think",
                r"(?:give me )?advice",
                r"help me (?:decide|choose)"
            ],
            "check_accountability": [
                r"am i procrastinating",
                r"(?:check|show) accountability",
                r"keep me on track"
            ]
        }
        
        # Category mapping
        self.intent_categories = {
            "get_mrr": "status",
            "get_revenue": "status",
            "get_progress": "status",
            "get_next_task": "guidance",
            "check_launch": "status",
            "activate_sales_mode": "action",
            "activate_build_mode": "action",
            "activate_research_mode": "action",
            "log_workout": "logging",
            "log_food": "logging",
            "log_win": "logging",
            "get_advice": "guidance",
            "check_accountability": "guidance"
        }
    
    def parse(self, text: str) -> Optional[ParsedCommand]:
        """
        Parse natural language text into structured command
        
        Args:
            text: Raw voice input (e.g., "Jarvis what's my MRR")
        
        Returns:
            ParsedCommand or None if no match
        """
        # Normalize text
        text = text.lower().strip()
        
        # Remove wake word
        text = re.sub(r'^(?:hey |hi )?jarvis,? ', '', text)
        
        # Try to match against patterns
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Extract parameters
                    params = self._extract_parameters(intent, match, text)
                    
                    return ParsedCommand(
                        category=self.intent_categories.get(intent, "unknown"),
                        intent=intent,
                        parameters=params,
                        confidence=0.9,  # High confidence on regex match
                        raw_input=text
                    )
        
        # Fallback: fuzzy matching
        fuzzy_result = self._fuzzy_match(text)
        if fuzzy_result:
            return fuzzy_result
        
        return None
    
    def _extract_parameters(self, intent: str, match: re.Match, text: str) -> Dict[str, Any]:
        """Extract parameters from regex match"""
        params = {}
        
        # Handle specific intents with parameters
        if intent == "activate_sales_mode":
            # Extract number of leads
            if match.groups():
                try:
                    params["leads"] = int(match.group(1))
                except:
                    params["leads"] = 5  # default
            else:
                params["leads"] = 5
        
        elif intent in ["log_workout", "log_food", "log_win"]:
            # Extract description
            if match.groups():
                params["description"] = match.group(1).strip()
        
        return params
    
    def _fuzzy_match(self, text: str) -> Optional[ParsedCommand]:
        """Fuzzy matching for ambiguous commands"""
        # Simple keyword matching as fallback
        keywords = {
            "status": ["get_progress"],
            "mrr": ["get_mrr"],
            "revenue": ["get_revenue"],
            "leads": ["activate_sales_mode"],
            "build": ["activate_build_mode"],
            "workout": ["log_workout"],
            "track": ["check_accountability"]
        }
        
        for keyword, intents in keywords.items():
            if keyword in text:
                intent = intents[0]
                return ParsedCommand(
                    category=self.intent_categories.get(intent, "unknown"),
                    intent=intent,
                    parameters={},
                    confidence=0.6,  # Lower confidence for fuzzy match
                    raw_input=text
                )
        
        return None
    
    def get_supported_commands(self) -> List[Dict[str, str]]:
        """Get list of all supported commands with examples"""
        examples = {
            "get_mrr": "Jarvis what's my MRR",
            "get_revenue": "Jarvis how much am I making",
            "get_progress": "Jarvis am I on track",
            "get_next_task": "Jarvis what should I work on",
            "check_launch": "Jarvis how's the launch going",
            "activate_sales_mode": "Jarvis find 10 leads",
            "activate_build_mode": "Jarvis activate build mode",
            "log_workout": "Jarvis log workout shoulder press 180 pounds",
            "log_food": "Jarvis log food chicken breast and rice",
            "log_win": "Jarvis log win first paying customer",
            "get_advice": "Jarvis what do you think",
            "check_accountability": "Jarvis am I procrastinating"
        }
        
        return [
            {
                "intent": intent,
                "category": self.intent_categories[intent],
                "example": examples.get(intent, "")
            }
            for intent in self.patterns.keys()
        ]


# CLI interface
if __name__ == "__main__":
    import sys
    
    parser = VoiceCommandParser()
    
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        result = parser.parse(text)
        
        if result:
            print(f"✅ Parsed Command:")
            print(f"   Intent: {result.intent}")
            print(f"   Category: {result.category}")
            print(f"   Confidence: {result.confidence*100:.0f}%")
            if result.parameters:
                print(f"   Parameters: {result.parameters}")
        else:
            print("❌ Could not parse command")
            print("\nSupported commands:")
            for cmd in parser.get_supported_commands()[:5]:
                print(f"   • {cmd['example']}")
    else:
        print("Usage: python command_parser.py <command>")
        print("\nSupported commands:")
        for cmd in parser.get_supported_commands():
            print(f"   • {cmd['example']}")
