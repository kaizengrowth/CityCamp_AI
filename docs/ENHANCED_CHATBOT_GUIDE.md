# Enhanced ChatBot Guide - Deep Research & Document Retrieval

## Overview

Your CityCamp AI chatbot has been upgraded with powerful research capabilities:

- **GPT-4 Turbo** for superior reasoning and understanding
- **Web Search** using Google Custom Search API
- **Document Retrieval** for PDFs, meeting minutes, and government documents
- **Function Calling** for intelligent tool usage
- **Markdown Support** with clickable links and rich formatting

## 🚀 New Features

### 1. **GPT-4 Turbo Integration**
- Upgraded from GPT-3.5-turbo to GPT-4-turbo-preview
- Better reasoning and understanding of complex queries
- Improved function calling capabilities
- Increased context window (1000 tokens vs 500)

### 2. **Web Search Capabilities**
- Real-time search for current Tulsa government information
- Prioritizes official sources (tulsa.gov, tulsacouncil.org)
- Filters results to recent information (last 1-2 years)
- Automatically adds Tulsa-specific context to searches

### 3. **Document Retrieval System**
- Retrieves and analyzes PDF documents
- Extracts text from meeting minutes and government documents
- Processes up to 10 pages per document
- Supports both PDFs and web pages

### 4. **Enhanced User Experience**
- **Markdown formatting** with bold text, lists, and links
- **Clickable links** that open in new tabs
- **Better paragraph spacing** for readability
- **Rich text formatting** for professional appearance

## 🛠️ Setup Requirements

### Environment Variables

Add these to your `.env` file:

```bash
# OpenAI API (required)
OPENAI_API_KEY=your_openai_api_key_here

# Google Custom Search API (optional but recommended)
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here
```

### Google Custom Search Setup

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Custom Search API:**
   - Navigate to "APIs & Services" → "Library"
   - Search for "Custom Search API"
   - Click "Enable"

3. **Create API Key:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy the API key to your `.env` file

4. **Set up Custom Search Engine:**
   - Go to [Google Custom Search](https://cse.google.com/)
   - Click "Add" to create a new search engine
   - Add sites to search: `tulsa.gov`, `tulsacouncil.org`
   - Get your Search Engine ID from the "Setup" tab

## 🎯 Available Functions

The chatbot can now intelligently use these tools:

### 1. `search_web`
- Searches the web for current Tulsa government information
- Automatically adds Tulsa-specific context
- Returns formatted results with titles, links, and snippets

### 2. `retrieve_document`
- Downloads and analyzes documents from URLs
- Extracts text from PDFs and web pages
- Provides document summaries and key information

### 3. `search_tulsa_documents`
- Specifically searches for Tulsa government documents
- Focuses on PDFs, meeting minutes, and official records
- Filters by document type and recency

## 📝 Example Interactions

### Basic Query
**User:** "What happened at the last Tulsa City Council meeting?"

**AI Response:** The chatbot will:
1. Search local database for recent meetings
2. If needed, search the web for current information
3. Provide formatted response with links

### Document Analysis
**User:** "Can you analyze the latest budget proposal?"

**AI Response:** The chatbot will:
1. Search for budget-related documents
2. Retrieve the most relevant PDF
3. Extract and summarize key information
4. Provide clickable links to source documents

### Current Events
**User:** "What's the latest news about Tulsa infrastructure projects?"

**AI Response:** The chatbot will:
1. Search the web for recent news
2. Filter results to official sources
3. Provide formatted summary with links

## 🔧 Technical Implementation

### Architecture
```
User Query → GPT-4 → Function Calling → Research Tools → Enhanced Response
```

### Key Components

1. **ChatbotService** (`app/services/chatbot_service.py`)
   - Main orchestrator with GPT-4 integration
   - Function calling logic
   - Enhanced system prompts

2. **ResearchService** (`app/services/research_service.py`)
   - Web search implementation
   - Document retrieval and processing
   - Content formatting utilities

3. **Enhanced Frontend** (`frontend/src/components/ChatbotWidget.tsx`)
   - Markdown rendering with react-markdown
   - Clickable links and rich formatting
   - Improved layout and spacing

### Response Flow

1. **User sends message** → Frontend
2. **Message processed** → Backend API
3. **GPT-4 analyzes** → Determines if tools needed
4. **Functions called** → Web search, document retrieval
5. **Results formatted** → Markdown with links
6. **Response sent** → Frontend renders with formatting

## 🎨 Markdown Features

The chatbot now supports rich formatting:

- **Bold text** for emphasis
- [Clickable links](https://tulsa.gov) that open in new tabs
- • Bullet points for lists
- Proper paragraph spacing
- Code blocks for technical information
- Blockquotes for important notices

## 🔐 Security & Guardrails

### Tulsa-Only Focus
- Strict guardrails ensure responses only about Tulsa, Oklahoma
- Redirects non-Tulsa queries to local topics
- Emphasizes "Tulsa" in all responses

### API Security
- Rate limiting on external API calls
- Timeout protection for web requests
- Content filtering for appropriate responses

### Data Privacy
- No storage of search queries
- Temporary document processing
- Secure API key handling

## 🧪 Testing

### Manual Testing
1. Start both backend and frontend servers
2. Open the chatbot widget
3. Try these test queries:
   - "What's happening with Tulsa city budget?"
   - "Find me the latest city council meeting minutes"
   - "Tell me about current Tulsa infrastructure projects"

### Expected Behavior
- Responses should include **bold text** and [clickable links]
- Web searches should return current, relevant information
- Document retrieval should work for PDF files
- All responses should maintain Tulsa focus

## 📊 Performance

### Response Times
- Simple queries: 2-3 seconds
- Web search queries: 5-8 seconds
- Document retrieval: 8-15 seconds (depending on document size)

### API Limits
- Google Custom Search: 100 queries/day (free tier)
- OpenAI GPT-4: Based on your plan
- Document processing: 10 pages per PDF

## 🔄 Fallback Behavior

If external services are unavailable:
1. **No Google API key:** Uses local database only
2. **OpenAI unavailable:** Provides fallback responses
3. **Document retrieval fails:** Graceful error handling

## 📈 Future Enhancements

Potential improvements:
- Vector database for document search
- Real-time meeting transcription
- Multi-language support
- Voice interaction capabilities
- Advanced analytics and reporting

## 🆘 Troubleshooting

### Common Issues

1. **"Google Custom Search API not configured"**
   - Check `GOOGLE_API_KEY` and `GOOGLE_CSE_ID` in `.env`
   - Verify API is enabled in Google Cloud Console

2. **"Error getting AI response"**
   - Check `OPENAI_API_KEY` in `.env`
   - Verify OpenAI account has sufficient credits

3. **"Document could not be retrieved"**
   - Check internet connection
   - Verify document URL is accessible
   - Some PDFs may be protected or corrupted

### Debug Mode
Enable debug logging in `app/core/config.py`:
```python
debug: bool = True
```

## 📞 Support

For issues or questions:
1. Check the logs in the backend console
2. Verify all environment variables are set
3. Test with simple queries first
4. Ensure all dependencies are installed

---

**🎉 Your ChatBot is now powered by advanced AI research capabilities!**

Users can now get real-time, accurate information about Tulsa government with properly formatted responses and clickable links to official sources.
