#!/usr/bin/env python3
"""
Script to seed sample campaigns in the database for testing
"""

import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import get_db
from app.models import Campaign, User
from sqlalchemy.orm import Session

def create_sample_campaigns():
    """Create sample campaigns for testing"""

    # Get database session
    db = next(get_db())

    try:
        # Find or create a user to be the campaign creator
        creator = db.query(User).filter(User.email == "admin@example.com").first()
        if not creator:
            print("No admin user found. Please create a user with email 'admin@example.com' first.")
            return

        # Sample campaigns data
        campaigns_data = [
            {
                "title": "Better Public Transit Initiative",
                "description": "Supporting improved bus routes and schedules for Tulsa residents. This campaign aims to increase frequency of bus services, add new routes to underserved areas, and improve accessibility features.",
                "short_description": "Improving bus routes and schedules for better public transportation",
                "category": "transportation",
                "tags": ["transit", "public transport", "accessibility", "urban planning"],
                "goals": "Increase bus frequency by 50%, add 5 new routes, and improve accessibility features",
                "target_signatures": 500,
                "current_signatures": 124,
                "status": "active",
                "is_public": True,
                "allow_new_members": True,
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=90),
            },
            {
                "title": "Parks & Recreation Funding",
                "description": "Increase funding for park maintenance and youth programs. Our city's parks are vital community spaces that need proper maintenance and programming to serve all residents effectively.",
                "short_description": "Increase funding for park maintenance and youth programs",
                "category": "environment",
                "tags": ["parks", "recreation", "youth", "community", "funding"],
                "goals": "Secure additional $500k annually for park maintenance and youth programming",
                "target_signatures": 250,
                "current_signatures": 87,
                "status": "active",
                "is_public": True,
                "allow_new_members": True,
                "start_date": datetime.utcnow() - timedelta(days=15),
                "end_date": datetime.utcnow() + timedelta(days=60),
            },
            {
                "title": "Affordable Housing Development",
                "description": "Advocate for more affordable housing options throughout Tulsa. Rising housing costs are displacing long-term residents and making it difficult for workers to live where they work.",
                "short_description": "Advocate for more affordable housing options",
                "category": "housing",
                "tags": ["housing", "affordable", "development", "zoning", "community"],
                "goals": "Promote policies for 1000+ affordable housing units over 3 years",
                "target_signatures": 750,
                "current_signatures": 203,
                "status": "active",
                "is_public": True,
                "allow_new_members": True,
                "start_date": datetime.utcnow() - timedelta(days=30),
                "end_date": datetime.utcnow() + timedelta(days=120),
            },
            {
                "title": "Complete Streets Initiative",
                "description": "Make Tulsa streets safer for pedestrians, cyclists, and public transit users. Complete streets are designed for all users, not just cars.",
                "short_description": "Make streets safer for all users",
                "category": "transportation",
                "tags": ["streets", "safety", "pedestrians", "cycling", "accessibility"],
                "goals": "Implement complete streets design on 20 major corridors",
                "target_signatures": 400,
                "current_signatures": 56,
                "status": "active",
                "is_public": True,
                "allow_new_members": True,
                "start_date": datetime.utcnow() - timedelta(days=7),
                "end_date": datetime.utcnow() + timedelta(days=100),
            }
        ]

        created_campaigns = []
        for campaign_data in campaigns_data:
            # Check if campaign already exists
            existing = db.query(Campaign).filter(Campaign.title == campaign_data["title"]).first()
            if existing:
                print(f"Campaign '{campaign_data['title']}' already exists, skipping...")
                continue

            # Create campaign
            campaign = Campaign(
                creator_id=creator.id,
                **campaign_data
            )

            db.add(campaign)
            created_campaigns.append(campaign)

        if created_campaigns:
            db.commit()
            print(f"\n✅ Successfully created {len(created_campaigns)} sample campaigns:")
            for campaign in created_campaigns:
                print(f"   - {campaign.title}")
        else:
            print("\n✅ All sample campaigns already exist in the database")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating sample campaigns: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seeding sample campaigns...")
    create_sample_campaigns()
    print("\n🎉 Sample campaign seeding complete!")
