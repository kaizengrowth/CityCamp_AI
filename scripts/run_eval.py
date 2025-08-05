#!/usr/bin/env python3
"""
Quick Evaluation Runner for CityCamp AI Chatbot

Simple script to run chatbot evaluations with different configurations.
"""

import asyncio
import argparse
import json
from pathlib import Path

# Import the main evaluator
from eval_chatbot_system import ChatbotEvaluator


async def run_quick_eval():
    """Run a quick evaluation with basic test cases"""
    print("🚀 Running Quick Chatbot Evaluation")

    evaluator = ChatbotEvaluator()

    # Quick test cases
    quick_tests = [
        {
            "category": "basic",
            "question": "What is the Tulsa City Council?",
            "expected_keywords": ["city council", "tulsa", "elected"],
            "should_use_rag": False,
            "difficulty": "easy"
        },
        {
            "category": "rag_test",
            "question": "What is Tulsa's budget for public safety?",
            "expected_keywords": ["budget", "public safety", "police", "fire"],
            "should_use_rag": True,
            "difficulty": "medium"
        },
        {
            "category": "edge_case",
            "question": "What's the weather like?",
            "expected_keywords": ["weather", "not available", "civic"],
            "should_use_rag": False,
            "difficulty": "easy"
        }
    ]

    results = []
    for test_case in quick_tests:
        result = await evaluator.run_single_test(test_case)
        results.append(result)

    summary = evaluator._calculate_summary(results)
    evaluator.print_summary(summary)

    return summary


async def run_rag_focused_eval():
    """Run evaluation focused on RAG system performance"""
    print("🔍 Running RAG-Focused Evaluation")

    evaluator = ChatbotEvaluator()

    # RAG-specific test cases
    rag_tests = [
        {
            "category": "document_search",
            "question": "What is Tulsa's budget for public safety?",
            "expected_keywords": ["budget", "public safety", "million"],
            "should_use_rag": True,
            "difficulty": "medium"
        },
        {
            "category": "document_search",
            "question": "What are the latest ordinances about housing?",
            "expected_keywords": ["ordinance", "housing", "development"],
            "should_use_rag": True,
            "difficulty": "medium"
        },
        {
            "category": "document_search",
            "question": "What was discussed in the last city council meeting?",
            "expected_keywords": ["meeting", "discussed", "council"],
            "should_use_rag": True,
            "difficulty": "hard"
        },
        {
            "category": "no_rag_needed",
            "question": "How many council districts are in Tulsa?",
            "expected_keywords": ["nine", "9", "districts"],
            "should_use_rag": False,
            "difficulty": "easy"
        }
    ]

    results = []
    for test_case in rag_tests:
        result = await evaluator.run_single_test(test_case)
        results.append(result)

    summary = evaluator._calculate_summary(results)
    evaluator.print_summary(summary)

    # RAG-specific analysis
    rag_results = [r for r in results if r["test_case"]["should_use_rag"]]
    rag_accuracy = sum(1 for r in rag_results if r["metrics"].get("uses_rag", False)) / len(rag_results)

    print(f"\n🎯 RAG System Analysis:")
    print(f"  RAG Detection Accuracy: {rag_accuracy:.2f}")
    print(f"  RAG-based Tests: {len(rag_results)}/{len(results)}")

    return summary


async def run_performance_test():
    """Run performance-focused evaluation"""
    print("⚡ Running Performance Test")

    evaluator = ChatbotEvaluator()

    # Simple question for performance testing
    test_case = {
        "category": "performance",
        "question": "What is the Tulsa City Council?",
        "expected_keywords": ["city council", "tulsa"],
        "should_use_rag": False,
        "difficulty": "easy"
    }

    # Run multiple times to get average performance
    times = []
    for i in range(5):
        print(f"  Run {i+1}/5...")
        result = await evaluator.run_single_test(test_case)
        times.append(result["response_time"])

    avg_time = sum(times) / len(times)
    print(f"\n⏱️  Performance Results:")
    print(f"  Average Response Time: {avg_time:.2f}s")
    print(f"  Fastest: {min(times):.2f}s")
    print(f"  Slowest: {max(times):.2f}s")

    if avg_time < 2.0:
        print("  🟢 Excellent performance!")
    elif avg_time < 5.0:
        print("  🟡 Good performance")
    else:
        print("  🔴 Performance needs improvement")


def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(description="CityCamp AI Chatbot Evaluation Runner")
    parser.add_argument(
        "--mode",
        choices=["quick", "full", "rag", "performance", "llm-judge"],
        default="quick",
        help="Evaluation mode to run"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to custom configuration file"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory for results"
    )

    args = parser.parse_args()

    print(f"🧪 Starting {args.mode} evaluation...")

    if args.mode == "quick":
        asyncio.run(run_quick_eval())
    elif args.mode == "full":
        evaluator = ChatbotEvaluator()
        asyncio.run(evaluator.run_evaluation_suite())
    elif args.mode == "rag":
        asyncio.run(run_rag_focused_eval())
    elif args.mode == "performance":
        asyncio.run(run_performance_test())
    elif args.mode == "llm-judge":
        from llm_judge_evaluator import EnhancedLLMEvaluator
        evaluator = EnhancedLLMEvaluator()
        asyncio.run(evaluator.run_llm_evaluation_suite())


if __name__ == "__main__":
    main()
