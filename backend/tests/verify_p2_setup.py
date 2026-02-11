#!/usr/bin/env python3
"""
P2 Installation & Verification Script
Tests that all NLP dependencies are installed and the cognitive pipeline works
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import spacy
        print("  ✓ spacy")
    except ImportError as e:
        print(f"  ✗ spacy - {e}")
        return False
    
    try:
        import nltk
        print("  ✓ nltk")
    except ImportError as e:
        print(f"  ✗ nltk - {e}")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("  ✓ sentence-transformers")
    except ImportError as e:
        print(f"  ✗ sentence-transformers - {e}")
        return False
    
    try:
        import aiosmtplib
        print("  ✓ aiosmtplib")
    except ImportError as e:
        print(f"  ✗ aiosmtplib - {e}")
        return False
    
    try:
        from jinja2 import Environment
        print("  ✓ jinja2")
    except ImportError as e:
        print(f"  ✗ jinja2 - {e}")
        return False
    
    return True


def test_spacy_model():
    """Test that spaCy model is downloaded"""
    print("\nTesting spaCy model...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("  ✓ en_core_web_sm loaded")
        
        # Test basic NLP
        doc = nlp("Hello, how are you today?")
        print(f"  ✓ Processed {len(doc)} tokens")
        
        return True
    except OSError:
        print("  ✗ en_core_web_sm not found")
        print("    Run: python -m spacy download en_core_web_sm")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_nltk_data():
    """Test that NLTK data is downloaded"""
    print("\nTesting NLTK data...")
    
    try:
        import nltk
        from nltk.corpus import stopwords
        
        words = stopwords.words('english')
        print(f"  ✓ Loaded {len(words)} stopwords")
        return True
    except LookupError:
        print("  ✗ NLTK stopwords not found")
        print("    Run: python -c \"import nltk; nltk.download('stopwords')\"")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_cognitive_analyzer():
    """Test the cognitive analyzer"""
    print("\nTesting Cognitive Analyzer...")
    
    try:
        from app.cognitive.analyzer import CognitiveAnalyzer
        
        analyzer = CognitiveAnalyzer()
        print("  ✓ CognitiveAnalyzer initialized")
        
        # Test with sample transcript
        sample_transcript = """Clara: Hello Dorothy! How are you doing today?
Dorothy: Oh, I'm doing well, thank you. I've been thinking about my garden.
Clara: That's wonderful! Tell me about your garden.
Dorothy: Well, I planted some tomatoes this year. They're growing nicely."""
        
        import asyncio
        
        async def run_test():
            metrics = await analyzer.analyze_conversation(
                transcript=sample_transcript,
                patient_name="Dorothy",
                response_times=[1.2, 1.5]
            )
            return metrics
        
        metrics = asyncio.run(run_test())
        
        print(f"  ✓ Analysis complete")
        print(f"    - Vocabulary diversity: {metrics['vocabulary_diversity']:.3f}")
        print(f"    - Topic coherence: {metrics['topic_coherence']:.3f}")
        print(f"    - Word-finding pauses: {metrics['word_finding_pauses']}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_store():
    """Test the in-memory data store"""
    print("\nTesting InMemoryDataStore...")
    
    try:
        from app.storage import InMemoryDataStore
        import asyncio
        
        async def run_test():
            store = InMemoryDataStore()
            print("  ✓ InMemoryDataStore initialized")
            
            # Test getting patient
            patient = await store.get_patient("patient-dorothy-001")
            if patient:
                print(f"  ✓ Retrieved patient: {patient['name']}")
            else:
                print("  ✗ Patient not found")
                return False
            
            # Test getting conversations
            convs = await store.get_conversations("patient-dorothy-001", limit=5)
            print(f"  ✓ Retrieved {len(convs)} conversations")
            
            # Test getting baseline
            baseline = await store.get_cognitive_baseline("patient-dorothy-001")
            if baseline and baseline.get("established"):
                print(f"  ✓ Baseline established: TTR={baseline['vocabulary_diversity']:.3f}")
            else:
                print("  ⚠ Baseline not established yet")
            
            return True
        
        return asyncio.run(run_test())
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_routes():
    """Test that API routes are importable"""
    print("\nTesting API Routes...")
    
    try:
        from app.routes import (
            patients_router,
            conversations_router,
            wellness_router,
            alerts_router
        )
        print("  ✓ All route modules imported")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("ClaraCare P2 - Installation & Verification Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("spaCy Model", test_spacy_model()))
    results.append(("NLTK Data", test_nltk_data()))
    results.append(("Cognitive Analyzer", test_cognitive_analyzer()))
    results.append(("Data Store", test_data_store()))
    results.append(("API Routes", test_api_routes()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:.<40} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 60)
    if all_passed:
        print("✓ All tests passed! P2 is ready to use.")
    else:
        print("✗ Some tests failed. Please install missing dependencies.")
        print("\nTo install all dependencies:")
        print("  pip install -r requirements.txt")
        print("  python -m spacy download en_core_web_sm")
        print("  python -c \"import nltk; nltk.download('stopwords')\"")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
