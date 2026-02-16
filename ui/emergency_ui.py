"""
emergency_ui.py — Emergency department screen for Gemma-Health Sentinel.
Digital ER form + AI sidebar with real-time contraindication checking.
"""

import gradio as gr
from ui.components import (
    CUSTOM_CSS, create_header, create_patient_banner_html,
    create_alert_html, get_gradio_theme
)
from ai.analyzer import check_vitals, check_vitals_simple, analyze_conversation, generate_suggestions
from ai.medgemma_client import ask_medgemma
from ai.prompts import SYSTEM_PROMPT


def _get_cache():
    """Get the current session cache from the reception module."""
    from ui.reception_ui import get_current_cache
    return get_current_cache()


def on_load_patient():
    """Load the current patient's data into the emergency form."""
    cache = _get_cache()
    if cache is None:
        return (
            "<div style='text-align:center;color:#dc2626;padding:30px;font-size:16px;'>"
            "⚠️ لم يتم اختيار مريض — ارجع لواجهة الاستقبال</div>",
            "",  # ai_summary
            "",  # past_history
            "",  # current_meds
            "",  # red_alerts
        )

    # Patient banner
    banner_data = cache.get_patient_banner_data()
    visit_reason = ""
    priority = ""
    for update in cache.session_updates:
        if update.get('field') == 'visit_reason':
            visit_reason = update.get('value', '')
        if update.get('field') == 'priority':
            priority = update.get('value', '')

    banner_html = create_patient_banner_html(banner_data, visit_reason, priority)

    # AI Summary
    ai_summary = cache.ai_summary or "لم يتم توليد ملخص بعد"

    # Pre-fill past history from DB
    diseases = cache.chronic_diseases
    surgeries = cache.surgeries
    past_history = ""
    if diseases:
        past_history += "الأمراض المزمنة:\n"
        for d in diseases:
            past_history += f"• {d['disease_name']} ({d.get('severity', '')}) — منذ {d.get('diagnosed_date', '')}\n"
    if surgeries:
        past_history += "\nالعمليات السابقة:\n"
        for s in surgeries:
            past_history += f"• {s['surgery_name']} ({s.get('surgery_date', '')})\n"

    # Pre-fill current medications
    meds = cache.medications
    current_meds = ""
    if meds:
        for m in meds:
            current_meds += f"• {m['drug_name']} — {m.get('dose', '')} — {m.get('frequency', '')}\n"

    # Initial red alerts (from contraindications)
    red_alerts = ""
    if cache.contraindications:
        red_alerts += "<h4 style='color:#dc2626;text-align:right;'>🔴 موانع مسجلة لهذا المريض:</h4>"
        for ci in cache.contraindications:
            if ci['risk_level'] == 'critical':
                red_alerts += create_alert_html(
                    'critical',
                    f"ممنوع: {ci['contraindicated_substance']}",
                    ci['reason'],
                    f"المرض: {ci['disease_name']} | المصدر: {ci.get('source', '')}"
                )

    return banner_html, ai_summary, past_history, current_meds, red_alerts


def on_check_substance(substance_text):
    """Check medications/substances against patient contraindications."""
    cache = _get_cache()
    if cache is None or not substance_text or not substance_text.strip():
        return ""

    alerts = cache.check_multiple_substances(substance_text)

    if not alerts:
        return create_alert_html('success', 'لا توجد تعارضات', 'لم يتم اكتشاف أي تعارض مع المواد المذكورة')

    html = ""
    for a in alerts:
        html += create_alert_html(a['type'], a['title'], a['message'], a.get('details', ''))
    return html


def on_check_vitals(systolic, diastolic, heart_rate, spo2, temp, resp_rate, gcs):
    """Validate vital signs and generate alerts."""
    cache = _get_cache()

    vitals = {
        'systolic_bp': systolic,
        'diastolic_bp': diastolic,
        'heart_rate': heart_rate,
        'spo2': spo2,
        'temperature': temp,
        'respiratory_rate': resp_rate,
        'gcs': gcs,
    }

    # Update cache
    if cache:
        cache.current_vitals = vitals

    # Check vitals
    alerts = check_vitals(vitals, cache)
    vitals_text = check_vitals_simple(vitals)

    # Generate HTML for alerts
    alerts_html = ""
    if alerts:
        for a in alerts:
            alerts_html += create_alert_html(a['type'], a['title'], a['message'], a.get('details', ''))
    else:
        alerts_html = create_alert_html('success', 'العلامات الحيوية طبيعية', 'جميع القيم ضمن المدى الطبيعي')

    return vitals_text, alerts_html


