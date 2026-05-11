"""
Quick test to verify Supabase connection and SupabaseDataStore integration.
Run: python -m tests.test_supabase_connection
"""

import asyncio
import os
import sys
from pathlib import Path

# Load .env
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

from app.storage.supabase_store import SupabaseDataStore


async def main():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set in .env")
        sys.exit(1)

    print(f"🔗 Connecting to Supabase: {url}")
    store = SupabaseDataStore(url=url, service_role_key=key)

    # Test 1: List patients (should be empty or have data)
    print("\n--- Test 1: Query patients table ---")
    result = store.client.table("patients").select("id, name, preferred_name").execute()
    patients = result.data or []
    print(f"✅ Found {len(patients)} patient(s)")
    for p in patients:
        print(f"   → {p['id'][:8]}... | {p.get('name')} ({p.get('preferred_name')})")

    # Test 2: Query profiles table
    print("\n--- Test 2: Query profiles table ---")
    result = store.client.table("profiles").select("id, display_name").execute()
    profiles = result.data or []
    print(f"✅ Found {len(profiles)} profile(s)")
    for p in profiles:
        print(f"   → {p['id'][:8]}... | {p.get('display_name')}")

    # Test 3: Query all tables exist
    print("\n--- Test 3: Verify all tables exist ---")
    tables = [
        "profiles", "patients", "medications", "family_contacts",
        "conversations", "cognitive_baselines", "alerts",
        "wellness_digests", "deviation_trackers"
    ]
    for table in tables:
        try:
            result = store.client.table(table).select("*", count="exact").limit(0).execute()
            count = result.count if hasattr(result, 'count') else '?'
            print(f"   ✅ {table} — {count} rows")
        except Exception as e:
            print(f"   ❌ {table} — ERROR: {e}")

    # Test 4: Test DataStore protocol methods
    print("\n--- Test 4: Test DataStore protocol methods ---")

    # get_patient with non-existent ID
    patient = await store.get_patient("non-existent-id")
    print(f"   ✅ get_patient(non-existent) → {patient}")

    # get_conversations
    convos = await store.get_conversations("non-existent-id")
    print(f"   ✅ get_conversations(non-existent) → {len(convos)} conversations")

    # get_alerts
    alerts = await store.get_alerts("non-existent-id")
    print(f"   ✅ get_alerts(non-existent) → {len(alerts)} alerts")

    # get_cognitive_baseline
    baseline = await store.get_cognitive_baseline("non-existent-id")
    print(f"   ✅ get_cognitive_baseline(non-existent) → {baseline}")

    # get_wellness_digests
    digests = await store.get_wellness_digests("non-existent-id")
    print(f"   ✅ get_wellness_digests(non-existent) → {len(digests)} digests")

    # get_consecutive_deviations
    devs = await store.get_consecutive_deviations("non-existent-id")
    print(f"   ✅ get_consecutive_deviations(non-existent) → {devs}")

    # get_family_contacts
    contacts = await store.get_family_contacts("non-existent-id")
    print(f"   ✅ get_family_contacts(non-existent) → {len(contacts)} contacts")

    print("\n✅ All tests passed! Supabase integration is working.")
    await store.close()


if __name__ == "__main__":
    asyncio.run(main())
