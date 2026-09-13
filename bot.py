import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==========================================
# CONFIGURATION
# ==========================================
BOT_TOKEN = "8727302993:AAGrpEMX5kjwhFojnQFvmOO0U0JhUoe7krw"

# မိမိ၏ Telegram User ID ဂဏန်း (အမှန်ထည့်ထားပါသည်)
ADMIN_ID = 1580210387

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = BASE_DIR


# ==========================================
# HELPER FUNCTIONS
# ==========================================
def get_images_by_keyword(keyword):
    found_files = []
    if os.path.exists(IMAGES_DIR):
        all_files = sorted(os.listdir(IMAGES_DIR))
        for filename in all_files:
            if keyword.lower() in filename.lower():
                full_path = os.path.join(IMAGES_DIR, filename)
                found_files.append(full_path)
    return found_files


async def send_photos(chat_id, context, keyword, caption_text):
    image_paths = get_images_by_keyword(keyword)
    opened_files = []
    media_group = []

    try:
        for path in image_paths:
            f = open(path, "rb")
            opened_files.append(f)
            if len(media_group) == 0:
                media_group.append(InputMediaPhoto(f, caption=caption_text))
            else:
                media_group.append(InputMediaPhoto(f))

        if media_group:
            await context.bot.send_media_group(chat_id=chat_id, media=media_group)
        else:
            await context.bot.send_message(chat_id=chat_id, text=f"{keyword} စာသားပါသော ပုံများကို ရှာမတွေ့ပါ။")
    except Exception as e:
        print(f"[ERROR Photo] {e}")
        await context.bot.send_message(chat_id=chat_id, text=f"အမှားဖြစ်ပေါ်ပါသည်: {e}")
    finally:
        for f in opened_files:
            f.close()


def custom_auto_reply(user_message):
    msg = user_message.lower().strip()

    # 1. မင်္ဂလာပါ / နှုတ်ဆက်ခြင်း
    if any(k in msg for k in ["hi", "hello", "မင်္ဂလာပါ", "ဟဲလို"]):
        return "မင်္ဂလာပါရှင့် ✨ Buffalo688 မှ ကြိုဆိုပါတယ်ရှင့်။ ဘာများ ကူညီပေးရမလဲရှင့်?"

    # 2. အကောင့်ဖွင့်ခြင်း
    elif any(k in msg for k in ["အကောင့်ဖွင့်", "acc ဖွင့်", "account", "ဖွင့်ချင်"]):
        return "ဟုတ်ကဲ့ပါရှင့် အကောင့်သစ် ဖွင့်ပေးဖို့အတွက် ဖုန်းနံပါတ်လေး ပို့ပေးပါဦးနော် ✨\n\nအကောင့်ဖွင့်ပြီးပါက နေ့စဉ် 5% Cash Back ဘောနပ်စ် ရရှိပါမည်ရှင့် 🎁"

    # 3. ငွေသွင်းနည်း
    elif any(k in msg for k in ["ငွေသွင်း", "ငွေဖြည့်", "သွင်းနည်း", "deposit"]):
        return "📱 ဆော့ဝဲထဲကနေ တိုက်ရိုက် ငွေဖြည့်နိုင်ပါတယ်ရှင့်။ ငွေသွင်းနည်း ပုံများကို '💰 ငွေသွင်းနည်း' ခလုတ်ကို နှိပ်၍ ကြည့်ရှုနိုင်ပါတယ်ရှင့် ✨"

    # 4. ငွေထုတ်နည်း
    elif any(k in msg for k in ["ငွေထုတ်", "ထုတ်နည်း", "withdraw"]):
        return "📱 ဆော့ဝဲထဲကနေ တိုက်ရိုက် ငွေထုတ်ယူနိုင်ပါတယ်ရှင့်။ ငွေထုတ်နည်း ပုံများကို '💸 ငွေထုတ်နည်း' ခလုတ်ကို နှိပ်၍ ကြည့်ရှုနိုင်ပါတယ်ရှင့် ✨"

    # 5. ဘောနပ်စ် / ပရိုမိုးရှင်း
    elif any(k in msg for k in ["bonus", "ဘောနပ်", "ပရိုမိုးရှင်း", "cashback", "ရှုံးကြေး"]):
        return "ညီမတို့ Buffalo688 မှာ ကံမကောင်းလို့ ရှုံးသွားခဲ့ရင်တောင် နေ့စဉ် 5% Cash Back ဘောနပ်စ် ပြန်လည်ပေးအပ်နေပါတယ်ရှင့် ✨"

    # 6. အနည်းဆုံး သွင်းငွေ/ထုတ်ငွေ
    elif any(k in msg for k in ["အနည်းဆုံး", "ဘယ်လောက်သွင်း", "ဘယ်လောက်ထုတ်"]):
        return "အနည်းဆုံး ငွေသွင်း/ငွေထုတ် ပမာဏမှာ 3,000 ကျပ် ဖြစ်ပါတယ်ရှင့် ✨"

    # 7. ဆော့ဝဲဒေါင်းလုဒ်
    elif any(k in msg for k in ["app", "ဆော့ဝဲ", "download", "ဒေါင်း"]):
        return "📲 Buffalo688 ဆော့ဝဲဒေါင်းလုဒ်ရယူရန် လင့်ခ် -\nhttps://m.buffalo688.club/auth/register?code=K8PYVL"

    # 8. သီးသန့် အဖြေမရှိပါက မူလအတိုင်း စောင့်ခိုင်းသည့် စာ
    else:
        return "ဟုတ်ကဲ့ပါရှင့်၊ မေးမြန်းထားသော စာအတွက် အက်ဒမင်မှ ခဏအတွင်း အကြောင်းပြန်ပေးပါလိမ့်မည်ရှင့် ✨"


