#!/usr/bin/env python3
"""
LLM-as-Judge Evaluation System for CityCamp AI Chatbot

This module uses a separate LLM instance to evaluate chatbot responses,
providing more nuanced and intelligent assessment than keyword-based metrics.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import statistics

# Add the backend directory to the Python path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.config import Settings
from openai import AsyncOpenAI


class LLMJudge:
    """LLM-as-Judge evaluation system using OpenAI"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def evaluate_response(
        self,
        question: str,
        response: str,
        context: Dict = None
    ) -> Dict:
        """
        Use LLM to evaluate a chatbot response

        Args:
            question: The original user question
            response: The chatbot's response to evaluate
            context: Additional context (category, expected behavior, etc.)

        Returns:
            Dictionary with evaluation scores and feedback
        """

        # Construct evaluation prompt
        evaluation_prompt = self._build_evaluation_prompt(question, response, context)

        try:
            # Get LLM evaluation
            start_time = time.time()
            evaluation_response = await self.client.chat.completions.create(
                model="gpt-4",  # Use GPT-4 for more reliable evaluation
                messages=[
                    {
                        "role": "system",
                        "content": self._get_judge_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": evaluation_prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent evaluation
                max_tokens=800
            )
            evaluation_time = time.time() - start_time

            # Parse the evaluation response
            evaluation_text = evaluation_response.choices[0].message.content
            parsed_evaluation = self._parse_evaluation_response(evaluation_text)

            # Add metadata
            parsed_evaluation.update({
                "evaluation_time": evaluation_time,
                "judge_model": "gpt-4",
                "timestamp": datetime.now().isoformat(),
                "raw_evaluation": evaluation_text
            })

            return parsed_evaluation

        except Exception as e:
            return {
                "error": str(e),
                "accuracy": 0.0,
                "helpfulness": 0.0,
                "relevance": 0.0,
                "completeness": 0.0,
                "overall_score": 0.0,
                "feedback": f"Evaluation failed: {str(e)}",
                "evaluation_time": 0.0,
                "timestamp": datetime.now().isoformat()
            }

    def _get_judge_system_prompt(self) -> str:
        """Get the system prompt for the LLM judge"""
        return """You are an expert evaluator for a civic engagement chatbot serving the city of Tulsa, Oklahoma. Your job is to evaluate chatbot responses for quality, accuracy, and helpfulness.

EVALUATION CRITERIA:
1. ACCURACY (0-10): Is the information factually correct and relevant to Tulsa civic matters?
2. HELPFULNESS (0-10): Does the response actually help the user with their civic question?
3. RELEVANCE (0-10): How well does the response address the specific question asked?
4. COMPLETENESS (0-10): Does the response provide sufficient information without being overly verbose?
5. CIVIC APPROPRIATENESS (0-10): Is the response appropriate for a civic/government context?

RESPONSE FORMAT:
You must respond with a JSON object containing:
{
  "accuracy": <score 0-10>,
  "helpfulness": <score 0-10>,
  "relevance": <score 0-10>,
  "completeness": <score 0-10>,
  "civic_appropriateness": <score 0-10>,
  "overall_score": <average of all scores>,
  "feedback": "<detailed explanation of scores>",
  "strengths": ["<strength1>", "<strength2>"],
  "improvements": ["<improvement1>", "<improvement2>"],
  "rag_usage": "<appropriate|inappropriate|not_needed>",
  "grade": "<A|B|C|D|F>"
}

SPECIAL CONSIDERATIONS:
- For Tulsa-specific questions, accuracy is critical
- Responses should be concise but complete
- Off-topic questions should be redirected gracefully to civic matters
- RAG usage should be appropriate (use documents when needed, don't when not needed)
- Responses should encourage civic engagement

Be thorough but fair in your evaluation."""

    def _build_evaluation_prompt(self, question: str, response: str, context: Dict = None) -> str:
        """Build the evaluation prompt for the LLM judge"""

        context_info = ""
        if context:
            context_info = f"""
CONTEXT:
- Category: {context.get('category', 'unknown')}
- Difficulty: {context.get('difficulty', 'unknown')}
- Should use RAG: {context.get('should_use_rag', 'unknown')}
- Expected keywords: {context.get('expected_keywords', [])}
"""

        return f"""Please evaluate this chatbot response for a Tulsa civic engagement platform:

QUESTION: "{question}"

RESPONSE: "{response}"
{context_info}
Provide your evaluation as a JSON object following the specified format."""

    def _parse_evaluation_response(self, evaluation_text: str) -> Dict:
        """Parse the LLM judge's evaluation response"""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', evaluation_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                evaluation_data = json.loads(json_str)

                # Normalize scores to 0-1 scale
                normalized_scores = {}
                for key in ['accuracy', 'helpfulness', 'relevance', 'completeness', 'civic_appropriateness']:
                    if key in evaluation_data:
                        normalized_scores[key] = evaluation_data[key] / 10.0

                # Calculate overall score
                if normalized_scores:
                    overall_score = sum(normalized_scores.values()) / len(normalized_scores)
                else:
                    overall_score = 0.0

                return {
                    **normalized_scores,
                    "overall_score": overall_score,
                    "feedback": evaluation_data.get("feedback", ""),
                    "strengths": evaluation_data.get("strengths", []),
                    "improvements": evaluation_data.get("improvements", []),
                    "rag_usage": evaluation_data.get("rag_usage", "unknown"),
                    "grade": evaluation_data.get("grade", "F")
                }
            else:
                # Fallback if JSON parsing fails
                return self._fallback_parse(evaluation_text)

        except Exception as e:
            return self._fallback_parse(evaluation_text, error=str(e))

    def _fallback_parse(self, evaluation_text: str, error: str = None) -> Dict:
        """Fallback parsing when JSON extraction fails"""
        # Try to extract numeric scores with regex
        import re

        scores = {}
        patterns = {
            'accuracy': r'accuracy[:\s]+(\d+(?:\.\d+)?)',
            'helpfulness': r'helpfulness[:\s]+(\d+(?:\.\d+)?)',
            'relevance': r'relevance[:\s]+(\d+(?:\.\d+)?)',
            'completeness': r'completeness[:\s]+(\d+(?:\.\d+)?)',
            'civic_appropriateness': r'civic[_\s]*appropriateness[:\s]+(\d+(?:\.\d+)?)'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, evaluation_text.lower())
            if match:
                score = float(match.group(1))
                scores[key] = min(score / 10.0, 1.0) if score > 1 else score

        overall_score = sum(scores.values()) / len(scores) if scores else 0.0

        return {
            **scores,
            "overall_score": overall_score,
            "feedback": evaluation_text[:500] + "..." if len(evaluation_text) > 500 else evaluation_text,
            "strengths": [],
            "improvements": [],
            "rag_usage": "unknown",
            "grade": "F" if overall_score < 0.6 else "D" if overall_score < 0.7 else "C" if overall_score < 0.8 else "B" if overall_score < 0.9 else "A",
            "parsing_error": error
        }


class EnhancedLLMEvaluator:
    """Enhanced evaluator combining traditional metrics with LLM-as-Judge"""

    def __init__(self):
        self.settings = Settings()
        self.llm_judge = LLMJudge(self.settings)

        # Import the original evaluator for comparison
        from eval_chatbot_system import ChatbotEvaluator
        self.traditional_evaluator = ChatbotEvaluator()

    async def comprehensive_evaluation(self, test_case: Dict, response: str, response_time: float) -> Dict:
        """
        Run both traditional and LLM-based evaluation

        Args:
            test_case: Test case configuration
            response: Chatbot response to evaluate
            response_time: Time taken to generate response

        Returns:
            Combined evaluation results
        """

        # Get traditional metrics
        traditional_eval = await self.traditional_evaluator.evaluate_response(
            test_case, response, response_time
        )

        # Get LLM judge evaluation
        llm_eval = await self.llm_judge.evaluate_response(
            question=test_case["question"],
            response=response,
            context=test_case
        )

        # Combine evaluations
        combined_evaluation = {
            "test_case": test_case,
            "response": response,
            "response_time": response_time,
            "traditional_metrics": traditional_eval["metrics"],
            "llm_judge_metrics": llm_eval,
            "combined_metrics": self._combine_metrics(traditional_eval["metrics"], llm_eval),
            "timestamp": datetime.now().isoformat()
        }

        return combined_evaluation

    def _combine_metrics(self, traditional: Dict, llm: Dict) -> Dict:
        """Combine traditional and LLM metrics into a unified score"""

        # Weight the different evaluation approaches
        traditional_weight = 0.3
        llm_weight = 0.7

        # Get traditional overall score
        traditional_score = traditional.get("overall_score", 0.0)

        # Get LLM overall score
        llm_score = llm.get("overall_score", 0.0)

        # Combined overall score
        combined_score = (traditional_score * traditional_weight) + (llm_score * llm_weight)

        # Detailed breakdown
        return {
            "combined_overall_score": combined_score,
            "traditional_score": traditional_score,
            "llm_score": llm_score,
            "accuracy_comparison": {
                "keyword_match": traditional.get("keyword_score", 0.0),
                "llm_accuracy": llm.get("accuracy", 0.0)
            },
            "quality_comparison": {
                "traditional_quality": traditional.get("quality_score", 0.0),
                "llm_helpfulness": llm.get("helpfulness", 0.0),
                "llm_completeness": llm.get("completeness", 0.0)
            },
            "relevance_comparison": {
                "traditional_relevance": traditional.get("relevance_score", 0.0),
                "llm_relevance": llm.get("relevance", 0.0)
            },
            "grade": llm.get("grade", "F"),
            "llm_feedback": llm.get("feedback", ""),
            "strengths": llm.get("strengths", []),
            "improvements": llm.get("improvements", []),
            "rag_assessment": {
                "traditional_rag_appropriate": traditional.get("rag_appropriate", False),
                "llm_rag_usage": llm.get("rag_usage", "unknown")
            }
        }

    async def run_llm_evaluation_suite(self, test_cases: List[Dict] = None) -> Dict:
        """Run comprehensive evaluation suite with LLM judge"""

        if test_cases is None:
            test_cases = self.traditional_evaluator.load_test_cases()

        print("🧪 Starting Enhanced LLM-as-Judge Evaluation Suite")
        print("=" * 60)

        results = []

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] Category: {test_case['category']}")
            print(f"Question: {test_case['question'][:60]}...")

            # Get chatbot response
            start_time = time.time()
            try:
                chatbot_response = await self.traditional_evaluator.chatbot_service.get_response(
                    message=test_case["question"],
                    conversation_history=[]
                )
                response_time = time.time() - start_time

                # Run comprehensive evaluation
                evaluation = await self.comprehensive_evaluation(test_case, chatbot_response, response_time)

                # Print summary
                combined_score = evaluation["combined_metrics"]["combined_overall_score"]
                grade = evaluation["combined_metrics"]["grade"]
                print(f"  ✅ Combined Score: {combined_score:.3f} (Grade: {grade}) ({response_time:.2f}s)")
                print(f"     Traditional: {evaluation['combined_metrics']['traditional_score']:.3f}")
                print(f"     LLM Judge: {evaluation['combined_metrics']['llm_score']:.3f}")

                results.append(evaluation)

            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                error_result = {
                    "test_case": test_case,
                    "response": f"ERROR: {str(e)}",
                    "response_time": time.time() - start_time,
                    "traditional_metrics": {"overall_score": 0.0, "error": str(e)},
                    "llm_judge_metrics": {"overall_score": 0.0, "error": str(e)},
                    "combined_metrics": {"combined_overall_score": 0.0, "grade": "F"},
                    "timestamp": datetime.now().isoformat()
                }
                results.append(error_result)

            # Small delay between tests
            await asyncio.sleep(1)

        # Calculate summary
        summary = self._calculate_enhanced_summary(results)

        # Save results
        self._save_enhanced_results(results, summary)

        # Print summary
        self._print_enhanced_summary(summary)

        return {
            "results": results,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }

    def _calculate_enhanced_summary(self, results: List[Dict]) -> Dict:
        """Calculate summary statistics for enhanced evaluation"""

        if not results:
            return {}

        # Extract scores
        combined_scores = []
        traditional_scores = []
        llm_scores = []
        response_times = []
        grades = []

        for result in results:
            if "error" not in result.get("combined_metrics", {}):
                combined_scores.append(result["combined_metrics"]["combined_overall_score"])
                traditional_scores.append(result["combined_metrics"]["traditional_score"])
                llm_scores.append(result["combined_metrics"]["llm_score"])
                response_times.append(result["response_time"])
                grades.append(result["combined_metrics"]["grade"])

        # Calculate averages
        summary = {
            "total_tests": len(results),
            "successful_tests": len(combined_scores),
            "failed_tests": len(results) - len(combined_scores),
            "combined_average_score": statistics.mean(combined_scores) if combined_scores else 0,
            "traditional_average_score": statistics.mean(traditional_scores) if traditional_scores else 0,
            "llm_average_score": statistics.mean(llm_scores) if llm_scores else 0,
            "average_response_time": statistics.mean(response_times) if response_times else 0,
            "grade_distribution": {grade: grades.count(grade) for grade in set(grades)} if grades else {},
            "score_improvement": 0  # Will be calculated if we have baseline
        }

        # Calculate improvement (LLM vs Traditional)
        if traditional_scores and llm_scores:
            summary["score_improvement"] = statistics.mean(llm_scores) - statistics.mean(traditional_scores)

        return summary

    def _save_enhanced_results(self, results: List[Dict], summary: Dict):
        """Save enhanced evaluation results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path("evaluation_results")
        results_dir.mkdir(exist_ok=True)

        # Save detailed results
        detailed_file = results_dir / f"llm_judge_eval_detailed_{timestamp}.json"
        with open(detailed_file, 'w') as f:
            json.dump({
                "results": results,
                "summary": summary,
                "timestamp": datetime.now().isoformat(),
                "evaluation_type": "llm_as_judge_enhanced"
            }, f, indent=2)

        # Save summary report
        summary_file = results_dir / f"llm_judge_eval_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write("LLM-AS-JUDGE EVALUATION SUMMARY\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Total Tests: {summary['total_tests']}\n")
            f.write(f"Successful: {summary['successful_tests']}\n")
            f.write(f"Failed: {summary['failed_tests']}\n\n")

            f.write("SCORING COMPARISON:\n")
            f.write(f"Combined Score: {summary['combined_average_score']:.3f}\n")
            f.write(f"Traditional Score: {summary['traditional_average_score']:.3f}\n")
            f.write(f"LLM Judge Score: {summary['llm_average_score']:.3f}\n")
            f.write(f"Score Improvement: {summary['score_improvement']:+.3f}\n\n")

            f.write("GRADE DISTRIBUTION:\n")
            for grade, count in summary['grade_distribution'].items():
                f.write(f"  {grade}: {count}\n")

            f.write(f"\nAverage Response Time: {summary['average_response_time']:.2f}s\n")

        print(f"\n📊 Enhanced Results saved to:")
        print(f"  📄 Detailed: {detailed_file}")
        print(f"  📋 Summary: {summary_file}")

    def _print_enhanced_summary(self, summary: Dict):
        """Print enhanced evaluation summary"""
        print("\n" + "=" * 60)
        print("🎯 LLM-AS-JUDGE EVALUATION SUMMARY")
        print("=" * 60)

        print(f"📊 Combined Score: {summary['combined_average_score']:.3f}/1.0")
        print(f"📈 Traditional Score: {summary['traditional_average_score']:.3f}/1.0")
        print(f"🤖 LLM Judge Score: {summary['llm_average_score']:.3f}/1.0")
        print(f"📊 Score Improvement: {summary['score_improvement']:+.3f}")
        print(f"⏱️  Average Response Time: {summary['average_response_time']:.2f}s")
        print(f"✅ Success Rate: {summary['successful_tests']}/{summary['total_tests']}")

        print(f"\n🎓 Grade Distribution:")
        for grade, count in summary['grade_distribution'].items():
            print(f"  {grade}: {count}")

        print(f"\n💡 RECOMMENDATIONS:")
        if summary['combined_average_score'] < 0.7:
            print("  - Focus on improving response quality and accuracy")
        if summary['score_improvement'] > 0.1:
            print("  - LLM judge identifies significant quality issues missed by traditional metrics")
        elif summary['score_improvement'] < -0.1:
            print("  - Traditional metrics may be too lenient compared to LLM assessment")
        if summary['average_response_time'] > 5.0:
            print("  - Consider optimizing response time performance")


async def main():
    """Main function to run LLM-as-Judge evaluation"""
    print("🚀 CityCamp AI LLM-as-Judge Evaluation System")
    print("Enhanced evaluation using GPT-4 as an intelligent judge...")

    evaluator = EnhancedLLMEvaluator()

    try:
        # Run enhanced evaluation suite
        evaluation_data = await evaluator.run_llm_evaluation_suite()

        print(f"\n🎉 Enhanced evaluation complete!")
        print(f"Results show the difference between traditional metrics and LLM-based assessment.")

    except Exception as e:
        print(f"❌ Enhanced evaluation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
