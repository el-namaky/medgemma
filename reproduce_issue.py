import sys
import os

# Ensure we are in the project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force Mock Mode
os.environ['MEDGEMMA_MOCK'] = 'true'

from ai.medgemma_client import load_medgemma, ask_medgemma

print("=" * 50)
print("🧪 Testing Mock Mode Improvements")
print("=" * 50)

# Load Model (Mock)
print("\n[Init] Loading model...")
load_medgemma()

# Test 1: Choking (Explicit Handler)
print("\n[Test 1] Query: 'ما هي الاسعفات الاولية للاختناق'")
response_choking = ask_medgemma("ما هي الاسعفات الاولية للاختناق")
if "هيمليك" in response_choking or "Heimlich" in response_choking:
    print("✅ Success: Choking handler worked.")
    print(f"   Excerpt: {response_choking[:100]}...")
else:
    print("❌ Failure: Choking handler did not return expected text.")
    print(f"   Response: {response_choking}")

# Test 2: Unknown Query (Generic Fallback + Disclaimer)
print("\n[Test 2] Query: 'General unknown query'")
response_unknown = ask_medgemma("General unknown query")
if "وضع المحاكاة" in response_unknown or "Demo Mode" in response_unknown:
    print("✅ Success: Generic fallback includes Demo Mode disclaimer.")
    print(f"   Excerpt: {response_unknown[:100]}...")
else:
    print("❌ Failure: Generic fallback missing disclaimer.")
    print(f"   Response: {response_unknown}")

print("\n" + "=" * 50)
print("End of Test")
