"""
diagnosis_ui.py — Deep diagnosis screen for Gemma-Health Sentinel.
The Diagnostic Detective Loop — step-by-step AI reasoning to final diagnosis.
"""

import gradio as gr
from ui.components import (
    CUSTOM_CSS, create_header, create_alert_html, get_gradio_theme
)
from ai.analyzer import run_diagnosis_loop, check_vitals_simple
from ai.medgemma_client import ask_medgemma
from ai.prompts import SYSTEM_PROMPT


def _get_cache():
    """Get the current session cache."""
    from ui.reception_ui import get_current_cache
    return get_current_cache()


def on_load_diagnosis_data():
    """Load current patient data and form inputs for diagnosis."""
    cache = _get_cache()
    if cache is None:
        return (
            "<div style='text-align:center;color:#dc2626;padding:30px;'>⚠️ لم يتم اختيار مريض</div>",
            "", ""
        )

    # Build input summary
    p = cache.patient_info
    summary_parts = []
    summary_parts.append(f"👤 المريض: {p.get('name', '')} — {p.get('age', '')} سنة — {p.get('gender', '')}")

    if cache.chronic_diseases:
        diseases = ", ".join([d['disease_name'] for d in cache.chronic_diseases])
        summary_parts.append(f"🔴 الأمراض المزمنة: {diseases}")

    if cache.allergies:
        allergies = ", ".join([a['allergen'] for a in cache.allergies])
        summary_parts.append(f"⚠️ الحساسيات: {allergies}")

    if cache.medications:
        meds = ", ".join([f"{m['drug_name']} {m.get('dose', '')}" for m in cache.medications])
        summary_parts.append(f"💊 الأدوية الحالية: {meds}")

    if cache.current_vitals:
        summary_parts.append(f"\n📊 العلامات الحيوية:\n{check_vitals_simple(cache.current_vitals)}")

    if cache.current_complaint:
        summary_parts.append(f"\n📋 سبب الزيارة: {cache.current_complaint}")

    if cache.abnormal_labs:
        summary_parts.append("\n🔬 تحاليل غير طبيعية:")
        for lab in cache.abnormal_labs:
            summary_parts.append(f"  • {lab['test_name']}: {lab['result_value']} (الطبيعي: {lab.get('normal_range', '')})")

    input_summary = "\n".join(summary_parts)

    # Show contraindications
    contra_html = ""
    if cache.contraindications:
        contra_html = "<h4 style='color:#dc2626;text-align:right;'>⚠️ المواد الممنوعة لهذا المريض:</h4>"
        for ci in cache.contraindications:
            contra_html += create_alert_html(
                'critical' if ci['risk_level'] == 'critical' else 'high',
                f"{ci['contraindicated_substance']} — {ci['risk_level']}",
                ci['reason'],
                f"المرض: {ci['disease_name']}"
            )

    return input_summary, "", contra_html


def on_run_diagnosis(chief_complaint, additional_notes, transcript):
    """Run the diagnostic detective loop."""
    cache = _get_cache()
    if cache is None:
        return "⚠️ لم يتم اختيار مريض — ارجع لواجهة الاستقبال", ""

    if not chief_complaint or not chief_complaint.strip():
        return "⚠️ يرجى إدخال الشكوى الرئيسية", ""

    # Compile form data
    form_data = f"""
الشكوى الرئيسية: {chief_complaint}
ملاحظات إضافية: {additional_notes or 'لا يوجد'}
العلامات الحيوية: {check_vitals_simple(cache.current_vitals) if cache.current_vitals else 'لم تُدخل'}
"""

    # Session updates from reception/emergency
    if cache.session_updates:
        form_data += "\nتحديثات الجلسة:\n"
        for u in cache.session_updates:
            form_data += f"  • {u.get('field', '')}: {u.get('value', '')}\n"

    # Run the diagnosis loop
    ai_result, substance_alerts = run_diagnosis_loop(
        cache,
        chief_complaint,
        form_data,
        transcript or ""
    )

    # Build red alerts HTML
    red_alerts_html = ""

    # Substance alerts from the text
    if substance_alerts:
        red_alerts_html += "<h4 style='color:#dc2626;text-align:right;'>🔴 تحذيرات اكتشفها النموذج:</h4>"
        for a in substance_alerts:
            red_alerts_html += create_alert_html(a['type'], a['title'], a['message'], a.get('details', ''))

    # Add contraindication warnings for this patient
    if cache.contraindications:
        critical_contras = [ci for ci in cache.contraindications if ci['risk_level'] == 'critical']
        if critical_contras:
            red_alerts_html += "<h4 style='color:#dc2626;text-align:right;margin-top:15px;'>🔴 تجنب وصف المواد التالية:</h4>"
            for ci in critical_contras:
                red_alerts_html += create_alert_html(
                    'critical',
                    f"ممنوع: {ci['contraindicated_substance']}",
                    ci['reason'],
                    f"المرض: {ci['disease_name']} | المصدر: {ci.get('source', '')}"
                )

    if not red_alerts_html:
        red_alerts_html = create_alert_html('success', 'لا توجد تحذيرات حرجة', 'لم يتم اكتشاف أي تعارضات أو مخاطر')

    return ai_result, red_alerts_html


