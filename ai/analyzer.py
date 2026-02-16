"""
analyzer.py — Medical data analysis and AI-powered insights.
Handles vital sign validation, conversation analysis, and suggestion generation.
"""

from ai.medgemma_client import ask_medgemma
from ai.prompts import (
    SYSTEM_PROMPT, CONVERSATION_ANALYSIS_PROMPT, SUGGESTION_PROMPT
)

# ── Vital Signs Normal Ranges ──
VITAL_RANGES = {
    'systolic_bp': {'min': 90, 'max': 140, 'unit': 'mmHg', 'name': 'ضغط الدم الانقباضي', 'critical_low': 80, 'critical_high': 180},
    'diastolic_bp': {'min': 60, 'max': 90, 'unit': 'mmHg', 'name': 'ضغط الدم الانبساطي', 'critical_low': 50, 'critical_high': 110},
    'heart_rate': {'min': 60, 'max': 100, 'unit': 'نبضة/دقيقة', 'name': 'معدل نبضات القلب', 'critical_low': 40, 'critical_high': 150},
    'spo2': {'min': 95, 'max': 100, 'unit': '%', 'name': 'نسبة الأكسجين', 'critical_low': 88, 'critical_high': 101},
    'temperature': {'min': 36.1, 'max': 37.2, 'unit': '°C', 'name': 'درجة الحرارة', 'critical_low': 34, 'critical_high': 40},
    'respiratory_rate': {'min': 12, 'max': 20, 'unit': 'نفس/دقيقة', 'name': 'معدل التنفس', 'critical_low': 8, 'critical_high': 30},
    'gcs': {'min': 15, 'max': 15, 'unit': 'درجة', 'name': 'مستوى الوعي GCS', 'critical_low': 8, 'critical_high': 16},
}


def check_vitals(vitals_dict, session_cache=None):
    """
    Validate vital signs against normal ranges.
    Returns list of alerts with context from patient history.
    """
    alerts = []

    for key, value in vitals_dict.items():
        if value is None or value == '' or key not in VITAL_RANGES:
            continue

        try:
            v = float(value)
        except (ValueError, TypeError):
            continue

        ranges = VITAL_RANGES[key]

        # Critical values
        if v <= ranges['critical_low'] or v >= ranges['critical_high']:
            alert = {
                'type': 'critical',
                'title': f"🔴 قيمة حرجة: {ranges['name']}",
                'message': f"القيمة: {v} {ranges['unit']} — الطبيعي: {ranges['min']}–{ranges['max']} {ranges['unit']}",
                'details': ''
            }
            # Add context from patient history
            if session_cache:
                diseases = session_cache.get_disease_names()
                if 'قصور في الشريان التاجي' in diseases and key in ('systolic_bp', 'heart_rate'):
                    alert['details'] = '⚠️ المريض لديه تاريخ قصور شريان تاجي + دعامة → ECG فوري + Troponin'
                elif 'ربو' in diseases and key == 'spo2':
                    alert['details'] = '⚠️ المريض يعاني من ربو — قد يحتاج Nebulizer فوري'
                elif 'Myasthenia Gravis' in diseases and key in ('spo2', 'respiratory_rate'):
                    alert['details'] = '⚠️ المريضة تعاني MG — خطر فشل تنفسي — مراقبة FVC'
            alerts.append(alert)

        # Abnormal but not critical
        elif v < ranges['min'] or v > ranges['max']:
            alerts.append({
                'type': 'high',
                'title': f"🟡 قيمة غير طبيعية: {ranges['name']}",
                'message': f"القيمة: {v} {ranges['unit']} — الطبيعي: {ranges['min']}–{ranges['max']} {ranges['unit']}",
                'details': ''
            })

    return alerts


def check_vitals_simple(vitals_dict):
    """Return vital sign status as formatted text for display."""
    results = []
    for key, value in vitals_dict.items():
        if value is None or value == '' or key not in VITAL_RANGES:
            continue
        try:
            v = float(value)
        except (ValueError, TypeError):
            continue
        
        ranges = VITAL_RANGES[key]
        if v <= ranges['critical_low'] or v >= ranges['critical_high']:
            results.append(f"🔴 {ranges['name']}: {v} {ranges['unit']} (حرج!)")
        elif v < ranges['min'] or v > ranges['max']:
            results.append(f"🟡 {ranges['name']}: {v} {ranges['unit']} (غير طبيعي)")
        else:
            results.append(f"🟢 {ranges['name']}: {v} {ranges['unit']} (طبيعي)")
    
    return "\n".join(results) if results else "لم يتم إدخال علامات حيوية"


def analyze_conversation(transcript, session_cache):
    """Analyze doctor-patient conversation using MedGemma."""
    if not transcript or not transcript.strip():
        return "لم يتم تقديم نص محادثة"

    # First, check for dangerous substances in the text
    substance_alerts = session_cache.check_multiple_substances(transcript)

    # Then use AI for deeper analysis
    prompt = CONVERSATION_ANALYSIS_PROMPT.format(
        transcript=transcript,
        patient_context=session_cache.get_context_for_ai()
    )

    ai_analysis = ask_medgemma(prompt, system_prompt=SYSTEM_PROMPT)
    return ai_analysis, substance_alerts


def generate_suggestions(session_cache, clinical_data="", vitals_text=""):
    """Generate AI-powered suggestions for the ER doctor."""
    prompt = SUGGESTION_PROMPT.format(
        patient_context=session_cache.get_context_for_ai(),
        clinical_data=clinical_data,
        vitals=vitals_text
    )

    return ask_medgemma(prompt, system_prompt=SYSTEM_PROMPT)


def run_diagnosis_loop(session_cache, chief_complaint, form_data, transcript=""):
    """Run the deep diagnosis detective loop."""
    from ai.prompts import DIAGNOSIS_LOOP_PROMPT

    prompt = DIAGNOSIS_LOOP_PROMPT.format(
        session_cache_context=session_cache.get_context_for_ai(),
        chief_complaint=chief_complaint,
        form_data=form_data,
        transcript=transcript
    )

    # Also check for substances mentioned
    all_text = f"{chief_complaint} {form_data} {transcript}"
    substance_alerts = session_cache.check_multiple_substances(all_text)

    ai_result = ask_medgemma(prompt, system_prompt=SYSTEM_PROMPT, max_tokens=2048)
    return ai_result, substance_alerts
