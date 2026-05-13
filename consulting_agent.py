#!/usr/bin/env python3
"""
Consulting Agent AI
An AI-powered management consulting assistant that replaces the work
of strategy consulting firms with multi-agent AI analysis.

Usage:
    python consulting_agent.py --company "Tesla" --question "Should Tesla enter the electric boat market?" --ticker TSLA
    python consulting_agent.py --company "Apple" --question "Analyze Apple's growth strategy and market position" --ticker AAPL
    python consulting_agent.py --company "Company Name" --question "Your business question" --question-file question.txt
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.orchestrator import ConsultingOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description="Consulting Agent AI - AI-powered strategy consultant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --company "Tesla" --question "Market entry strategy for India" --ticker TSLA
  %(prog)s --company "Nike" --question "Competitive analysis against Adidas and Under Armour" --ticker NKE
  %(prog)s --company "Starbucks" --question-file my_question.txt --ticker SBUX
        """,
    )

    parser.add_argument(
        "--company",
        "-c",
        type=str,
        required=True,
        help="Company name to analyze",
    )

    question_group = parser.add_mutually_exclusive_group(required=True)
    question_group.add_argument(
        "--question",
        "-q",
        type=str,
        help="Business question to analyze (inline)",
    )
    question_group.add_argument(
        "--question-file",
        "-f",
        type=str,
        help="File containing the business question",
    )

    parser.add_argument(
        "--ticker",
        "-t",
        type=str,
        default=None,
        help="Stock ticker symbol (e.g., TSLA, AAPL, MSFT)",
    )

    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Generate PDF output (requires weasyprint)",
    )

    args = parser.parse_args()

    question = args.question
    if args.question_file:
        try:
            with open(args.question_file, "r") as f:
                question = f.read().strip()
        except Exception as e:
            print(f"Error reading question file: {e}")
            sys.exit(1)

    if not question:
        print("Error: No question provided.")
        sys.exit(1)

    output_format = "pdf" if args.pdf else "md"

    print(f"\n  Consulting Agent AI v1.0")
    print(f"  Starting analysis for: {args.company}")
    print()

    orchestrator = ConsultingOrchestrator()
    try:
        output_path = orchestrator.run(
            company=args.company,
            question=question,
            ticker=args.ticker,
        )
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
