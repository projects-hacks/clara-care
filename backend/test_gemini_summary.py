"""
Local test: Verify Gemini summarization is working and well-formatted.
Run from backend dir: python test_gemini_summary.py
"""
import asyncio
import os
import sys

# Ensure the backend app is importable
sys.path.insert(0, os.path.dirname(__file__))

# Load .env
from dotenv import load_dotenv
load_dotenv()

from app.cognitive.post_call_analyzer import _gemini_summarize

# ── Realistic test transcript (a typical Clara call) ────────────────────────
TEST_TRANSCRIPT = """
Clara: Good morning, Emily! How are you feeling today?
Emily: Oh, hi dear. I'm doing alright, I suppose. A bit tired today.
Clara: I'm sorry to hear you're tired. Did you sleep well last night?
Emily: Not really. I kept waking up. I think it might be the weather changing. You know how my joints act up.
Clara: That makes sense. The weather has been quite unpredictable lately. Have you taken your medication this morning?
Emily: Yes, I took my lisinopril and the metformin with breakfast. I had some toast and tea.
Clara: That's great that you remembered! What are you planning for today?
Emily: Well, I was thinking about going out to the garden. The tomatoes need watering. And my neighbor Mrs. Rodriguez said she'd stop by this afternoon to bring me some of her famous enchiladas.
Clara: Oh that sounds lovely! Mrs. Rodriguez sounds like a wonderful neighbor.
Emily: She really is. You know, I was thinking... I haven't talked to my daughter Sarah in a few days. I miss her. Could you let her know I'd love a call when she has time?
Clara: Of course, Emily. I'll make sure Sarah knows you'd love to hear from her.
Emily: Thank you, dear. You know, I was watching this cooking show yesterday and they made the most beautiful pasta dish. It reminded me of when I used to make fresh pasta with my mother. Those were such good times.
Clara: That sounds like a beautiful memory. Do you still enjoy cooking?
Emily: I do, but it's harder now. My hands aren't as steady. Maybe I should try that pasta recipe though. Start simple.
Clara: That sounds like a wonderful idea! Starting simple is always smart.
Emily: Yes. Oh, I wanted to ask - what's the weather going to be like tomorrow? I need to know if I should cover my tomato plants.
Clara: It looks like tomorrow will be sunny and warm, around 75 degrees. Your tomatoes should be just fine!
Emily: Oh good. That's a relief. Well, thank you for chatting with me, dear. These calls really do brighten my morning.
Clara: It's always a pleasure talking with you, Emily. Enjoy those enchiladas later!
Emily: I will! Goodbye, dear.
"""

TEST_PATIENT_CONTEXT = {
    "name": "Emily Chen",
    "preferred_name": "Emily",
    "location": "San Jose, CA",
    "family_names": ["Sarah Chen", "Michael Chen"],
    "interests": ["gardening", "cooking", "watching cooking shows"],
}


async def main():
    print("=" * 70)
    print("  GEMINI SUMMARIZATION TEST")
    print("=" * 70)
    
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("\n❌ GEMINI_API_KEY not found in environment. Check .env file.")
        return
    print(f"\n✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test 1: Generate summary with full context
    print("\n" + "-" * 70)
    print("TEST 1: Summary with full patient context")
    print("-" * 70)
    summary = await _gemini_summarize(TEST_TRANSCRIPT, patient_context=TEST_PATIENT_CONTEXT)
    if summary:
        print(f"\n✅ Summary generated ({len(summary)} chars):\n")
        print(f'  "{summary}"')
        print(f"\n  Word count: {len(summary.split())}")
        
        # Quality checks
        issues = []
        import re as _re
        summary_lower = summary.lower()
        if _re.search(r'\bclara\b', summary_lower) or _re.search(r'\bai\b', summary_lower) or _re.search(r'\bcompanion\b', summary_lower):
            issues.append("❌ Contains 'Clara', 'AI', or 'companion' — should not")
        if _re.search(r'\bcaller\b', summary_lower) or _re.search(r'\bhost\b', summary_lower):
            issues.append("❌ Contains 'caller' or 'host' — should not")
        if "Emily" not in summary:
            issues.append("⚠️  Doesn't mention 'Emily' by name")
        if len(summary.split()) > 80:
            issues.append("⚠️  Over 80 words — might be too long")
        if len(summary.split()) < 15:
            issues.append("⚠️  Under 15 words — might be too short")
        
        if issues:
            print("\n  Quality issues:")
            for issue in issues:
                print(f"    {issue}")
        else:
            print("\n  ✅ All quality checks passed!")
    else:
        print("\n❌ No summary returned. Check API key and model availability.")
    
    # Test 2: Generate summary without context (fallback)
    print("\n" + "-" * 70)
    print("TEST 2: Summary without patient context (minimal)")
    print("-" * 70)
    summary2 = await _gemini_summarize(TEST_TRANSCRIPT, patient_context=None)
    if summary2:
        print(f"\n✅ Summary generated ({len(summary2)} chars):\n")
        print(f'  "{summary2}"')
    else:
        print("\n❌ No summary returned.")
    
    # Test 3: Full analyze_transcript pipeline
    print("\n" + "-" * 70)
    print("TEST 3: Full analyze_transcript pipeline (Deepgram + Gemini)")
    print("-" * 70)
    try:
        from app.cognitive.post_call_analyzer import analyze_transcript
        result = await analyze_transcript(
            TEST_TRANSCRIPT,
            medications=["lisinopril", "metformin"],
            patient_context=TEST_PATIENT_CONTEXT,
        )
        print(f"\n✅ Pipeline completed successfully!")
        print(f"\n  Summary: \"{result.get('summary', 'N/A')}\"")
        print(f"  Mood: {result.get('mood', 'N/A')}")
        print(f"  Mood Explanation: {result.get('mood_explanation', 'N/A')}")
        print(f"  Topics: {result.get('topics', [])}")
        print(f"  Engagement: {result.get('engagement_level', 'N/A')}")
        print(f"  Medication: {result.get('medication_status', {})}")
        print(f"  Safety Flags: {result.get('safety_flags', [])}")
        print(f"  Desire to Connect: {result.get('desire_to_connect', False)}")
    except Exception as exc:
        print(f"\n⚠️  Pipeline test skipped or failed: {exc}")
        print("  (This is expected if DEEPGRAM_API_KEY is not set locally)")
    
    print("\n" + "=" * 70)
    print("  DONE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
