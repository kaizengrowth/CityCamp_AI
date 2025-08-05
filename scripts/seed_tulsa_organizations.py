#!/usr/bin/env python3
"""
Seed Tulsa Organizations
Populate the database with real Tulsa community organizations including Community Outreach Plan partners
"""

import os
import sys
import argparse
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


# Comprehensive Tulsa Organizations Data including Community Outreach Plan
TULSA_ORGANIZATIONS = [
    # Original community organizations
    {
        "name": "Tulsa Community Foundation",
        "slug": "tulsa-community-foundation",
        "description": "The Tulsa Community Foundation connects generous people with nonprofits and causes they care about to strengthen our community. Since 1952, we have awarded more than $700 million in grants and scholarships to build a stronger, more equitable Tulsa region.",
        "short_description": "Connecting generous people with causes to strengthen Tulsa since 1952.",
        "website_url": "https://www.tulsacf.org",
        "organization_type": "nonprofit",
        "focus_areas": ["community_building", "economic_development", "education", "arts_culture"],
        "service_areas": ["Greater Tulsa Area", "Northeastern Oklahoma"],
        "founded_year": 1952,
        "is_verified": True,
        "contact_email": "info@tulsacf.org",
        "address": "7030 S Yale Ave #600, Tulsa, OK 74136"
    },
    {
        "name": "Housing Partners of Tulsa",
        "slug": "housing-partners-tulsa",
        "description": "Housing Partners of Tulsa works to create and preserve affordable housing opportunities for low and moderate-income families, seniors, and individuals with special needs. We develop innovative housing solutions and provide homeownership counseling services.",
        "short_description": "Creating affordable housing opportunities for Tulsa families.",
        "website_url": "https://www.housingpartnersoftulsa.org",
        "organization_type": "nonprofit",
        "focus_areas": ["housing", "social_justice", "community_building"],
        "founded_year": 1995,
        "is_verified": True,
        "contact_email": "info@housingpartnersoftulsa.org"
    },
    {
        "name": "Tulsa Area United Way",
        "slug": "tulsa-area-united-way",
        "description": "United Way of Metropolitan Tulsa fights for the health, education and financial stability of every person in our community. We focus on creating long-lasting change by addressing the underlying causes of problems through strategic partnerships and community investment.",
        "short_description": "Fighting for health, education, and financial stability in Tulsa.",
        "website_url": "https://www.unitedwaytulsa.org",
        "organization_type": "nonprofit",
        "focus_areas": ["education", "healthcare", "economic_development", "social_justice"],
        "founded_year": 1924,
        "is_verified": True,
        "member_count": 50000
    },
    {
        "name": "Mental Health Association Oklahoma",
        "slug": "mha-oklahoma",
        "description": "Mental Health Association Oklahoma promotes mental wellness through advocacy, education, and support services. We work to reduce stigma and improve access to mental health care while providing crisis intervention and community education programs.",
        "short_description": "Promoting mental wellness through advocacy and education.",
        "website_url": "https://www.mhaok.org",
        "organization_type": "nonprofit",
        "focus_areas": ["healthcare", "social_justice", "education"],
        "founded_year": 1950,
        "is_verified": True
    },
    {
        "name": "Tulsa Remote",
        "slug": "tulsa-remote",
        "description": "Tulsa Remote is a program that brings remote workers to Tulsa by providing financial incentives and community support, helping to grow Tulsa's population and economy. The program offers $10,000 grants, community events, and professional networking opportunities.",
        "short_description": "Bringing remote workers to Tulsa to grow our community.",
        "website_url": "https://www.tulsaremote.com",
        "organization_type": "economic_development",
        "focus_areas": ["economic_development", "community_building"],
        "founded_year": 2018,
        "is_verified": True,
        "member_count": 3000
    },

    # Community Outreach Plan Organizations
    {
        "name": "Terrence Crutcher Foundation",
        "slug": "terrence-crutcher-foundation",
        "description": "The Terrence Crutcher Foundation works to improve police and community relations through education, advocacy, and community engagement. Founded in memory of Terence Crutcher, we focus on police violence prevention, mental health outreach, and supporting families affected by police violence in Tulsa's Black communities.",
        "short_description": "Neighborhood organizing in Tulsa's Black communities, focusing on police violence and mental health outreach.",
        "website_url": "https://www.tcrucherfoundation.org",
        "organization_type": "advocacy",
        "focus_areas": ["social_justice", "public_safety", "community_building", "healthcare"],
        "service_areas": ["North Tulsa", "Tulsa Metro"],
        "founded_year": 2016,
        "is_verified": True,
        "organization_type": "nonprofit"
    },
    {
        "name": "Growing Together Tulsa",
        "slug": "growing-together-tulsa",
        "description": "Growing Together Tulsa is a resident-led organization focused on education and housing advocacy in the Kendall-Whittier neighborhood. We work to strengthen our community through neighborhood organizing, educational programs, and affordable housing initiatives that preserve our historic character.",
        "short_description": "Resident-led education and housing advocacy centered on Tulsa's Kendall-Whittier neighborhood.",
        "website_url": "https://www.growingtogethertulsa.org",
        "organization_type": "community_group",
        "focus_areas": ["education", "housing", "community_building", "historic_preservation"],
        "service_areas": ["Kendall-Whittier"],
        "is_verified": True
    },
    {
        "name": "South Tulsa Community House",
        "slug": "south-tulsa-community-house",
        "description": "South Tulsa Community House provides vital services like food assistance, computer access, and legal aid to residents of Riverwood and surrounding neighborhoods. We serve as a community hub offering emergency assistance, educational programs, and advocacy for one of Tulsa's most high-need areas.",
        "short_description": "Providing vital services like food, computer access, and legal aid in Riverwood, one of Tulsa's most high-need neighborhoods.",
        "website_url": "https://www.stulsa.org",
        "organization_type": "nonprofit",
        "focus_areas": ["social_justice", "community_building", "economic_development", "education"],
        "service_areas": ["Riverwood", "South Tulsa"],
        "is_verified": True,
        "contact_email": "info@stulsa.org"
    },
    {
        "name": "El Centro",
        "slug": "el-centro-tulsa",
        "description": "El Centro offers immigrant education and resource services in East Tulsa, providing ESL classes, citizenship preparation, community advocacy, and family support services. We serve as a cultural bridge helping immigrant families integrate while preserving their heritage and addressing systemic barriers.",
        "short_description": "Offers immigrant education & resource services in East Tulsa.",
        "website_url": "https://www.elcentrotulsa.org",
        "organization_type": "nonprofit",
        "focus_areas": ["education", "social_justice", "community_building"],
        "service_areas": ["East Tulsa"],
        "is_verified": True,
        "contact_email": "info@elcentrotulsa.org"
    },
    {
        "name": "Zomi Community USA - Tulsa Chapter",
        "slug": "zomi-community-usa-tulsa",
        "description": "Zomi Community USA provides resources and support to the Burmese immigrant enclave in South Tulsa. We offer cultural preservation programs, English language learning, job placement assistance, and community advocacy to help Zomi and other Burmese families thrive in their new home.",
        "short_description": "Provides resources to the Burmese immigrant enclave in South Tulsa.",
        "website_url": "https://www.zomicommunityusa.org",
        "organization_type": "cultural",
        "focus_areas": ["education", "community_building", "social_justice", "economic_development"],
        "service_areas": ["South Tulsa"],
        "is_verified": True
    },
    {
        "name": "Emergency Infant Services",
        "slug": "emergency-infant-services",
        "description": "Emergency Infant Services has broad reach among low-income families across Tulsa, providing mothers with essential resources for childcare, including diapers, formula, baby clothing, and parenting education. We work to ensure every baby has what they need to thrive during their critical early months.",
        "short_description": "Broad reach among low-income families across Tulsa, providing mothers with resources for childcare.",
        "website_url": "https://www.emergencyinfantservices.org",
        "organization_type": "nonprofit",
        "focus_areas": ["healthcare", "social_justice", "youth_development"],
        "service_areas": ["Tulsa Metro"],
        "founded_year": 1983,
        "is_verified": True,
        "contact_email": "info@emergencyinfantservices.org"
    },
    {
        "name": "Take Control Initiative",
        "slug": "take-control-initiative",
        "description": "Take Control Initiative promotes women's healthcare access with a strong community outreach presence throughout Tulsa. We provide reproductive health education, contraceptive access, STI testing, and advocacy for comprehensive women's health services, particularly in underserved communities.",
        "short_description": "Promotes women's healthcare access, with a strong outreach presence.",
        "website_url": "https://www.takecontrolok.org",
        "organization_type": "advocacy",
        "focus_areas": ["healthcare", "social_justice", "education"],
        "service_areas": ["Tulsa Metro"],
        "is_verified": True
    },
    {
        "name": "Oklahomans for Equality",
        "slug": "oklahomans-for-equality",
        "description": "Oklahomans for Equality (OkEq) serves as a center for LGBTQ+ community organizing and civic engagement in Tulsa. We provide advocacy, education, support services, and community events while working to advance equality and protect civil rights for LGBTQ+ individuals and families.",
        "short_description": "Center for LGBTQ+ community organizing and civic engagement.",
        "website_url": "https://www.okeq.org",
        "organization_type": "advocacy",
        "focus_areas": ["social_justice", "community_building", "education"],
        "service_areas": ["Tulsa Metro", "Oklahoma"],
        "founded_year": 1980,
        "is_verified": True,
        "contact_email": "info@okeq.org"
    },

    # Additional established Tulsa organizations
    {
        "name": "Tulsa Preservation Commission",
        "slug": "tulsa-preservation-commission",
        "description": "The Tulsa Preservation Commission works to identify, evaluate, designate and preserve buildings, structures, objects, districts and areas of historical, architectural or cultural significance. We promote heritage tourism and ensure Tulsa's architectural legacy is protected for future generations.",
        "short_description": "Preserving Tulsa's historic buildings and cultural heritage.",
        "website_url": "https://www.cityoftulsa.org/government/boards-authorities-commissions/tulsa-preservation-commission/",
        "organization_type": "advocacy",
        "focus_areas": ["historic_preservation", "arts_culture", "community_building"],
        "is_verified": True
    },
    {
        "name": "Kendall Whittier Main Street",
        "slug": "kendall-whittier-main-street",
        "description": "Kendall Whittier Main Street is a grassroots economic development organization working to revitalize the historic Kendall Whittier neighborhood through business development, historic preservation, and community engagement. We support local entrepreneurs and preserve our neighborhood's unique character.",
        "short_description": "Revitalizing the historic Kendall Whittier neighborhood.",
        "website_url": "https://www.kendallwhittier.org",
        "organization_type": "community_group",
        "focus_areas": ["economic_development", "historic_preservation", "community_building"],
        "service_areas": ["Kendall Whittier"],
        "is_verified": True
    },
    {
        "name": "Brady Arts District Association",
        "slug": "brady-arts-district",
        "description": "The Brady Arts District Association promotes and supports the arts, culture, and entertainment in Tulsa's premier arts district, fostering creativity and economic development. We coordinate events, support local artists, and advocate for the cultural vitality of downtown Tulsa.",
        "short_description": "Promoting arts, culture, and entertainment in Tulsa's premier arts district.",
        "website_url": "https://www.bradyartsdistrict.com",
        "organization_type": "business_association",
        "focus_areas": ["arts_culture", "economic_development", "community_building"],
        "service_areas": ["Brady Arts District"],
        "is_verified": True
    },
    {
        "name": "INCOG - Indian Nations Council of Governments",
        "slug": "incog",
        "description": "INCOG is a voluntary association of local governments serving the Tulsa metropolitan area, providing planning, coordination, and technical assistance to member communities. We facilitate regional cooperation on transportation, economic development, and environmental planning initiatives.",
        "short_description": "Regional planning and coordination for the Tulsa metro area.",
        "website_url": "https://www.incog.org",
        "organization_type": "advocacy",
        "focus_areas": ["transportation", "economic_development", "government_accountability"],
        "service_areas": ["Tulsa Metropolitan Area"],
        "is_verified": True
    }
]


