"""
queries.py — Database query functions for Gemma-Health Sentinel.
All queries return dictionaries for easy consumption.
"""

from db.init_db import get_connection


def _rows_to_dicts(rows):
    """Convert sqlite3.Row objects to plain dicts."""
    return [dict(row) for row in rows]


def get_patient_info(patient_id):
    """Get basic patient information."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_chronic_diseases(patient_id):
    """Get patient's chronic diseases."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM chronic_diseases WHERE patient_id = ?", (patient_id,)).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_allergies(patient_id):
    """Get patient's allergies."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM allergies WHERE patient_id = ?", (patient_id,)).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_medications(patient_id):
    """Get patient's current medications."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM current_medications WHERE patient_id = ?", (patient_id,)).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_surgeries(patient_id):
    """Get patient's surgical history."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM surgeries WHERE patient_id = ?", (patient_id,)).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_visits(patient_id):
    """Get patient's visit history."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM visits WHERE patient_id = ? ORDER BY visit_date DESC", (patient_id,)).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_lab_results(patient_id):
    """Get patient's lab results."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM lab_results WHERE patient_id = ? ORDER BY test_date DESC", (patient_id,)).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_abnormal_labs(patient_id):
    """Get only abnormal lab results."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM lab_results WHERE patient_id = ? AND is_abnormal = 1 ORDER BY test_date DESC",
        (patient_id,)
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_all_contraindications(disease_names):
    """Get all contraindications for a list of disease names."""
    if not disease_names:
        return []
    placeholders = ','.join('?' * len(disease_names))
    conn = get_connection()
    rows = conn.execute(
        f"SELECT * FROM contraindications WHERE disease_name IN ({placeholders}) ORDER BY risk_level",
        disease_names
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def search_contraindications(patient_diseases, substance):
    """Search for contraindications between patient diseases and a specific substance."""
    if not patient_diseases:
        return []
    placeholders = ','.join('?' * len(patient_diseases))
    conn = get_connection()
    rows = conn.execute(
        f"""SELECT * FROM contraindications 
            WHERE disease_name IN ({placeholders}) 
            AND LOWER(contraindicated_substance) LIKE LOWER(?)
            ORDER BY 
                CASE risk_level 
                    WHEN 'critical' THEN 1 
                    WHEN 'high' THEN 2 
                    WHEN 'moderate' THEN 3 
                END""",
        patient_diseases + ['%' + substance + '%']
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_relevant_history(patient_id, complaint_keywords):
    """Search visits by keyword relevance to the current complaint."""
    if not complaint_keywords:
        return get_visits(patient_id)
    conn = get_connection()
    conditions = " OR ".join(["reason LIKE ? OR diagnosis LIKE ? OR treatment LIKE ?"] * len(complaint_keywords))
    params = []
    for kw in complaint_keywords:
        params.extend([f'%{kw}%', f'%{kw}%', f'%{kw}%'])
    rows = conn.execute(
        f"SELECT * FROM visits WHERE patient_id = ? AND ({conditions}) ORDER BY visit_date DESC",
        [patient_id] + params
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_patient_full_record(patient_id):
    """Get the complete medical record for a patient (all tables)."""
    return {
        'patient': get_patient_info(patient_id),
        'chronic_diseases': get_chronic_diseases(patient_id),
        'allergies': get_allergies(patient_id),
        'medications': get_medications(patient_id),
        'surgeries': get_surgeries(patient_id),
        'visits': get_visits(patient_id),
        'lab_results': get_lab_results(patient_id),
        'abnormal_labs': get_abnormal_labs(patient_id),
    }


def get_all_patients_summary():
    """Get a summary list of all patients for the dropdown."""
    conn = get_connection()
    rows = conn.execute("SELECT patient_id, name, age, gender FROM patients ORDER BY patient_id").fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def add_new_patient(national_id, name, age, gender, blood_type, phone, emergency_contact,
                    diseases=None, allergies_list=None, medications=None):
    """Add a new patient with optional medical data. Returns the new patient_id."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO patients (national_id, name, age, gender, blood_type, phone, emergency_contact)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (national_id, name, age, gender, blood_type, phone, emergency_contact)
    )
    patient_id = cursor.lastrowid

    if diseases:
        for d in diseases:
            cursor.execute(
                "INSERT INTO chronic_diseases (patient_id, disease_name, severity) VALUES (?, ?, ?)",
                (patient_id, d.get('name', ''), d.get('severity', 'متوسط'))
            )

    if allergies_list:
        for a in allergies_list:
            cursor.execute(
                "INSERT INTO allergies (patient_id, allergen, reaction_type, severity) VALUES (?, ?, ?, ?)",
                (patient_id, a.get('allergen', ''), a.get('reaction', ''), a.get('severity', 'متوسط'))
            )

    if medications:
        for m in medications:
            cursor.execute(
                "INSERT INTO current_medications (patient_id, drug_name, dose, frequency, reason) VALUES (?, ?, ?, ?, ?)",
                (patient_id, m.get('name', ''), m.get('dose', ''), m.get('frequency', ''), m.get('reason', ''))
            )

    conn.commit()
    conn.close()
    return patient_id


def add_visit(patient_id, visit_date, department, reason, diagnosis="", treatment="", doctor_notes=""):
    """Record a new visit for the patient."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO visits (patient_id, visit_date, department, reason, diagnosis, treatment, doctor_notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (patient_id, visit_date, department, reason, diagnosis, treatment, doctor_notes)
    )
    conn.commit()
    conn.close()
