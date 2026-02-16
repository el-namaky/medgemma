"""
chat_ui.py — Simple Chat Interface for direct model interaction.
"""

import gradio as gr
from ai.medgemma_client import ask_medgemma

def respond(message, history):
    """
    Generate a response from MedGemma without any system prompt using ChatInterface.
    history is the list of [user_msg, bot_msg] pairs provided by ChatInterface, 
    but ask_medgemma currently takes a single prompt. 
    
    For a simple chat without memory (as per "just a simple chat" request and existing client limitation 
    which seems to be request-response based in ask_medgemma), we will just send the current message.
    
    If we wanted context, we'd need to format the history. 
    However, the user asked for "just a chat with the model without a system prompt", 
    implying a raw interface. We'll stick to the current message for simplicity unless 
    context is strictly required, but passing history is better for a "chat" feel.
    
    Let's reconstruct a simple prompt from history if needed, but ask_medgemma 
    seems designed for single-turn or manual context handling. 
    Let's just pass the message for now to be safe and raw.
    """
    # If we want to include history, we would concatenate it. 
    # For now, let's keep it simple as requested: "Just a chat ... without system prompt"
    
    # We can use the history if we want to maintain context, i.e., 
    # full_prompt = form_prompt(history + [[message, None]])
    # But ask_medgemma does its own tokenization. 
    
    # Let's try sending just the message first as it's the safest interpretation of "raw".
    response = ask_medgemma(message, system_prompt="")
    return response

def create_chat_ui():
    """Create the Chat Interface tab."""
    with gr.Column():
        gr.Markdown("### 💬 محادثة مباشرة مع النموذج (بدون توجيه)")
        
        chat = gr.ChatInterface(
            fn=respond,
            chatbot=gr.Chatbot(height=500, type="messages"),
            textbox=gr.Textbox(placeholder="اكتب رسالتك هنا...", container=False, scale=7),
            title=None,
            description="هذه واجهة محادثة مباشرة مع نموذج MedGemma بدون أي System Prompt.",
            theme="soft",
            examples=["مرحباً", "من أنت؟", "تحدث عن الطب"],
            cache_examples=False,
            clear_btn="🗑️ مسح",
        )
