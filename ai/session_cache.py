"""
session_cache.py — In-memory cache for patient data during a session.
Loads all patient data once from SQLite, then all checks run from memory.
"""

from db.queries import (
    get_patient_info, get_chronic_diseases, get_allergies,
    get_medications, get_surgeries, get_visits, get_lab_results,
    get_abnormal_labs, get_all_contraindications
)


class SessionCache:
    """
    Created when a patient is selected in the reception UI.
    Stays in memory for the entire doctor-patient session.
    """

    def __init__(self, patient_id):
        self.patient_id = patient_id

        # Load everything once from SQLite
        self.patient_info = get_patient_info(patient_id)
        self.chronic_diseases = get_chronic_diseases(patient_id)
        self.allergies = get_allergies(patient_id)
        self.medications = get_medications(patient_id)
        self.surgeries = get_surgeries(patient_id)
        self.visits = get_visits(patient_id)
        self.lab_results = get_lab_results(patient_id)
        self.abnormal_labs = get_abnormal_labs(patient_id)

        # Load all contraindications related to this patient's diseases
        disease_names = [d['disease_name'] for d in self.chronic_diseases]
        self.contraindications = get_all_contraindications(disease_names)

        # AI summary (generated once)
        self.ai_summary = None

        # Session updates log
        self.session_updates = []

        # Current form data
        self.current_vitals = {}
        self.current_complaint = ""
        self.current_transcript = ""

        print(f"✅ Session cache created for patient: {self.patient_info.get('name', 'Unknown')}")
        print(f"   Diseases: {len(self.chronic_diseases)} | Allergies: {len(self.allergies)} | "
              f"Medications: {len(self.medications)} | Contraindications: {len(self.contraindications)}")

    def check_substance(self, substance_name):
        """
        Instant check — no database query needed.
        Returns list of alerts (dicts with type, title, message, details).
        """
        if not substance_name or not substance_name.strip():
            return []

        alerts = []
        substance_lower = substance_name.lower().strip()

        # Check against contraindications (disease-substance interactions)
        for ci in self.contraindications:
            ci_substance = ci['contraindicated_substance'].lower()
            if ci_substance in substance_lower or substance_lower in ci_substance:
                risk = ci['risk_level']
                alert_type = 'critical' if risk == 'critical' else ('high' if risk == 'high' else 'moderate')
                alerts.append({
                    'type': alert_type,
                    'title': f"خطر {'حرج' if risk == 'critical' else 'عالي' if risk == 'high' else 'متوسط'}: "
                             f"تعارض {substance_name} مع {ci['disease_name']}",
                    'message': ci['reason'],
                    'details': f"المصدر: {ci.get('source', 'N/A')} | مستوى الخطر: {risk}",
                    'risk_level': risk
                })

        # Check against allergies
        for allergy in self.allergies:
            allergen_lower = allergy['allergen'].lower()
            if allergen_lower in substance_lower or substance_lower in allergen_lower:
                alerts.append({
                    'type': 'critical',
                    'title': f"🚨 حساسية مسجلة: {allergy['allergen']}",
                    'message': f"المريض لديه حساسية من {allergy['allergen']} — "
                               f"رد فعل سابق: {allergy.get('reaction_type', 'غير محدد')}",
                    'details': f"شدة الحساسية: {allergy.get('severity', 'غير محدد')}",
                    'risk_level': 'critical'
                })

        return alerts

    def check_multiple_substances(self, text):
        """Check a text field for any mentioned substances against the patient's data."""
        all_alerts = []

        # All known dangerous substances from contraindications
        known_substances = set()
        for ci in self.contraindications:
            known_substances.add(ci['contraindicated_substance'])
        for al in self.allergies:
            known_substances.add(al['allergen'])

        # Check each known substance against the text
        text_lower = text.lower()
        for substance in known_substances:
            if substance.lower() in text_lower:
                alerts = self.check_substance(substance)
                all_alerts.extend(alerts)

        # Deduplicate
        seen = set()
        unique_alerts = []
        for a in all_alerts:
            key = a['title']
            if key not in seen:
                seen.add(key)
                unique_alerts.append(a)

        return unique_alerts

    def get_context_for_ai(self):
        """Compile all cached data into a text context for MedGemma."""
        parts = []

        # Patient info
        p = self.patient_info
        parts.append(f"المريض: {p.get('name', '')} — {p.get('age', '')} سنة — {p.get('gender', '')} — "
                     f"فصيلة الدم: {p.get('blood_type', '')}")

        # Chronic diseases
        if self.chronic_diseases:
            diseases_str = ", ".join([f"{d['disease_name']} ({d.get('severity', '')})" for d in self.chronic_diseases])
            parts.append(f"الأمراض المزمنة: {diseases_str}")

        # Allergies
        if self.allergies:
            allergy_str = ", ".join([f"{a['allergen']} ({a.get('reaction_type', '')})" for a in self.allergies])
            parts.append(f"الحساسيات: {allergy_str}")

        # Current medications
        if self.medications:
            med_str = ", ".join([f"{m['drug_name']} {m.get('dose', '')} {m.get('frequency', '')}" for m in self.medications])
            parts.append(f"الأدوية الحالية: {med_str}")

        # Surgeries
        if self.surgeries:
            surg_str = ", ".join([f"{s['surgery_name']} ({s.get('surgery_date', '')})" for s in self.surgeries])
            parts.append(f"العمليات السابقة: {surg_str}")

        # Recent visits
        if self.visits:
            parts.append("الزيارات الأخيرة:")
            for v in self.visits[:3]:
                parts.append(f"  - {v.get('visit_date', '')}: {v.get('reason', '')} → {v.get('diagnosis', '')}")

        # Abnormal labs
        if self.abnormal_labs:
            parts.append("تحاليل غير طبيعية:")
            for lab in self.abnormal_labs:
                parts.append(f"  - {lab['test_name']}: {lab['result_value']} (الطبيعي: {lab.get('normal_range', '')})")

        # Contraindications
        if self.contraindications:
            parts.append("المواد الممنوعة:")
            for ci in self.contraindications:
                parts.append(f"  - {ci['contraindicated_substance']} ({ci['risk_level']}): {ci['reason']}")

        # Current vitals if available 
        if self.current_vitals:
            parts.append("العلامات الحيوية الحالية:")
            for k, v in self.current_vitals.items():
                parts.append(f"  - {k}: {v}")

        return "\n".join(parts)

    def add_session_update(self, field, value):
        """Log a new update in this session."""
        from utils.helpers import get_timestamp
        self.session_updates.append({
            'field': field,
            'value': value,
            'timestamp': get_timestamp()
        })

    def get_disease_names(self):
        """Get list of disease names for this patient."""
        return [d['disease_name'] for d in self.chronic_diseases]

    def get_allergy_names(self):
        """Get list of allergen names for this patient."""
        return [a['allergen'] for a in self.allergies]

    def get_medication_names(self):
        """Get list of medication names for this patient."""
        return [m['drug_name'] for m in self.medications]

    def get_patient_banner_data(self):
        """Get data for the patient banner in emergency UI."""
        return {
            'name': self.patient_info.get('name', ''),
            'age': self.patient_info.get('age', ''),
            'blood_type': self.patient_info.get('blood_type', ''),
            'gender': self.patient_info.get('gender', ''),
            'allergies': [a['allergen'] for a in self.allergies],
            'diseases': [d['disease_name'] for d in self.chronic_diseases],
        }
