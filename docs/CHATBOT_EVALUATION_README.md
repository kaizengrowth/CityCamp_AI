# Chatbot Evaluation System

A comprehensive evaluation framework for testing the RAG-enhanced CityCamp AI chatbot system, measuring response quality, accuracy, performance, and RAG system effectiveness.

## 🎯 Overview

The evaluation system provides automated testing of the chatbot's responses across different categories, difficulty levels, and scenarios. It measures:

- **Response Quality**: Grammar, structure, and helpfulness
- **Accuracy**: Keyword matching and factual correctness
- **Relevance**: How well responses address the questions
- **Performance**: Response time and system efficiency
- **RAG Effectiveness**: Document retrieval and usage accuracy

## 🚀 Quick Start

### Basic Evaluation
```bash
# Run quick evaluation (3 test cases)
python scripts/run_eval.py --mode quick

# Run full evaluation suite (10+ test cases)
python scripts/run_eval.py --mode full

# Focus on RAG system performance
python scripts/run_eval.py --mode rag

# Performance benchmarking
python scripts/run_eval.py --mode performance

# LLM-as-Judge evaluation (GPT-4 evaluates responses)
python scripts/run_eval.py --mode llm-judge
```

### Advanced Usage
```bash
# Use custom configuration
python scripts/run_eval.py --mode full --config scripts/eval_config.json

# Save results to specific directory
python scripts/run_eval.py --mode full --output ./my_results/

# Run comprehensive evaluation
python scripts/eval_chatbot_system.py

# Run LLM-as-Judge evaluation directly
python scripts/llm_judge_evaluator.py
```

## 📊 Evaluation Metrics

### 1. **Overall Score (0-1 scale)**
Composite score combining all metrics:
- **0.9-1.0**: Excellent (Grade A)
- **0.8-0.9**: Good (Grade B)
- **0.7-0.8**: Acceptable (Grade C)
- **0.6-0.7**: Needs Improvement (Grade D)
- **<0.6**: Poor (Grade F)

### 2. **Individual Metrics**

#### **Keyword Score**
- Measures presence of expected keywords in responses
- Indicates factual accuracy and topic relevance

#### **Quality Score**
- Assesses response structure, completeness, and helpfulness
- Penalizes very short/long responses and generic answers
- Rewards well-structured, informative responses

#### **Relevance Score**
- Measures how well the response addresses the specific question
- Compares question and response word overlap
- Filters out common words for better accuracy

#### **Conciseness Score**
- Evaluates appropriate response length
- Optimal range: 20-100 words
- Penalizes overly brief or verbose responses

#### **RAG Accuracy**
- Measures whether the system correctly uses/avoids document search
- Tracks appropriate RAG system engagement
- Identifies when documents should/shouldn't be referenced

### 3. **LLM-as-Judge Metrics**

#### **LLM Accuracy Score**
- GPT-4 evaluates factual correctness and Tulsa civic relevance
- More nuanced than keyword matching
- Considers context and appropriateness

#### **LLM Helpfulness Score**
- Assesses how well the response actually helps the user
- Evaluates actionable information and guidance
- Identifies generic vs. specific responses

#### **LLM Completeness Score**
- Evaluates information sufficiency without verbosity
- Balances thoroughness with conciseness
- Considers user's likely follow-up needs

#### **Civic Appropriateness Score**
- Measures suitability for government/civic context
- Evaluates tone, formality, and engagement encouragement
- Identifies inappropriate responses

#### **Combined Score**
- Weighted combination of traditional metrics (30%) and LLM evaluation (70%)
- Provides balanced assessment leveraging both approaches
- More reliable than either method alone

## 📁 Test Categories

### **Basic Civic Knowledge**
- General questions about Tulsa government
- Should not require document search
- Tests fundamental chatbot knowledge

**Example**: "What is the Tulsa City Council?"

### **Document Search (RAG)**
- Questions requiring specific document information
- Tests RAG system integration
- Measures document retrieval accuracy

**Example**: "What is Tulsa's budget for public safety?"

### **Policy Analysis**
- Complex questions requiring synthesis
- Tests advanced reasoning capabilities
- May involve multiple documents

**Example**: "How does Tulsa's transportation budget compare to other cities?"

### **Meeting Information**
- Questions about city council meetings
- Tests meeting data integration
- Varies in RAG requirement

