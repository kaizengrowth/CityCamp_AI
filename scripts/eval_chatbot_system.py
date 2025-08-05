#!/usr/bin/env python3
"""
Chatbot Evaluation System for CityCamp AI

This script provides comprehensive evaluation of the RAG-enhanced chatbot system,
testing response quality, accuracy, relevance, and performance metrics.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import statistics
import re

# Add the backend directory to the Python path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.config import Settings
from app.core.database import SessionLocal
from app.services.chatbot_service import ChatbotService
from app.services.vector_service import VectorService
from app.services.document_processing_service import DocumentProcessingService


class ChatbotEvaluator:
    """Comprehensive chatbot evaluation system"""

    def __init__(self):
        self.settings = Settings()
        self.chatbot_service = ChatbotService(self.settings)
        self.vector_service = VectorService(self.settings)
        self.results = []

    def load_test_cases(self) -> List[Dict]:
        """Load test cases for evaluation"""
        return [
            # Basic Civic Knowledge
            {
                "category": "basic_civic",
                "question": "What is the Tulsa City Council?",
                "expected_keywords": ["city council", "elected", "representatives", "tulsa"],
                "should_use_rag": False,
                "difficulty": "easy"
            },
            {
                "category": "basic_civic",
                "question": "How many council districts are there in Tulsa?",
                "expected_keywords": ["nine", "9", "districts", "council"],
                "should_use_rag": False,
                "difficulty": "easy"
            },

            # Document-Based Questions (RAG)
            {
                "category": "document_search",
                "question": "What is Tulsa's budget for public safety?",
                "expected_keywords": ["budget", "public safety", "police", "fire", "million"],
                "should_use_rag": True,
                "difficulty": "medium"
            },
            {
                "category": "document_search",
                "question": "What are the latest ordinances about housing development?",
                "expected_keywords": ["ordinance", "housing", "development", "zoning"],
                "should_use_rag": True,
                "difficulty": "medium"
            },

            # Complex Policy Questions
            {
                "category": "policy_analysis",
                "question": "How does Tulsa's transportation budget compare to other cities?",
                "expected_keywords": ["transportation", "budget", "compare", "infrastructure"],
                "should_use_rag": True,
                "difficulty": "hard"
            },
            {
                "category": "policy_analysis",
                "question": "What are the environmental policies for waste management in Tulsa?",
                "expected_keywords": ["environmental", "waste", "management", "policy", "recycling"],
                "should_use_rag": True,
                "difficulty": "hard"
            },

            # Meeting-Specific Questions
            {
                "category": "meeting_info",
                "question": "When is the next city council meeting?",
                "expected_keywords": ["meeting", "council", "date", "time"],
                "should_use_rag": False,
                "difficulty": "easy"
            },
            {
                "category": "meeting_info",
                "question": "What topics were discussed in the last council meeting?",
                "expected_keywords": ["topics", "discussed", "meeting", "agenda"],
                "should_use_rag": True,
                "difficulty": "medium"
            },

            # Edge Cases
            {
                "category": "edge_case",
                "question": "What's the weather like today?",
                "expected_keywords": ["weather", "not available", "civic", "government"],
                "should_use_rag": False,
                "difficulty": "easy"
            },
            {
                "category": "edge_case",
                "question": "How do I pay my water bill?",
                "expected_keywords": ["water", "bill", "payment", "utility", "online"],
                "should_use_rag": False,
                "difficulty": "medium"
            }
        ]

    async def evaluate_response(self, test_case: Dict, response: str, response_time: float) -> Dict:
        """Evaluate a single chatbot response"""

        # Basic metrics
        word_count = len(response.split())
        char_count = len(response)

        # Keyword matching
        keywords_found = []
        response_lower = response.lower()
        for keyword in test_case["expected_keywords"]:
            if keyword.lower() in response_lower:
                keywords_found.append(keyword)

        keyword_score = len(keywords_found) / len(test_case["expected_keywords"])

        # Response quality metrics
        quality_score = self._assess_response_quality(response)
        relevance_score = self._assess_relevance(test_case["question"], response)
        conciseness_score = self._assess_conciseness(response)

        # RAG usage detection
        rag_indicators = ["based on", "according to", "document", "budget", "ordinance", "policy"]
        uses_rag = any(indicator in response_lower for indicator in rag_indicators)
        rag_appropriate = uses_rag == test_case["should_use_rag"]

        return {
            "test_case": test_case,
            "response": response,
            "response_time": response_time,
            "metrics": {
                "word_count": word_count,
                "char_count": char_count,
                "keyword_score": keyword_score,
                "keywords_found": keywords_found,
                "quality_score": quality_score,
                "relevance_score": relevance_score,
                "conciseness_score": conciseness_score,
                "uses_rag": uses_rag,
                "rag_appropriate": rag_appropriate,
                "overall_score": (keyword_score + quality_score + relevance_score + conciseness_score) / 4
            },
            "timestamp": datetime.now().isoformat()
        }

    def _assess_response_quality(self, response: str) -> float:
        """Assess overall response quality (0-1 scale)"""
        score = 1.0

        # Penalize very short responses
        if len(response.split()) < 10:
            score -= 0.3

        # Penalize very long responses
        if len(response.split()) > 200:
            score -= 0.2

        # Check for complete sentences
        sentences = response.split('.')
        if len(sentences) < 2:
            score -= 0.2

        # Check for helpful structure
        if any(marker in response for marker in ['•', '-', '1.', '2.', ':']):
            score += 0.1

        # Penalize generic responses
        generic_phrases = ["i can help", "let me know", "feel free to ask"]
        if any(phrase in response.lower() for phrase in generic_phrases):
            score -= 0.1

        return max(0.0, min(1.0, score))

    def _assess_relevance(self, question: str, response: str) -> float:
        """Assess how relevant the response is to the question"""
        question_words = set(question.lower().split())
        response_words = set(response.lower().split())

        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'what', 'how', 'when', 'where', 'why', 'who'}

        question_words -= common_words
        response_words -= common_words

        if not question_words:
            return 0.5

        overlap = len(question_words & response_words)
        relevance_score = overlap / len(question_words)

        return min(1.0, relevance_score)

    def _assess_conciseness(self, response: str) -> float:
        """Assess if response is appropriately concise"""
        word_count = len(response.split())

        # Optimal range: 20-100 words
        if 20 <= word_count <= 100:
            return 1.0
        elif word_count < 20:
            return 0.7  # Too short
        elif word_count <= 150:
            return 0.8  # Acceptable length
        else:
            return max(0.3, 1.0 - (word_count - 150) / 200)  # Too long

    async def run_single_test(self, test_case: Dict) -> Dict:
        """Run a single test case"""
        print(f"Testing: {test_case['question'][:50]}...")

        start_time = time.time()
        try:
            response = await self.chatbot_service.get_response(
                message=test_case["question"],
                conversation_history=[]
            )
            response_time = time.time() - start_time

            evaluation = await self.evaluate_response(test_case, response, response_time)
            print(f"  ✅ Score: {evaluation['metrics']['overall_score']:.2f} ({response_time:.2f}s)")
            return evaluation

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return {
                "test_case": test_case,
                "response": f"ERROR: {str(e)}",
                "response_time": time.time() - start_time,
                "metrics": {
                    "overall_score": 0.0,
                    "error": str(e)
                },
                "timestamp": datetime.now().isoformat()
            }

    async def run_evaluation_suite(self) -> Dict:
        """Run the complete evaluation suite"""
        print("🧪 Starting Chatbot Evaluation Suite")
        print("=" * 50)

        test_cases = self.load_test_cases()
        results = []

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] Category: {test_case['category']}")
            result = await self.run_single_test(test_case)
            results.append(result)

            # Small delay to avoid overwhelming the API
            await asyncio.sleep(1)

        # Calculate summary statistics
        summary = self._calculate_summary(results)

        # Save results
        self._save_results(results, summary)

        return {
            "results": results,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }

    def _calculate_summary(self, results: List[Dict]) -> Dict:
        """Calculate summary statistics"""
        if not results:
            return {}

        # Overall scores
        overall_scores = [r["metrics"].get("overall_score", 0) for r in results if "error" not in r["metrics"]]
        response_times = [r["response_time"] for r in results]

        # Category breakdown
        category_scores = {}
        for result in results:
            category = result["test_case"]["category"]
            if category not in category_scores:
                category_scores[category] = []
            if "error" not in result["metrics"]:
                category_scores[category].append(result["metrics"]["overall_score"])

        category_averages = {
            cat: statistics.mean(scores) if scores else 0
            for cat, scores in category_scores.items()
        }

        # Difficulty breakdown
        difficulty_scores = {}
        for result in results:
            difficulty = result["test_case"]["difficulty"]
            if difficulty not in difficulty_scores:
                difficulty_scores[difficulty] = []
            if "error" not in result["metrics"]:
                difficulty_scores[difficulty].append(result["metrics"]["overall_score"])

        difficulty_averages = {
            diff: statistics.mean(scores) if scores else 0
            for diff, scores in difficulty_scores.items()
        }

        # RAG usage analysis
        rag_tests = [r for r in results if r["test_case"]["should_use_rag"]]
        rag_accuracy = sum(1 for r in rag_tests if r["metrics"].get("rag_appropriate", False)) / len(rag_tests) if rag_tests else 0

        return {
            "total_tests": len(results),
            "successful_tests": len(overall_scores),
            "failed_tests": len(results) - len(overall_scores),
            "overall_average_score": statistics.mean(overall_scores) if overall_scores else 0,
            "score_std_dev": statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0,
            "average_response_time": statistics.mean(response_times),
            "max_response_time": max(response_times),
            "min_response_time": min(response_times),
            "category_averages": category_averages,
            "difficulty_averages": difficulty_averages,
            "rag_accuracy": rag_accuracy,
            "grade": self._assign_grade(statistics.mean(overall_scores) if overall_scores else 0)
        }

    def _assign_grade(self, score: float) -> str:
        """Assign a letter grade based on overall score"""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"

    def _save_results(self, results: List[Dict], summary: Dict):
        """Save evaluation results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path("evaluation_results")
        results_dir.mkdir(exist_ok=True)

        # Save detailed results
        detailed_file = results_dir / f"chatbot_eval_detailed_{timestamp}.json"
        with open(detailed_file, 'w') as f:
            json.dump({
                "results": results,
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)

        # Save summary report
        summary_file = results_dir / f"chatbot_eval_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write("CHATBOT EVALUATION SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Total Tests: {summary['total_tests']}\n")
            f.write(f"Successful: {summary['successful_tests']}\n")
            f.write(f"Failed: {summary['failed_tests']}\n\n")
            f.write(f"Overall Grade: {summary['grade']}\n")
            f.write(f"Average Score: {summary['overall_average_score']:.3f}\n")
            f.write(f"Average Response Time: {summary['average_response_time']:.2f}s\n\n")

            f.write("CATEGORY BREAKDOWN:\n")
            for category, score in summary['category_averages'].items():
                f.write(f"  {category}: {score:.3f}\n")

            f.write("\nDIFFICULTY BREAKDOWN:\n")
            for difficulty, score in summary['difficulty_averages'].items():
                f.write(f"  {difficulty}: {score:.3f}\n")

            f.write(f"\nRAG System Accuracy: {summary['rag_accuracy']:.3f}\n")

        print(f"\n📊 Results saved to:")
        print(f"  📄 Detailed: {detailed_file}")
        print(f"  📋 Summary: {summary_file}")

    def print_summary(self, summary: Dict):
        """Print evaluation summary to console"""
        print("\n" + "=" * 50)
        print("🎯 EVALUATION SUMMARY")
        print("=" * 50)
        print(f"📊 Overall Grade: {summary['grade']}")
        print(f"📈 Average Score: {summary['overall_average_score']:.3f}/1.0")
        print(f"⏱️  Average Response Time: {summary['average_response_time']:.2f}s")
        print(f"✅ Success Rate: {summary['successful_tests']}/{summary['total_tests']}")

        print(f"\n📂 Category Performance:")
        for category, score in summary['category_averages'].items():
            print(f"  {category}: {score:.3f}")

        print(f"\n🎚️  Difficulty Performance:")
        for difficulty, score in summary['difficulty_averages'].items():
            print(f"  {difficulty}: {score:.3f}")

        print(f"\n🔍 RAG System Accuracy: {summary['rag_accuracy']:.3f}")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if summary['overall_average_score'] < 0.7:
            print("  - Consider improving response quality and relevance")
        if summary['average_response_time'] > 5.0:
            print("  - Response times are slow, optimize performance")
        if summary['rag_accuracy'] < 0.8:
            print("  - RAG system needs better document retrieval tuning")
        if summary['overall_average_score'] >= 0.8:
            print("  - System performing well! Consider expanding test cases")


async def main():
    """Main evaluation function"""
    print("🚀 CityCamp AI Chatbot Evaluation System")
    print("Testing RAG-enhanced chatbot responses...")

    evaluator = ChatbotEvaluator()

    try:
        # Run evaluation suite
        evaluation_data = await evaluator.run_evaluation_suite()

        # Print summary
        evaluator.print_summary(evaluation_data["summary"])

        print(f"\n🎉 Evaluation complete!")

    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
