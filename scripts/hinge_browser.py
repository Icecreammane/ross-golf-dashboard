#!/usr/bin/env python3
"""
Hinge Browser Automation
Handles login, profile extraction, and swiping actions using Playwright
"""

import json
import time
import random
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import base64

WORKSPACE = Path("/Users/clawdbot/clawd")
PREFS_FILE = WORKSPACE / "data" / "hinge_preferences.json"
ACTIVITY_FILE = WORKSPACE / "data" / "hinge_activity.json"
SESSION_FILE = WORKSPACE / "data" / "hinge_session.json"


class HingeBrowser:
    def __init__(self):
        self.prefs = self.load_preferences()
        self.session = self.load_session()
        self.browser = None
        self.page = None
        
    def load_preferences(self) -> Dict:
        """Load user preferences"""
        with open(PREFS_FILE) as f:
            return json.load(f)
    
    def load_session(self) -> Dict:
        """Load saved session data"""
        if SESSION_FILE.exists():
            with open(SESSION_FILE) as f:
                return json.load(f)
        return {
            'cookies': None,
            'last_login': None,
            'login_method': None
        }
    
    def save_session(self):
        """Save session data"""
        with open(SESSION_FILE, 'w') as f:
            json.dump(self.session, f, indent=2)
    
    def save_preferences(self):
        """Save updated preferences"""
        with open(PREFS_FILE, 'w') as f:
            json.dump(self.prefs, f, indent=2)
    
    async def setup_browser(self, use_existing_session: bool = True):
        """
        Initialize Playwright browser
        
        NOTE: This requires Playwright to be installed:
        pip install playwright
        playwright install chromium
        """
        from playwright.async_api import async_playwright
        
        self.playwright = await async_playwright().start()
        
        # Use persistent context to maintain login
        user_data_dir = WORKSPACE / "data" / "hinge_browser_profile"
        user_data_dir.mkdir(exist_ok=True)
        
        self.browser = await self.playwright.chromium.launch_persistent_context(
            str(user_data_dir),
            headless=False,  # Show browser for debugging
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        self.page = await self.browser.new_page()
        
    async def login(self, phone_number: Optional[str] = None):
        """
        Login to Hinge
        
        Hinge login flow:
        1. Go to web.hinge.co
        2. Enter phone number
        3. Enter verification code (user must provide)
        4. Save session
        
        NOTE: This requires manual intervention for the verification code
        """
        print("🔐 Logging into Hinge...")
        
        await self.page.goto('https://web.hinge.co/')
        await asyncio.sleep(3)
        
        # Check if already logged in
        if await self.page.locator('text="Discover"').count() > 0:
            print("✅ Already logged in!")
            self.session['last_login'] = datetime.now().isoformat()
            self.save_session()
            return True
        
        # If not logged in, user needs to login manually
        print("\n" + "=" * 60)
        print("⚠️  MANUAL LOGIN REQUIRED")
        print("=" * 60)
        print("Please log into Hinge in the browser window that opened.")
        print("The script will wait for you to complete login...")
        print("=" * 60)
        
        # Wait for login to complete (detect "Discover" button)
        try:
            await self.page.wait_for_selector('text="Discover"', timeout=120000)  # 2 minute timeout
            print("✅ Login successful!")
            self.session['last_login'] = datetime.now().isoformat()
            self.save_session()
            return True
        except Exception as e:
            print(f"❌ Login timeout or failed: {e}")
            return False
    
    async def extract_profile_data(self) -> Optional[Dict]:
        """
        Extract current profile data from the page
        
        Returns profile dict or None if no more profiles
        """
        try:
            # Wait for profile card to load
            await self.page.wait_for_selector('[class*="profile"]', timeout=5000)
            await asyncio.sleep(1)
            
            profile = {}
            
            # Extract name and age
            name_element = await self.page.query_selector('[class*="name"]')
            if name_element:
                name_text = await name_element.inner_text()
                # Format usually: "Sarah, 27"
                parts = name_text.split(',')
                if len(parts) >= 2:
                    profile['name'] = parts[0].strip()
                    profile['age'] = int(parts[1].strip())
                else:
                    profile['name'] = name_text.strip()
                    profile['age'] = None
            
            # Extract bio/prompts
            bio_parts = []
            prompts = await self.page.query_selector_all('[class*="prompt"]')
            for prompt in prompts:
                text = await prompt.inner_text()
                bio_parts.append(text)
            profile['bio'] = '\n'.join(bio_parts)
            
            # Extract height (if visible in vitals)
            height_element = await self.page.query_selector('text=/[0-9]\'[0-9]/')
            if height_element:
                profile['height'] = await height_element.inner_text()
            else:
                profile['height'] = None
            
            # Extract distance
            distance_element = await self.page.query_selector('[class*="distance"]')
            if distance_element:
                distance_text = await distance_element.inner_text()
                # Extract number from "5 miles away"
                import re
                match = re.search(r'(\d+(?:\.\d+)?)', distance_text)
                if match:
                    profile['distance'] = float(match.group(1))
            
            if 'distance' not in profile:
                profile['distance'] = 0
            
            # Extract photos (as base64 for vision analysis)
            photos = []
            img_elements = await self.page.query_selector_all('img[src*="hinge"]')
            for img in img_elements[:3]:  # Limit to first 3 photos
                try:
                    src = await img.get_attribute('src')
                    if src and src.startswith('http'):
                        # Download image and convert to base64
                        # For now, just store URL (vision analysis would fetch it)
                        photos.append(src)
                except:
                    pass
            
            profile['photos'] = photos
            profile['timestamp'] = datetime.now().isoformat()
            
            return profile
            
        except Exception as e:
            print(f"❌ Failed to extract profile: {e}")
            return None
    
    async def like_profile(self):
        """Click the 'Like' button"""
        try:
            # Find and click like button (usually a heart icon)
            like_button = await self.page.query_selector('[aria-label*="ike"], [class*="like"], button:has-text("Like")')
            if like_button:
                await like_button.click()
                await self.random_delay()
                return True
            else:
                print("⚠️  Like button not found")
                return False
        except Exception as e:
            print(f"❌ Failed to like: {e}")
            return False
    
    async def skip_profile(self):
        """Click the 'X' button"""
        try:
            skip_button = await self.page.query_selector('[aria-label*="ass"], [class*="skip"], button:has-text("Pass")')
            if skip_button:
                await skip_button.click()
                await self.random_delay()
                return True
            else:
                print("⚠️  Skip button not found")
                return False
        except Exception as e:
            print(f"❌ Failed to skip: {e}")
            return False
    
    async def random_delay(self):
        """Add human-like random delay"""
        if self.prefs['automation']['randomize_delays']:
            min_delay = self.prefs['automation']['min_delay_seconds']
            max_delay = self.prefs['automation']['max_delay_seconds']
            delay = random.uniform(min_delay, max_delay)
            await asyncio.sleep(delay)
        else:
            await asyncio.sleep(2)
    
    async def check_for_matches(self) -> List[Dict]:
        """
        Check for new matches
        
        Returns list of new match data
        """
        matches = []
        
        try:
            # Look for match notification/modal
            match_modal = await self.page.query_selector('[class*="match"], text="It\'s a Match"')
            if match_modal:
                # Extract match info
                match_data = await self.extract_profile_data()
                if match_data:
                    matches.append(match_data)
                
                # Close modal
                close_button = await self.page.query_selector('[aria-label*="lose"], button:has-text("Close")')
                if close_button:
                    await close_button.click()
                    await asyncio.sleep(1)
        except Exception as e:
            print(f"⚠️  Error checking matches: {e}")
        
        return matches
    
    async def close(self):
        """Clean up browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


async def test_browser():
    """Test browser automation"""
    browser = HingeBrowser()
    
    try:
        await browser.setup_browser()
        
        # Login
        login_success = await browser.login()
        if not login_success:
            print("❌ Login failed")
            return
        
        # Extract one profile
        print("\n🔍 Extracting profile data...")
        profile = await browser.extract_profile_data()
        if profile:
            print(f"\n✅ Extracted profile:")
            print(json.dumps(profile, indent=2))
        
        # Wait before closing
        await asyncio.sleep(3)
        
    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_browser())