def on_analyze_conversation(transcript):
    """Analyze doctor-patient conversation."""
    cache = _get_cache()
    if cache is None:
        return "⚠️ لم يتم اختيار مريض", ""

    if not transcript or not transcript.strip():
        return "لم يتم تقديم نص محادثة", ""

    result = analyze_conversation(transcript, cache)
    if isinstance(result, tuple):
        ai_analysis, substance_alerts = result
    else:
        ai_analysis = result
        substance_alerts = []

    # Generate alerts HTML
    alerts_html = ""
    if substance_alerts:
        alerts_html = "<h4 style='color:#dc2626;text-align:right;'>🔴 تنبيهات من المحادثة:</h4>"
        for a in substance_alerts:
            alerts_html += create_alert_html(a['type'], a['title'], a['message'], a.get('details', ''))

    return ai_analysis, alerts_html


def on_update_analysis(chief_complaint, hpi, medications_given, substance_taken):
    """Update AI analysis based on current form data."""
    cache = _get_cache()
    if cache is None:
        return "⚠️ لم يتم اختيار مريض"

    clinical_data = f"""
الشكوى الرئيسية: {chief_complaint}
تاريخ الشكوى: {hpi}
الأدوية المعطاة: {medications_given}
ما تناوله المريض قبل الحضور: {substance_taken}
"""
    vitals_text = check_vitals_simple(cache.current_vitals) if cache.current_vitals else ""

    suggestions = generate_suggestions(cache, clinical_data, vitals_text)
    return suggestions


def on_medications_given_change(meds_text):
    """Check administered medications against patient data."""
    return on_check_substance(meds_text)


