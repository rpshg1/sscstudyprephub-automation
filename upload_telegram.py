"""
Upload generated PDF to Telegram Channel @sscstudyprephub
Uses Telegram Bot API (sendDocument)
"""

import os
import sys
import requests


def upload_to_telegram(pdf_path, bot_token=None, chat_id=None, custom_caption=None):
    bot_token = (bot_token or "").strip() or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = (chat_id or "").strip() or os.getenv("TELEGRAM_CHAT_ID", "").strip() or "@sscstudyprephub"

    if not bot_token:
        print("[!] TELEGRAM_BOT_TOKEN is not set.")
        print("    Please set TELEGRAM_BOT_TOKEN in your environment or repository secrets.")
        return False, "TELEGRAM_BOT_TOKEN not provided"

    if not os.path.exists(pdf_path):
        print(f"[!] PDF file does not exist: {pdf_path}")
        return False, "PDF not found"

    filename = os.path.basename(pdf_path)

    if not custom_caption:
        caption = (
            "📚 <b>Daily Bilingual Current Affairs Capsule (English + हिंदी)</b>\n"
            "🎯 <b>Target:</b> SSC CGL, CHSL, MTS, CPO, Railway RRB, Banking & State PSCs\n\n"
            "✨ <i>Inside Today's Detailed PDF:</i>\n"
            "• 🇮🇳 India & Government Schemes (राष्ट्रीय व सरकारी योजनाएं)\n"
            "• 🏛️ States & Major Cities News (राज्य एवं प्रमुख शहर)\n"
            "• 🌐 World & International Affairs (अंतर्राष्ट्रीय समाचार)\n"
            "• 💰 Economy, Banking & Finance (अर्थव्यवस्था एवं बैंकिंग)\n"
            "• 🚀 Science, Tech, Defence & Sports (विज्ञान, रक्षा व खेल)\n"
            "• 🎯 Bilingual Practice MCQs (अभ्यास प्रश्नोत्तरी)\n\n"
            "▶️ <b>YouTube:</b> https://youtube.com/@sscstudyprephub\n"
            "📢 <b>Telegram:</b> @sscstudyprephub"
        )
    else:
        caption = custom_caption

    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

    try:
        print(f"Uploading {filename} to Telegram channel {chat_id}...")
        with open(pdf_path, "rb") as f:
            files = {"document": (filename, f, "application/pdf")}
            data = {
                "chat_id": chat_id,
                "caption": caption,
                "parse_mode": "HTML"
            }
            res = requests.post(url, data=data, files=files, timeout=90)
            res_json = res.json()

            if res_json.get("ok"):
                print("Successfully uploaded to Telegram!")
                return True, res_json
            else:
                desc = res_json.get("description", "Unknown error")
                print(f"[!] Telegram API error: {desc}")
                return False, desc
    except Exception as e:
        print(f"[!] Exception during upload: {e}")
        return False, str(e)


if __name__ == "__main__":
    target_pdf = sys.argv[1] if len(sys.argv) > 1 else "SSC_Current_Affairs_test.pdf"
    upload_to_telegram(target_pdf)
