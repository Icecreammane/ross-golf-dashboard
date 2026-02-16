#!/usr/bin/env python3
"""
Auto Job Application System
Pre-fills job applications and generates custom cover letters

Flow:
1. Load high-rated jobs (8+) from job_matches.json
2. Generate custom cover letter for each
3. Create draft application package
4. Save for Ross's review
5. Optionally: Pre-fill forms with Playwright (when URLs support it)

Safety: NEVER auto-submit without explicit approval
"""

import json
import sys
from datetime import datetime
from pathlib import Path
import subprocess
from typing import Dict, List

# Paths
WORKSPACE = Path.home() / "clawd"
DATA_DIR = WORKSPACE / "data"
APPLICATIONS_DIR = WORKSPACE / "applications"
APPLICATIONS_FILE = DATA_DIR / "applications.json"
RESUME_PATH = Path.home() / "Documents" / "resume.pdf"

# Ensure directories exist
APPLICATIONS_DIR.mkdir(exist_ok=True)

# Ross's Profile
PROFILE = {
    "name": "Ross Caster",
    "email": "ross.caster@example.com",  # TODO: Update with real email
    "phone": "(615) 555-0123",  # TODO: Update with real phone
    "linkedin": "https://www.linkedin.com/in/rosscaster",
    "current_title": "Senior Product Development Scientist",
    "current_company": "Mars Petcare",
    "years_experience": 5,
    "education": "Bachelor of Science in Food Science",
    "location": "Nashville, TN",
    "willing_to_relocate": "Florida",
    "experience_summary": """
Senior Product Development Scientist at Mars Petcare with 5+ years of experience 
in R&D formulation and product innovation. Led successful projects including Nutro 
renovation and IAMS NCH development. Deep expertise in food science applications, 
nutritional formulation, and bringing products from concept through commercialization.
    """.strip(),
    "key_achievements": [
        "Led Nutro renovation project resulting in improved nutritional profile",
        "Developed IAMS NCH formulations with enhanced palatability",
        "Managed Portfolio Architecture initiatives across multiple product lines",
        "Expertise in sensory evaluation and consumer testing",
        "Cross-functional team leadership and project management"
    ],
    "skills": [
        "R&D Formulation", "Product Development", "Food Science",
        "Pet Food Development", "Nutritional Formulation", "Sensory Evaluation",
        "Quality Assurance", "Regulatory Compliance", "Process Optimization",
        "Project Management", "Cross-functional Leadership"
    ]
}


def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def load_json_safe(filepath, default=None):
    """Safely load JSON file"""
    try:
        if Path(filepath).exists():
            with open(filepath, 'r') as f:
                return json.load(f)
    except Exception as e:
        log(f"Error loading {filepath}: {e}")
    return default


def generate_cover_letter(job: Dict) -> str:
    """
    Generate personalized cover letter using template
    (Ollama disabled for speed - can enable later if needed)
    """
    
    # Use template for fast generation
    # TODO: Enable Ollama for more natural letters after testing
    cover_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job['title']} position at {job['company']}. With my current role as a Senior Product Development Scientist at Mars Petcare, I have developed extensive experience in R&D formulation and product innovation that aligns perfectly with your requirements.

In my tenure at Mars, I have successfully led product development initiatives including the Nutro renovation project and IAMS NCH development. My work in Portfolio Architecture has given me a comprehensive understanding of bringing products from concept through commercialization. These experiences have honed my skills in formulation science, sensory evaluation, and cross-functional team leadership.

What excites me most about this opportunity at {job['company']} is the chance to contribute to innovative product development while relocating to Florida, which has been a personal goal. I am particularly drawn to {job['company']}'s commitment to quality and innovation in the industry.

Key qualifications I bring:
• 5+ years of R&D experience in food science and product development
• Proven track record in formulation optimization and product launches
• Deep expertise in nutritional science and sensory evaluation
• Strong project management and cross-functional collaboration skills
• Passion for innovation and continuous improvement

I am eager to bring my expertise in product development to {job['company']} and would welcome the opportunity to discuss how my background can contribute to your team's success.

Thank you for considering my application. I look forward to speaking with you soon.