**Example**: "What topics were discussed in the last council meeting?"

### **Edge Cases**
- Off-topic or unusual questions
- Tests system boundaries and error handling
- Should gracefully redirect to civic topics

**Example**: "What's the weather like today?"

## 🤖 LLM-as-Judge Evaluation

### **What is LLM-as-Judge?**

LLM-as-Judge uses GPT-4 as an intelligent evaluator to assess chatbot responses more comprehensively than traditional keyword-based metrics. It provides:

- **Nuanced Understanding**: Evaluates context, tone, and appropriateness
- **Semantic Analysis**: Goes beyond keyword matching to understand meaning
- **Quality Assessment**: Identifies helpful vs. generic responses
- **Civic Context**: Specialized evaluation for government/civic applications

### **How It Works**

1. **Chatbot Response Generation**: Your chatbot generates a response to a test question
2. **LLM Judge Evaluation**: GPT-4 evaluates the response across multiple criteria
3. **Structured Scoring**: Returns scores for accuracy, helpfulness, relevance, completeness, and civic appropriateness
4. **Combined Analysis**: Merges traditional metrics with LLM assessment for comprehensive evaluation

### **LLM Judge Criteria**

```json
{
  "accuracy": "Factual correctness and Tulsa civic relevance (0-10)",
  "helpfulness": "How well it helps users with civic questions (0-10)",
  "relevance": "How well it addresses the specific question (0-10)",
  "completeness": "Sufficient info without being verbose (0-10)",
  "civic_appropriateness": "Suitable for government context (0-10)"
}
```

### **Sample LLM Judge Output**

```json
{
  "accuracy": 8.5,
  "helpfulness": 9.0,
  "relevance": 8.0,
  "completeness": 7.5,
  "civic_appropriateness": 9.5,
  "overall_score": 8.5,
  "grade": "B",
  "feedback": "Response provides accurate information about Tulsa city council with helpful details for civic engagement. Could include more specific next steps.",
  "strengths": ["Clear explanation", "Encouraging tone", "Actionable information"],
  "improvements": ["Add specific contact information", "Include meeting participation details"]
}
```

### **When to Use LLM-as-Judge**

**Best For:**
- Quality assessment of response helpfulness
- Evaluating civic appropriateness and tone
- Detecting generic vs. personalized responses
- Complex policy explanation evaluation
- User experience and engagement assessment

**Traditional Metrics Better For:**
- Performance benchmarking (speed)
- Basic factual accuracy (keyword presence)
- RAG system functionality testing
- Large-scale automated testing

### **Running LLM-as-Judge Evaluation**

```bash
# Quick LLM-as-Judge test
python scripts/run_eval.py --mode llm-judge

# Full enhanced evaluation with comparison
python scripts/llm_judge_evaluator.py

# Custom configuration
python scripts/run_eval.py --mode llm-judge --config scripts/llm_judge_config.json
```

## 🔧 Configuration

### Evaluation Settings (`eval_config.json`)

```json
{
  "evaluation_settings": {
    "max_response_time": 10.0,
    "min_score_threshold": 0.7,
    "save_results": true,
    "verbose_output": true,
    "test_delay_seconds": 1.0
  },
  "scoring_weights": {
    "keyword_match": 0.25,
    "quality": 0.25,
    "relevance": 0.25,
    "conciseness": 0.25
  }
}
```

### Custom Test Cases

Add your own test cases to the configuration:

```json
{
  "custom_test_cases": [
    {
      "category": "tulsa_specific",
      "question": "What is the River Parks Authority?",
      "expected_keywords": ["river", "parks", "authority", "tulsa"],
      "should_use_rag": true,
      "difficulty": "medium",
      "priority": "high"
    }
  ]
}
```

## 📈 Performance Benchmarks

### Response Time
- **Excellent**: < 2.0 seconds
- **Good**: 2.0-5.0 seconds
- **Acceptable**: 5.0-10.0 seconds
- **Poor**: > 10.0 seconds

### Accuracy Score
- **Excellent**: > 0.9
- **Good**: 0.8-0.9
- **Acceptable**: 0.7-0.8
- **Poor**: < 0.7

### RAG Precision
- **Excellent**: > 0.95 (correctly identifies when to use RAG)
- **Good**: 0.85-0.95
- **Acceptable**: 0.75-0.85
- **Poor**: < 0.75

