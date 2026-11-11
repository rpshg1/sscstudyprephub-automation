"""
Magazine-Grade Bilingual (English + Hindi) PDF Generator for SSC STUDY PREP HUB
- Renders HTML5 + CSS3 via Headless Chrome/Chromium/Edge for flawless Devanagari Hindi shaping & crisp SVG icons
- Embeds circular brand logo & socials (Telegram & YouTube @sscstudyprephub)
- Stamps an invisible full-page hyperlink annotation on every page redirecting to YouTube
- ZERO visible text mentioning clicking/tapping anywhere to redirect to YouTube
"""

import os
import sys
import html
import shutil
import base64
import datetime
import tempfile
import subprocess
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link

YOUTUBE_URL = "https://www.youtube.com/@sscstudyprephub"
TELEGRAM_HANDLE = "@sscstudyprephub"

SVG_ICONS = {
    "national": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18"/><path d="M5 21V7l8-4v18"/><path d="M19 21V11l-6-4"/><path d="M9 9v.01"/><path d="M9 12v.01"/><path d="M9 15v.01"/><path d="M9 18v.01"/></svg>',
    "states": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    "cities": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/><path d="M12 10h.01"/><path d="M12 14h.01"/><path d="M16 10h.01"/><path d="M16 14h.01"/><path d="M8 10h.01"/><path d="M8 14h.01"/></svg>',
    "international": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
    "economy": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
    "science_defence": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/></svg>',
    "sports": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>',
    "hindi": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8V6Z"/></svg>',
    "quiz": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>',
    "telegram": '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>',
    "youtube": '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>',
}

CATEGORY_META = [
    ("national", "NATIONAL & GOVERNANCE NEWS", "राष्ट्रीय एवं सरकारी समाचार", "#1e3a8a", "#eff6ff"),
    ("states", "STATES CURRENT AFFAIRS", "प्रमुख राज्य समाचार", "#047857", "#ecfdf5"),
    ("cities", "CITIES & URBAN UPDATES", "प्रमुख शहर एवं शहरी विकास", "#0f766e", "#f0fdfa"),
    ("international", "INTERNATIONAL & WORLD AFFAIRS", "अंतर्राष्ट्रीय समाचार", "#4338ca", "#eef2ff"),
    ("economy", "ECONOMY, BANKING & FINANCE", "अर्थव्यवस्था एवं बैंकिंग", "#b45309", "#fffbeb"),
    ("science_defence", "SCIENCE, TECH & DEFENCE", "विज्ञान, प्रौद्योगिकी एवं रक्षा", "#0369a1", "#f0f9ff"),
    ("sports", "SPORTS & CHAMPIONSHIPS", "खेल एवं प्रतियोगिताएं", "#be123c", "#fff1f2"),
]


def find_browser_executable():
    env_browser = os.getenv("CHROME_PATH", "").strip()
    if env_browser and os.path.exists(env_browser):
        return env_browser

    candidates = [
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
        "chrome",
        "msedge",
    ]
    for c in candidates:
        found = shutil.which(c)
        if found:
            return found

    win_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for p in win_paths:
        if os.path.exists(p):
            return p

    raise RuntimeError("No Chromium/Chrome/Edge executable found for PDF rendering.")


def esc(text):
    return html.escape(str(text or "")).strip()


