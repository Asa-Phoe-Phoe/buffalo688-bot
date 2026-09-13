import os
import asyncio
from flask import Flask
from threading import Thread

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    InputMediaPhoto
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from openai import OpenAI


# ==========================================
# CONFIGURATION
# ==========================================

# မင်းရဲ့ လက်ရှိ Telegram Bot Token ကို ဒီနေရာမှာထည့်ပါ
BOT_TOKEN = "8727302993:AAFzD62UaT-wAmbcv6rc47P4ewmzUuLn9_8"

# မင်းရဲ့ Telegram User ID
ADMIN_ID = 1580210387

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = BASE_DIR


# ==========================================
# AI ADD-ON CONFIGURATION
# ==========================================

# Render Environment Variable ထဲက OPENAI_API_KEY ကိုယူမယ်
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if OPENAI_API_KEY:
    ai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    ai_client = None


AI_SYSTEM_PROMPT = """
မင်းက Buffalo688 Telegram Customer Service Assistant ဖြစ်တယ်။

Customer တွေနဲ့ မြန်မာလို သဘာဝကျကျ၊ ယဉ်ကျေးပြီး
တိုတိုရှင်းရှင်း ပြောပါ။

Customer မေးတဲ့အကြောင်းအရာကို နားလည်ပြီး
အကောင်းဆုံးဖြေကြားပေးပါ။

မသိတဲ့အချက်အလက်ကို မခန့်မှန်းပါနဲ့။
မသေချာတဲ့အရာရှိရင် Admin ကို ဆက်သွယ်ဖို့ ပြောပါ။

Customer က ရိုင်းစိုင်းတဲ့စကားသုံးရင်လည်း
ယဉ်ကျေးစွာ ပြန်ဖြေပါ။

Password, OTP, API Key, private token
လိုမျိုး လျှို့ဝှက်အချက်အလက်တွေကို မတောင်းပါနဲ့။

Customer service assistant တစ်ယောက်လို
သဘာဝကျကျ ပြောဆိုပါ။
"""


# Customer တစ်ယောက်ချင်းစီရဲ့ AI conversation မှတ်ထားမယ်
ai_history = {}


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

                if os.path.isfile(full_path):
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
                media_group.append(
                    InputMediaPhoto(
                        f,
                        caption=caption_text
                    )
                )
            else:
                media_group.append(
                    InputMediaPhoto(f)
                )

        if media_group:

            await context.bot.send_media_group(
                chat_id=chat_id,
                media=media_group
            )

        else:

            await context.bot.send_message(
                chat_id=chat_id,
                text=f"images folder ထဲတွင် {keyword} စာသားပါသော ပုံများကို ရှာမတွေ့ပါ။"
            )

    except Exception as e:

        print(f"[ERROR] {e}")

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"အမှားဖြစ်ပေါ်ပါသည်: {e}"
        )

    finally:

        for f in opened_files:
            f.close()