Best regards,
{PROFILE['name']}
{PROFILE['current_title']}
{PROFILE['phone']}
{PROFILE['email']}"""
    
    return cover_letter


def create_application_package(job: Dict) -> Dict:
    """
    Create complete application package for a job
    Includes cover letter, resume reference, and pre-filled data
    """
    
    log(f"📝 Creating application for: {job['title']} at {job['company']}")
    
    # Generate cover letter
    cover_letter = generate_cover_letter(job)
    
    # Create application data
    application = {
        "job_id": f"{job['company'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}",
        "created_at": datetime.now().isoformat(),
        "status": "draft",
        "job": {
            "title": job['title'],
            "company": job['company'],
            "location": job['location'],
            "url": job.get('url', ''),
            "match_score": job.get('match_score', 0),
            "description": job.get('description', '')
        },
        "cover_letter": cover_letter,
        "resume_path": str(RESUME_PATH) if RESUME_PATH.exists() else "GENERATE_NEEDED",
        "form_data": {
            "first_name": PROFILE['name'].split()[0],
            "last_name": PROFILE['name'].split()[-1],
            "full_name": PROFILE['name'],
            "email": PROFILE['email'],
            "phone": PROFILE['phone'],
            "linkedin": PROFILE['linkedin'],
            "current_title": PROFILE['current_title'],
            "current_company": PROFILE['current_company'],
            "years_experience": PROFILE['years_experience'],
            "education": PROFILE['education'],
            "current_location": PROFILE['location'],
            "willing_to_relocate": True,
            "desired_location": PROFILE['willing_to_relocate']
        }
    }
    
    # Save individual application file
    app_file = APPLICATIONS_DIR / f"{application['job_id']}.json"
    with open(app_file, 'w') as f:
        json.dump(application, f, indent=2)
    
    log(f"   ✅ Application package saved: {app_file.name}")
    
    return application


def generate_applications():
    """
    Main function: Generate applications for high-rated jobs
    """
    
    log("🚀 Auto Job Application System - Starting")
    log("=" * 60)
    
    # Load job matches
    jobs_data = load_json_safe(DATA_DIR / "job_matches.json", {"jobs": []})
    jobs = jobs_data.get("jobs", [])
    
    # Filter for high-rated jobs (8+)
    high_rated = [j for j in jobs if j.get("match_score", 0) >= 8]
    high_rated = sorted(high_rated, key=lambda x: x.get("match_score", 0), reverse=True)
    
    if not high_rated:
        log("⚠️  No high-rated jobs (8+) found. Run job scan first.")
        return
    
    log(f"📊 Found {len(high_rated)} high-rated job(s) to process")
    log("")
    
    # Load existing applications tracker
    applications_data = load_json_safe(APPLICATIONS_FILE, {"applications": []})
    existing_apps = applications_data.get("applications", [])
    
    # Track which jobs already have applications
    existing_job_ids = {app['job_id'] for app in existing_apps}
    
    # Generate applications
    new_applications = []
    
    for job in high_rated:
        # Create job ID
        job_id = f"{job['company'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
        
        # Skip if already applied
        if job_id in existing_job_ids:
            log(f"⏭️  Skipping {job['title']} at {job['company']} (already applied)")
            continue
        
        # Create application
        application = create_application_package(job)
        new_applications.append(application)
    
    if not new_applications:
        log("✅ No new applications needed - all high-rated jobs already processed")
        return
    
    # Add to tracker
    applications_data['applications'].extend(new_applications)
    
    # Save tracker
    with open(APPLICATIONS_FILE, 'w') as f:
        json.dump(applications_data, f, indent=2)
    
    log("")
    log("=" * 60)
    log(f"✅ COMPLETE: {len(new_applications)} application(s) ready for review")
    log("=" * 60)
    log("")
    log("📂 Review applications:")
    for app in new_applications:
        log(f"   • {app['job']['title']} at {app['job']['company']}")
        log(f"     File: applications/{app['job_id']}.json")
    log("")
    log("🔍 Next steps:")
    log("   1. Review cover letters in applications/ directory")
    log("   2. Customize as needed")
    log("   3. Apply via company websites")
    log("   4. Update status in applications.json")


def show_pending_applications():
    """Show all pending applications"""
    
    applications_data = load_json_safe(APPLICATIONS_FILE, {"applications": []})
    apps = applications_data.get("applications", [])
    
    pending = [a for a in apps if a.get("status") == "draft"]
    
    if not pending:
        print("No pending applications")
        return
    
    print(f"\n📋 {len(pending)} Pending Application(s):\n")
    
    for app in pending:
        print(f"🔹 {app['job']['title']}")
        print(f"   Company: {app['job']['company']}")
        print(f"   Location: {app['job']['location']}")
        print(f"   Match Score: {app['job']['match_score']}/10")
        print(f"   URL: {app['job']['url']}")
        print(f"   File: applications/{app['job_id']}.json")
        print("")


def main():
    """CLI entry point"""
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 auto_job_apply.py generate   # Generate applications for high-rated jobs")
        print("  python3 auto_job_apply.py pending    # Show pending applications")
        return 1
    
    command = sys.argv[1]
    
    if command == "generate":
        generate_applications()
    elif command == "pending":
        show_pending_applications()
    else:
        print(f"Unknown command: {command}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
