"""
helpers.py — General utility functions for Gemma-Health Sentinel.
"""

from datetime import datetime


def get_timestamp():
    """Get current timestamp as formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_date():
    """Get current date as formatted string."""
    return datetime.now().strftime("%Y-%m-%d")


def format_patient_label(patient):
    """Format patient name for dropdown display with emoji indicators."""
    pid = patient.get('patient_id', '?')
    name = patient.get('name', 'غير معروف')
    age = patient.get('age', '?')
    return f"{name} — {age} سنة"


def format_vital_status(value, low, high, unit=""):
    """Check if vital sign is within normal range and return formatted status."""
    try:
        v = float(value)
        if v < low:
            return f"🔴 {value} {unit} (منخفض — الطبيعي: {low}-{high})"
        elif v > high:
            return f"🔴 {value} {unit} (مرتفع — الطبيعي: {low}-{high})"
        else:
            return f"🟢 {value} {unit}"
    except (ValueError, TypeError):
        return f"⚪ {value} {unit}"


def format_alert_html(alert_type, title, message, details=""):
    """Format an alert as HTML for Gradio display."""
    colors = {
        'critical': ('#dc2626', '#fef2f2', '🔴'),
        'high': ('#ea580c', '#fff7ed', '🟠'),
        'moderate': ('#ca8a04', '#fefce8', '🟡'),
        'info': ('#2563eb', '#eff6ff', '🔵'),
        'success': ('#16a34a', '#f0fdf4', '✅'),
    }
    color, bg, icon = colors.get(alert_type, colors['info'])
    return f"""
    <div style="background: {bg}; border-right: 4px solid {color}; 
                padding: 12px 16px; margin: 8px 0; border-radius: 8px;
                direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, sans-serif;">
        <div style="font-weight: bold; color: {color}; font-size: 15px; margin-bottom: 4px;">
            {icon} {title}
        </div>
        <div style="color: #374151; font-size: 14px;">{message}</div>
        {f'<div style="color: #6b7280; font-size: 12px; margin-top: 4px;">{details}</div>' if details else ''}
    </div>
    """


def format_patient_card_html(record):
    """Generate HTML for the patient card display."""
    patient = record.get('patient', {})
    diseases = record.get('chronic_diseases', [])
    allergies = record.get('allergies', [])
    medications = record.get('medications', [])
    visits = record.get('visits', [])

    # Patient header
    html = f"""
    <div style="background: linear-gradient(135deg, #1e3a5f, #2d5a8e); color: white; 
                padding: 20px; border-radius: 12px; direction: rtl; text-align: right;
                font-family: 'Segoe UI', Tahoma, sans-serif; margin-bottom: 12px;">
        <div style="font-size: 22px; font-weight: bold; margin-bottom: 8px;">
            👤 {patient.get('name', '')}
        </div>
        <div style="display: flex; gap: 20px; flex-wrap: wrap; font-size: 14px; opacity: 0.9;">
            <span>🎂 {patient.get('age', '')} سنة</span>
            <span>⚧ {patient.get('gender', '')}</span>
            <span>🩸 {patient.get('blood_type', '')}</span>
            <span>📞 {patient.get('phone', '')}</span>
        </div>
    </div>
    """

    # Chronic diseases
    if diseases:
        disease_items = "".join([
            f"<div style='padding: 6px 12px; background: #fef2f2; border-radius: 6px; margin: 4px 0; color: #991b1b;'>"
            f"🔴 {d['disease_name']} — {d.get('severity', '')} "
            f"{'(' + d.get('notes', '') + ')' if d.get('notes') else ''}</div>"
            for d in diseases
        ])
        html += f"""
        <div style="background: white; padding: 12px; border-radius: 8px; margin-bottom: 8px; 
                    direction: rtl; text-align: right; border: 1px solid #fecaca;">
            <div style="font-weight: bold; color: #991b1b; margin-bottom: 8px;">🔴 الأمراض المزمنة</div>
            {disease_items}
        </div>"""

    # Allergies
    if allergies:
        allergy_items = "".join([
            f"<div style='padding: 6px 12px; background: #fff7ed; border-radius: 6px; margin: 4px 0; color: #9a3412;'>"
            f"⚠️ {a['allergen']} — {a.get('reaction_type', '')} ({a.get('severity', '')})</div>"
            for a in allergies
        ])
        html += f"""
        <div style="background: white; padding: 12px; border-radius: 8px; margin-bottom: 8px; 
                    direction: rtl; text-align: right; border: 1px solid #fed7aa;">
            <div style="font-weight: bold; color: #9a3412; margin-bottom: 8px;">⚠️ الحساسيات</div>
            {allergy_items}
        </div>"""

    # Current medications
    if medications:
        med_items = "".join([
            f"<div style='padding: 6px 12px; background: #eff6ff; border-radius: 6px; margin: 4px 0; color: #1e40af;'>"
            f"💊 {m['drug_name']} — {m.get('dose', '')} — {m.get('frequency', '')}</div>"
            for m in medications
        ])
        html += f"""
        <div style="background: white; padding: 12px; border-radius: 8px; margin-bottom: 8px; 
                    direction: rtl; text-align: right; border: 1px solid #bfdbfe;">
            <div style="font-weight: bold; color: #1e40af; margin-bottom: 8px;">💊 الأدوية الحالية</div>
            {med_items}
        </div>"""

    # Last visit
    if visits:
        last = visits[0]
        html += f"""
        <div style="background: white; padding: 12px; border-radius: 8px; 
                    direction: rtl; text-align: right; border: 1px solid #d1d5db;">
            <div style="font-weight: bold; color: #374151; margin-bottom: 8px;">📅 آخر زيارة</div>
            <div style="color: #4b5563; font-size: 14px;">
                {last.get('visit_date', '')} — {last.get('department', '')} — {last.get('reason', '')}
                <br>التشخيص: {last.get('diagnosis', '')}
            </div>
        </div>"""

    return html