# ==========================================
# ORIGINAL TELEGRAM BOT HANDLERS
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    inline_keyboard = [

        [
            InlineKeyboardButton(
                "🎰 ကျဝှဲဂိမ်း အကောင့်ဖွင့်မယ်",
                callback_data="register"
            )
        ],

        [
            InlineKeyboardButton(
                "▶️ ဆော့ဝဲဒေါင်းမယ်",
                url="https://m.buffalo688.club/auth/register?code=K8PYVL"
            )
        ],

        [
            InlineKeyboardButton(
                "🌐 တိုက်ရိုက်လင့်",
                url="https://m.buffalo688.club/auth/register?code=K8PYVL"
            )
        ],

        [
            InlineKeyboardButton(
                "💰 ငွေသွင်းနည်း",
                callback_data="deposit"
            ),
            InlineKeyboardButton(
                "💸 ငွေထုတ်နည်း",
                callback_data="withdraw"
            )
        ],

        [
            InlineKeyboardButton(
                "👸 အက်ဒမင်နဲ့ ဆက်သွယ်ရန်",
                url="https://t.me/maylay18181"
            )
        ]
    ]

    reply_keyboard = [

        ["🐂 အကောင့်ဖွင့်မယ် 🚀"],

        [
            "▶️ ဆော့ဝဲဒေါင်းမည်",
            "🌐 တိုက်ရိုက်လင့်"
        ],

        [
            "💰 ငွေသွင်းနည်း",
            "💸 ငွေထုတ်နည်း"
        ],

        ["👸 အကောင့် ဆက်သွယ်ရန်"]
    ]

    inline_markup = InlineKeyboardMarkup(inline_keyboard)

    reply_markup = ReplyKeyboardMarkup(
        reply_keyboard,
        resize_keyboard=True
    )

    welcome_text = """🌸 မင်္ဂလာပါရှင့် 🌸

Buffalo688 ကျွဲဂိမ်းတိုက်ရိုက်ဆိုက်ကြီးကနေ ကြိုဆိုပါတယ်။

ညီမတို့ဂိမ်းဆိုဒ်ကြီးမှာ
ကံမကောင်းလို့ ရှုံးသွားရင်တောင်
နေ့စဉ် 5% ပြန်ရမယ်"""

    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup
    )

    await update.message.reply_text(
        "အောက်ပါ ခလုတ်များကို အသုံးပြုနိုင်ပါသည် -",
        reply_markup=inline_markup
    )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    if query.data == "register":

        await query.message.reply_text(
            "ဟုတ်ကဲ့ပါရှင့် အကောင့်သစ်လေး ဖွင့်ပေးဖို့အတွက် "
            "အစ်ကိုရဲ့ ဖုန်းနံပါတ်လေး ပြောပေးပါဦးရှင့် ✨🌸"
        )

        await query.message.reply_text(
            "အကောင့်ဖွင့်ပြီးပါက နေ့စဉ် 5% Cash Back "
            "ဘောနပ်စ် ရရှိပါမည်ရှင့် 🎁"
        )

        await query.message.reply_text(
            "အဆင်မပြေတာရှိရင် အက်ဒမင်ထံ "
            "တိုက်ရိုက် ဆက်သွယ်မေးမြန်းနိုင်ပါသည်ခင်ဗျာ 👸"
        )


    elif query.data == "deposit":

        await query.message.reply_text(
            "📱 ဆော့ဝဲထဲကနေ တိုက်ရိုက် ငွေဖြည့်နည်းလေးကို "
            "ပုံလေးတွေနဲ့ တဆင့်ချင်းရှင်းပြပေးထားပါတယ်ရှင့် ✨"
        )

        deposit_caption = """⚠️ အချက်အလက်လေး မှန်ကန်အောင်တင်ပေးပါနော် 💯

⚡️ အချက်အလက်လေးမှန်ကန်ရင် ၁၀ စက္ကန့်အတွင်း
ဂိမ်းထဲပိုက်ဆံရောက်လာပါမယ်ရှင့် 📲💸"""

        await send_photos(
            query.message.chat_id,
            context,
            "deposit",
            deposit_caption
        )


    elif query.data == "withdraw":

        await query.message.reply_text(
            "📱 ဆော့ဝဲထဲကနေ တိုက်ရိုက် ငွေထုတ်နည်းလေးကို "
            "ပုံလေးတွေနဲ့ တဆင့်ချင်းရှင်းပြပေးထားပါတယ်ရှင့် ✨"
        )

        withdraw_caption = """⚡️ အချက်အလက်လေးမှန်ကန်အောင် ထည့်ပြီးရင်
10 စက္ကန့်အတွင်း Kpay, Wave ထဲ
ထုတ်ငွေလေးဝင်လာပါမယ်ရှင့် 📲💸"""

        await send_photos(
            query.message.chat_id,
            context,
            "withdraw",
            withdraw_caption
        )


# ==========================================
# ORIGINAL TEXT HANDLER
# ==========================================

