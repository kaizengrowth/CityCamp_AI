# RAG System for CityCamp AI

A comprehensive Retrieval-Augmented Generation (RAG) system that enables the Tulsa civic chatbot to search and reference city documents, budgets, legislation, and policies.

## 🏗️ Architecture Overview

The RAG system consists of several integrated components that work together to provide accurate, document-based responses:

```
📄 Document Upload → 🔤 Text Extraction → ✂️ Chunking
                ↓
🧠 AI Analysis (Summary/Keywords) → 🔢 Generate Embeddings
                ↓
💾 Store in Vector DB ← 🗄️ Store in PostgreSQL
                ↓
🔍 User Query → 🎯 Vector Search → 📋 Retrieve Chunks
                ↓
🤖 Combine with Context → ✨ Generate AI Response
```

## 🧩 Components

### 1. Database Models
- **Document**: Stores document metadata, content, and processing status
- **DocumentChunk**: Text chunks optimized for vector search
- **DocumentCollection**: Organize documents into categories
- **DocumentCollectionMembership**: Many-to-many relationships

### 2. Vector Database
- **ChromaDB**: Local/development vector storage
- **FAISS**: High-performance production vector search
- **OpenAI Embeddings**: text-embedding-3-small model

### 3. Document Processing
- **Multi-format support**: PDF, DOCX, TXT files
- **Smart text extraction**: Multiple PDF parsing methods
- **Intelligent chunking**: Token-aware with overlap
- **AI enhancement**: Auto-generated summaries and keywords

### 4. Enhanced Chatbot
- **RAG integration**: Semantic document search
- **Function calling**: OpenAI function calling for document retrieval
- **Contextual responses**: Combines retrieved docs with AI generation

### 5. Document Management API
- **Upload endpoints**: Process and store documents
- **Search endpoints**: Vector-based document search
- **Admin endpoints**: Document management and reprocessing

## 🚀 Quick Start

### Prerequisites

1. **Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **OpenAI API Key**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

3. **Database Setup**
   ```bash
   # Run the database migration
   cd backend
   python -m alembic upgrade head
   ```

### Test the System

Run the comprehensive test script:

```bash
python scripts/test_rag_system.py
```

This will:
- Create a sample Tulsa budget document
- Process it through the RAG pipeline
- Test vector search functionality
- Demonstrate chatbot integration

## 📚 Usage Guide

### 1. Document Upload via API

```python
import requests

# Upload a document
files = {'file': open('tulsa_budget_2024.pdf', 'rb')}
data = {
    'title': 'Tulsa Budget 2024',
    'document_type': 'budget',
    'category': 'finance',
    'tags': 'budget,2024,finance',
    'is_public': True
}

response = requests.post(
    'http://localhost:8000/api/v1/documents/upload',
    files=files,
    data=data,
    headers={'Authorization': 'Bearer your-jwt-token'}
)
```

### 2. Search Documents

```python
import requests

# Search for documents
search_data = {
    'query': 'public safety budget allocation',
    'document_type': 'budget',
    'max_results': 5
}

response = requests.post(
    'http://localhost:8000/api/v1/documents/search',
    json=search_data
)

results = response.json()
for result in results['results']:
    print(f"Document: {result['document']['title']}")
    print(f"Relevance: {result['relevance_score']:.3f}")
    print(f"Excerpt: {result['excerpt'][:200]}...")
```

### 3. Chatbot Integration

The chatbot automatically uses the RAG system when users ask questions:

```
User: "What is Tulsa's budget for public safety?"
Bot: "Based on the 2024 budget documents, Tulsa has allocated $320 million for public safety, with $180 million for the Police Department and $140 million for the Fire Department."
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your-openai-api-key
DATABASE_URL=postgresql://user:pass@localhost/db

# Optional
VECTOR_STORE_TYPE=chromadb  # or 'faiss'
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
```

### Document Types

The system supports these document types:
- `budget`: City budgets and financial documents
- `legislation`: Ordinances, resolutions, policies
- `meeting_minutes`: City council and committee minutes
- `policy`: Administrative policies and procedures
- `report`: Studies, analyses, and reports
- `ordinance`: City ordinances and regulations

### Categories

Documents can be categorized by topic:
- `finance`: Budget and financial matters
- `transportation`: Roads, transit, infrastructure
- `housing`: Housing policies and programs
- `public_safety`: Police, fire, emergency services
- `utilities`: Water, sewer, electricity
- `parks`: Parks and recreation
- `planning`: Zoning and urban planning

## 📊 API Endpoints

### Document Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/documents/` | GET | List documents with filtering |
| `/api/v1/documents/{id}` | GET | Get specific document |
| `/api/v1/documents/search` | POST | Vector search documents |
| `/api/v1/documents/upload` | POST | Upload new document |
| `/api/v1/documents/{id}/reprocess` | POST | Reprocess document (admin) |
| `/api/v1/documents/{id}` | DELETE | Delete document (admin) |
| `/api/v1/documents/stats` | GET | Get document statistics |

