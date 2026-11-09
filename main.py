"""
Daily Current Affairs Automation Orchestrator
Target: SSC STUDY PREP HUB (@sscstudyprephub)
"""

import os
import sys
import datetime
from dotenv import load_dotenv

# Load local environment variables if .env exists
load_dotenv()

from fetch_news import fetch_all_current_affairs
from generate_pdf import generate_pdf
from upload_telegram import upload_to_telegram

def run_daily_automation():
    print("=" * 60)
    print("  SSC STUDY PREP HUB - DAILY AUTOMATION STARTING")
    print(f"  Execution Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, "logo.jpg")

    # 1. Fetch Current Affairs
    print("\n[Step 1/3] Fetching latest Current Affairs...")
    try:
        affairs_data = fetch_all_current_affairs()
        date_str = affairs_data.get("date_str", datetime.datetime.now().strftime("%A, %d %B %Y"))
        print(f"-> Successfully collected news for: {date_str}")
    except Exception as e:
        print(f"[ERROR] Failed to fetch current affairs: {e}")
        sys.exit(1)

    # 2. Generate PDF
    print("\n[Step 2/3] Generating Branded PDF with YouTube Invisible Link...")
    today_clean = datetime.date.today().strftime("%Y_%m_%d")
    pdf_filename = f"SSC_Current_Affairs_{today_clean}.pdf"
    pdf_output_path = os.path.join(base_dir, pdf_filename)

    try:
        generate_pdf(affairs_data, pdf_output_path, logo_path)
        print(f"-> PDF generated: {pdf_output_path}")
    except Exception as e:
        print(f"[ERROR] PDF generation failed: {e}")
        sys.exit(1)

    # 3. Upload to Telegram
    print("\n[Step 3/3] Uploading PDF to Telegram Channel @sscstudyprephub...")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "@sscstudyprephub").strip()

    if not bot_token:
        print("\n" + "!" * 60)
        print("NOTICE: TELEGRAM_BOT_TOKEN is not configured yet!")
        print(f"Generated PDF is saved locally at:\n{pdf_output_path}")
        print("To enable automatic Telegram delivery:")
        print("1. Get your Bot Token from @BotFather on Telegram.")
        print("2. Add the bot as an Administrator in your channel @sscstudyprephub.")
        print("3. Add TELEGRAM_BOT_TOKEN to your .env or GitHub Secrets.")
        print("!" * 60 + "\n")
        return

    success, result = upload_to_telegram(pdf_output_path, bot_token=bot_token, chat_id=chat_id)
    if success:
        print("\n🎉 AUTOMATION COMPLETED SUCCESSFULLY! PDF posted to Telegram.")
    else:
        print(f"\n[WARNING] Telegram upload failed: {result}")
        print("Check your TELEGRAM_BOT_TOKEN and make sure the bot is an admin in @sscstudyprephub.")

if __name__ == "__main__":
    run_daily_automation()