## 📊 Results & Reports

### Automated Reports

The system generates two types of reports:

1. **Detailed JSON Report**
   - Complete test results with all metrics
   - Individual response analysis
   - Timestamp and configuration info
   - File: `evaluation_results/chatbot_eval_detailed_TIMESTAMP.json`

2. **Summary Text Report**
   - High-level performance overview
   - Category and difficulty breakdowns
   - Recommendations for improvement
   - File: `evaluation_results/chatbot_eval_summary_TIMESTAMP.txt`

### Sample Summary Report

```
CHATBOT EVALUATION SUMMARY
==================================================

Timestamp: 2025-01-15T14:30:00Z
Total Tests: 10
Successful: 9
Failed: 1

Overall Grade: B
Average Score: 0.823
Average Response Time: 3.45s

CATEGORY BREAKDOWN:
  basic_civic: 0.856
  document_search: 0.789
  policy_analysis: 0.801
  meeting_info: 0.834
  edge_case: 0.745

DIFFICULTY BREAKDOWN:
  easy: 0.891
  medium: 0.798
  hard: 0.756

RAG System Accuracy: 0.875
```

## 🛠️ Customization

### Adding New Test Categories

1. **Define test cases** in your configuration:
```json
{
  "category": "new_category",
  "question": "Your test question?",
  "expected_keywords": ["keyword1", "keyword2"],
  "should_use_rag": true,
  "difficulty": "medium"
}
```

2. **Extend evaluation logic** in `eval_chatbot_system.py`:
```python
def _assess_custom_metric(self, response: str) -> float:
    # Your custom evaluation logic
    return score
```

### Custom Scoring Weights

Adjust the importance of different metrics:

```json
{
  "scoring_weights": {
    "keyword_match": 0.4,    # Emphasize factual accuracy
    "quality": 0.3,          # Structure and helpfulness
    "relevance": 0.2,        # Question relevance
    "conciseness": 0.1       # Appropriate length
  }
}
```

## 🚨 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure you're in the project root
cd /path/to/CityCamp_AI
python scripts/eval_chatbot_system.py
```

**2. Database Connection Issues**
```bash
# Check database is running
python scripts/test_db_connection.py

# Verify environment variables
echo $DATABASE_URL
echo $OPENAI_API_KEY
```

**3. Slow Response Times**
- Check OpenAI API rate limits
- Verify network connectivity
- Consider reducing test case complexity

**4. Low Accuracy Scores**
- Review expected keywords for relevance
- Check if RAG system has appropriate documents
- Verify chatbot prompt engineering

### Debug Mode

Run with verbose output for detailed debugging:

```bash
python scripts/eval_chatbot_system.py --verbose
```

## 📝 Best Practices

### Writing Good Test Cases

1. **Specific Keywords**: Use precise, measurable keywords
   ```json
   "expected_keywords": ["budget", "2024", "million", "public safety"]
   ```

2. **Appropriate Difficulty**: Match complexity to expectations
   - Easy: Basic facts, single concepts
   - Medium: Specific information, document lookup
   - Hard: Analysis, synthesis, complex reasoning

3. **Clear RAG Requirements**: Specify when documents should be used
   ```json
   "should_use_rag": true  // Requires document search
   "should_use_rag": false // General knowledge only
   ```

### Evaluation Frequency

- **Development**: Run quick evaluations frequently
- **Pre-deployment**: Full evaluation suite
- **Production**: Scheduled evaluations with monitoring
- **After Changes**: RAG-focused evaluation for document updates

### Interpreting Results

- **Focus on trends**: Track improvements over time
- **Category analysis**: Identify specific weakness areas
- **RAG accuracy**: Ensure appropriate document usage
- **Performance**: Monitor response time degradation

## 🔄 Integration with CI/CD

### GitHub Actions Example

```yaml
name: Chatbot Evaluation
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run evaluation
        run: python scripts/run_eval.py --mode full
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: evaluation-results
          path: evaluation_results/
```

## 📚 Additional Resources

- [RAG System Documentation](RAG_SYSTEM_README.md)
- [Chatbot Service Code](../backend/app/services/chatbot_service.py)
- [Vector Service Implementation](../backend/app/services/vector_service.py)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)

---

**Built for comprehensive chatbot quality assurance** 🤖✅
