#!/usr/bin/env python3
"""
Test OpenAI Connection
Simple test to verify OpenAI API key is working correctly
"""

import os
import sys
from pathlib import Path

def test_openai_connection(api_key: str = None):
    """Test OpenAI API connection"""
    
    print("🧪 Testing OpenAI API Connection")
    print("=" * 40)
    
    # Set API key if provided
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key
        print("🔑 Using provided API key")
    elif os.environ.get('OPENAI_API_KEY'):
        print("🔑 Using API key from environment")
    else:
        print("❌ No OpenAI API key found!")
        print("   Use: python test_openai_connection.py --api-key YOUR_KEY")
        print("   Or set OPENAI_API_KEY environment variable")
        return False
    
    try:
        # Test direct OpenAI import
        print("\n1️⃣ Testing OpenAI library import...")
        from openai import OpenAI
        print("✅ OpenAI library imported successfully")
        
        # Test client initialization
        print("\n2️⃣ Testing OpenAI client initialization...")
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        print("✅ OpenAI client initialized successfully")
        
        # Test simple API call
        print("\n3️⃣ Testing simple API call...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use cheaper model for testing
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, API test successful!' and nothing else."}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ API call successful! Response: {result}")
        
        # Test AI categorization service
        print("\n4️⃣ Testing AI Categorization Service...")
        sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
        from app.services.ai_categorization_service import AICategorization
        
        ai_service = AICategorization()
        if ai_service.openai_client:
            print("✅ AI Categorization Service initialized successfully")
        else:
            print("❌ AI Categorization Service failed to initialize")
            return False
        
        # Test with sample content
        print("\n5️⃣ Testing AI categorization with sample content...")
        sample_content = """
        City Council Meeting - January 15, 2024
        The meeting was called to order at 4:00 PM.
        Agenda Item 1: Budget approval for downtown renovation project
        Council Member Smith voted yes, Council Member Jones voted no.
        Motion passed 3-2.
        """
        
        categories, keywords, summary, detailed_summary, voting_records, vote_stats = ai_service.categorize_content_with_ai(sample_content)
        
        print(f"✅ AI Categorization successful!")
        print(f"   Categories: {categories}")
        print(f"   Keywords: {keywords}")
        print(f"   Summary: {summary[:100]}...")
        print(f"   Voting Records: {len(voting_records)}")
        print(f"   Vote Statistics: {vote_stats}")
        
        print("\n🎉 All tests passed! OpenAI integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        
        # Common error diagnosis
        if "Incorrect API key" in str(e) or "Invalid API key" in str(e):
            print("\n🔍 Diagnosis: Invalid API key")
            print("   • Check your OpenAI API key is correct")
            print("   • Ensure you have credits in your OpenAI account")
            print("   • Verify the key has the right permissions")
        elif "quota" in str(e).lower():
            print("\n🔍 Diagnosis: Quota exceeded")
            print("   • You may have exceeded your OpenAI usage limits")
            print("   • Check your OpenAI dashboard for usage and billing")
        elif "model" in str(e).lower():
            print("\n🔍 Diagnosis: Model access issue")
            print("   • GPT-4 requires special access - try gpt-3.5-turbo first")
            print("   • Check your OpenAI account tier and model permissions")
        
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Test OpenAI API connection")
    parser.add_argument("--api-key", type=str, help="OpenAI API key to test")
    
    args = parser.parse_args()
    
    success = test_openai_connection(args.api_key)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 