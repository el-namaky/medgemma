"""
app.py — Main entry point for Gemma-Health Sentinel.
Combines all 3 screens (Reception + Emergency + Diagnosis) into a single tabbed Gradio app.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
from db.init_db import init_database
from db.seed_data import seed_all
from ai.medgemma_client import load_medgemma
from ui.components import CUSTOM_CSS, get_gradio_theme
from ui.reception_ui import create_reception_ui
from ui.emergency_ui import create_emergency_ui
from ui.diagnosis_ui import create_diagnosis_ui
from ui.chat_ui import create_chat_ui


def main():
    """Launch the complete Gemma-Health Sentinel application."""
    print("=" * 60)
    print("🏥 Gemma-Health Sentinel — MVP")
    print("   نظام الطوارئ الذكي بالذكاء الاصطناعي")
    print("=" * 60)

    # ── Step 1: Initialize Database ──
    print("\n📦 Step 1: Initializing database...")
    init_database()
    seed_all()

    # ── Step 2: Load AI Model ──
    print("\n🧠 Step 2: Loading MedGemma...")
    load_medgemma()

    # ── Step 3: Build Gradio App ──
    print("\n🎨 Step 3: Building Gradio interface...")

    with gr.Blocks(
        theme=get_gradio_theme(),
        css=CUSTOM_CSS,
        title="Gemma-Health Sentinel — نظام الطوارئ الذكي"
    ) as app:

        # App Header
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
                    padding: 25px 40px; border-radius: 16px; text-align: center; margin-bottom: 20px;
                    box-shadow: 0 8px 32px rgba(30, 58, 95, 0.4);">
            <h1 style="color: white; margin: 0; font-size: 32px; font-weight: 800;">
                🏥 Gemma-Health Sentinel
            </h1>
            <p style="color: #94a3b8; margin: 8px 0 0; font-size: 16px;">
                نظام الطوارئ الذكي — مدعوم بـ MedGemma AI
            </p>
            <div style="display: flex; justify-content: center; gap: 30px; margin-top: 12px;">
                <span style="color: #60a5fa; font-size: 13px;">🚪 استقبال</span>
                <span style="color: #f97316; font-size: 13px;">→</span>
                <span style="color: #f87171; font-size: 13px;">🚨 طوارئ</span>
                <span style="color: #f97316; font-size: 13px;">→</span>
                <span style="color: #a78bfa; font-size: 13px;">🔍 تشخيص معمق</span>
            </div>
        </div>
        """)

        # Main Tabs
        with gr.Tabs() as tabs:
            with gr.Tab("🚪 الاستقبال", id="reception"):
                create_reception_ui()

            with gr.Tab("🚨 الطوارئ", id="emergency"):
                create_emergency_ui()

            with gr.Tab("🔍 التشخيص المعمق", id="diagnosis"):
                create_diagnosis_ui()

            with gr.Tab("💬 محادثة عامة", id="chat"):
                create_chat_ui()

        # Footer
        gr.HTML("""
        <div style="text-align: center; padding: 15px; margin-top: 20px; color: #64748b; font-size: 12px;">
            <p>🏥 Gemma-Health Sentinel v1.0 — Powered by MedGemma 4B | MedGemma Impact Challenge 2026</p>
            <p>⚠️ هذا النظام أداة مساعدة للطبيب وليس بديلاً عن الحكم الطبي السريري</p>
        </div>
        """)

    # ── Step 4: Launch ──
    print("\n🚀 Launching Gemma-Health Sentinel...")
    print("   Open: http://localhost:7860")
    print("=" * 60)

    # Check if we should enable public sharing (useful for Colab/Spaces)
    enable_share = os.environ.get("GRADIO_SHARE", "false").lower() == "true"

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=enable_share,
        show_error=True,
    )


if __name__ == "__main__":
    main()
