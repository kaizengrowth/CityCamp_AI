import logging
import os
from typing import List, Optional

import openai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class Representative(BaseModel):
    name: str
    position: str
    email: str
    district: Optional[str] = None
    phone: Optional[str] = None


class EmailComposeRequest(BaseModel):
    address: str
    issue: str
    tone: str  # 'formal', 'friendly', 'urgent'
    representatives: List[Representative]


class EmailComposition(BaseModel):
    subject: str
    body: str
    tone: str
    representatives: List[Representative]


# Sample representatives data - in production this would come from a database
TULSA_REPRESENTATIVES = [
    {
        "name": "G.T. Bynum",
        "position": "Mayor",
        "email": "mayor@cityoftulsa.org",
        "phone": "(918) 596-7777",
    },
    {
        "name": "Vanessa Hall-Harper",
        "position": "City Councilor - District 1",
        "email": "vhall-harper@cityoftulsa.org",
        "district": "District 1",
    },
    {
        "name": "Jeannie Cue",
        "position": "City Councilor - District 2",
        "email": "jcue@cityoftulsa.org",
        "district": "District 2",
    },
    {
        "name": "Phil Lakin",
        "position": "City Councilor - District 3",
        "email": "plakin@cityoftulsa.org",
        "district": "District 3",
    },
    {
        "name": "Laura Bellis",
        "position": "City Councilor - District 4",
        "email": "lbellis@cityoftulsa.org",
        "district": "District 4",
    },
    {
        "name": "Eddie Huff",
        "position": "City Councilor - District 5",
        "email": "ehuff@cityoftulsa.org",
        "district": "District 5",
    },
    {
        "name": "Christian Bengel",
        "position": "City Councilor - District 6",
        "email": "cbengel@cityoftulsa.org",
        "district": "District 6",
    },
    {
        "name": "Lori Decter Wright",
        "position": "City Councilor - District 7",
        "email": "lwright@cityoftulsa.org",
        "district": "District 7",
    },
    {
        "name": "Hall Walker",
        "position": "City Councilor - District 8",
        "email": "hwalker@cityoftulsa.org",
        "district": "District 8",
    },
    {
        "name": "Jayme Fowler",
        "position": "City Councilor - District 9",
        "email": "jfowler@cityoftulsa.org",
        "district": "District 9",
    },
]


@router.get("/find")
async def find_representatives(address: str):
    """
    Find representatives for a given address.
    In production, this would use geocoding and district mapping APIs.
    For now, returns all Tulsa representatives.
    """
    try:
        # In a real implementation, you would:
        # 1. Geocode the address to get coordinates
        # 2. Determine which council district the address is in
        # 3. Return the specific councilor + mayor

        # For demo purposes, return a subset of representatives
        return {
            "representatives": TULSA_REPRESENTATIVES[:3],  # Mayor + first 2 councilors
            "address": address,
        }
    except Exception as e:
        logger.error(f"Error finding representatives: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Unable to find representatives for this address"
        )


@router.post("/compose-email")
async def compose_email(request: EmailComposeRequest) -> EmailComposition:
    """
    Generate an AI-powered email to city representatives based on the user's concern.
    """
    try:
        # Use OpenAI for AI-powered email generation if available
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if openai_api_key:
            subject, body = await generate_ai_email(
                request.issue,
                request.tone,
                request.representatives[0] if request.representatives else None,
            )
        else:
            # Fallback to template-based generation
            subject, body = generate_template_email(
                request.issue,
                request.tone,
                request.representatives[0] if request.representatives else None,
            )

        return EmailComposition(
            subject=subject,
            body=body,
            tone=request.tone,
            representatives=request.representatives,
        )

    except Exception as e:
        logger.error(f"Error composing email: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Unable to generate email composition"
        )


async def generate_ai_email(
    issue: str, tone: str, representative: Optional[Representative]
) -> tuple[str, str]:
    """
    Use OpenAI to generate a professional email to city representatives.
    """
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")

        rep_info = (
            f"{representative.name} ({representative.position})"
            if representative
            else "the representative"
        )

        tone_instruction = {
            "formal": "formal and professional",
            "friendly": "friendly but respectful",
            "urgent": "urgent but respectful",
        }.get(tone, "professional")

        prompt = f"""
        Write a {tone_instruction} email to {rep_info} about the following civic issue:

        Issue: {issue}

        The email should:
        1. Have an appropriate subject line
        2. Be respectful and constructive
        3. Clearly explain the issue and its impact
        4. Request specific action or consideration
        5. Thank them for their service
        6. Include placeholders for sender contact information

        Return the response in the format:
        SUBJECT: [subject line]

        BODY: [email body]
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that helps citizens write effective emails to their elected officials.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.7,
        )

        content = response.choices[0].message.content.strip()

        # Parse the response
        if "SUBJECT:" in content and "BODY:" in content:
            parts = content.split("BODY:")
            subject = parts[0].replace("SUBJECT:", "").strip()
            body = parts[1].strip()
        else:
            # Fallback parsing
            lines = content.split("\n")
            subject = lines[0] if lines else "Concern from Constituent"
            body = "\n".join(lines[1:]) if len(lines) > 1 else content

        return subject, body

    except Exception as e:
        logger.error(f"Error with OpenAI API: {str(e)}")
        # Fallback to template-based generation
        return generate_template_email(issue, tone, representative)


def generate_template_email(
    issue: str, tone: str, representative: Optional[Representative]
) -> tuple[str, str]:
    """
    Generate email using templates when AI is not available.
    """
    # Generate subject based on issue keywords
    keywords = issue.lower()
    if "pothole" in keywords or "road" in keywords:
        subject = "Road Maintenance Concern"
    elif "park" in keywords or "recreation" in keywords:
        subject = "Parks and Recreation Matter"
    elif "traffic" in keywords:
        subject = "Traffic Safety Issue"
    elif "budget" in keywords or "tax" in keywords:
        subject = "Budget and Taxation Concern"
    else:
        subject = "Community Concern from Constituent"

    if tone == "urgent":
        subject = f"URGENT: {subject}"

    # Generate greeting based on tone and representative
    if representative:
        if tone == "formal":
            greeting = (
                f"Dear {representative.position} {representative.name.split(' ')[-1]},"
            )
        else:
            greeting = f"Hello {representative.name.split(' ')[0]},"
    else:
        greeting = "Dear Representative,"

    # Generate intro based on tone
    if tone == "formal":
        intro = "I am writing to bring to your attention an important matter affecting our community."
    elif tone == "urgent":
        intro = "I am reaching out regarding an urgent matter that requires immediate attention."
    else:
        intro = "I hope this message finds you well. I wanted to share a concern that affects our neighborhood."

    # Generate body
    body = f"""{greeting}

{intro}

{issue}

I would appreciate your consideration of this matter and any action you might be able to take to address this concern. As a constituent, I value your leadership and commitment to improving our community.

Thank you for your time and service to Tulsa.

Best regards,
[Your Name]
[Your Address]
[Your Phone Number]
[Your Email]"""

    return subject, body
