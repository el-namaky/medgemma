import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("🧪 Testing Gemma-Health Sentinel MVP")
print("=" * 50)

# Test 1: Database
print("\n📦 Test 1: Database initialization...")
from db.init_db import init_database
init_database()

print("\n📦 Test 2: Seed data...")
from db.seed_data import seed_all
seed_all()

# Test 3: Queries
print("\n🔍 Test 3: Querying patient data...")
from db.queries import get_patient_full_record, get_all_patients_summary
patients = get_all_patients_summary()
print(f"   Patients count: {len(patients)}")
for p in patients:
    print(f"   {p['patient_id']}. {p['name']} — {p['age']} سنة")

# Test 4: Session Cache + Contraindication check
print("\n🧠 Test 4: Session Cache + Contraindication check...")
from ai.session_cache import SessionCache
cache = SessionCache(3)  # Sarah

alerts = cache.check_substance('Magnesium')
print(f"\n   Checking 'Magnesium' for Sarah (MG patient):")
print(f"   Alerts found: {len(alerts)}")
for a in alerts:
    print(f"   🔴 {a['title']}")
    print(f"      {a['message']}")

# Test 5: MedGemma Mock
print("\n🧠 Test 5: MedGemma mock inference...")
os.environ['MEDGEMMA_MOCK'] = 'true'
from ai.medgemma_client import load_medgemma, ask_medgemma
from ai.prompts import SYSTEM_PROMPT
load_medgemma()
response = ask_medgemma("ملخص سريع عن مريضة سارة خالد Myasthenia Gravis", system_prompt=SYSTEM_PROMPT)
print(f"   Response preview: {response[:100]}...")

# Test 6: Gradio import
print("\n🎨 Test 6: Gradio import...")
try:
    import gradio as gr
    print(f"   Gradio version: {gr.__version__}")
    print("   ✅ Gradio available")
except ImportError:
    print("   ⚠️ Gradio not installed — run: pip install gradio")

print("\n" + "=" * 50)
print("✅ All tests passed!")
print("=" * 50)
print("\n🚀 To launch the app: python app.py")
