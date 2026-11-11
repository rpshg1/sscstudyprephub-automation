# 🚀 SSC Study Prep Hub - Daily Bilingual Current Affairs Automation

An automated daily cloud pipeline that fetches detailed Current Affairs (India, States, Cities, World, Economy, Science & Defence, Sports, Native PIB Hindi, and Bilingual Practice MCQs), builds a magazine-grade **Bilingual (English + हिंदी) PDF** with an invisible full-page YouTube redirect, and posts it automatically to Telegram channel `@sscstudyprephub` every morning — **without touching your laptop or GitHub daily**.

---

## 🌟 Key Features

1. **Zero Daily Touch & Daily Deduplication Guard**:
   - Scheduled via GitHub Actions cloud cron at **`3 2 * * *` UTC (~07:33–08:00 AM IST)** — off-peak minute avoids `:00`/`:30` runner congestion.
   - Built-in **IST Daily Deduplication** checks completed runs for today's Indian date so delayed triggers never post duplicate PDFs on the same day.
2. **Detailed, Multi-Category Bilingual Coverage (English + हिंदी)**:
   - National & Governance News (The Hindu, Indian Express, PIB)
   - States Current Affairs
   - Major Cities & Urban Development
   - International & World Affairs
   - Economy, Banking & Finance
   - Science, Technology & Defence
   - Sports & Championships
   - Native Hindi PIB & National Highlights
   - 5 Dynamic Bilingual Practice MCQs
   - Context-aware Bilingual Static GK & Exam Pointers
3. **Magazine-Grade PDF Rendering**:
   - Uses Headless Chrome/Chromium + `pypdf` for flawless Devanagari Hindi typography, crisp SVG icons, your embedded circular emblem logo (`logo.jpg`), and clean social branding (`@sscstudyprephub`).
   - Invisible full-page URI link overlay on every page redirecting to `https://www.youtube.com/@sscstudyprephub` (with zero visible "click anywhere" hints).

---

## 🛠️ Setup Checklist

1. **Telegram Bot (`@BotFather`)**:
   - Create a bot and copy its HTTP API Token.
   - Add the bot as **Administrator** in `@sscstudyprephub` with **Post Messages** permission.
2. **GitHub Repository Secret**:
   - Go to **Settings** -> **Secrets and variables** -> **Actions** in your repo.
   - Add `TELEGRAM_BOT_TOKEN`. (`TELEGRAM_CHAT_ID` defaults automatically to `@sscstudyprephub`).

---

## 💻 Local Testing

```bash
pip install -r requirements.txt
python main.py
```
