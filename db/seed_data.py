"""
seed_data.py — Seed the database with 5 demo patients and contraindications.
Each patient has a specific clinical scenario designed for the hackathon demo.
"""

import sqlite3
import os
from db.init_db import get_connection, init_database


def seed_all():
    """Seed the database with all demo data."""
    conn = get_connection()
    cursor = conn.cursor()

    # Clear existing data
    for table in [
        "contraindications", "lab_results", "visits", "surgeries",
        "current_medications", "allergies", "chronic_diseases", "patients"
    ]:
        cursor.execute(f"DELETE FROM {table}")

    # ══════════════════════════════════════════════════════════════
    # المريض 1: عبد الله يوسف — 56 سنة — مريض قلب عالي الخطورة
    # ══════════════════════════════════════════════════════════════
    cursor.execute("""
        INSERT INTO patients (patient_id, national_id, name, age, gender, blood_type, phone, emergency_contact)
        VALUES (1, '29012345678901', 'عبد الله يوسف', 56, 'ذكر', 'A+', '01012345678', '01098765432')
    """)

    # أمراض مزمنة
    cursor.executemany("INSERT INTO chronic_diseases (patient_id, disease_name, diagnosed_date, severity, notes) VALUES (?, ?, ?, ?, ?)", [
        (1, 'قصور في الشريان التاجي', '2020-03-15', 'شديد', 'تم تركيب دعامة في 2023'),
        (1, 'ارتفاع ضغط الدم', '2018-07-20', 'متوسط', 'مسيطر عليه بالأدوية'),
    ])

    # أدوية حالية
    cursor.executemany("INSERT INTO current_medications (patient_id, drug_name, dose, frequency, reason) VALUES (?, ?, ?, ?, ?)", [
        (1, 'Aspirin', '75mg', 'مرة يومياً', 'مضاد تجلط — بعد الدعامة'),
        (1, 'Atorvastatin', '20mg', 'مرة يومياً مساءً', 'خفض الكوليسترول'),
        (1, 'Bisoprolol', '5mg', 'مرة يومياً صباحاً', 'تنظيم ضربات القلب وخفض الضغط'),
    ])

    # عمليات سابقة
    cursor.execute("INSERT INTO surgeries (patient_id, surgery_name, surgery_date, notes) VALUES (?, ?, ?, ?)",
        (1, 'قسطرة قلبية مع تركيب دعامة', '2023-06-10', 'دعامة في الشريان الأمامي النازل LAD — نجحت بدون مضاعفات'))

    # زيارات سابقة
    cursor.executemany("INSERT INTO visits (patient_id, visit_date, department, reason, diagnosis, treatment, doctor_notes) VALUES (?, ?, ?, ?, ?, ?, ?)", [
        (1, '2024-11-20', 'طوارئ', 'ألم صدري حاد', 'ذبحة صدرية غير مستقرة', 'نيتروجليسرين + مراقبة', 'تحسن بعد العلاج — يحتاج متابعة'),
        (1, '2025-03-15', 'عيادة القلب', 'متابعة دورية', 'حالة مستقرة', 'استمرار الأدوية', 'ECG طبيعي — الضغط مسيطر عليه'),
    ])

    # تحاليل سابقة
    cursor.executemany("INSERT INTO lab_results (patient_id, test_name, result_value, normal_range, test_date, is_abnormal) VALUES (?, ?, ?, ?, ?, ?)", [
        (1, 'Troponin I', '0.02 ng/mL', '< 0.04 ng/mL', '2024-11-20', 0),
        (1, 'LDL Cholesterol', '145 mg/dL', '< 100 mg/dL', '2025-03-15', 1),
        (1, 'HDL Cholesterol', '38 mg/dL', '> 40 mg/dL', '2025-03-15', 1),
        (1, 'HbA1c', '5.8%', '< 5.7%', '2025-03-15', 1),
        (1, 'Creatinine', '1.1 mg/dL', '0.7-1.3 mg/dL', '2025-03-15', 0),
    ])

    # ══════════════════════════════════════════════════════════════
    # المريض 2: أحمد محمد علي — 58 سنة — سكري + ضغط + حساسية بنسلين
    # ══════════════════════════════════════════════════════════════
    cursor.execute("""
        INSERT INTO patients (patient_id, national_id, name, age, gender, blood_type, phone, emergency_contact)
        VALUES (2, '29112345678902', 'أحمد محمد علي', 58, 'ذكر', 'B+', '01123456789', '01187654321')
    """)

    cursor.executemany("INSERT INTO chronic_diseases (patient_id, disease_name, diagnosed_date, severity, notes) VALUES (?, ?, ?, ?, ?)", [
        (2, 'ارتفاع ضغط الدم', '2015-01-10', 'متوسط', 'مسيطر عليه بالأملوديبين'),
        (2, 'سكري نوع 2', '2017-05-22', 'متوسط', 'HbA1c آخر قراءة 7.2%'),
    ])

    # حساسيات
    cursor.execute("INSERT INTO allergies (patient_id, allergen, reaction_type, severity) VALUES (?, ?, ?, ?)",
        (2, 'Penicillin', 'صدمة تحسسية (Anaphylaxis)', 'شديد'))

    cursor.executemany("INSERT INTO current_medications (patient_id, drug_name, dose, frequency, reason) VALUES (?, ?, ?, ?, ?)", [
        (2, 'Amlodipine', '5mg', 'مرة يومياً', 'خفض ضغط الدم'),
        (2, 'Metformin', '500mg', 'مرتين يومياً', 'تنظيم السكر'),
    ])

    cursor.executemany("INSERT INTO visits (patient_id, visit_date, department, reason, diagnosis, treatment, doctor_notes) VALUES (?, ?, ?, ?, ?, ?, ?)", [
        (2, '2025-01-10', 'عيادة الباطنة', 'متابعة سكري', 'سكري غير منضبط', 'زيادة جرعة Metformin', 'يحتاج التزام أكثر بالحمية'),
    ])

    cursor.executemany("INSERT INTO lab_results (patient_id, test_name, result_value, normal_range, test_date, is_abnormal) VALUES (?, ?, ?, ?, ?, ?)", [
        (2, 'HbA1c', '7.2%', '< 7.0%', '2025-01-10', 1),
        (2, 'Fasting Blood Sugar', '165 mg/dL', '70-100 mg/dL', '2025-01-10', 1),
        (2, 'Creatinine', '1.0 mg/dL', '0.7-1.3 mg/dL', '2025-01-10', 0),
        (2, 'Blood Pressure', '150/95 mmHg', '< 140/90 mmHg', '2025-01-10', 1),
    ])

    # ══════════════════════════════════════════════════════════════
    # المريض 3: سارة خالد — 34 سنة — Myasthenia Gravis (المريض المحوري)
    # ══════════════════════════════════════════════════════════════
    cursor.execute("""
        INSERT INTO patients (patient_id, national_id, name, age, gender, blood_type, phone, emergency_contact)
        VALUES (3, '29212345678903', 'سارة خالد', 34, 'أنثى', 'O+', '01234567890', '01276543210')
    """)

    cursor.execute("INSERT INTO chronic_diseases (patient_id, disease_name, diagnosed_date, severity, notes) VALUES (?, ?, ?, ?, ?)",
        (3, 'Myasthenia Gravis', '2022-08-14', 'متوسط', 'Anti-AChR antibodies إيجابية — تستجيب للعلاج بـ Pyridostigmine'))

    cursor.executemany("INSERT INTO current_medications (patient_id, drug_name, dose, frequency, reason) VALUES (?, ?, ?, ?, ?)", [
        (3, 'Pyridostigmine', '60mg', 'ثلاث مرات يومياً', 'علاج Myasthenia Gravis — مثبط كولينستراز'),
    ])

    cursor.executemany("INSERT INTO visits (patient_id, visit_date, department, reason, diagnosis, treatment, doctor_notes) VALUES (?, ?, ?, ?, ?, ?, ?)", [
        (3, '2024-06-20', 'عيادة الأعصاب', 'متابعة MG', 'Myasthenia Gravis مستقرة', 'استمرار Pyridostigmine', 'تحسن ملحوظ — قوة العضلات جيدة'),
        (3, '2025-01-08', 'طوارئ', 'ضعف عام + صعوبة بلع', 'تفاقم MG — أزمة محتملة', 'IV Immunoglobulin + مراقبة تنفسية', 'كانت قد أوقفت الدواء لمدة يومين'),
    ])

    cursor.executemany("INSERT INTO lab_results (patient_id, test_name, result_value, normal_range, test_date, is_abnormal) VALUES (?, ?, ?, ?, ?, ?)", [
        (3, 'Anti-AChR Antibodies', '15.2 nmol/L', '< 0.4 nmol/L', '2022-08-14', 1),
        (3, 'CBC - WBC', '7.5 × 10³/µL', '4.5-11.0 × 10³/µL', '2025-01-08', 0),
        (3, 'Thyroid Function (TSH)', '2.8 mIU/L', '0.4-4.0 mIU/L', '2024-06-20', 0),
        (3, 'CRP', '3.2 mg/L', '< 5 mg/L', '2025-01-08', 0),
    ])

    # ══════════════════════════════════════════════════════════════
    # المريض 4: محمود عبد الرحمن — 41 سنة — ربو + حساسية أسبرين
    # ══════════════════════════════════════════════════════════════
    cursor.execute("""
        INSERT INTO patients (patient_id, national_id, name, age, gender, blood_type, phone, emergency_contact)
        VALUES (4, '29312345678904', 'محمود عبد الرحمن', 41, 'ذكر', 'AB+', '01345678901', '01365432109')
    """)

    cursor.execute("INSERT INTO chronic_diseases (patient_id, disease_name, diagnosed_date, severity, notes) VALUES (?, ?, ?, ?, ?)",
        (4, 'ربو', '2010-04-05', 'متوسط', 'يستخدم بخاخ إنقاذ عند الحاجة'))

    cursor.executemany("INSERT INTO allergies (patient_id, allergen, reaction_type, severity) VALUES (?, ?, ?, ?)", [
        (4, 'Aspirin', 'تشنج قصبي (Bronchospasm)', 'شديد'),
        (4, 'غبار', 'حساسية أنفية + ضيق تنفس', 'متوسط'),
    ])

    cursor.execute("INSERT INTO current_medications (patient_id, drug_name, dose, frequency, reason) VALUES (?, ?, ?, ?, ?)",
        (4, 'Salbutamol Inhaler', '100mcg', 'عند الحاجة', 'بخاخ إنقاذ للربو'))

    cursor.executemany("INSERT INTO visits (patient_id, visit_date, department, reason, diagnosis, treatment, doctor_notes) VALUES (?, ?, ?, ?, ?, ?, ?)", [
        (4, '2024-12-05', 'طوارئ', 'نوبة ربو حادة', 'نوبة ربو حادة — Status Asthmaticus', 'Nebulizer + Systemic Steroids', 'تحسن خلال ساعتين — نصيحة بتجنب المهيجات'),
    ])

    cursor.executemany("INSERT INTO lab_results (patient_id, test_name, result_value, normal_range, test_date, is_abnormal) VALUES (?, ?, ?, ?, ?, ?)", [
        (4, 'SpO2', '91%', '> 95%', '2024-12-05', 1),
        (4, 'ABG - pH', '7.38', '7.35-7.45', '2024-12-05', 0),
        (4, 'ABG - pCO2', '48 mmHg', '35-45 mmHg', '2024-12-05', 1),
        (4, 'CBC - Eosinophils', '8%', '1-4%', '2024-12-05', 1),
    ])

    # ══════════════════════════════════════════════════════════════
    # المريض 5: فاطمة حسن — 31 سنة — سليمة مع تاريخ عائلي
    # ══════════════════════════════════════════════════════════════
    cursor.execute("""
        INSERT INTO patients (patient_id, national_id, name, age, gender, blood_type, phone, emergency_contact)
        VALUES (5, '29412345678905', 'فاطمة حسن', 31, 'أنثى', 'O-', '01456789012', '01454321098')
    """)

    # حساسيات فقط
    cursor.execute("INSERT INTO allergies (patient_id, allergen, reaction_type, severity) VALUES (?, ?, ?, ?)",
        (5, 'Sulfa drugs', 'طفح جلدي', 'خفيف'))

    cursor.executemany("INSERT INTO visits (patient_id, visit_date, department, reason, diagnosis, treatment, doctor_notes) VALUES (?, ?, ?, ?, ?, ?, ?)", [
        (5, '2025-02-01', 'عيادة عامة', 'صداع متكرر', 'صداع توتري', 'Paracetamol + نصائح', 'لا توجد علامات خطر — تاريخ عائلي: الأم سكري'),
    ])

    cursor.executemany("INSERT INTO lab_results (patient_id, test_name, result_value, normal_range, test_date, is_abnormal) VALUES (?, ?, ?, ?, ?, ?)", [
        (5, 'CBC', 'طبيعي', 'طبيعي', '2025-02-01', 0),
        (5, 'Fasting Blood Sugar', '92 mg/dL', '70-100 mg/dL', '2025-02-01', 0),
        (5, 'TSH', '2.1 mIU/L', '0.4-4.0 mIU/L', '2025-02-01', 0),
    ])

    # ══════════════════════════════════════════════════════════════
    # جدول موانع الأدوية والتفاعلات (عام — غير مرتبط بمريض محدد)
    # ══════════════════════════════════════════════════════════════
    contraindications_data = [
        # Myasthenia Gravis
        ('Myasthenia Gravis', 'Magnesium', 'critical', 'يثبط النقل العصبي العضلي (NMJ) ويزيد ضعف العضلات بشكل خطير — قد يسبب أزمة تنفسية', 'MG Foundation / UpToDate'),
        ('Myasthenia Gravis', 'Aminoglycosides', 'critical', 'يفاقم ضعف العضلات ويمكن أن يسبب أزمة Myasthenic Crisis', 'FDA Drug Safety Communication'),
        ('Myasthenia Gravis', 'Beta-blockers', 'high', 'قد يزيد ضعف العضلات ويخفي علامات التدهور', 'British National Formulary'),
        ('Myasthenia Gravis', 'Fluoroquinolones', 'high', 'يفاقم ضعف العضلات — تحذير FDA صندوق أسود', 'FDA Black Box Warning'),
        ('Myasthenia Gravis', 'Succinylcholine', 'critical', 'استجابة غير متوقعة — مقاومة أو حساسية مفرطة', 'Miller\'s Anesthesia'),
        ('Myasthenia Gravis', 'D-Penicillamine', 'critical', 'قد يحرض أو يفاقم Myasthenia Gravis', 'UpToDate'),
        ('Myasthenia Gravis', 'Telithromycin', 'critical', 'تقارير عن تفاقم حاد ووفاة في مرضى MG', 'FDA Safety Alert'),

        # أمراض القلب
        ('قصور في الشريان التاجي', 'NSAIDs', 'high', 'يزيد خطر الأحداث القلبية الوعائية والجلطات', 'AHA Guidelines'),
        ('قصور في الشريان التاجي', 'Triptans', 'high', 'يسبب تضيق الأوعية التاجية', 'ESC Guidelines'),
        ('ارتفاع ضغط الدم', 'NSAIDs', 'moderate', 'يرفع ضغط الدم ويقلل فعالية خافضات الضغط', 'JNC Guidelines'),
        ('ارتفاع ضغط الدم', 'Pseudoephedrine', 'high', 'يرفع ضغط الدم بشكل كبير', 'FDA OTC Guidelines'),

        # السكري
        ('سكري نوع 2', 'Corticosteroids', 'high', 'يرفع مستوى السكر في الدم بشكل كبير', 'ADA Standards of Care'),
        ('سكري نوع 2', 'Thiazide Diuretics', 'moderate', 'قد يرفع مستوى السكر في الدم', 'ADA Standards of Care'),

        # الربو
        ('ربو', 'Beta-blockers', 'high', 'يسبب تضيق الشعب الهوائية — خطر نوبة ربو شديدة', 'GINA Guidelines'),
        ('ربو', 'Aspirin', 'high', 'قد يسبب نوبة ربو في مرضى Aspirin-sensitive asthma', 'GINA Guidelines'),
        ('ربو', 'NSAIDs', 'moderate', 'قد يفاقم الربو في بعض المرضى', 'GINA Guidelines'),

        # القصور الكلوي
        ('قصور كلوي', 'NSAIDs', 'high', 'يزيد من تدهور وظائف الكلى', 'KDIGO Guidelines'),
        ('قصور كلوي', 'Metformin', 'high', 'خطر الحماض اللبني (Lactic Acidosis)', 'FDA Drug Safety'),
        ('قصور كلوي', 'Aminoglycosides', 'high', 'سمية كلوية — يتراكم في حالة القصور', 'Sanford Guide'),

        # القرحة المعدية
        ('قرحة معدة', 'Aspirin', 'high', 'يزيد خطر النزيف المعدي', 'ACG Guidelines'),
        ('قرحة معدة', 'NSAIDs', 'high', 'يسبب تآكل الغشاء المخاطي ويفاقم القرحة', 'ACG Guidelines'),
        ('قرحة معدة', 'Corticosteroids', 'moderate', 'يزيد خطر القرحة والنزيف', 'ACG Guidelines'),
    ]

    cursor.executemany(
        "INSERT INTO contraindications (disease_name, contraindicated_substance, risk_level, reason, source) VALUES (?, ?, ?, ?, ?)",
        contraindications_data
    )

    conn.commit()
    conn.close()
    print("✅ Seed data inserted successfully — 5 patients + contraindications table")


if __name__ == "__main__":
    init_database()
    seed_all()