def create_emergency_ui():
    """Create the emergency department Gradio interface."""
    with gr.Column():
        gr.HTML(create_header(
            "Gemma-Health Sentinel — الطوارئ",
            "النموذج الرقمي للطوارئ + مساعد AI ذكي"
        ))

        # Load patient button
        load_btn = gr.Button("📥 تحميل بيانات المريض من الاستقبال", variant="primary")

        # Patient Banner
        patient_banner = gr.HTML(
            value="<div style='text-align:center;color:#94a3b8;padding:20px;'>"
                  "اضغط 'تحميل بيانات المريض' بعد اختيار مريض في الاستقبال</div>"
        )

        # ── Main Layout: Form (2/3) + AI Sidebar (1/3) ──
        with gr.Row():
            # ═══ LEFT SIDE: Digital ER Form (2/3) ═══
            with gr.Column(scale=2):
                with gr.Tabs():
                    # ── Section 1: Vital Signs ──
                    with gr.Tab("💓 العلامات الحيوية"):
                        gr.HTML("<h3 style='text-align:right;color:#1e3a5f;'>📊 العلامات الحيوية</h3>")
                        with gr.Row():
                            systolic = gr.Number(label="ضغط الدم الانقباضي (mmHg)", value=None)
                            diastolic = gr.Number(label="ضغط الدم الانبساطي (mmHg)", value=None)
                        with gr.Row():
                            heart_rate = gr.Number(label="نبضات القلب (نبضة/دقيقة)", value=None)
                            spo2 = gr.Number(label="نسبة الأكسجين SpO2 (%)", value=None)
                        with gr.Row():
                            temperature = gr.Number(label="درجة الحرارة (°C)", value=None)
                            resp_rate = gr.Number(label="معدل التنفس (نفس/دقيقة)", value=None)
                        gcs = gr.Slider(minimum=3, maximum=15, value=15, step=1, label="مستوى الوعي GCS")

                        check_vitals_btn = gr.Button("🔍 فحص العلامات الحيوية", variant="secondary")
                        vitals_status = gr.Textbox(label="حالة العلامات الحيوية", interactive=False, lines=5)
                        vitals_alerts = gr.HTML()

                    # ── Section 2: Complaint & History ──
                    with gr.Tab("📝 الشكوى والتاريخ"):
                        chief_complaint = gr.Textbox(
                            label="الشكوى الرئيسية (Chief Complaint)",
                            placeholder="مثال: ألم حاد في الصدر منذ ساعتين...",
                            lines=2
                        )
                        hpi = gr.Textbox(
                            label="تاريخ الشكوى (HPI)",
                            placeholder="متى بدأ؟ هل حدث من قبل؟ ما يزيده/يقلله؟",
                            lines=3
                        )
                        past_history = gr.Textbox(
                            label="التاريخ المرضي السابق 🟡 (يُملأ تلقائياً)",
                            lines=4,
                            interactive=True
                        )
                        family_history = gr.Textbox(
                            label="التاريخ العائلي",
                            placeholder="أمراض في العائلة...",
                            lines=2
                        )
                        current_meds_display = gr.Textbox(
                            label="الأدوية التي يتناولها المريض حالياً 🟡 (يُملأ تلقائياً)",
                            lines=3,
                            interactive=True
                        )

                        gr.HTML("<hr style='border-color:#dc2626;margin:15px 0;'>")
                        gr.HTML("<h4 style='text-align:right;color:#dc2626;'>⚠️ ما تناوله المريض قبل الحضور (يُفحص فوراً!)</h4>")
                        substance_taken = gr.Textbox(
                            label="المواد/الأدوية التي تناولها المريض",
                            placeholder="مثال: مغنيسيوم، باراسيتامول...",
                            lines=2
                        )
                        substance_alerts = gr.HTML()

                    # ── Section 3: Physical Examination ──
                    with gr.Tab("🩺 الفحص السريري"):
                        exam_general = gr.Textbox(label="الفحص العام (General)", lines=2, placeholder="المظهر العام، الوعي...")
                        exam_cardio = gr.Textbox(label="فحص القلب (Cardiovascular)", lines=2, placeholder="أصوات القلب، النبض...")
                        exam_chest = gr.Textbox(label="فحص الصدر (Chest)", lines=2, placeholder="أصوات التنفس، حشرجات...")
                        exam_abdomen = gr.Textbox(label="فحص البطن (Abdomen)", lines=2, placeholder="ألم، انتفاخ...")
                        exam_neuro = gr.Textbox(label="فحص عصبي (Neurological)", lines=2, placeholder="قوة العضلات، المنعكسات...")
                        exam_notes = gr.Textbox(label="ملاحظات إضافية", lines=2)

                    # ── Section 4: Orders ──
                    with gr.Tab("📋 الطلبات"):
                        gr.HTML("<h4 style='text-align:right;color:#1e3a5f;'>🔬 التحاليل المطلوبة</h4>")
                        labs_requested = gr.CheckboxGroup(
                            choices=[
                                "CBC", "Troponin", "D-dimer", "CRP",
                                "Blood Sugar", "Kidney Function", "Liver Function",
                                "ABG", "Electrolytes", "Urine Analysis", "Blood Culture"
                            ],
                            label="التحاليل",
                        )
                        gr.HTML("<h4 style='text-align:right;color:#1e3a5f;'>📷 الأشعة المطلوبة</h4>")
                        imaging_requested = gr.CheckboxGroup(
                            choices=[
                                "أشعة صدر", "CT Head", "CT Chest", "CT Abdomen",
                                "MRI", "Echo", "أشعة بطن"
                            ],
                            label="الأشعة",
                        )

                        gr.HTML("<hr style='margin:15px 0;'>")
                        gr.HTML("<h4 style='text-align:right;color:#dc2626;'>💉 الأدوية المعطاة في الطوارئ ⚠️ (يُفحص فوراً!)</h4>")
                        medications_given = gr.Textbox(
                            label="الأدوية المعطاة (الدواء + الجرعة + طريقة الإعطاء)",
                            placeholder="مثال: Paracetamol 1g IV\nNormal Saline 500ml IV",
                            lines=3
                        )
                        med_alerts = gr.HTML()

                    # ── Section 5: Diagnosis & Decision ──
                    with gr.Tab("✅ التشخيص والقرار"):
                        initial_diagnosis = gr.Textbox(
                            label="التشخيص المبدئي",
                            placeholder="التشخيص المبدئي...",
                            lines=2
                        )
                        decision = gr.Dropdown(
                            choices=[
                                "خروج مع علاج",
                                "تحويل لقسم داخلي",
                                "عناية مركزة",
                                "عمليات",
                                "متابعة بالطوارئ"
                            ],
                            label="القرار",
                        )
                        final_notes = gr.Textbox(
                            label="ملاحظات إضافية",
                            lines=3
                        )
                        save_btn = gr.Button("✅ اعتماد وحفظ", variant="primary", size="lg")
                        save_result = gr.Textbox(label="النتيجة", interactive=False)

            # ═══ RIGHT SIDE: AI Sidebar (1/3) ═══
            with gr.Column(scale=1):
                # Section 1: AI Summary
                gr.HTML("<h3 style='text-align:right;color:#2563eb;'>🧠 ملخص الحالة</h3>")
                ai_summary_display = gr.Textbox(
                    label="ملخص AI",
                    interactive=False,
                    lines=10
                )

                # Section 2: Red Alerts
                gr.HTML("<h3 style='text-align:right;color:#dc2626;'>🔴 التنبيهات الحمراء</h3>")
                red_alerts_display = gr.HTML()

                # Section 3: AI Suggestions
                gr.HTML("<h3 style='text-align:right;color:#ca8a04;'>🟡 اقتراحات ذكية</h3>")
                update_analysis_btn = gr.Button("🔄 تحديث التحليل", variant="secondary")
                suggestions_display = gr.Textbox(
                    label="اقتراحات AI",
                    interactive=False,
                    lines=10
                )

                # Section 4: Conversation Analysis
                gr.HTML("<hr style='margin:15px 0;'>")
                gr.HTML("<h3 style='text-align:right;color:#7c3aed;'>🎙️ تحليل المحادثة</h3>")
                transcript_input = gr.Textbox(
                    label="نص المحادثة مع المريض",
                    placeholder="الصق هنا نص المحادثة بين الطبيب والمريض...\nمثال:\nالطبيب: ما الذي أتى بك اليوم؟\nالمريض: عندي ضعف شديد وصعوبة في البلع...",
                    lines=6
                )
                analyze_btn = gr.Button("🔍 تحليل المحادثة", variant="secondary")
                conversation_analysis = gr.Textbox(
                    label="نتيجة التحليل",
                    interactive=False,
                    lines=8
                )
                conversation_alerts = gr.HTML()

        # ── Event Handlers ──
        load_btn.click(
            fn=on_load_patient,
            outputs=[patient_banner, ai_summary_display, past_history,
                     current_meds_display, red_alerts_display]
        )

        check_vitals_btn.click(
            fn=on_check_vitals,
            inputs=[systolic, diastolic, heart_rate, spo2, temperature, resp_rate, gcs],
            outputs=[vitals_status, vitals_alerts]
        )

        substance_taken.change(
            fn=on_check_substance,
            inputs=[substance_taken],
            outputs=[substance_alerts]
        )

        medications_given.change(
            fn=on_medications_given_change,
            inputs=[medications_given],
            outputs=[med_alerts]
        )

        update_analysis_btn.click(
            fn=on_update_analysis,
            inputs=[chief_complaint, hpi, medications_given, substance_taken],
            outputs=[suggestions_display]
        )

        analyze_btn.click(
            fn=on_analyze_conversation,
            inputs=[transcript_input],
            outputs=[conversation_analysis, conversation_alerts]
        )

        save_btn.click(
            fn=lambda diag, dec, notes: f"✅ تم حفظ السجل\nالتشخيص: {diag}\nالقرار: {dec}",
            inputs=[initial_diagnosis, decision, final_notes],
            outputs=[save_result]
        )


if __name__ == "__main__":
    from db.init_db import init_database
    from db.seed_data import seed_all
    from ai.medgemma_client import load_medgemma

    init_database()
    seed_all()
    load_medgemma()

    with gr.Blocks(theme=get_gradio_theme(), css=CUSTOM_CSS, title="Gemma-Health Sentinel — الطوارئ") as demo:
        create_emergency_ui()
    demo.launch(share=False)