# ==========================================
# TELEGRAM BOT HANDLERS
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inline_keyboard = [
        [InlineKeyboardButton("🎰 ကျဝှဲဂိမ်း အကောင့်ဖွင့်မယ်", callback_data="register")],
        [InlineKeyboardButton("▶️ ဆော့ဝဲဒေါင်းမယ်", url="https://m.buffalo688.club/auth/register?code=K8PYVL")],
        [InlineKeyboardButton("🌐 တိုက်ရိုက်လင့်", url="https://m.buffalo688.club/auth/register?code=K8PYVL")],
        [
            InlineKeyboardButton("💰 ငွေသွင်းနည်း", callback_data="deposit"),
            InlineKeyboardButton("💸 ငွေထုတ်နည်း", callback_data="withdraw")
        ],
        [InlineKeyboardButton("👸 အက်ဒမင်နဲ့ ဆက်သွယ်ရန်", url="https://t.me/maylay18181")]
    ]

    reply_keyboard = [
        ["🐂 အကောင့်ဖွင့်မယ် 🚀"],
        ["▶️ ဆော့ဝဲဒေါင်းမည်", "🌐 တိုက်ရိုက်လင့်"],
        ["💰 ငွေသွင်းနည်း", "💸 ငွေထုတ်နည်း"],
        ["👸 အကောင့် ဆက်သွယ်ရန်"]
    ]

    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    welcome_text = """🌸 မင်္ဂလာပါရှင့် 🌸

Buffalo688 ကျွဲဂိမ်းတိုက်ရိုက်ဆိုက်ကြီးကနေ ကြိုဆိုပါတယ်။

ညီမတို့ဂိမ်းဆိုဒ်ကြီး မှာ 
ကံမကောင်းလို့ ရှုံးသွားရင်တောင်
နေ့စဉ် 5% ပြန်ရမယ်"""

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    await update.message.reply_text("အောက်ပါ ခလုတ်များကို အသုံးပြုနိုင်ပါသည် -", reply_markup=inline_markup)


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "register":
        await query.message.reply_text("ဟုတ်ကဲ့ပါရှင့် အကောင့်သစ်လေး ဖွင့်ပေးဖို့အတွက် အစ်ကိုရဲ့ ဖုန်းနံပါတ်လေး ပြောပေးပါဦးရှင့် ✨🌸")
        await query.message.reply_text("အကောင့်ဖွင့်ပြီးပါက နေ့စဉ် 5% Cash Back ဘောနပ်စ် ရရှိပါမည်ရှင့် 🎁")
        await query.message.reply_text("အဆင်မပြေတာရှိရင် အက်ဒမင်ထံ တိုက်ရိုက် ဆက်သွယ်မေးမြန်းနိုင်ပါသည်ခင်ဗျာ 👸")

    elif query.data == "deposit":
        await query.message.reply_text("📱 ဆော့ဝဲထဲကနေ တိုက်ရိုက် ငွေဖြည့်နည်းလေးကို ပုံလေးတွေနဲ့ တဆင့်ချင်းရှင်းပြပေးထားပါတယ်ရှင့် ✨")
        deposit_caption = """⚠️ အချက်အလက်လေး မှန်ကန်အောင်တင်ပေးပါနော် 💯\n\n⚡️ အချက်အလက်လေးမှန်ကန်ရင် ၁၀ စက္ကန့်အတွင်း ဂိမ်းထဲပိုက်ဆံရောက်လာပါမယ်ရှင့် 📲💸"""
        await send_photos(query.message.chat_id, context, "deposit", deposit_caption)

    elif query.data == "withdraw":
        await query.message.reply_text("📱 ဆော့ဝဲထဲကနေ တိုက်ရိုက် ငွေထုတ်နည်းလေးကို ပုံလေးတွေနဲ့ တဆင့်ချင်းရှင်းပြပေးထားပါတယ်ရှင့် ✨")
        withdraw_caption = """⚡️ အချက်အလက်လေးမှန်ကန်အောင် ထည့်ပြီးရင် 10 စက္ကန့်အတွင်း Kpay, Wave ထဲ ထုတ်ငွေလေးဝင်လာပါမယ်ရှင့် 📲💸"""
        await send_photos(query.message.chat_id, context, "withdraw", withdraw_caption)


