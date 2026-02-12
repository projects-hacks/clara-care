#!/usr/bin/env python3
"""
Seed Sanity CMS with rich demo data for ClaraCare.

Creates:
  - 2 patients (Dorothy Chen, Margaret Wilson)
  - 2 family members (Sarah Chen, James Wilson)
  - 10+ conversations with varied moods and nostalgia engagement
  - Cognitive baselines
  - Wellness digests
  - Alerts across different types/severities

Uses SanityDataStore methods directly (matching DataStore protocol).
Run: python -m scripts.seed_sanity   (from backend/)
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta, date, UTC

# Add backend to path so `app.*` imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from app.storage.sanity import SanityDataStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _create_doc(store: SanityDataStore, doc: dict) -> str:
    """Create a Sanity document via the mutations API (with detailed error logging)."""
    try:
        resp = await store._client.post(
            f"{store.base_url}/mutate/{store.dataset}",
            json={"mutations": [{"createOrReplace": doc}]},
        )
        if resp.status_code >= 400:
            print(f"    ⚠ HTTP {resp.status_code}: {resp.text[:300]}")
        resp.raise_for_status()
    except Exception as exc:
        print(f"    ⚠ Error creating {doc['_id']}: {exc}")
        raise
    return doc["_id"]


# ---------------------------------------------------------------------------
# Seed functions
# ---------------------------------------------------------------------------

async def seed_patients(store: SanityDataStore) -> None:
    """Create two patient documents."""
    patients = [
        {
            "_type": "patient",
            "_id": "patient-dorothy-001",
            "name": "Dorothy Chen",
            "preferredName": "Dorothy",
            "dateOfBirth": "1951-03-15",
            "birthYear": 1951,
            "age": 75,
            "location": {"city": "San Francisco", "state": "CA", "timezone": "America/Los_Angeles"},
            "medications": [
                {"_key": "med1", "name": "Lisinopril", "dosage": "10mg", "schedule": "9 AM daily"},
                {"_key": "med2", "name": "Vitamin D", "dosage": "2000 IU", "schedule": "Morning with breakfast"},
            ],
            "familyContacts": [{"_ref": "family-sarah-001", "_type": "reference", "_key": "fc1"}],
            "preferences": {
                "favoriteTopics": ["gardening", "1960s music", "family", "cooking"],
                "communicationStyle": ["warm and patient"],
                "interests": ["music", "gardening", "family history"],
            },
            "cognitiveThresholds": {"deviationThreshold": 0.20, "consecutiveTrigger": 3},
        },
        {
            "_type": "patient",
            "_id": "patient-margaret-002",
            "name": "Margaret Wilson",
            "preferredName": "Margaret",
            "dateOfBirth": "1943-07-22",
            "birthYear": 1943,
            "age": 83,
            "location": {"city": "Portland", "state": "OR", "timezone": "America/Los_Angeles"},
            "medications": [
                {"_key": "med1", "name": "Metformin", "dosage": "500mg", "schedule": "Morning and evening"},
                {"_key": "med2", "name": "Aspirin", "dosage": "81mg", "schedule": "Morning"},
            ],
            "familyContacts": [{"_ref": "family-james-002", "_type": "reference", "_key": "fc1"}],
            "preferences": {
                "favoriteTopics": ["knitting", "classic movies", "baking", "birds"],
                "communicationStyle": ["gentle and cheerful"],
                "interests": ["birdwatching", "baking", "old Hollywood"],
            },
            "cognitiveThresholds": {"deviationThreshold": 0.20, "consecutiveTrigger": 3},
        },
    ]
    for p in patients:
        await _create_doc(store, p)
        print(f"  ✓ Patient: {p['name']} ({p['_id']})")


async def seed_family(store: SanityDataStore) -> None:
    """Create family member documents (without patient refs first to avoid circular deps)."""
    members = [
        {
            "_type": "familyMember",
            "_id": "family-sarah-001",
            "name": "Sarah Chen",
            "email": "sarah.chen@email.com",
            "phone": "+14155550123",
            "relationship": "Daughter",
            "notificationPreferences": {"dailyDigest": True, "instantAlerts": True, "weeklyReport": True},
        },
        {
            "_type": "familyMember",
            "_id": "family-james-002",
            "name": "James Wilson",
            "email": "james.wilson@email.com",
            "phone": "+15035550456",
            "relationship": "Son",
            "notificationPreferences": {"dailyDigest": True, "instantAlerts": True, "weeklyReport": False},
        },
    ]
    for m in members:
        await _create_doc(store, m)
        print(f"  ✓ Family: {m['name']} ({m['relationship']})")


async def patch_family_refs(store: SanityDataStore) -> None:
    """Patch patient references into family members (after patients exist)."""
    patches = [
        {"patch": {"id": "family-sarah-001", "set": {"patients": [{"_ref": "patient-dorothy-001", "_type": "reference", "_key": "p1"}]}}},
        {"patch": {"id": "family-james-002", "set": {"patients": [{"_ref": "patient-margaret-002", "_type": "reference", "_key": "p1"}]}}},
    ]
    for p in patches:
        try:
            resp = await store._client.post(
                f"{store.base_url}/mutate/{store.dataset}",
                json={"mutations": [p]},
            )
            resp.raise_for_status()
        except Exception as exc:
            print(f"    ⚠ Patch error: {exc}")
    print("  ✓ Patched patient references into family members")


async def seed_conversations(store: SanityDataStore) -> None:
    """Create 12 conversations for Dorothy (all 6 moods, some with nostalgia)."""
    base = datetime.now(UTC) - timedelta(days=14)
    convos = [
        # 1 - nostalgic with nostalgia engagement
        {"_id": "conv-d-001", "mood": "nostalgic", "dur": 420,
         "summary": "Dorothy shared memories of gardening with her mother in the 1960s.",
         "cm": {"vocabularyDiversity": 0.65, "topicCoherence": 0.88, "repetitionCount": 2, "repetitionRate": 0.04, "wordFindingPauses": 1, "responseLatency": 1.4},
         "ne": {"triggered": True, "era": "1966-1976", "contentUsed": "Shared memories of 1960s gardening", "engagementScore": 8}},
        # 2 - neutral
        {"_id": "conv-d-002", "mood": "neutral", "dur": 360,
         "summary": "Talked about medication schedule. Dorothy mentioned she sometimes forgets afternoon vitamins.",
         "cm": {"vocabularyDiversity": 0.60, "topicCoherence": 0.85, "repetitionCount": 3, "repetitionRate": 0.06, "wordFindingPauses": 2, "responseLatency": 1.6},
         "ne": None},
        # 3 - happy
        {"_id": "conv-d-003", "mood": "happy", "dur": 480,
         "summary": "Dorothy excitedly talked about her grandson's upcoming graduation.",
         "cm": {"vocabularyDiversity": 0.68, "topicCoherence": 0.90, "repetitionCount": 1, "repetitionRate": 0.02, "wordFindingPauses": 0, "responseLatency": 1.2},
         "ne": None},
        # 4 - happy
        {"_id": "conv-d-004", "mood": "happy", "dur": 300,
         "summary": "Discussed upcoming lunch plans with neighbor.",
         "cm": {"vocabularyDiversity": 0.62, "topicCoherence": 0.87, "repetitionCount": 2, "repetitionRate": 0.05, "wordFindingPauses": 1, "responseLatency": 1.5},
         "ne": None},
        # 5 - nostalgic with nostalgia engagement
        {"_id": "conv-d-005", "mood": "nostalgic", "dur": 450,
         "summary": "Talked about 1960s music - The Beatles, The Beach Boys. Dorothy very nostalgic.",
         "cm": {"vocabularyDiversity": 0.61, "topicCoherence": 0.89, "repetitionCount": 2, "repetitionRate": 0.04, "wordFindingPauses": 2, "responseLatency": 1.6},
         "ne": {"triggered": True, "era": "1966-1976", "contentUsed": "The Beatles released I Want to Hold Your Hand in 1963", "engagementScore": 9}},
        # 6 - happy
        {"_id": "conv-d-006", "mood": "happy", "dur": 390,
         "summary": "Dorothy shared a recipe for her famous apple pie. Talked about family gatherings.",
         "cm": {"vocabularyDiversity": 0.63, "topicCoherence": 0.86, "repetitionCount": 3, "repetitionRate": 0.06, "wordFindingPauses": 1, "responseLatency": 1.5},
         "ne": None},
        # 7 - neutral
        {"_id": "conv-d-007", "mood": "neutral", "dur": 330,
         "summary": "General check-in. Dorothy mentioned feeling a bit tired but overall good.",
         "cm": {"vocabularyDiversity": 0.59, "topicCoherence": 0.84, "repetitionCount": 4, "repetitionRate": 0.07, "wordFindingPauses": 3, "responseLatency": 1.8},
         "ne": None},
        # 8 - sad
        {"_id": "conv-d-008", "mood": "sad", "dur": 280,
         "summary": "Dorothy seemed a bit down today. Mentioned missing her late husband.",
         "cm": {"vocabularyDiversity": 0.55, "topicCoherence": 0.80, "repetitionCount": 3, "repetitionRate": 0.08, "wordFindingPauses": 4, "responseLatency": 2.0},
         "ne": None},
        # 9 - confused
        {"_id": "conv-d-009", "mood": "confused", "dur": 250,
         "summary": "Dorothy had trouble remembering if she had taken her medication.",
         "cm": {"vocabularyDiversity": 0.52, "topicCoherence": 0.75, "repetitionCount": 5, "repetitionRate": 0.10, "wordFindingPauses": 5, "responseLatency": 2.2},
         "ne": None},
        # 10 - distressed
        {"_id": "conv-d-010", "mood": "distressed", "dur": 200,
         "summary": "Dorothy was upset about not being able to find her reading glasses.",
         "cm": {"vocabularyDiversity": 0.50, "topicCoherence": 0.72, "repetitionCount": 4, "repetitionRate": 0.09, "wordFindingPauses": 6, "responseLatency": 2.5},
         "ne": None},
        # 11 - nostalgic with nostalgia engagement
        {"_id": "conv-d-011", "mood": "nostalgic", "dur": 500,
         "summary": "Dorothy reminisced about her wedding day and first dance. Highly engaged.",
         "cm": {"vocabularyDiversity": 0.67, "topicCoherence": 0.91, "repetitionCount": 1, "repetitionRate": 0.03, "wordFindingPauses": 0, "responseLatency": 1.3},
         "ne": {"triggered": True, "era": "1966-1976", "contentUsed": "Frank Sinatra's Fly Me to the Moon was popular", "engagementScore": 10}},
        # 12 - happy
        {"_id": "conv-d-012", "mood": "happy", "dur": 400,
         "summary": "Talked about her garden blooming. Dorothy was cheerful and chatty.",
         "cm": {"vocabularyDiversity": 0.64, "topicCoherence": 0.88, "repetitionCount": 2, "repetitionRate": 0.04, "wordFindingPauses": 1, "responseLatency": 1.4},
         "ne": None},
    ]

    for i, c in enumerate(convos):
        ts = (base + timedelta(days=i)).isoformat()
        doc: dict = {
            "_type": "conversation",
            "_id": c["_id"],
            "patient": {"_ref": "patient-dorothy-001", "_type": "reference"},
            "timestamp": ts,
            "duration": c["dur"],
            "transcript": f"Clara: Hello Dorothy! How are you today?\nDorothy: {c['summary'][:60]}...",
            "summary": c["summary"],
            "mood": c["mood"],
            "cognitiveMetrics": c["cm"],
        }
        if c["ne"]:
            doc["nostalgiaEngagement"] = c["ne"]
        await _create_doc(store, doc)
        ne_label = " + nostalgia" if c["ne"] else ""
        print(f"  ✓ Conversation {i+1}: {c['mood']}{ne_label}")


async def seed_alerts(store: SanityDataStore) -> None:
    """Create 5 alerts with different types and severities."""
    now = datetime.now(UTC)
    alerts_data = [
        {"_id": "alert-d-001", "pid": "patient-dorothy-001", "type": "word_finding_difficulty", "sev": "low",
         "desc": "Slight increase in word-finding pauses detected", "ack": True, "ack_by": "family-sarah-001",
         "ts": (now - timedelta(days=5)).isoformat()},
        {"_id": "alert-d-002", "pid": "patient-dorothy-001", "type": "repetition_increase", "sev": "low",
         "desc": "Repetition rate slightly elevated in recent conversation", "ack": False, "ack_by": None,
         "ts": (now - timedelta(days=3)).isoformat()},
        {"_id": "alert-d-003", "pid": "patient-dorothy-001", "type": "coherence_drop", "sev": "medium",
         "desc": "Topic coherence dropped below baseline in confused conversation", "ack": False, "ack_by": None,
         "ts": (now - timedelta(days=2)).isoformat()},
        {"_id": "alert-d-004", "pid": "patient-dorothy-001", "type": "word_finding_difficulty", "sev": "medium",
         "desc": "Multiple word-finding pauses in distressed conversation", "ack": False, "ack_by": None,
         "ts": (now - timedelta(days=1)).isoformat()},
        {"_id": "alert-d-005", "pid": "patient-dorothy-001", "type": "vocabulary_decline", "sev": "high",
         "desc": "Significant vocabulary diversity decline over last 3 conversations", "ack": False, "ack_by": None,
         "ts": (now - timedelta(hours=6)).isoformat()},
    ]
    for a in alerts_data:
        doc: dict = {
            "_type": "alert",
            "_id": a["_id"],
            "patient": {"_ref": a["pid"], "_type": "reference"},
            "alertType": a["type"],
            "severity": a["sev"],
            "description": a["desc"],
            "acknowledged": a["ack"],
            "timestamp": a["ts"],
        }
        if a["ack_by"]:
            doc["acknowledgedBy"] = {"_ref": a["ack_by"], "_type": "reference"}
        await _create_doc(store, doc)
        print(f"  ✓ Alert: {a['type']} ({a['sev']})")


async def seed_baselines(store: SanityDataStore) -> None:
    """Create cognitive baselines for Dorothy."""
    await store.save_cognitive_baseline("patient-dorothy-001", {
        "patient_id": "patient-dorothy-001",
        "established": True,
        "baseline_date": (date.today() - timedelta(days=7)).isoformat(),
        "vocabulary_diversity": 0.626,
        "vocabulary_diversity_std": 0.031,
        "topic_coherence": 0.870,
        "topic_coherence_std": 0.021,
        "repetition_rate": 0.049,
        "repetition_rate_std": 0.016,
        "word_finding_pauses": 1.43,
        "word_finding_pauses_std": 0.98,
        "avg_response_time": 1.51,
        "response_time_std": 0.18,
        "conversation_count": 7,
        "last_updated": datetime.now(UTC).isoformat(),
    })
    print("  ✓ Baseline for Dorothy")


async def seed_digests(store: SanityDataStore) -> None:
    """Create recent wellness digests."""
    for i in range(7):
        d = date.today() - timedelta(days=6 - i)
        conv_id = f"conv-d-{i+1:03d}"
        moods = ["nostalgic", "neutral", "happy", "happy", "nostalgic", "happy", "neutral"]
        scores = [85, 78, 92, 80, 86, 82, 75]
        await store.save_wellness_digest({
            "id": f"digest-d-{i+1:03d}",
            "patient_id": "patient-dorothy-001",
            "date": d.isoformat(),
            "overall_mood": moods[i],
            "highlights": [f"Day {i+1} conversation highlights"],
            "cognitive_score": scores[i],
            "cognitive_trend": "stable",
            "recommendations": [],
            "conversation_id": conv_id,
            "created_at": datetime.now(UTC).isoformat(),
        })
    print("  ✓ 7 wellness digests for Dorothy")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    print("🌱 Seeding Sanity CMS with ClaraCare demo data...\n")

    project_id = os.getenv("SANITY_PROJECT_ID")
    dataset = os.getenv("SANITY_DATASET", "production")
    token = os.getenv("SANITY_TOKEN")

    if not project_id or not token:
        print("❌ Missing SANITY_PROJECT_ID or SANITY_TOKEN in .env")
        print("   Set them and try again.")
        sys.exit(1)

    store = SanityDataStore(project_id=project_id, dataset=dataset, token=token)
    print(f"Connected to Sanity project: {project_id} / {dataset}\n")

    try:
        print("--- Family Members (no patient refs yet) ---")
        await seed_family(store)

        print("\n--- Patients ---")
        await seed_patients(store)

        print("\n--- Patch family → patient refs ---")
        await patch_family_refs(store)

        print("\n--- Conversations (12 for Dorothy) ---")
        await seed_conversations(store)

        print("\n--- Alerts (5) ---")
        await seed_alerts(store)

        print("\n--- Baselines ---")
        await seed_baselines(store)

        print("\n--- Digests ---")
        await seed_digests(store)

        print("\n" + "=" * 60)
        print("🎉 Seed complete!")
        print("=" * 60)
        print("  Patients:       2 (Dorothy + Margaret)")
        print("  Family:         2 (Sarah + James)")
        print("  Conversations: 12 (6 moods, 3 with nostalgia)")
        print("  Alerts:         5 (low/medium/high)")
        print("  Baselines:      1")
        print("  Digests:        7")
        print(f"\n  Studio: https://{project_id}.sanity.studio")
        print(f"  Insights API: GET /api/patients/patient-dorothy-001/insights")
        print("=" * 60)
    except Exception as exc:
        print(f"\n❌ Seed failed: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await store.close()


if __name__ == "__main__":
    asyncio.run(main())
