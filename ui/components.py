"""
components.py — Shared UI components for Gradio interfaces.
Provides RTL Arabic theme, color constants, and reusable HTML components.
"""

import gradio as gr

# ── Color Palette ──
COLORS = {
    'primary': '#1e3a5f',
    'primary_light': '#2d5a8e',
    'danger': '#dc2626',
    'danger_bg': '#fef2f2',
    'warning': '#ea580c',
    'warning_bg': '#fff7ed',
    'caution': '#ca8a04',
    'caution_bg': '#fefce8',
    'info': '#2563eb',
    'info_bg': '#eff6ff',
    'success': '#16a34a',
    'success_bg': '#f0fdf4',
    'bg_dark': '#0f172a',
    'bg_card': '#1e293b',
    'text': '#f8fafc',
    'text_muted': '#94a3b8',
}

# ── RTL CSS Theme ──
CUSTOM_CSS = """
/* Global RTL + Arabic styling */
.gradio-container {
    direction: rtl !important;
    font-family: 'Segoe UI', 'Tahoma', 'Arial', sans-serif !important;
}

/* Dark theme adjustments */
.dark .gradio-container {
    background: #0f172a !important;
}

/* Custom header */
.sentinel-header {
    background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8e 50%, #1e3a5f 100%);
    padding: 20px 30px;
    border-radius: 12px;
    color: white;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(30, 58, 95, 0.3);
}

.sentinel-header h1 {
    margin: 0;
    font-size: 28px;
    font-weight: bold;
}

.sentinel-header p {
    margin: 5px 0 0;
    opacity: 0.85;
    font-size: 14px;
}

/* Patient banner */
.patient-banner {
    background: linear-gradient(135deg, #1e3a5f, #2d5a8e);
    color: white;
    padding: 15px 20px;
    border-radius: 10px;
    margin-bottom: 15px;
    direction: rtl;
    text-align: right;
}

/* Alert cards */
.alert-critical {
    background: #fef2f2;
    border-right: 4px solid #dc2626;
    padding: 12px 16px;
    margin: 8px 0;
    border-radius: 8px;
    direction: rtl;
    text-align: right;
}

.alert-warning {
    background: #fff7ed;
    border-right: 4px solid #ea580c;
    padding: 12px 16px;
    margin: 8px 0;
    border-radius: 8px;
    direction: rtl;
    text-align: right;
}

.alert-info {
    background: #eff6ff;
    border-right: 4px solid #2563eb;
    padding: 12px 16px;
    margin: 8px 0;
    border-radius: 8px;
    direction: rtl;
    text-align: right;
}

.alert-success {
    background: #f0fdf4;
    border-right: 4px solid #16a34a;
    padding: 12px 16px;
    margin: 8px 0;
    border-radius: 8px;
    direction: rtl;
    text-align: right;
}

/* Section separator */
.section-divider {
    border-top: 2px solid #334155;
    margin: 20px 0;
}

/* Tab styling */
.tabs .tab-nav button {
    font-size: 15px !important;
    font-weight: 600 !important;
}

/* Vital signs grid */
.vitals-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

/* Form inputs RTL */
input, textarea, select {
    direction: rtl !important;
    text-align: right !important;
}

/* Status badge */
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
}

.status-critical { background: #dc2626; color: white; }
.status-high { background: #ea580c; color: white; }
.status-moderate { background: #ca8a04; color: white; }
.status-normal { background: #16a34a; color: white; }

/* Detective loop steps */
.detective-step {
    background: #1e293b;
    border-right: 3px solid #3b82f6;
    padding: 12px 16px;
    margin: 8px 0;
    border-radius: 6px;
    color: #e2e8f0;
    direction: rtl;
    text-align: right;
    font-family: 'Courier New', monospace;
    white-space: pre-wrap;
}
"""


def create_header(title, subtitle=""):
    """Create a styled header HTML component."""
    return f"""
    <div class="sentinel-header">
        <h1>🏥 {title}</h1>
        {'<p>' + subtitle + '</p>' if subtitle else ''}
    </div>
    """


def create_patient_banner_html(banner_data, visit_reason="", priority=""):
    """Create the patient banner for emergency UI."""
    allergies_html = ""
    if banner_data.get('allergies'):
        allergy_badges = " ".join([
            f"<span style='background:#dc2626;color:white;padding:2px 8px;border-radius:12px;font-size:12px;margin:0 3px;'>⚠️ {a}</span>"
            for a in banner_data['allergies']
        ])
        allergies_html = f"<div style='margin-top:8px;'>الحساسيات: {allergy_badges}</div>"

    diseases_html = ""
    if banner_data.get('diseases'):
        disease_badges = " ".join([
            f"<span style='background:#ea580c;color:white;padding:2px 8px;border-radius:12px;font-size:12px;margin:0 3px;'>🔴 {d}</span>"
            for d in banner_data['diseases']
        ])
        diseases_html = f"<div style='margin-top:4px;'>الأمراض: {disease_badges}</div>"

    priority_colors = {
        'عادي': '#16a34a', 'متوسط': '#ca8a04',
        'طوارئ': '#dc2626', 'حرج': '#000000'
    }
    priority_color = priority_colors.get(priority, '#6b7280')
    priority_emoji = {'عادي': '🟢', 'متوسط': '🟡', 'طوارئ': '🔴', 'حرج': '⚫'}.get(priority, '⚪')

    return f"""
    <div style="background: linear-gradient(135deg, #1e3a5f, #2d5a8e); color: white; 
                padding: 20px; border-radius: 12px; direction: rtl; text-align: right;
                font-family: 'Segoe UI', Tahoma, sans-serif; margin-bottom: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <span style="font-size: 22px; font-weight: bold;">👤 {banner_data.get('name', '')}</span>
                <span style="opacity: 0.8; margin: 0 10px;">|</span>
                <span>{banner_data.get('age', '')} سنة</span>
                <span style="opacity: 0.8; margin: 0 10px;">|</span>
                <span>🩸 {banner_data.get('blood_type', '')}</span>
            </div>
            <div>
                <span style="background:{priority_color}; color:white; padding:4px 16px; 
                             border-radius:20px; font-size:14px; font-weight:600;">
                    {priority_emoji} {priority if priority else 'غير محدد'}
                </span>
            </div>
        </div>
        {f'<div style="margin-top: 8px; opacity: 0.9;">📋 سبب الزيارة: {visit_reason}</div>' if visit_reason else ''}
        {allergies_html}
        {diseases_html}
    </div>
    """


def create_alert_html(alert_type, title, message, details=""):
    """Create a styled alert card."""
    styles = {
        'critical': ('#dc2626', '#fef2f2', '🔴'),
        'high': ('#ea580c', '#fff7ed', '🟠'),
        'moderate': ('#ca8a04', '#fefce8', '🟡'),
        'info': ('#2563eb', '#eff6ff', '🔵'),
        'success': ('#16a34a', '#f0fdf4', '✅'),
    }
    color, bg, icon = styles.get(alert_type, styles['info'])

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


def get_gradio_theme():
    """Get a custom Gradio theme for the application."""
    return gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("IBM Plex Sans Arabic"),
    )
