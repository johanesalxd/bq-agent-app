#!/usr/bin/env python3
"""
Test script for BQML RAG corpus functionality.

Usage:
    python test_rag.py "Your query here"
    python test_rag.py  # Uses default query
"""

from setup.rag_corpus.create_bqml_corpus import rag_response
import os
from pathlib import Path
import sys

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_rag_queries():
    """Test the RAG function with various BQML queries."""

    # Check if corpus is configured
    corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")
    if not corpus_name:
        print("❌ BQML_RAG_CORPUS_NAME not found in environment variables")
        print("Make sure your .env file is properly configured")
        return

    print(f"✅ Using RAG corpus: {corpus_name}")
    print("=" * 60)

    # Test queries
    test_queries = [
        "What BQML model types are available?",
        "How do I create a logistic regression model?",
        "How to evaluate BQML model performance?",
        "What is BQML forecasting with ARIMA?",
        "How to create clustering models in BigQuery ML?"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 40)

        try:
            result = rag_response(query)
            print(f"📄 Result: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")

        print("-" * 40)


def test_single_query(query):
    """Test a single query."""
    corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")
    if not corpus_name:
        print("❌ BQML_RAG_CORPUS_NAME not found in environment variables")
        return

    print(f"✅ Using RAG corpus: {corpus_name}")
    print(f"🔍 Query: {query}")
    print("=" * 60)

    try:
        result = rag_response(query)
        print(f"📄 Result: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Single query from command line
        query = " ".join(sys.argv[1:])
        test_single_query(query)
    else:
        # Run all test queries
        test_rag_queries()
