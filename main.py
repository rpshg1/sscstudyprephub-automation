"""
Daily Bilingual Current Affairs Automation Orchestrator
Target: SSC STUDY PREP HUB (@sscstudyprephub)
- Includes IST-date daily deduplication so a delayed schedule never posts twice in one day
- Validates fetched news breadth across categories before building & uploading PDF
"""

import os
import sys
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

from fetch_news import fetch_all_current_affairs
from generate_pdf import generate_pdf
from upload_telegram import upload_to_telegram


def get_ist_now():
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)


def already_posted_today_ist():
    """
    When triggered automatically via GitHub Actions `schedule`, check if another run
    already succeeded earlier today (IST) so we never post duplicate PDFs in the same day.
    Manual `workflow_dispatch` triggers bypass this guard unless deduplication is desired.
    """
    event_name = os.getenv("GITHUB_EVENT_NAME", "").strip()
    if event_name != "schedule":
        return False

    gh_token = os.getenv("GITHUB_TOKEN", "").strip()
    gh_repo = os.getenv("GITHUB_REPOSITORY", "").strip()
    current_run_id = os.getenv("GITHUB_RUN_ID", "").strip()

    if not gh_token or not gh_repo:
        return False

    ist_today_str = get_ist_now().strftime("%Y-%m-%d")
    try:
        headers = {
            "Authorization": f"Bearer {gh_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        url = f"https://api.github.com/repos/{gh_repo}/actions/runs?status=completed&per_page=15"
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            runs = res.json().get("workflow_runs", [])
            for r in runs:
                if str(r.get("id")) == current_run_id:
                    continue
                if r.get("conclusion") != "success":
                    continue
                created_utc_str = r.get("created_at", "")
                if not created_utc_str:
                    continue
                dt_utc = datetime.datetime.strptime(created_utc_str, "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=datetime.timezone.utc
                )
                dt_ist = dt_utc + datetime.timedelta(hours=5, minutes=30)
                if dt_ist.strftime("%Y-%m-%d") == ist_today_str:
                    print(
                        f"[DEDUP] Run #{r.get('run_number')} ({r.get('id')}) already completed successfully "
                        f"today at {dt_ist.strftime('%H:%M IST')}. Skipping duplicate scheduled run."
                    )
                    return True
    except Exception as e:
        print(f"[WARN] Deduplication check failed (continuing normally): {e}")

    return False


def run_daily_automation():
    ist_now = get_ist_now()
    print("=" * 64, flush=True)
    print("  SSC STUDY PREP HUB - DAILY BILINGUAL AUTOMATION STARTING", flush=True)
    print(f"  Execution Time (IST): {ist_now.strftime('%Y-%m-%d %H:%M:%S IST')}", flush=True)
    print("=" * 64, flush=True)

    if already_posted_today_ist():
        print("Exiting cleanly to prevent duplicate post today.", flush=True)
        return

    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, "logo.jpg")

    # 1. Fetch Current Affairs (Bilingual + Detailed)
    print("\n[Step 1/3] Fetching detailed bilingual Current Affairs...", flush=True)
    try:
        affairs_data = fetch_all_current_affairs()
        categories = affairs_data.get("categories", {})
        total_items = sum(len(v) for v in categories.values())
        active_cats = sum(1 for v in categories.values() if len(v) > 0)
        print(f"-> Collected {total_items} detailed items across {active_cats} categories.", flush=True)
        if total_items < 6 or active_cats < 3:
            print(f"[ERROR] Insufficient news gathered ({total_items} items across {active_cats} categories). Aborting to avoid sending incomplete PDF.", flush=True)
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to fetch current affairs: {e}", flush=True)
        sys.exit(1)

    # 2. Generate Bilingual Branded PDF
    print("\n[Step 2/3] Generating Bilingual Branded PDF...", flush=True)
    today_clean = ist_now.strftime("%Y_%m_%d")
    pdf_filename = f"SSC_Current_Affairs_{today_clean}.pdf"
    pdf_output_path = os.path.join(base_dir, pdf_filename)

    try:
        generate_pdf(affairs_data, pdf_output_path, logo_path)
        print(f"-> PDF generated: {pdf_output_path}", flush=True)
    except Exception as e:
        print(f"[ERROR] PDF generation failed: {e}", flush=True)
        sys.exit(1)

    # 3. Upload to Telegram
    print("\n[Step 3/3] Uploading PDF to Telegram Channel @sscstudyprephub...", flush=True)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip() or "@sscstudyprephub"

    if not bot_token:
        print("\n" + "!" * 60)
        print("NOTICE: TELEGRAM_BOT_TOKEN is not configured locally.")
        print(f"Generated PDF saved at: {pdf_output_path}")
        print("!" * 60 + "\n")
        return

    success, result = upload_to_telegram(pdf_output_path, bot_token=bot_token, chat_id=chat_id)
    if success:
        print("\nAUTOMATION COMPLETED SUCCESSFULLY! Bilingual PDF posted to Telegram.", flush=True)
    else:
        print(f"\n[ERROR] Telegram upload failed: {result}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    run_daily_automation()