def seed_organizations(aws_db_url: str = None, dry_run: bool = True):
    """Seed the database with Tulsa organizations including Community Outreach Plan partners"""
    
    print("🌱 Seeding Tulsa Organizations Database")
    print("=" * 50)
    
    # Set database URL if provided
    if aws_db_url:
        os.environ['DATABASE_URL'] = aws_db_url
        print(f"🔗 Using AWS Database: {aws_db_url.split('@')[1] if '@' in aws_db_url else 'configured'}")
    else:
        print("🔗 Using local database configuration")
    
    print(f"🔍 Mode: {'DRY RUN' if dry_run else 'LIVE SEEDING'}")
    print(f"📋 Organizations to add: {len(TULSA_ORGANIZATIONS)}")
    print()
    
    try:
        from app.core.database import SessionLocal
        from app.models.organization import Organization
        
        db = SessionLocal()
        
        added_count = 0
        skipped_count = 0
        
        for i, org_data in enumerate(TULSA_ORGANIZATIONS, 1):
            print(f"🏛️ [{i}/{len(TULSA_ORGANIZATIONS)}] {org_data['name']}")
            
            # Check if organization already exists
            existing_org = db.query(Organization).filter(Organization.slug == org_data['slug']).first()
            
            if existing_org:
                print(f"   ⏭️  Already exists, skipping")
                skipped_count += 1
                continue
            
            if not dry_run:
                # Create new organization
                organization = Organization(**org_data)
                db.add(organization)
                db.commit()
                db.refresh(organization)
                print(f"   ✅ Created organization #{organization.id}")
                added_count += 1
            else:
                print(f"   🔍 Would create: {org_data.get('organization_type', 'unknown')} | {', '.join(org_data.get('focus_areas', []))}")
        
        if not dry_run:
            db.close()
        
        # Summary
        print("\n📊 Seeding Summary:")
        print(f"   Organizations processed: {len(TULSA_ORGANIZATIONS)}")
        if not dry_run:
            print(f"   Successfully added: {added_count}")
        print(f"   Already existed: {skipped_count}")
        
        if dry_run:
            print("\n🔍 This was a dry run. Use --apply to create organizations.")
        else:
            print(f"\n✅ Successfully seeded {added_count} Tulsa organizations!")
        
        print("\n🎯 Organization Types Added:")
        type_counts = {}
        for org in TULSA_ORGANIZATIONS:
            org_type = org.get('organization_type', 'unknown')
            type_counts[org_type] = type_counts.get(org_type, 0) + 1
        
        for org_type, count in sorted(type_counts.items()):
            print(f"   • {org_type.replace('_', ' ').title()}: {count}")

        print("\n🤝 Community Outreach Plan Organizations:")
        outreach_orgs = [
            "Terrence Crutcher Foundation", "Growing Together Tulsa", "South Tulsa Community House",
            "El Centro", "Zomi Community USA - Tulsa Chapter", "Emergency Infant Services", 
            "Take Control Initiative", "Oklahomans for Equality"
        ]
        for org_name in outreach_orgs:
            print(f"   ✅ {org_name}")
            
    except Exception as e:
        print(f"❌ Seeding failed: {str(e)}")
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Seed Tulsa organizations database")
    parser.add_argument("--aws-db-url", type=str, help="AWS RDS database URL")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry run)")
    
    args = parser.parse_args()
    
    success = seed_organizations(args.aws_db_url, dry_run=not args.apply)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 