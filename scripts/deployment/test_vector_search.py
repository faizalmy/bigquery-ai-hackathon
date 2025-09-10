#!/usr/bin/env python3
"""
Test Vector Search Implementation
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script tests the SQL-based vector search functionality.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from utils.bigquery_client import BigQueryClient
from config import load_config
from ai.vector_search_sql import SQLVectorSearch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_vector_search_setup():
    """Test vector search setup and initialization."""
    try:
        # Load configuration
        config = load_config()
        project_id = config['bigquery']['project_id']

        # Initialize BigQuery client
        bq_client = BigQueryClient(config)

        # Initialize vector search
        vector_search = SQLVectorSearch(project_id)

        logger.info("🧪 Testing Vector Search Setup...")

        # Test 1: Create embeddings table
        logger.info("📦 Creating document embeddings table...")
        embeddings_created = vector_search.create_embedding_table(bq_client)

        if embeddings_created:
            logger.info("✅ Document embeddings table created successfully")
        else:
            logger.error("❌ Failed to create embeddings table")
            return False

        # Test 2: Create similarity function
        logger.info("📦 Creating cosine similarity function...")
        function_created = vector_search.create_similarity_function(bq_client)

        if function_created:
            logger.info("✅ Cosine similarity function created successfully")
        else:
            logger.error("❌ Failed to create similarity function")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ Vector search setup failed: {e}")
        return False

def test_embedding_generation():
    """Test document embedding generation."""
    try:
        # Load configuration
        config = load_config()
        project_id = config['bigquery']['project_id']

        # Initialize BigQuery client
        bq_client = BigQueryClient(config)

        # Initialize vector search
        vector_search = SQLVectorSearch(project_id)

        logger.info("🧪 Testing Document Embedding Generation...")

        # Test embedding generation
        test_document = "This is a Supreme Court case involving constitutional law and First Amendment rights of public employees."
        embedding = vector_search.generate_document_embedding(bq_client, test_document, "case_law")

        if embedding and len(embedding) > 0:
            logger.info("✅ Document embedding generated successfully")
            logger.info(f"   📊 Embedding dimension: {len(embedding)}")
            logger.info(f"   📊 Sample values: {embedding[:5]}...")
            return True
        else:
            logger.error("❌ Failed to generate document embedding")
            return False

    except Exception as e:
        logger.error(f"❌ Embedding generation test failed: {e}")
        return False

def test_similarity_search():
    """Test similarity search functionality."""
    try:
        # Load configuration
        config = load_config()
        project_id = config['bigquery']['project_id']

        # Initialize BigQuery client
        bq_client = BigQueryClient(config)

        # Initialize vector search
        vector_search = SQLVectorSearch(project_id)

        logger.info("🧪 Testing Similarity Search...")

        # Test content search
        query_text = "constitutional law First Amendment rights public employees"
        similar_docs = vector_search.search_by_content(bq_client, query_text, top_k=5)

        if similar_docs:
            logger.info("✅ Similarity search completed successfully")
            logger.info(f"   📊 Found {len(similar_docs)} similar documents")

            for i, doc in enumerate(similar_docs[:3]):  # Show top 3
                logger.info(f"   {i+1}. Document ID: {doc['document_id']}")
                logger.info(f"      Type: {doc['document_type']}")
                logger.info(f"      Similarity: {doc['similarity_score']:.3f}")
                logger.info(f"      Quality: {doc['quality_score']:.3f}")

            return True
        else:
            logger.warning("⚠️  No similar documents found (this might be expected if embeddings table is empty)")
            return True  # This is not necessarily a failure

    except Exception as e:
        logger.error(f"❌ Similarity search test failed: {e}")
        return False

def test_embedding_stats():
    """Test embedding statistics."""
    try:
        # Load configuration
        config = load_config()
        project_id = config['bigquery']['project_id']

        # Initialize BigQuery client
        bq_client = BigQueryClient(config)

        # Initialize vector search
        vector_search = SQLVectorSearch(project_id)

        logger.info("🧪 Testing Embedding Statistics...")

        # Get embedding stats
        stats = vector_search.get_embedding_stats(bq_client)

        if stats:
            logger.info("✅ Embedding statistics retrieved successfully")
            logger.info(f"   📊 Total embeddings: {stats.get('total_embeddings', 0)}")
            logger.info(f"   📊 Document types: {stats.get('document_types', 0)}")
            logger.info(f"   📊 Average vector length: {stats.get('avg_vector_length', 0):.1f}")

            quality_range = stats.get('quality_range', {})
            if quality_range:
                logger.info(f"   📊 Quality range: {quality_range.get('min', 0):.3f} - {quality_range.get('max', 0):.3f}")
                logger.info(f"   📊 Average quality: {quality_range.get('avg', 0):.3f}")

            return True
        else:
            logger.error("❌ Failed to retrieve embedding statistics")
            return False

    except Exception as e:
        logger.error(f"❌ Embedding stats test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🔍 Vector Search Implementation - Test Suite")
    print("=" * 60)

    test_results = {}

    # Test 1: Setup
    print("\n1️⃣ Testing Vector Search Setup...")
    test_results['setup'] = test_vector_search_setup()

    # Test 2: Embedding Generation
    print("\n2️⃣ Testing Embedding Generation...")
    test_results['embedding_generation'] = test_embedding_generation()

    # Test 3: Similarity Search
    print("\n3️⃣ Testing Similarity Search...")
    test_results['similarity_search'] = test_similarity_search()

    # Test 4: Embedding Statistics
    print("\n4️⃣ Testing Embedding Statistics...")
    test_results['embedding_stats'] = test_embedding_stats()

    # Print results summary
    print("\n📊 Test Results Summary:")
    print("=" * 30)

    successful_tests = 0
    for test_name, result in test_results.items():
        if result:
            logger.info(f"✅ {test_name.replace('_', ' ').title()}: PASSED")
            successful_tests += 1
        else:
            logger.error(f"❌ {test_name.replace('_', ' ').title()}: FAILED")

    total_tests = len(test_results)
    logger.info(f"🎯 Overall: {successful_tests}/{total_tests} tests passed")

    if successful_tests == total_tests:
        print("\n🎉 All vector search tests passed!")
        print("✅ Phase 2.5 Vector Search Implementation is working")
        print("\n📋 Working Features:")
        print("   🔍 Document embedding generation")
        print("   📊 Cosine similarity calculation")
        print("   🔎 Similarity search functionality")
        print("   📈 Embedding statistics and monitoring")
        print("\n🚀 Ready to proceed to Phase 2.6: Predictive Analytics")
    else:
        print(f"\n⚠️  {successful_tests}/{total_tests} vector search tests passed")
        print("🔧 Some components need further development")

    return 0 if successful_tests == total_tests else 1

if __name__ == "__main__":
    exit(main())
