import os
import requests
from flask import Flask, render_template_string, request, redirect, url_for
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from supabase import create_client, Client

# Environment Variables များကို ချိတ်ဆက်ခြင်း
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Supabase Client တည်ဆောက်ခြင်း
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Flask App တည်ဆောက်ခြင်း (Web Dashboard အတွက်)
app = Flask(__name__)

# --- WEB ADMIN DASHBOARD HTML TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="my">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Telegram Bot</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h2 { color: #333; text-align: center; }
        .message-box { border-bottom: 1px solid #eee; padding: 15px 0; }
        .user-info { font-weight: bold; color: #007bff; }
        .timestamp { font-size: 12px; color: #888; float: right; }
        .text { margin: 8px 0; font-size: 15px; color: #333; }
        .sender-admin { color: #28a745; font-weight: bold; }
        .sender-user { color: #dc3545; font-weight: bold; }
        .reply-form { margin-top: 10px; display: flex; gap: 10px; }
        .reply-form input[type="text"] { flex: 1; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        .reply-form button { padding: 8px 15px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .reply-form button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h2>💬 Telegram Bot Admin Dashboard</h2>
        <hr>
        {% for msg in messages %}
        <div class="message-box">
            <span class="timestamp">{{ msg.created_at }}</span>
            <div class="user-info">User ID: {{ msg.user_id }} | Name: {{ msg.name }}</div>
            <div class="text">
                {% if msg.sender == 'admin' %}
                    <span class="sender-admin">[Admin to User]:</span>
                {% else %}
                    <span class="sender-user">[User]:</span>
                {% endif %}
                {{ msg.message }}
            </div>
            
            <!-- Web ကနေ တိုက်ရိုက် စာပြန်ရန် Form -->
            <form class="reply-form" action="/reply" method="POST">
                <input type="hidden" name="user_id" value="{{ msg.user_id }}">
                <input type="text" name="reply_message" placeholder="ဖောက်သည်ဆီသို့ စာပို့ရန်..." required>
                <button type="submit">စာပို့မည်</button>
            </form>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route("/")
def admin_dashboard():
    # Supabase မှ မက်ဆေ့ချ်များကို အသစ်ဆုံး အရင်ပေါ်အောင် ဆွဲထုတ်ခြင်း
    response = supabase.table("messages").select("*").order("id", desc=True).limit(50).execute()
    messages = response.data if response.data else []
    return render_template_string(HTML_TEMPLATE, messages=messages)

@app.route("/reply", methods=["POST"])
def web_reply():
    user_id = request.form.get("user_id")
    reply_message = request.form.get("reply_message")
    
    if user_id and reply_message:
        # Telegram Bot API ကိုသုံးပြီး ဖောက်သည်ဆီ တိုက်ရိုက်ပို့ခြင်း
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": user_id,
            "text": f"👑 **Admin မှ တိုက်ရိုက်ပြောကြားချက်:**\n\n{reply_message}",
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload)
        
        # Supabase ထဲသို့ Admin ရဲ့ ပို့လိုက်သော မက်ဆေ့ချ်ကို မှတ်တမ်းတင်ခြင်း
        supabase.table("messages").insert({
            "user_id": str(user_id),
            "name": "Admin",
            "message": reply_message,
            "sender": "admin"
        }).execute()
        
    return redirect(url_for('admin_dashboard'))


# --- TELEGRAM BOT LOGIC ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_id = str(user.id)
    name = f"{user.first_name or ''} {user.last_name or ''}".strip()

    # ဖောက်သည်ဆီက စာဝင်လာရင် Supabase ထဲ သိမ်းမည်
    supabase.table("messages").insert({
        "user_id": user_id,
        "name": name,
        "message": text,
        "sender": "user"
    }).execute()

    # Admin ထံသို့ Forward လုပ်ပေးမည်
    if user_id != str(ADMIN_ID):
        forward_text = f"📩 **စာအသစ်ရောက်ရှိပါပြီ**\n👤 **နာမည်:** {name}\n🆔 **ID:** `{user_id}`\n\n💬 **စာသား:** {text}"
        await context.bot.send_message(chat_id=ADMIN_ID, text=forward_text, parse_mode="Markdown")
        await update.message.reply_text("မင်္ဂလာပါရှင့်။ မက်ဆေ့ချ်ကို လက်ခံရရှိပါပြီ။ အမြန်ဆုံး ပြန်လည်ဆက်သွယ်ပေးပါမည်။")


# --- START BOTH FLASK & BOT ---
if __name__ == "__main__":
    from threading import Thread
    
    # Telegram Bot ကို Background Thread ဖြင့် အလုပ်လုပ်ခိုင်းခြင်း
    def run_telegram_bot():
        app_bot = ApplicationBuilder().token(TOKEN).build()
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app_bot.run_polling()

    bot_thread = Thread(target=run_telegram_bot)
    bot_thread.start()

    # Render ပေါ်တွင် Flask Web Server ကို စတင်ခြင်း (Port 10000 ဖြင့်)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)