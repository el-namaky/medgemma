"""
reception_ui.py — Reception screen for Gemma-Health Sentinel.
Patient selection/creation, patient card display, and transfer to ER.
"""

import gradio as gr
from db.init_db import init_database, get_connection
from db.seed_data import seed_all
from db.queries import (
    get_all_patients_summary, get_patient_full_record, add_new_patient
)
from ai.session_cache import SessionCache
from ai.medgemma_client import ask_medgemma, load_medgemma
from ai.prompts import SYSTEM_PROMPT, SUMMARY_PROMPT
from ui.components import CUSTOM_CSS, create_header, get_gradio_theme
from utils.helpers import format_patient_card_html

# ── Global State ──
_current_cache = None
_current_patient_id = None


def _get_patient_choices():
    """Get formatted patient list for dropdown."""
    # Patient-specific emojis
    emojis = {
        1: '❤️ قلب',
        2: '💊 سكري + ضغط',
        3: '⚠️ Myasthenia Gravis',
        4: '🌬️ ربو',
        5: '✅ سليمة',
    }
    patients = get_all_patients_summary()
    choices = []
    for p in patients:
        pid = p['patient_id']
        emoji = emojis.get(pid, '')
        label = f"{p['name']} — {p['age']} سنة — {emoji}"
        choices.append((label, pid))
    return choices


def on_patient_select(patient_choice):
    """Handle patient selection from dropdown."""
    global _current_cache, _current_patient_id

    if patient_choice is None:
        return "", "<div style='text-align:center;color:#94a3b8;padding:40px;'>اختر مريضاً من القائمة</div>", ""

    patient_id = patient_choice
    _current_patient_id = patient_id

    # Create session cache (loads all data once)
    _current_cache = SessionCache(patient_id)

    # Generate patient card HTML
    record = get_patient_full_record(patient_id)
    card_html = format_patient_card_html(record)

    # Generate AI summary
    ai_status = "🧠 AI يجهّز ملخص الحالة..."
    context = _current_cache.get_context_for_ai()
    prompt = SUMMARY_PROMPT.format(patient_context=context)
    ai_summary = ask_medgemma(prompt, system_prompt=SYSTEM_PROMPT)
    _current_cache.ai_summary = ai_summary

    return ai_summary, card_html, "✅ تم تحميل بيانات المريض وتجهيز ملخص AI"


def on_add_patient(national_id, name, age, gender, blood_type, phone,
                   emergency_contact, diseases_text, allergies_text, medications_text):
    """Handle new patient registration."""
    if not name or not name.strip():
        return "❌ يرجى إدخال اسم المريض", _get_patient_choices()

    # Parse diseases
    diseases = []
    if diseases_text and diseases_text.strip():
        for d in diseases_text.strip().split('\n'):
            d = d.strip()
            if d:
                diseases.append({'name': d, 'severity': 'متوسط'})

    # Parse allergies
    allergies_list = []
    if allergies_text and allergies_text.strip():
        for a in allergies_text.strip().split('\n'):
            a = a.strip()
            if a:
                allergies_list.append({'allergen': a, 'reaction': '', 'severity': 'متوسط'})

    # Parse medications
    medications = []
    if medications_text and medications_text.strip():
        for m in medications_text.strip().split('\n'):
            m = m.strip()
            if m:
                medications.append({'name': m, 'dose': '', 'frequency': '', 'reason': ''})

    try:
        patient_id = add_new_patient(
            national_id or '', name, int(age) if age else 0,
            gender or 'غير محدد', blood_type or '', phone or '',
            emergency_contact or '', diseases, allergies_list, medications
        )
        return f"✅ تم إضافة المريض بنجاح (ID: {patient_id})", _get_patient_choices()
    except Exception as e:
        return f"❌ خطأ: {str(e)}", _get_patient_choices()


def on_transfer_to_er(visit_reason, priority, notes):
    """Handle transfer to emergency department."""
    global _current_cache

    if _current_cache is None:
        return "❌ يرجى اختيار مريض أولاً"

    if not visit_reason or not visit_reason.strip():
        return "❌ يرجى إدخال سبب الزيارة"

    # Store visit info in session cache
    _current_cache.current_complaint = visit_reason
    _current_cache.add_session_update('visit_reason', visit_reason)
    _current_cache.add_session_update('priority', priority)
    _current_cache.add_session_update('reception_notes', notes)

    # Record the visit
    from utils.helpers import get_date
    from db.queries import add_visit
    add_visit(
        _current_cache.patient_id,
        get_date(),
        'طوارئ',
        visit_reason,
        doctor_notes=notes or ''
    )

    return f"""✅ تم تسجيل وتحويل المريض للطوارئ بنجاح!

📋 تفاصيل التحويل:
• المريض: {_current_cache.patient_info.get('name', '')}
• سبب الزيارة: {visit_reason}
• الأولوية: {priority}

🧠 ملخص AI جاهز لطبيب الطوارئ
➡️ انتقل لتبويب "🚨 الطوارئ" للمتابعة"""


def get_current_cache():
    """Get the current session cache (used by emergency/diagnosis UIs)."""
    return _current_cache