async def handle_text_messages(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text
    chat_id = update.message.chat_id
    user = update.message.from_user


    # ======================================
    # 1. မူလ Bot ခလုတ်စာသားများ
    # ======================================

    if "အကောင့်ဖွင့်မယ်" in text:

        await update.message.reply_text(
            "ဟုတ်ကဲ့ပါရှင့် အကောင့်သစ်လေး ဖွင့်ပေးဖို့အတွက် "
            "အစ်ကိုရဲ့ ဖုန်းနံပါတ်လေး ပြောပေးပါဦးရှင့် ✨🌸"
        )

        await update.message.reply_text(
            "အကောင့်ဖွင့်ပြီးပါက နေ့စဉ် 5% Cash Back "
            "ဘောနပ်စ် ရရှိပါမည်ရှင့် 🎁"
        )

        await update.message.reply_text(
            "အဆင်မပြေတာရှိရင် အက်ဒမင်ထံ "
            "တိုက်ရိုက် ဆက်သွယ်မေးမြန်းနိုင်ပါသည်ခင်ဗျာ 👸"
        )


    elif "ဆော့ဝဲဒေါင်းမည်" in text:

        await update.message.reply_text(
            "📲 **Buffalo688 ဆော့ဝဲဒေါင်းလုဒ်ရယူရန် လင့်ခ် -**\n"
            "https://m.buffalo688.club/auth/register?code=K8PYVL"
        )


    elif "တိုက်ရိုက်လင့်" in text:

        await update.message.reply_text(
            "🌐 **Buffalo688 တိုက်ရိုက်ဆိုက်သို့ ဝင်ရောက်ရန် -**\n"
            "https://m.buffalo688.club/auth/register?code=K8PYVL"
        )


    elif "ငွေသွင်းနည်း" in text:

        await update.message.reply_text(
            "📱 ဆော့ဝဲထဲကနေ တိုက်ရိုက် ငွေဖြည့်နည်းလေးကို "
            "ပုံလေးတွေနဲ့ တဆင့်ချင်းရှင်းပြပေးထားပါတယ်ရှင့် ✨"
        )

        deposit_caption = """⚠️ အချက်အလက်လေး မှန်ကန်အောင်တင်ပေးပါနော် 💯

⚡️ အချက်အလက်လေးမှန်ကန်ရင် ၁၀ စက္ကန့်အတွင်း
ဂိမ်းထဲပိုက်ဆံရောက်လာပါမယ်ရှင့် 📲💸"""

        await send_photos(
            chat_id,
            context,
            "deposit",
            deposit_caption
        )


    elif "ငွေထုတ်နည်း" in text:

        await update.message.reply_text(
            "📱 ဆော့ဝဲထဲကနေ တိုက်ရိုက် ငွေထုတ်နည်းလေးကို "
            "ပုံလေးတွေနဲ့ တဆင့်ချင်းရှင်းပြပေးထားပါတယ်ရှင့် ✨"
        )

        withdraw_caption = """⚡️ အချက်အလက်လေးမှန်ကန်အောင် ထည့်ပြီးရင်
10 စက္ကန့်အတွင်း Kpay, Wave ထဲ
ထုတ်ငွေလေးဝင်လာပါမယ်ရှင့် 📲💸"""

        await send_photos(
            chat_id,
            context,
            "withdraw",
            withdraw_caption
        )


    elif "ဆက်သွယ်ရန်" in text:

        await update.message.reply_text(
            "👸 **အက်ဒမင်ထံ တိုက်ရိုက် ဆက်သွယ်ရန် လင့်ခ် -**\n"
            "https://t.me/maylay18181"
        )


    # ======================================
    # 2. Admin Reply
    # ======================================

    elif user.id == ADMIN_ID:

        if update.message.reply_to_message:

            original_msg = (
                update.message.reply_to_message.text
                or update.message.reply_to_message.caption
            )

            if original_msg and "🆔 User ID:" in original_msg:

                try:

                    target_user_id = int(
                        original_msg
                        .split("🆔 User ID:")[1]
                        .split("\n")[0]
                        .replace("`", "")
                        .strip()
                    )

                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text=text
                    )

                    await update.message.reply_text(
                        "✅ စာပြန်ပြီးပါပြီခင်ဗျာ။"
                    )

                except Exception as e:

                    await update.message.reply_text(
                        f"❌ စာပြန်ရာတွင် အမှားဖြစ်ပေါ်ပါသည်: {e}"
                    )


    # ======================================
    # 3. Customer → Admin Notification
    # ======================================

    else:

        admin_msg = (
            f"📩 **ဖောက်သည်ထံမှ စာအသစ် ရောက်ရှိပါသည်**\n\n"
            f"👤 **Name:** {user.full_name}\n"
            f"🆔 User ID: `{user.id}`\n"
            f"💬 **Message:** {text}"
        )

        try:

            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_msg,
                parse_mode="Markdown"
            )

        except Exception as e:

            print(f"[ERROR Admin Alert] {e}")


