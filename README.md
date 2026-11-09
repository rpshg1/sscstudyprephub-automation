# 🚀 SSC Study Prep Hub - Daily Current Affairs Automation

An automated daily pipeline that fetches fresh Current Affairs (India, States, World, Economy, Sports, Sci-Tech, MCQs), designs a branded PDF with an invisible full-page YouTube channel redirect, and automatically uploads it to Telegram channel `@sscstudyprephub` every morning without touching your laptop or GitHub daily!

---

## 🌟 Key Features

1. **Zero Daily Touch (100% Cloud Autonomous)**:
   - Powered by GitHub Actions cron. Runs on cloud servers every morning at **08:00 AM IST (02:30 UTC)**.
   - You **never** need to keep your laptop awake or open GitHub daily. Set it up once and it runs 365 days a year automatically.
2. **Comprehensive Current Affairs Coverage**:
   - 🇮🇳 National & Governance News
   - 🏛️ State-Wise Highlights & Schemes
   - 🌐 International & Global Affairs
   - 💰 Economy, Banking & RBI Policy
   - 🚀 Science, Technology & Defence (ISRO, DRDO)
   - 🏆 Sports, Appointments & Awards
   - 🎯 Daily Practice MCQs / Exam Booster
3. **Professional Exam-Grade PDF**:
   - Branded with your custom logo (`logo.jpg`) and gold/dark theme.
   - Social ribbons for Telegram (`@sscstudyprephub`) & YouTube (`@sscstudyprephub`).
   - Dynamic page numbers (`Page X of Y`).
4. **Full-Page Invisible Hyperlink**:
   - Every single page of the PDF has an invisible link overlay.
   - Tapping anywhere on any page in the PDF instantly redirects students to your YouTube channel: `https://www.youtube.com/@sscstudyprephub`.

---

## 🛠️ Step 1: Telegram Bot Setup (Takes 2 Minutes)

1. Open Telegram and search for **`@BotFather`**.
2. Send `/newbot` and follow the prompts:
   - Choose a bot name (e.g., `SSC Prep Hub Bot`)
   - Choose a username (e.g., `sscstudyprephub_bot`)
3. Copy the **HTTP API Token** provided by BotFather (looks like `782348234:AAH...`).
4. Open your Telegram Channel **`@sscstudyprephub`**:
   - Go to Channel Info -> **Administrators** -> **Add Admin**.
   - Search for your bot username and add it as an Administrator.
   - Grant it permission to **Post Messages**.

---

## ☁️ Step 2: Push to GitHub for 100% Cloud Automation

To make this run daily without touching your laptop or GitHub:

1. Create a new repository named **`sscstudyprephub-automation`** on [GitHub](https://github.com/new) (can be Private or Public).
2. Push your committed code from this folder:
   ```bash
   git push -u origin main
   ```
3. Add your Telegram Bot Token to GitHub Secrets:
   - In your GitHub repo, go to **Settings** -> **Secrets and variables** -> **Actions**.
   - Click **New repository secret**:
     - Name: `TELEGRAM_BOT_TOKEN`
     - Value: *(Paste your token from @BotFather)*
     - Click **Add secret**.
   - Add another secret (optional):
     - Name: `TELEGRAM_CHAT_ID`
     - Value: `@sscstudyprephub`
   - *(Optional AI Enhancement)*:
     - Name: `GEMINI_API_KEY`
     - Value: *(Your free Gemini key from Google AI Studio, if you want AI-generated MCQs)*

🎉 **That's it!** GitHub Actions will now automatically run the workflow `.github/workflows/daily_current_affairs.yml` every day at **08:00 AM IST**. You can also test it immediately by opening the **Actions** tab in your repo and clicking **Run workflow**.

---

## 💻 Optional: Local Testing on Your Laptop

If you ever want to test it locally on your computer:
1. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
2. Put your `TELEGRAM_BOT_TOKEN` inside `.env`.
3. Run:
   ```bash
   python main.py
   ```
The PDF will be generated and posted straight to `@sscstudyprephub`!