### Example Responses

**Document List Response:**
```json
{
  "documents": [
    {
      "id": 1,
      "title": "Tulsa Budget 2024",
      "document_type": "budget",
      "category": "finance",
      "summary": "The 2024 budget allocates $850 million...",
      "chunk_count": 15,
      "is_processed": true,
      "processing_status": "completed",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 20
}
```

**Search Response:**
```json
{
  "query": "public safety budget",
  "results": [
    {
      "document": {
        "id": 1,
        "title": "Tulsa Budget 2024",
        "document_type": "budget"
      },
      "relevance_score": 0.892,
      "excerpt": "Public Safety: $320 million - Police Department: $180 million...",
      "chunk_index": 3
    }
  ],
  "total_results": 1
}
```

## 🔍 Vector Search Details

### Embedding Model
- **Model**: OpenAI text-embedding-3-small
- **Dimensions**: 1536
- **Cost**: ~$0.02 per 1M tokens

### Chunking Strategy
- **Max tokens**: 1000 per chunk
- **Overlap**: 100 tokens between chunks
- **Method**: Paragraph-aware with sentence splitting

### Search Process
1. Generate embedding for user query
2. Perform cosine similarity search in vector database
3. Apply filters (document type, category)
4. Return top-k most relevant chunks
5. Combine with document metadata

## 🛠️ Development

### Adding New Document Types

1. **Update the Document model** (if needed):
   ```python
   # In backend/app/models/document.py
   # Add new document_type validation
   ```

2. **Add processing logic**:
   ```python
   # In backend/app/services/document_processing_service.py
   # Add type-specific processing if needed
   ```

3. **Update API schemas**:
   ```python
   # In backend/app/schemas/document.py
   # Add new types to validation
   ```

### Custom Vector Stores

To add a new vector store (e.g., Pinecone, Weaviate):

1. **Implement VectorStore interface**:
   ```python
   class PineconeVectorStore(VectorStore):
       async def add_vectors(self, vectors, metadata, ids):
           # Implementation

       async def search_vectors(self, query_vector, top_k):
           # Implementation
   ```

2. **Update VectorService**:
   ```python
   # Add new store option in vector_service.py
   ```

### Testing

Run the test suite:

```bash
# Unit tests
pytest tests/

# Integration tests
python scripts/test_rag_system.py

# Load testing
python scripts/load_test_rag.py
```

## 📈 Performance Considerations

### Vector Database Choice

**ChromaDB** (Development):
- ✅ Easy setup, no external dependencies
- ✅ Good for < 100k documents
- ❌ Single-node, limited scalability

**FAISS** (Production):
- ✅ High performance, optimized for similarity search
- ✅ Scales to millions of documents
- ✅ Multiple index types (flat, IVF, HNSW)
- ❌ No built-in persistence (handled by our service)

### Optimization Tips

1. **Chunk Size**: Smaller chunks (500-1000 tokens) for better precision
2. **Overlap**: 10-20% overlap to maintain context
3. **Batch Processing**: Process multiple documents together
4. **Index Type**: Use FAISS IVF for large datasets
5. **Embedding Caching**: Cache embeddings to reduce API calls

## 🔒 Security

### Access Control
- **Public documents**: Available to all users
- **Internal documents**: Require authentication
- **Restricted documents**: Admin-only access

### Data Privacy
- Documents are processed locally
- Only embeddings are stored in vector database
- Full text remains in PostgreSQL with access controls

### API Security
- JWT authentication for uploads
- Rate limiting on search endpoints
- Input validation and sanitization

## 🚨 Troubleshooting

### Common Issues

**1. Document Processing Fails**
```bash
# Check file format support
# Verify OpenAI API key
# Check disk space for temporary files
```

**2. Vector Search Returns No Results**
```bash
# Verify embeddings were generated
# Check vector database connection
# Validate query format
```

**3. Slow Search Performance**
```bash
# Consider switching to FAISS
# Optimize chunk size
# Add database indexes
```

### Debug Commands

```bash
# Check document processing status
curl "http://localhost:8000/api/v1/documents/stats"

# Test vector search directly
python -c "
from app.services.vector_service import VectorService
from app.core.config import Settings
import asyncio

async def test():
    vs = VectorService(Settings())
    results = await vs.search_documents('budget')
    print(results)

asyncio.run(test())
"
```

## 📖 Additional Resources

- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [FAISS Documentation](https://faiss.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## 📄 License

This project is part of the CityCamp AI system and follows the same licensing terms.

---

**Built with ❤️ for Tulsa civic engagement**