# ==========================================
# AI ADD-ON
# ==========================================

async def ai_reply_addon(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    if not update.message.text:
        return


    text = update.message.text.strip()


    # ======================================
    # မူလ Button / Keyword တွေကို AI မထိစေ
    # ======================================

    existing_keywords = (
        "အကောင့်ဖွင့်မယ်",
        "ဆော့ဝဲဒေါင်းမည်",
        "တိုက်ရိုက်လင့်",
        "ငွေသွင်းနည်း",
        "ငွေထုတ်နည်း",
        "ဆက်သွယ်ရန်"
    )

    if any(
        keyword in text
        for keyword in existing_keywords
    ):
        return


    # ======================================
    # Admin က Customer ကို Reply ပြန်တာ
    # AI မဝင်စေ
    # ======================================

    if (
        update.message.from_user
        and update.message.from_user.id == ADMIN_ID
    ):

        if update.message.reply_to_message:
            return


    # ======================================
    # API Key မရှိရင် AI မလုပ်
    # ======================================

    if ai_client is None:

        print(
            "[AI] OPENAI_API_KEY မရှိသေးပါ။"
        )

        return


    user = update.message.from_user
    user_id = user.id


    # ======================================
    # Conversation History
    # ======================================

    history = ai_history.setdefault(
        user_id,
        []
    )

    history.append(
        {
            "role": "user",
            "content": text
        }
    )


    # နောက်ဆုံး message 10 ခုသာ AI ကိုပို့
    recent_history = history[-10:]


    try:

        response = await asyncio.to_thread(

            ai_client.chat.completions.create,

            model="gpt-4o-mini",

            messages=[
                {
                    "role": "system",
                    "content": AI_SYSTEM_PROMPT
                },
                *recent_history
            ],

            temperature=0.4,

            max_tokens=500
        )


        reply = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )


        history.append(
            {
                "role": "assistant",
                "content": reply
            }
        )


        # History အရမ်းမကြီးအောင်
        ai_history[user_id] = history[-10:]


        # ==================================
        # Customer ကို AI Reply
        # ==================================

        await update.message.reply_text(
            reply
        )


    except Exception as e:

        print(
            f"[AI ERROR] {e}"
        )


# ==========================================
# FLASK WEB SERVER
# ==========================================

web_app = Flask(__name__)


@web_app.route('/')
def home():

    return "Buffalo688 Bot is Alive!"


def run_web():

    port = int(
        os.environ.get(
            "PORT",
            8080
        )
    )

    web_app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )


# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == '__main__':

    web_thread = Thread(
        target=run_web
    )

    web_thread.daemon = True

    web_thread.start()


    print(
        "Bot is starting polling..."
    )


    bot_app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )


    # ======================================
    # ORIGINAL HANDLERS
    # ======================================

    bot_app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    bot_app.add_handler(
        CallbackQueryHandler(
            button_click
        )
    )


    bot_app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text_messages
        )
    )


    # ======================================
    # AI ADD-ON HANDLER
    # ======================================
    #
    # မူလ handler ကို မဖျက်ဘဲ
    # AI ကို သီးခြား group နဲ့ ထပ်ထည့်ထားတယ်။
    #

    bot_app.add_handler(

        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            ai_reply_addon
        ),

        group=-1
    )


    bot_app.run_polling(
        drop_pending_updates=True
    )