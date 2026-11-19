# 🚀 SSC Study Prep Hub — Daily Bilingual Current Affairs Automation

[![Daily Current Affairs Automation](https://github.com/rpshg1/sscstudyprephub-automation/actions/workflows/daily_current_affairs.yml/badge.svg)](https://github.com/rpshg1/sscstudyprephub-automation/actions/workflows/daily_current_affairs.yml)
[![Telegram Channel](https://img.shields.io/badge/Telegram-@sscstudyprephub-2CA5E0?logo=telegram&logoColor=white)](https://t.me/sscstudyprephub)
[![YouTube Channel](https://img.shields.io/badge/YouTube-@sscstudyprephub-FF0000?logo=youtube&logoColor=white)](https://youtube.com/@sscstudyprephub)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An automated daily cloud pipeline that collects verified Current Affairs (National, States, Major Cities, World, Economy & Banking, Science & Defence, Sports, and Native Hindi PIB updates), formats them with relevant thumbnail visuals, generates 5 bilingual practice MCQs with explanations, compiles a magazine-grade **Bilingual (English + हिंदी) PDF**, and uploads it directly to the Telegram channel [**@sscstudyprephub**](https://t.me/sscstudyprephub) every morning — **100% automated and zero-touch**.

---

## ✨ Key Features

1. **Comprehensive Multi-Source News Coverage (English + हिंदी)**:
   - **National & Governance:** The Hindu, Indian Express, Press Information Bureau (PIB).
   - **States & Major Cities:** Regional governance and urban development initiatives.
   - **International Affairs:** Global summits, bilateral ties, and multilateral organizations.
   - **Economy, Banking & Finance:** RBI policies, fiscal indices, and market updates.
   - **Science, Tech & Defence:** ISRO missions, DRDO trials, defense procurements.
   - **Sports & Championships:** National and international tournaments, awards, and records.
   - **PIB Hindi Special:** Native Hindi government releases from Amar Ujala and PIB.
   - **Dynamic Practice MCQs:** 5 bilingual exam-oriented multiple-choice questions with answers.

2. **Magazine-Grade Branded PDF Engine**:
   - Built on Headless Chromium/Chrome for native Devanagari Hindi text shaping and crisp vector icons.
   - High-contrast gold & dark design scheme with official brand emblem (`logo.jpg`).
   - Clean category badges, visual thumbnail cards, and exam-focused Static GK callouts.
   - Integrated full-page invisible hyperlink overlay pointing to [YouTube channel `@sscstudyprephub`](https://www.youtube.com/@sscstudyprephub) on every page.

3. **Intelligent Cloud Orchestration**:
   - **Zero Daily Touch:** Runs entirely on GitHub Actions cloud infrastructure.
   - **Universal IST Deduplication:** Checks for completed runs on the current Indian date to ensure exactly one PDF is published per day, even if multiple retries or delayed cron events occur.
   - **API & Webhook Trigger Support:** Accepts `workflow_dispatch` and `repository_dispatch` for exact second-level triggers via free external cron schedulers (such as cron-job.org).

---

## ⚙️ Architecture

```
                               ┌────────────────────────┐
                               │  RSS Feeds (PIB, The   │
                               │ Hindu, Indian Express) │
                               └───────────┬────────────┘
                                           │
                                           ▼
┌───────────────────────┐      ┌────────────────────────┐
│  Scheduled Cloud Cron │      │  fetch_news.py         │
│  or External Webhook  ├─────►│  • Full text extract   │
└───────────────────────┘      │  • News thumbnail grab │
                               │  • Bilingual translate │
                               │  • 5 Practice MCQs     │
                               └───────────┬────────────┘
                                           │
                                           ▼
                               ┌────────────────────────┐
                               │  generate_pdf.py       │
                               │  • HTML5 + CSS3 Grid   │
                               │  • Headless Chrome PDF │
                               │  • pypdf Link Overlay  │
                               └───────────┬────────────┘
                                           │
                                           ▼
                               ┌────────────────────────┐
                               │  upload_telegram.py    │
                               │  • Telegram Bot API    │
                               │  • Target: Channel     │
                               │    @sscstudyprephub    │
                               └────────────────────────┘
```

---

## 🚀 Repository Setup

### 1. Telegram Channel & Bot
1. Open [@BotFather](https://t.me/BotFather) on Telegram and create a bot (`/newbot`).
2. Copy the HTTP API token provided.
3. Add your bot as an **Administrator** in your Telegram channel ([@sscstudyprephub](https://t.me/sscstudyprephub)) with permission to **Post Messages**.

### 2. GitHub Secrets Configuration
In your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions** and add:

| Secret Name | Required | Description |
| :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | **Yes** | Your Telegram bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Optional | Target channel (defaults to `@sscstudyprephub`) |
| `TRANSLATOR_EMAIL` | Optional | Your email for increased MyMemory translation limits |
| `GEMINI_API_KEY` | Optional | Google AI Studio API key (if using AI enhancements) |

---

## ⏰ Precision 08:00 AM IST Scheduling (Optional External Webhook)

Because GitHub Actions free scheduled cron queues can experience congestion during global peak windows, you can trigger the workflow at **exactly 08:00 AM IST sharp** using a free webhook:

1. Generate a GitHub Personal Access Token at [GitHub Settings](https://github.com/settings/tokens/new?scopes=repo,workflow).
2. Create a free recurring job on [cron-job.org](https://console.cron-job.org):
   - **URL:** `https://api.github.com/repos/rpshg1/sscstudyprephub-automation/dispatches`
   - **Schedule:** Every day at `08:00` (Timezone: `Asia/Kolkata`)
   - **Method:** `POST`
   - **Headers:**
     - `Authorization`: `Bearer YOUR_GITHUB_TOKEN`
     - `Accept`: `application/vnd.github.v3+json`
     - `User-Agent`: `cron-job-org`
   - **Request Body:**
     ```json
     {"event_type": "daily_trigger"}
     ```

---

## 💻 Local Development

```bash
# Clone the repository
git clone https://github.com/rpshg1/sscstudyprephub-automation.git
cd sscstudyprephub-automation

# Install dependencies
pip install -r requirements.txt

# Run full pipeline locally
python main.py
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