def encode_logo_base64(logo_path):
    if not logo_path or not os.path.exists(logo_path):
        return ""
    with open(logo_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    ext = os.path.splitext(logo_path)[1].lower().lstrip(".")
    if ext == "jpg":
        ext = "jpeg"
    return f"data:image/{ext};base64,{b64}"


def build_html(data, logo_path):
    date_en = esc(data.get("date_en", datetime.datetime.now().strftime("%A, %d %B %Y")))
    date_hi = esc(data.get("date_hi", ""))
    logo_uri = encode_logo_base64(logo_path)
    categories = data.get("categories", {})
    hindi_special = data.get("hindi_special", [])
    quiz = data.get("daily_quiz", [])

    sections_html = []

    for cat_key, title_en, title_hi, accent_hex, tint_hex in CATEGORY_META:
        items = categories.get(cat_key, [])
        if not items:
            continue

        icon_svg = SVG_ICONS.get(cat_key, "")
        cards_html = []
        for idx, it in enumerate(items, 1):
            t_en = esc(it.get("title_en", ""))
            t_hi = esc(it.get("title_hi", ""))
            d_en = esc(it.get("detail_en", ""))
            d_hi = esc(it.get("detail_hi", ""))
            gk_en = esc(it.get("gk_en", ""))
            gk_hi = esc(it.get("gk_hi", ""))
            src = esc(it.get("source", ""))

            cards_html.append(f"""
            <div class="news-card" style="border-left: 3.5px solid {accent_hex};">
                <div class="card-top">
                    <span class="num-pill" style="background:{accent_hex};">{idx:02d}</span>
                    <div class="titles">
                        <div class="title-en">{t_en}</div>
                        <div class="title-hi">{t_hi}</div>
                    </div>
                    {f'<span class="src-tag">{src}</span>' if src else ''}
                </div>
                <div class="detail-en">{d_en}</div>
                <div class="detail-hi-box">
                    <span class="lang-badge">हिंदी विश्लेषण</span> {d_hi}
                </div>
                <div class="gk-box">
                    <div class="gk-label">STATIC GK & EXAM POINTER (परीक्षा उपयोगी तथ्य)</div>
                    <div class="gk-en"><b>EN:</b> {gk_en}</div>
                    <div class="gk-hi"><b>HI:</b> {gk_hi}</div>
                </div>
            </div>
            """)

        sections_html.append(f"""
        <section class="category-block">
            <div class="section-banner" style="background: {accent_hex};">
                <span class="sec-icon">{icon_svg}</span>
                <span class="sec-title-en">{title_en}</span>
                <span class="sec-sep">|</span>
                <span class="sec-title-hi">{title_hi}</span>
            </div>
            {''.join(cards_html)}
        </section>
        """)

    # Native Hindi PIB & National Special Section
    if hindi_special:
        hi_cards = []
        for idx, h_it in enumerate(hindi_special, 1):
            hi_cards.append(f"""
            <div class="news-card" style="border-left: 3.5px solid #9a3412;">
                <div class="card-top">
                    <span class="num-pill" style="background:#9a3412;">{idx:02d}</span>
                    <div class="titles">
                        <div class="title-hi" style="font-size:11.5pt; color:#0f172a;">{esc(h_it.get('title_hi'))}</div>
                    </div>
                    <span class="src-tag">{esc(h_it.get('source'))}</span>
                </div>
                <div class="detail-hi-box" style="margin-top:6px;">{esc(h_it.get('detail_hi'))}</div>
            </div>
            """)
        sections_html.append(f"""
        <section class="category-block">
            <div class="section-banner" style="background: #9a3412;">
                <span class="sec-icon">{SVG_ICONS['hindi']}</span>
                <span class="sec-title-en">PIB & NATIONAL HINDI HIGHLIGHTS</span>
                <span class="sec-sep">|</span>
                <span class="sec-title-hi">प्रमुख सरकारी व राष्ट्रीय हिंदी सुर्खियाँ</span>
            </div>
            {''.join(hi_cards)}
        </section>
        """)

    # Bilingual Practice MCQs
    if quiz:
        quiz_cards = []
        for q_idx, q in enumerate(quiz, 1):
            opts_en = q.get("opts_en", [])
            opts_hi = q.get("opts_hi", [])
            opts_html = []
            for o_idx, o_en in enumerate(opts_en):
                o_hi = opts_hi[o_idx] if o_idx < len(opts_hi) else ""
                opts_html.append(f"""
                <div class="opt-item">
                    <span>{esc(o_en)}</span>
                    {f'<span class="opt-hi">/ {esc(o_hi)}</span>' if o_hi else ''}
                </div>
                """)
            quiz_cards.append(f"""
            <div class="quiz-card">
                <div class="quiz-q-en">Q{q_idx}. {esc(q.get('q_en'))}</div>
                <div class="quiz-q-hi">प्र.{q_idx}. {esc(q.get('q_hi'))}</div>
                <div class="opts-grid">{''.join(opts_html)}</div>
                <div class="quiz-ans">
                    <b>Answer / उत्तर:</b> {esc(q.get('ans_en'))}
                    {f' <br><span class="ans-hi">{esc(q.get("ans_hi"))}</span>' if q.get("ans_hi") else ''}
                </div>
            </div>
            """)

        sections_html.append(f"""
        <section class="category-block">
            <div class="section-banner" style="background: #0f172a;">
                <span class="sec-icon">{SVG_ICONS['quiz']}</span>
                <span class="sec-title-en">DAILY EXAM BOOSTER — PRACTICE MCQS</span>
                <span class="sec-sep">|</span>
                <span class="sec-title-hi">दैनिक अभ्यास प्रश्नोत्तरी</span>
            </div>
            {''.join(quiz_cards)}
        </section>
        """)

    logo_img_tag = f'<img src="{logo_uri}" class="brand-logo" alt="SSC Study Prep Hub">' if logo_uri else ""

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  @page {{
    size: A4;
    margin: 15mm 11mm 15mm 11mm;
    @top-left {{
      content: "SSC STUDY PREP HUB  |  Bilingual Current Affairs";
      font-family: 'Plus Jakarta Sans', 'Noto Sans Devanagari', 'Nirmala UI', sans-serif;
      font-size: 7.5pt;
      color: #64748b;
    }}
    @top-right {{
      content: "Telegram & YouTube: @sscstudyprephub";
      font-family: 'Plus Jakarta Sans', 'Noto Sans Devanagari', 'Nirmala UI', sans-serif;
      font-size: 7.5pt;
      font-weight: 700;
      color: #b45309;
    }}
    @bottom-left {{
      content: "SSC STUDY PREP HUB  •  @sscstudyprephub";
      font-family: 'Plus Jakarta Sans', 'Noto Sans Devanagari', 'Nirmala UI', sans-serif;
      font-size: 7.5pt;
      color: #64748b;
    }}
    @bottom-right {{
      content: "Page " counter(page) " of " counter(pages);
      font-family: 'Plus Jakarta Sans', 'Noto Sans Devanagari', 'Nirmala UI', sans-serif;
      font-size: 7.5pt;
      font-weight: 700;
      color: #334155;
    }}
  }}
  @page :first {{
    margin-top: 10mm;
    @top-left {{ content: ""; }}
    @top-right {{ content: ""; }}
  }}
  * {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }}
  body {{
    font-family: 'Plus Jakarta Sans', 'Noto Sans Devanagari', 'Segoe UI', 'Nirmala UI', sans-serif;
    color: #1e293b;
    margin: 0;
    padding: 0;
    line-height: 1.45;
  }}

  /* Header Card */
  .brand-header {{
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border-radius: 10px;
    padding: 14px 18px;
    display: flex;
    align-items: center;
    gap: 16px;
    color: #ffffff;
    border-bottom: 4px solid #d97706;
    margin-bottom: 10px;
  }}
  .brand-logo {{
    width: 68px;
    height: 68px;
    border-radius: 50%;
    border: 2.5px solid #f59e0b;
    object-fit: cover;
    flex-shrink: 0;
  }}
  .brand-text {{
    flex: 1;
  }}
  .brand-title {{
    font-size: 19pt;
    font-weight: 800;
    letter-spacing: 0.5px;
    color: #ffffff;
    line-height: 1.15;
  }}
  .brand-subtitle {{
    font-size: 9.5pt;
    font-weight: 700;
    color: #fbbf24;
    margin-top: 2px;
  }}
  .brand-meta {{
    font-size: 8.5pt;
    color: #cbd5e1;
    margin-top: 4px;
  }}
  .exam-pills {{
    margin-top: 6px;
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }}
  .exam-pill {{
    background: rgba(245, 158, 11, 0.18);
    border: 1px solid rgba(251, 191, 36, 0.45);
    color: #fde68a;
    font-size: 7pt;
    font-weight: 700;
    padding: 1.5px 6px;
    border-radius: 4px;
  }}

  /* Social Bar */
  .social-bar {{
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
  }}
  .social-chip {{
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 7px;
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 8.5pt;
    font-weight: 700;
    color: #ffffff;
    text-decoration: none;
  }}
  .chip-tg {{ background: #0284c7; }}
  .chip-yt {{ background: #dc2626; }}

  /* Section Banner */
  .category-block {{
    margin-bottom: 14px;
  }}
  .section-banner {{
    color: #ffffff;
    padding: 6px 11px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    gap: 7px;
    margin-bottom: 8px;
    page-break-after: avoid;
  }}
  .sec-icon {{
    display: inline-flex;
    align-items: center;
  }}
  .sec-title-en {{
    font-size: 9.5pt;
    font-weight: 800;
    letter-spacing: 0.3px;
  }}
  .sec-sep {{ opacity: 0.6; font-size: 9pt; }}
  .sec-title-hi {{
    font-size: 9.5pt;
    font-weight: 700;
  }}

  /* News Cards */
  .news-card {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 9px 11px;
    margin-bottom: 8px;
    page-break-inside: avoid;
  }}
  .card-top {{
    display: flex;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 5px;
  }}
  .num-pill {{
    color: #ffffff;
    font-size: 8pt;
    font-weight: 800;
    padding: 2px 6px;
    border-radius: 4px;
    flex-shrink: 0;
    margin-top: 1px;
  }}
  .titles {{
    flex: 1;
  }}
  .title-en {{
    font-size: 10pt;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.3;
  }}
  .title-hi {{
    font-size: 9.5pt;
    font-weight: 700;
    color: #b45309;
    line-height: 1.35;
    margin-top: 2px;
  }}
  .src-tag {{
    font-size: 7pt;
    font-weight: 700;
    color: #64748b;
    background: #f1f5f9;
    padding: 2px 6px;
    border-radius: 4px;
    white-space: nowrap;
  }}
  .detail-en {{
    font-size: 8.6pt;
    color: #334155;
    line-height: 1.48;
    text-align: justify;
    margin-bottom: 6px;
  }}
  .detail-hi-box {{
    font-size: 8.6pt;
    color: #1e293b;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 5px;
    padding: 6px 8px;
    line-height: 1.5;
    text-align: justify;
    margin-bottom: 6px;
  }}
  .lang-badge {{
    display: inline-block;
    background: #0f172a;
    color: #fbbf24;
    font-size: 7pt;
    font-weight: 700;
    padding: 1px 5px;
    border-radius: 3px;
    margin-right: 4px;
  }}
  .gk-box {{
    background: #fffbeb;
    border-left: 3px solid #d97706;
    border-radius: 0 4px 4px 0;
    padding: 5px 8px;
    font-size: 7.8pt;
    line-height: 1.4;
  }}
  .gk-label {{
    font-size: 7.2pt;
    font-weight: 800;
    color: #92400e;
    letter-spacing: 0.2px;
    margin-bottom: 1.5px;
  }}
  .gk-en {{ color: #78350f; }}
  .gk-hi {{ color: #78350f; margin-top: 1px; }}

  /* Quiz Cards */
  .quiz-card {{
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 11px;
    margin-bottom: 8px;
    page-break-inside: avoid;
  }}
  .quiz-q-en {{
    font-size: 9pt;
    font-weight: 700;
    color: #0f172a;
  }}
  .quiz-q-hi {{
    font-size: 8.8pt;
    font-weight: 600;
    color: #334155;
    margin-top: 2px;
    margin-bottom: 5px;
  }}
  .opts-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4px 10px;
    font-size: 8pt;
    color: #475569;
    margin-bottom: 5px;
  }}
  .opt-hi {{ color: #64748b; }}
  .quiz-ans {{
    background: #ecfdf5;
    border-left: 3px solid #059669;
    padding: 4px 8px;
    font-size: 8pt;
    color: #065f46;
    border-radius: 0 4px 4px 0;
  }}
  .ans-hi {{ color: #047857; }}

  /* Final Social Card */
  .end-brand-box {{
    background: #0f172a;
    color: #f8fafc;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: center;
    border-top: 3px solid #d97706;
    margin-top: 10px;
    page-break-inside: avoid;
  }}
  .end-title {{
    font-size: 10pt;
    font-weight: 800;
    color: #fbbf24;
  }}
  .end-socials {{
    font-size: 8.5pt;
    color: #e2e8f0;
    margin-top: 3px;
  }}
</style>
</head>
<body>

  <div class="brand-header">
    {logo_img_tag}
    <div class="brand-text">
      <div class="brand-title">SSC STUDY PREP HUB</div>
      <div class="brand-subtitle">DAILY CURRENT AFFAIRS CAPSULE &bull; दैनिक करेंट अफेयर्स कैप्सूल (BILINGUAL)</div>
      <div class="brand-meta"><b>Date:</b> {date_en} &nbsp;|&nbsp; <b>दिनांक:</b> {date_hi}</div>
      <div class="exam-pills">
        <span class="exam-pill">SSC CGL</span>
        <span class="exam-pill">SSC CHSL</span>
        <span class="exam-pill">SSC MTS &amp; CPO</span>
        <span class="exam-pill">RAILWAY RRB</span>
        <span class="exam-pill">BANKING IBPS/SBI</span>
        <span class="exam-pill">STATE PSC</span>
        <span class="exam-pill">CDS &amp; NDA</span>
      </div>
    </div>
  </div>

  <div class="social-bar">
    <div class="social-chip chip-tg">{SVG_ICONS['telegram']} <span>Telegram Channel: @sscstudyprephub</span></div>
    <div class="social-chip chip-yt">{SVG_ICONS['youtube']} <span>YouTube Channel: @sscstudyprephub</span></div>
  </div>

  {''.join(sections_html)}

  <div class="end-brand-box">
    <div class="end-title">SSC STUDY PREP HUB — DAILY BILINGUAL CURRENT AFFAIRS</div>
    <div class="end-socials">
      Telegram: <b>t.me/sscstudyprephub (@sscstudyprephub)</b> &nbsp;&bull;&nbsp;
      YouTube: <b>youtube.com/@sscstudyprephub (@sscstudyprephub)</b>
    </div>
  </div>

</body>
</html>"""
    return full_html


def stamp_full_page_invisible_link(raw_pdf_path, final_pdf_path, url=YOUTUBE_URL):
    reader = PdfReader(raw_pdf_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
        w = float(page.mediabox.width)
        h = float(page.mediabox.height)
        ann = Link(rect=(0, 0, w, h), url=url)
        writer.add_annotation(page_number=len(writer.pages) - 1, annotation=ann)

    with open(final_pdf_path, "wb") as f:
        writer.write(f)
    return len(writer.pages)


def generate_pdf(current_affairs_data, output_pdf_path, logo_image_path):
    browser = find_browser_executable()
    html_content = build_html(current_affairs_data, logo_image_path)

    with tempfile.TemporaryDirectory() as tmpdir:
        html_path = os.path.join(tmpdir, "capsule.html")
        raw_pdf_path = os.path.join(tmpdir, "capsule_raw.pdf")

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        cmd = [
            browser,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            f"--print-to-pdf={raw_pdf_path}",
            "--no-pdf-header-footer",
            "--virtual-time-budget=5000",
            html_path,
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        pages = stamp_full_page_invisible_link(raw_pdf_path, output_pdf_path, YOUTUBE_URL)

    size = os.path.getsize(output_pdf_path)
    print(f"Generated Bilingual Branded PDF: {output_pdf_path} ({pages} pages, {size} bytes)")
    return output_pdf_path


if __name__ == "__main__":
    from fetch_news import fetch_all_current_affairs
    data = fetch_all_current_affairs()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_file = os.path.join(base_dir, "logo.jpg")
    ist_today = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)).strftime("%Y_%m_%d")
    out_pdf = os.path.join(base_dir, f"SSC_Current_Affairs_{ist_today}.pdf")
    generate_pdf(data, out_pdf, logo_file)
