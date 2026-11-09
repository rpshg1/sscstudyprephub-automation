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
            f"📚 <b>Daily Current Affairs Capsule</b>\n"
            f"🎯 <b>Target:</b> SSC CGL, CHSL, MTS, CPO, CDS, NDA, Banking & State PSCs\n\n"
            f"✨ <i>Inside this Capsule:</i>\n"
            f"• 🇮🇳 National & State Governance Highlights\n"
            f"• 🌐 International Affairs & Global Summits\n"
            f"• 💰 Economy, Banking & RBI Updates\n"
            f"• 🏆 Sports, Appointments & Science-Defence\n"
            f"• 🎯 Daily Exam Booster Practice MCQs\n\n"
            f"🔗 <b>Subscribe on YouTube:</b> https://youtube.com/@sscstudyprephub\n"
            f"📢 <b>Join Telegram:</b> @sscstudyprephub\n"
            f"<i>(Note: Tap anywhere inside the PDF to visit our YouTube channel!)</i>"
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
                print(" Successfully uploaded to Telegram!")
                return True, res_json
            else:
                desc = res_json.get("description", "Unknown error")
                print(f"[!] Telegram API error: {desc}")
                return False, desc
    except Exception as e:
        print(f"[!] Exception during upload: {e}")
        return False, str(e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_pdf = sys.argv[1]
    else:
        target_pdf = "SSC_Current_Affairs_test.pdf"
    
    upload_to_telegram(target_pdf)
