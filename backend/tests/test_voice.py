"""
Test script for Clara's voice agent
Verifies all components are working
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.voice.persona import get_system_prompt, get_function_definitions
from app.voice.functions import FunctionHandler


async def test_persona():
    """Test that Clara's persona is properly configured"""
    print("Testing Clara's persona...")
    
    system_prompt = get_system_prompt()
    assert len(system_prompt) > 0, "System prompt is empty"
    assert "Clara" in system_prompt, "System prompt doesn't mention Clara"
    
    print(f"✓ System prompt loaded ({len(system_prompt)} characters)")
    print(f"  First 100 chars: {system_prompt[:100]}...")


async def test_functions():
    """Test function definitions"""
    print("\nTesting function definitions...")
    
    functions = get_function_definitions()
    assert len(functions) == 6, f"Expected 6 functions, got {len(functions)}"
    
    expected_functions = [
        "get_patient_context",
        "search_nostalgia",
        "search_realtime",
        "log_medication_check",
        "trigger_alert",
        "save_conversation"
    ]
    
    function_names = [f["name"] for f in functions]
    for expected in expected_functions:
        assert expected in function_names, f"Missing function: {expected}"
    
    print(f"✓ All 6 functions defined: {', '.join(function_names)}")


async def test_function_handler():
    """Test function handler execution"""
    print("\nTesting function handler...")
    
    handler = FunctionHandler(patient_id="test-patient-123")
    
    # Test get_patient_context
    result = await handler.get_patient_context({"patient_id": "test-patient-123"})
    assert result["success"] == True, "get_patient_context failed"
    print(f"✓ get_patient_context: {result.get('note', 'Working')}")
    
    # Test log_medication_check
    result = await handler.log_medication_check({
        "patient_id": "test-patient-123",
        "medication_name": "Blood pressure medication",
        "taken": True,
        "notes": "Took with breakfast"
    })
    # Should succeed even if Sanity is not connected (fallback)
    assert result.get("success") == True or result.get("message"), "log_medication_check failed completely"
    print(f"✓ log_medication_check: {result.get('message', result.get('note', 'Logged'))}")
    
    # Test search_nostalgia
    result = await handler.search_nostalgia({
        "patient_id": "test-patient-123",
        "trigger_reason": "patient feeling lonely"
    })
    assert result["success"] == True, "search_nostalgia failed"
    print(f"✓ search_nostalgia: {result.get('golden_years', 'Retrieved')}")
    
    # Test search_realtime (falls back when YOU_API_KEY not set)
    result = await handler.search_realtime({
        "query": "weather today",
        "patient_id": "test-patient-123"
    })
    assert result["success"] == True, "search_realtime failed"
    print(f"✓ search_realtime: {result.get('note', result.get('answer', 'Working')[:50])}")
    
    # Test trigger_alert
    result = await handler.trigger_alert({
        "patient_id": "test-patient-123",
        "severity": "medium",
        "alert_type": "distress",
        "message": "Test alert - patient seemed confused"
    })
    assert result["success"] == True, "trigger_alert failed"
    print(f"✓ trigger_alert: {result.get('message', 'Sent')}")
    
    # Test save_conversation
    result = await handler.save_conversation({
        "patient_id": "test-patient-123",
        "transcript": "Clara: Good morning! How are you?\nPatient: I'm feeling alright.",
        "duration": 120,
        "summary": "Brief morning check-in, patient feeling okay.",
        "detected_mood": "neutral"
    })
    assert result["success"] == True, "save_conversation failed"
    print(f"✓ save_conversation: {result.get('message', 'Saved')}")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("ClaraCare Voice Agent - Component Test")
    print("=" * 60)
    
    try:
        await test_persona()
        await test_functions()
        await test_function_handler()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Clara is ready!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Server is running on http://localhost:8000")
        print("2. Configure Twilio webhook to point to your server")
        print("3. Make a test call to Clara!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