async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat_id
    user = update.message.from_user

    # 1. မူလ Bot ခလုတ် စာသားများကို တုံ့ပြန်ခြင်း
    if "အကောင့်ဖွင့်မယ်" in text:
        await update.message.reply_text("ဟုတ်ကဲ့ပါရှင့် အကောင့်သစ်လေး ဖွင့်ပေးဖို့အတွက် အစ်ကိုရဲ့ ဖုန်းနံပါတ်လေး ပြောပေးပါဦးရှင့် ✨🌸")
        await update.message.reply_text("အကောင့်ဖွင့်ပြီးပါက နေ့စဉ် 5% Cash Back ဘောနပ်စ် ရရှိပါမည်ရှင့် 🎁")
        await update.message.reply_text("အဆင်မပြေတာရှိရင် အက်ဒမင်ထံ တိုက်ရိုက် ဆက်သွယ်မေးမြန်းနိုင်ပါသည်ခင်ဗျာ 👸")

    elif "ဆော့ဝဲဒေါင်းမည်" in text:
        await update.message.reply_text("📲 Buffalo688 ဆော့ဝဲဒေါင်းလုဒ်ရယူရန် လင့်ခ် -\nhttps://m.buffalo688.club/auth/register?code=K8PYVL")

    elif "တိုက်ရိုက်လင့်" in text:
        await update.message.reply_text("🌐 Buffalo688 တိုက်ရိုက်ဆိုက်သို့ ဝင်ရောက်ရန် -\nhttps://m.buffalo688.club/auth/register?code=K8PYVL")

    elif "ငွေသွင်းနည်း" in text:
        await update.message.reply_text("📱 ဆော့ဝဲထဲကနေ တိုက်ရိုက် ငွေဖြည့်နည်းလေးကို ပုံလေးတွေနဲ့ တဆင့်ချင်းရှင်းပြပေးထားပါတယ်ရှင့် ✨")
        deposit_caption = """⚠️ အချက်အလက်လေး မှန်ကန်အောင်တင်ပေးပါနော် 💯\n\n⚡️ အချက်အလက်လေးမှန်ကန်ရင် ၁၀ စက္ကန့်အတွင်း ဂိမ်းထဲပိုက်ဆံရောက်လာပါမယ်ရှင့် 📲💸"""
        await send_photos(chat_id, context, "deposit", deposit_caption)

    elif "ငွေထုတ်နည်း" in text:
        await update.message.reply_text("📱 ဆော့ဝဲထဲကနေ တိုက်ရိုက် ငွေထုတ်နည်းလေးကို ပုံလေးတွေနဲ့ တဆင့်ချင်းရှင်းပြပေးထားပါတယ်ရှင့် ✨")
        withdraw_caption = """⚡️ အချက်အလက်လေးမှန်ကန်အောင် ထည့်ပြီးရင် 10 စက္ကန့်အတွင်း Kpay, Wave ထဲ ထုတ်ငွေလေးဝင်လာပါမယ်ရှင့် 📲💸"""
        await send_photos(chat_id, context, "withdraw", withdraw_caption)

    elif "ဆက်သွယ်ရန်" in text:
        await update.message.reply_text("👸 အက်ဒမင်ထံ တိုက်ရိုက် ဆက်သွယ်ရန် လင့်ခ် -\nhttps://t.me/maylay18181")

    # 2. Admin (ADMIN_ID = 1580210387) မှ Reply နှိပ်၍ ဖောက်သည်ထံ စာပြန်ခြင်း
    elif user.id == ADMIN_ID:
        if update.message.reply_to_message:
            reply_msg = update.message.reply_to_message
            target_text = reply_msg.text or reply_msg.caption or ""
            
            if "ID:" in target_text:
                try:
                    lines = target_text.split("\n")
                    user_id_line = [l for l in lines if "ID:" in l][0]
                    target_user_id = int(user_id_line.split("ID:")[1].strip())
                    
                    await context.bot.send_message(chat_id=target_user_id, text=text)
                    await update.message.reply_text("✅ ဖောက်သည်ထံ စာပြန်ပြီးပါပြီခင်ဗျာ။")
                except Exception as e:
                    print(f"[Admin Reply Error] {e}")
                    await update.message.reply_text(f"❌ စာပြန်၍ မရပါ: {e}")
            else:
                await update.message.reply_text("⚠️ Reply နှိပ်ထားသော Message ထဲတွင် 'ID:' စာသား ပါဝင်ခြင်း မရှိပါခင်ဗျာ။")

    # 3. ဖောက်သည်မှ စာပို့လာပါက Auto-Reply ပို့ခြင်း + Admin ထံ စာလှမ်းပို့ပေးခြင်း
    else:
        auto_reply = custom_auto_reply(text)
        await update.message.reply_text(auto_reply)

        admin_msg = (
            f"📩 ဖောက်သည်ထံမှ စာအသစ် ရောက်ရှိပါသည်\n\n"
            f"👤 Name: {user.full_name}\n"
            f"🆔 User ID: {user.id}\n"
            f"💬 User Message: {text}\n"
            f"🤖 Bot Reply: {auto_reply}"
        )
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg)
        except Exception as e:
            print(f"[ERROR Admin Alert] {e}")


# ==========================================
# FLASK WEB SERVER
# ==========================================
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Buffalo688 Bot is Alive!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


# ==========================================
# MAIN EXECUTION
# ==========================================
def main():
    web_thread = Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()

    print("Bot is starting polling...")
    
    bot_app = Application.builder().token(BOT_TOKEN).build()

    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(button_click))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))

    bot_app.run_polling(drop_pending_updates=True, stop_signals=None)

if __name__ == '__main__':
    main()