def create_diagnosis_ui():
    """Create the deep diagnosis Gradio interface."""
    with gr.Column():
        gr.HTML(create_header(
            "Gemma-Health Sentinel — التشخيص المعمق",
            "🔍 The Diagnostic Detective Loop — حلقة البحث والتحليل المعمّق"
        ))

        # Load data button
        load_diag_btn = gr.Button("📥 تحميل بيانات المريض والنموذج", variant="primary")

        # ── Top Section: Input Summary ──
        gr.HTML("<h3 style='text-align:right;color:#1e3a5f;'>📋 ملخص المدخلات الحالية</h3>")
        input_summary = gr.Textbox(
            label="ملخص البيانات المتاحة",
            interactive=False,
            lines=10
        )

        # Complaint input for diagnosis
        gr.HTML("<hr style='margin: 15px 0;'>")
        with gr.Row():
            with gr.Column(scale=2):
                diag_complaint = gr.Textbox(
                    label="الشكوى الرئيسية للتشخيص",
                    placeholder="مثال: ضعف عام + صعوبة في البلع منذ يومين...",
                    lines=2
                )
                diag_notes = gr.Textbox(
                    label="ملاحظات إضافية من الفحص",
                    placeholder="أي ملاحظات من الفحص السريري أو المعمل...",
                    lines=3
                )
            with gr.Column(scale=1):
                diag_transcript = gr.Textbox(
                    label="نص المحادثة مع المريض (اختياري)",
                    placeholder="مثال:\nالمريض: تناولت مغنيسيوم بجرعة عالية أمس\nالطبيب: هل تشعرين بضعف في العضلات؟",
                    lines=5
                )

        run_diag_btn = gr.Button(
            "🔍 بدء التشخيص المعمق",
            variant="primary",
            size="lg"
        )

        # ── Bottom Section: Results ──
        with gr.Row():
            # Left: Detective Loop Log
            with gr.Column(scale=1):
                gr.HTML("<h3 style='text-align:right;color:#3b82f6;'>🔎 سجل حلقة التشخيص</h3>")
                diagnosis_log = gr.Textbox(
                    label="خطوات التشخيص (Detective Loop)",
                    interactive=False,
                    lines=20,
                )

            # Right: Red Alerts + Final Result
            with gr.Column(scale=1):
                gr.HTML("<h3 style='text-align:right;color:#dc2626;'>🔴 النتيجة النهائية + الاقتراحات الحمراء</h3>")
                red_alerts_display = gr.HTML()

        # ── Event Handlers ──
        load_diag_btn.click(
            fn=on_load_diagnosis_data,
            outputs=[input_summary, diagnosis_log, red_alerts_display]
        )

        run_diag_btn.click(
            fn=on_run_diagnosis,
            inputs=[diag_complaint, diag_notes, diag_transcript],
            outputs=[diagnosis_log, red_alerts_display]
        )


if __name__ == "__main__":
    from db.init_db import init_database
    from db.seed_data import seed_all
    from ai.medgemma_client import load_medgemma

    init_database()
    seed_all()
    load_medgemma()

    with gr.Blocks(theme=get_gradio_theme(), css=CUSTOM_CSS, title="Gemma-Health Sentinel — التشخيص") as demo:
        create_diagnosis_ui()
    demo.launch(share=False)
