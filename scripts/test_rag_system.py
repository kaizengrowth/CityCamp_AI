#!/usr/bin/env python3
"""
Test script for the RAG (Retrieval-Augmented Generation) system.
This script demonstrates how to upload documents and test the RAG functionality.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.core.config import Settings
from app.core.database import SessionLocal
from app.services.document_processing_service import DocumentProcessingService
from app.services.vector_service import VectorService


async def create_sample_document():
    """Create a sample Tulsa government document for testing"""
    sample_content = """
    CITY OF TULSA
    BUDGET SUMMARY 2024

    EXECUTIVE SUMMARY

    The City of Tulsa's 2024 budget reflects our commitment to public safety, infrastructure
    improvements, and community development. This budget allocates $850 million across various
    departments and initiatives.

    MAJOR ALLOCATIONS:

    Public Safety: $320 million
    - Police Department: $180 million
    - Fire Department: $140 million

    Infrastructure: $200 million
    - Streets and Transportation: $120 million
    - Water and Sewer: $80 million

    Parks and Recreation: $45 million
    - Park Maintenance: $25 million
    - Recreation Programs: $20 million

    Economic Development: $35 million
    - Small Business Support: $15 million
    - Downtown Revitalization: $20 million

    CAPITAL PROJECTS:

    1. Riverside Drive Improvements - $25 million
    2. New Fire Station Construction - $8 million
    3. Park Renovations - $12 million
    4. Technology Infrastructure - $15 million

    REVENUE SOURCES:

    Property Taxes: $400 million (47%)
    Sales Taxes: $250 million (29%)
    Utility Fees: $120 million (14%)
    Federal Grants: $80 million (10%)

    This budget prioritizes essential services while investing in Tulsa's future growth
    and sustainability. The allocation reflects community input gathered through public
    meetings and surveys conducted throughout 2023.
    """

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_content)
        return f.name


async def test_document_processing():
    """Test document processing and RAG functionality"""
    print("🚀 Testing RAG System for Tulsa CityCamp AI")
    print("=" * 50)

    # Initialize services
    settings = Settings()
    db = SessionLocal()

    try:
        # Create sample document
        print("📄 Creating sample Tulsa budget document...")
        doc_path = await create_sample_document()

        # Process document
        print("⚙️  Processing document...")
        processing_service = DocumentProcessingService(settings, db)

        document_data = {
            'title': 'City of Tulsa Budget Summary 2024',
            'document_type': 'budget',
            'category': 'finance',
            'tags': ['budget', '2024', 'finance', 'public safety', 'infrastructure'],
            'is_public': True,
            'uploaded_by': 1  # Assuming admin user exists
        }

        document = await processing_service.process_document(doc_path, document_data)

        if document:
            print(f"✅ Document processed successfully!")
            print(f"   - Document ID: {document.id}")
            print(f"   - Title: {document.title}")
            print(f"   - Type: {document.document_type}")
            print(f"   - Chunks: {document.chunk_count}")
            print(f"   - Status: {document.processing_status}")
            print(f"   - Summary: {document.summary[:100]}...")
            print(f"   - Keywords: {', '.join(document.keywords[:5])}")
        else:
            print("❌ Document processing failed")
            return

        # Test vector search
        print("\n🔍 Testing vector search...")
        vector_service = VectorService(settings)

        test_queries = [
            "What is the budget for public safety?",
            "How much money is allocated for infrastructure?",
            "Tell me about park funding",
            "What are the revenue sources for the city?"
        ]

        for query in test_queries:
            print(f"\n📝 Query: '{query}'")
            results = await vector_service.search_documents(query, top_k=2)

            if results:
                for i, result in enumerate(results, 1):
                    similarity = result.get('similarity', 0)
                    content = result.get('content', '')
                    print(f"   Result {i} (similarity: {similarity:.3f}):")
                    print(f"   {content[:150]}...")
            else:
                print("   No results found")

        print("\n🎉 RAG system test completed successfully!")

        # Clean up
        try:
            os.unlink(doc_path)
        except OSError:
            pass

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


async def test_chatbot_integration():
    """Test the chatbot with RAG integration"""
    print("\n🤖 Testing Chatbot with RAG Integration")
    print("=" * 50)

    from app.services.chatbot_service import ChatbotService

    settings = Settings()
    db = SessionLocal()

    try:
        chatbot = ChatbotService(db, settings)

        test_messages = [
            "What is Tulsa's budget for public safety?",
            "How much does the city spend on infrastructure?",
            "Tell me about Tulsa's park funding"
        ]

        for message in test_messages:
            print(f"\n💬 User: {message}")

            try:
                response = await chatbot.get_ai_response(message)
                print(f"🤖 Bot: {response}")
            except Exception as e:
                print(f"❌ Error: {e}")

    except Exception as e:
        print(f"❌ Chatbot test failed: {e}")

    finally:
        db.close()


def print_architecture_overview():
    """Print an overview of the RAG architecture"""
    print("\n📋 RAG System Architecture Overview")
    print("=" * 50)
    print("""
    🏗️  COMPONENTS:

    1. Document Models (SQLAlchemy)
       - Document: Stores document metadata and full text
       - DocumentChunk: Text chunks for vector search
       - DocumentCollection: Organize documents into collections

    2. Vector Database (ChromaDB/FAISS)
       - Stores embeddings for semantic search
       - Supports similarity search and filtering

    3. Document Processing Service
       - Extracts text from PDFs, DOCX, TXT files
       - Chunks text for optimal retrieval
       - Generates summaries and keywords using OpenAI

    4. Vector Service
       - Generates embeddings using OpenAI text-embedding-3-small
       - Manages vector storage and search operations

    5. Enhanced Chatbot Service
       - Integrates RAG with existing chatbot
       - Uses function calling to search documents
       - Provides contextual responses based on city documents

    6. Document Management API
       - Upload, search, and manage documents
       - Admin endpoints for document processing
       - Public endpoints for document discovery

    📊 WORKFLOW:

    1. Document Upload → Text Extraction → Chunking
    2. Generate Embeddings → Store in Vector DB
    3. User Query → Generate Query Embedding
    4. Vector Search → Retrieve Relevant Chunks
    5. Combine with Context → Generate Response

    🎯 USE CASES:

    - Search city budgets, policies, legislation
    - Get answers about city services and procedures
    - Find relevant meeting minutes and decisions
    - Discover city planning documents and reports
    """)


async def main():
    """Main test function"""
    print_architecture_overview()

    # Test basic functionality
    await test_document_processing()

    # Test chatbot integration (if OpenAI is configured)
    settings = Settings()
    if settings.is_openai_configured:
        await test_chatbot_integration()
    else:
        print("\n⚠️  OpenAI not configured - skipping chatbot test")

    print("\n🏁 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