def create_reception_ui():
    """Create the reception Gradio interface."""
    with gr.Column():
        # Header
        gr.HTML(create_header(
            "Gemma-Health Sentinel — الاستقبال",
            "نظام الاستقبال الذكي — اختر مريضاً أو سجّل مريضاً جديداً"
        ))

        with gr.Tabs():
            # ── Tab 1: Select Existing Patient ──
            with gr.Tab("📋 اختيار مريض موجود"):
                with gr.Row():
                    with gr.Column(scale=1):
                        patient_dropdown = gr.Dropdown(
                            choices=_get_patient_choices(),
                            label="🔍 اختر المريض",
                            info="اختر من المرضى المسجلين في النظام",
                            interactive=True,
                        )
                        status_text = gr.Textbox(
                            label="الحالة",
                            interactive=False,
                            lines=1
                        )

                    with gr.Column(scale=2):
                        patient_card = gr.HTML(
                            value="<div style='text-align:center;color:#94a3b8;padding:60px;font-size:18px;'>"
                                  "👈 اختر مريضاً من القائمة لعرض البطاقة الطبية</div>"
                        )

                with gr.Row():
                    with gr.Column():
                        ai_summary = gr.Textbox(
                            label="🧠 ملخص AI للحالة",
                            interactive=False,
                            lines=12,
                            info="يتم توليده تلقائياً عند اختيار المريض"
                        )

                # Transfer to ER section
                gr.HTML("<hr style='margin:20px 0;border-color:#334155;'>")
                gr.HTML("<h3 style='text-align:right;color:#1e3a5f;'>➡️ تسجيل الدخول للطوارئ</h3>")

                with gr.Row():
                    with gr.Column(scale=2):
                        visit_reason = gr.Textbox(
                            label="سبب الزيارة",
                            placeholder="مثال: ألم في الصدر منذ ساعتين...",
                            lines=2
                        )
                    with gr.Column(scale=1):
                        priority = gr.Radio(
                            choices=["🟢 عادي", "🟡 متوسط", "🔴 طوارئ", "⚫ حرج"],
                            label="مستوى الأولوية",
                            value="🟡 متوسط"
                        )

                reception_notes = gr.Textbox(
                    label="ملاحظات موظف الاستقبال (اختياري)",
                    placeholder="أي ملاحظات إضافية...",
                    lines=2
                )

                transfer_btn = gr.Button(
                    "📤 تسجيل وتحويل للطوارئ ➡️",
                    variant="primary",
                    size="lg"
                )
                transfer_result = gr.Textbox(label="نتيجة التحويل", interactive=False, lines=5)

            # ── Tab 2: New Patient Registration ──
            with gr.Tab("➕ مريض جديد"):
                gr.HTML("<h3 style='text-align:right;color:#1e3a5f;'>📝 تسجيل مريض جديد</h3>")

                with gr.Row():
                    new_national_id = gr.Textbox(label="الرقم القومي", placeholder="14 رقم")
                    new_name = gr.Textbox(label="الاسم الكامل *", placeholder="الاسم الثلاثي")

                with gr.Row():
                    new_age = gr.Number(label="السن", value=30, minimum=0, maximum=120)
                    new_gender = gr.Dropdown(
                        choices=["ذكر", "أنثى"],
                        label="الجنس",
                        value="ذكر"
                    )
                    new_blood_type = gr.Dropdown(
                        choices=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                        label="فصيلة الدم"
                    )

                with gr.Row():
                    new_phone = gr.Textbox(label="رقم الهاتف", placeholder="01XXXXXXXXX")
                    new_emergency = gr.Textbox(label="رقم الطوارئ", placeholder="01XXXXXXXXX")

                new_diseases = gr.Textbox(
                    label="الأمراض المزمنة (مرض واحد في كل سطر)",
                    placeholder="ارتفاع ضغط الدم\nسكري نوع 2",
                    lines=3
                )
                new_allergies = gr.Textbox(
                    label="الحساسيات (حساسية واحدة في كل سطر)",
                    placeholder="بنسلين\nأسبرين",
                    lines=2
                )
                new_medications = gr.Textbox(
                    label="الأدوية الحالية (دواء واحد في كل سطر)",
                    placeholder="أملوديبين 5mg\nميتفورمين 500mg",
                    lines=3
                )

                add_btn = gr.Button("💾 حفظ المريض الجديد", variant="primary", size="lg")
                add_result = gr.Textbox(label="النتيجة", interactive=False)

        # ── Event Handlers ──
        patient_dropdown.change(
            fn=on_patient_select,
            inputs=[patient_dropdown],
            outputs=[ai_summary, patient_card, status_text]
        )

        transfer_btn.click(
            fn=on_transfer_to_er,
            inputs=[visit_reason, priority, reception_notes],
            outputs=[transfer_result]
        )

        add_btn.click(
            fn=on_add_patient,
            inputs=[new_national_id, new_name, new_age, new_gender,
                    new_blood_type, new_phone, new_emergency,
                    new_diseases, new_allergies, new_medications],
            outputs=[add_result, patient_dropdown]
        )


if __name__ == "__main__":
    # Initialize DB
    init_database()
    seed_all()
    load_medgemma()

    with gr.Blocks(theme=get_gradio_theme(), css=CUSTOM_CSS, title="Gemma-Health Sentinel — الاستقبال") as demo:
        create_reception_ui()

    demo.launch(share=False)
