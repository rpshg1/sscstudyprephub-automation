"""
Comprehensive Bilingual (English + Hindi) Daily Current Affairs Fetcher
- Uses direct, reliable Indian & global publisher RSS feeds (The Hindu, Indian Express, PIB, Amar Ujala)
- Parallel full-article extraction via JSON-LD / HTML article body
- Parallel Bilingual English->Hindi translation via MyMemory API (50k/day free) with safe fallbacks
- Enriches items with context-aware Static GK Exam Pointers & Dynamic Bilingual MCQs
"""

import os
import re
import json
import html
import datetime
import feedparser
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

CATEGORY_FEEDS = {
    "national": [
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
        "https://indianexpress.com/section/india/feed/",
    ],
    "states": [
        "https://www.thehindu.com/news/national/other-states/feeder/default.rss",
        "https://indianexpress.com/section/india/feed/",
    ],
    "cities": [
        "https://indianexpress.com/section/cities/feed/",
        "https://www.thehindu.com/news/cities/feeder/default.rss",
    ],
    "international": [
        "https://www.thehindu.com/news/international/feeder/default.rss",
        "https://indianexpress.com/section/world/feed/",
    ],
    "economy": [
        "https://www.thehindu.com/business/Economy/feeder/default.rss",
        "https://indianexpress.com/section/business/feed/",
    ],
    "science_defence": [
        "https://www.thehindu.com/sci-tech/science/feeder/default.rss",
        "https://indianexpress.com/section/technology/science/feed/",
    ],
    "sports": [
        "https://www.thehindu.com/sport/feeder/default.rss",
        "https://indianexpress.com/section/sports/feed/",
    ],
}

STATIC_GK_MAP = [
    (["RBI", "Reserve Bank"], "RBI HQ: Mumbai | Established: 1 April 1935 (RBI Act 1934) | Nationalized: 1949", "आरबीआई मुख्यालय: मुंबई | स्थापना: 1 अप्रैल 1935 | राष्ट्रीयकरण: 1949"),
    (["SEBI"], "SEBI HQ: Mumbai | Statutory status: SEBI Act 1992 | Regulates Indian capital markets", "सेबी मुख्यालय: मुंबई | वैधानिक दर्जा: सेबी अधिनियम 1992 | पूंजी बाजार नियामक"),
    (["ISRO"], "ISRO HQ: Bengaluru | Founded: 15 Aug 1969 | Launch Site: Satish Dhawan Space Centre, Sriharikota (AP)", "इसरो मुख्यालय: बेंगलुरु | स्थापना: 15 अगस्त 1969 | प्रक्षेपण केंद्र: श्रीहरिकोटा (आंध्र प्रदेश)"),
    (["DRDO"], "DRDO HQ: New Delhi | Established: 1958 | Works under Ministry of Defence", "डीआरडीओ मुख्यालय: नई दिल्ली | स्थापना: 1958 | रक्षा मंत्रालय के अधीन कार्यरत"),
    (["NITI Aayog"], "NITI Aayog Formed: 1 Jan 2015 (replaced Planning Commission) | Ex-officio Chairperson: Prime Minister", "नीति आयोग गठन: 1 जनवरी 2015 | पदेन अध्यक्ष: भारत के प्रधानमंत्री"),
    (["Supreme Court", "CJI"], "Supreme Court of India established: 28 Jan 1950 | Articles 124–147 of the Constitution", "भारत का सर्वोच्च न्यायालय स्थापना: 28 जनवरी 1950 | संविधान के अनुच्छेद 124–147"),
    (["Election Commission", "ECI"], "Election Commission of India: Constitutional body under Article 324 | Founded: 25 Jan 1950 (National Voters' Day)", "भारत निर्वाचन आयोग: अनुच्छेद 324 के तहत संवैधानिक निकाय | स्थापना: 25 जनवरी 1950"),
    (["Tamil Nadu", "Chennai"], "Tamil Nadu Capital: Chennai | Key GI/Sites: Brihadeeswarar Temple (UNESCO), Nilgiri Biosphere", "तमिलनाडु राजधानी: चेन्नई | प्रमुख स्थल: बृहदेश्वर मंदिर (यूनेस्को), नीलगिरि बायोस्फीयर"),
    (["Maharashtra", "Mumbai", "Pune"], "Maharashtra Capital: Mumbai | Formed: 1 May 1960 | UNESCO Sites: Ajanta, Ellora, Elephanta Caves", "महाराष्ट्र राजधानी: मुंबई | स्थापना: 1 मई 1960 | यूनेस्को स्थल: अजंता-एलोरा की गुफाएं"),
    (["Uttar Pradesh", "Lucknow", "Varanasi", "Ayodhya", "Noida"], "Uttar Pradesh Capital: Lucknow | State Animal: Barasingha | Houses highest Lok Sabha seats (80)", "उत्तर प्रदेश राजधानी: लखनऊ | राजकीय पशु: बारहसिंगा | सर्वाधिक लोकसभा सीटें (80)"),
    (["Delhi", "New Delhi"], "NCT of Delhi: Union Territory with Legislature (69th Amendment Act, 1991, Article 239AA)", "राष्ट्रीय राजधानी क्षेत्र दिल्ली: विधानसभा सहित केंद्र शासित प्रदेश (69वां संशोधन, अनुच्छेद 239AA)"),
    (["Gurugram", "Haryana"], "Haryana Capital: Chandigarh | International Solar Alliance (ISA) HQ is located in Gurugram", "हरियाणा राजधानी: चंडीगढ़ | अंतर्राष्ट्रीय सौर गठबंधन (ISA) का मुख्यालय गुरुग्राम में स्थित है"),
    (["Karnataka", "Bengaluru"], "Karnataka Capital: Bengaluru (Silicon Valley of India) | Famous Sites: Hampi, Pattadakal", "कर्नाटक राजधानी: बेंगलुरु (भारत की सिलिकॉन वैली) | प्रमुख यूनेस्को स्थल: हम्पी, पट्टदकल"),
    (["Kerala", "Thiruvananthapuram", "Kochi"], "Kerala Capital: Thiruvananthapuram | First 100% literate state | Silent Valley National Park", "केरल राजधानी: तिरुवनंतपुरम | साइलेंट वैली राष्ट्रीय उद्यान केरल में स्थित है"),
    (["Manipur", "Imphal"], "Manipur Capital: Imphal | Keibul Lamjao (World's only floating National Park) on Loktak Lake", "मणिपुर राजधानी: इम्फाल | लोकटक झील पर विश्व का एकमात्र तैरता राष्ट्रीय उद्यान 'कीबुल लामजाओ' स्थित है"),
    (["Assam", "Guwahati"], "Assam Capital: Dispur | Kaziranga & Manas National Parks (UNESCO) | Majuli (World's largest river island)", "असम राजधानी: दिसपुर | काजीरंगा व मानस राष्ट्रीय उद्यान | माजुली विश्व का सबसे बड़ा नदी द्वीप"),
    (["Gujarat", "Ahmedabad", "Gandhinagar"], "Gujarat Capital: Gandhinagar | Longest coastline among Indian states (~1,600 km) | Gir National Park", "गुजरात राजधानी: गांधीनगर | भारत में सबसे लंबी तटरेखा वाला राज्य | गिर राष्ट्रीय उद्यान"),
    (["Rajasthan", "Jaipur"], "Rajasthan Capital: Jaipur (Pink City - UNESCO) | Largest Indian state by area | Thar Desert", "राजस्थान राजधानी: जयपुर (पिंक सिटी - यूनेस्को) | क्षेत्रफल की दृष्टि से भारत का सबसे बड़ा राज्य"),
    (["Bihar", "Patna"], "Bihar Capital: Patna | Valmiki National Park | Bodh Gaya Mahabodhi Temple (UNESCO)", "बिहार राजधानी: पटना | वाल्मीकि राष्ट्रीय उद्यान | बोधगया महाबोधि मंदिर (यूनेस्को)"),
    (["West Bengal", "Kolkata"], "West Bengal Capital: Kolkata | Sundarbans National Park (World's largest mangrove forest)", "पश्चिम बंगाल राजधानी: कोलकाता | सुंदरबन राष्ट्रीय उद्यान (विश्व का सबसे बड़ा मैंग्रोव वन)"),
    (["Odisha", "Bhubaneswar"], "Odisha Capital: Bhubaneswar | Chilika Lake (Largest brackish water lagoon in Asia) | Konark Sun Temple", "ओडिशा राजधानी: भुवनेश्वर | चिल्का झील (एशिया की सबसे बड़ी खारे पानी की झील) | कोणार्क सूर्य मंदिर"),
    (["UN", "United Nations", "UNESCO", "WHO", "UNICEF"], "United Nations Founded: 24 Oct 1945 | HQ: New York | 193 Member States | India is a founding member", "संयुक्त राष्ट्र स्थापना: 24 अक्टूबर 1945 | मुख्यालय: न्यूयॉर्क | भारत संस्थापक सदस्य है"),
    (["IMF", "World Bank"], "IMF & World Bank HQ: Washington, D.C. | Formed at Bretton Woods Conference (1944)", "आईएमएफ और विश्व बैंक मुख्यालय: वाशिंगटन डी.सी. | स्थापना: ब्रेटन वुड्स सम्मेलन (1944)"),
    (["IPL", "BCCI", "ICC", "Cricket"], "BCCI HQ: Mumbai (Est. 1928) | ICC HQ: Dubai, UAE (Est. 1909)", "बीसीसीआई मुख्यालय: मुंबई (स्थापना: 1928) | आईसीसी मुख्यालय: दुबई, यूएई (स्थापना: 1909)"),
    (["Chess", "FIDE"], "FIDE (International Chess Federation) HQ: Lausanne, Switzerland | Founded: 1924", "फिडे (अंतर्राष्ट्रीय शतरंज महासंघ) मुख्यालय: लुसाने, स्विट्जरलैंड | स्थापना: 1924"),
    (["Cabinet", "Ministry", "Union", "Parliament", "PIB"], "Parliament of India (Article 79): President, Lok Sabha (Lower House) & Rajya Sabha (Upper House)", "भारतीय संसद (अनुच्छेद 79): राष्ट्रपति, लोकसभा और राज्यसभा से मिलकर बनती है"),
]


def clean_text(raw):
    if not raw:
        return ""
    txt = re.sub(r"<[^>]+>", " ", str(raw))
    txt = html.unescape(txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def translate_chunk(chunk, email="rupesh907.rg@gmail.com"):
    if not chunk:
        return ""
    try:
        r = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": chunk, "langpair": "en|hi", "de": email},
            timeout=6,
        )
        if r.status_code == 200:
            res_txt = r.json().get("responseData", {}).get("translatedText", "")
            if res_txt and "MYMEMORY WARNING" not in res_txt and "QUERY LENGTH LIMIT" not in res_txt:
                return html.unescape(res_txt).strip()
    except Exception:
        pass
    return chunk


def translate_en_to_hi(text, email="rupesh907.rg@gmail.com"):
    if not text or not text.strip():
        return ""
    text = text.strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    cur = ""
    for s in sentences:
        if len(cur) + len(s) + 1 <= 430:
            cur = f"{cur} {s}".strip()
        else:
            if cur:
                chunks.append(cur)
            if len(s) > 430:
                for idx in range(0, len(s), 430):
                    chunks.append(s[idx:idx + 430])
                cur = ""
            else:
                cur = s
    if cur:
        chunks.append(cur)

    translated_parts = [translate_chunk(c, email=email) for c in chunks]
    return " ".join(translated_parts).strip()


def extract_article_body(url, fallback_summary=""):
    if not url:
        return fallback_summary

    boilerplate_phrases = (
        "subscribe", "sign up", "read more", "also read", "copyright",
        "all rights reserved", "follow us", "download our app", "click here",
        "comments have been", "published -", "updated -", "newsletter",
        "premium stories", "account subscription", "terms of use", "privacy policy"
    )

    extracted = ""
    try:
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            for sc in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(sc.string or "{}")
                    if isinstance(data, list):
                        data = data[0]
                    if isinstance(data, dict):
                        body = data.get("articleBody", "")
                        if body and len(body) > 120:
                            extracted = clean_text(body)
                            break
                except Exception:
                    continue

            if not extracted:
                selectors = [
                    "div.articlebodycontent p",
                    "div[id^='content-body-'] p",
                    "div.story_details p",
                    "div.full-details p",
                    "div.innner-page-main-about-us-content-right-part p",
                    "article p",
                ]
                paras = []
                for sel in selectors:
                    found = soup.select(sel)
                    if found:
                        for p in found:
                            t = clean_text(p.get_text(" ", strip=True))
                            low = t.lower()
                            if len(t) > 55 and not any(bp in low for bp in boilerplate_phrases):
                                paras.append(t)
                        if len(paras) >= 2:
                            break
                if paras:
                    extracted = " ".join(paras)
    except Exception:
        pass

    text_to_use = extracted if len(extracted) > len(fallback_summary) else fallback_summary
    text_to_use = clean_text(text_to_use)
    # Remove inline URLs, The Hindu 'storyline 1' / 'story ' markers, and '| Explained' snippets
    text_to_use = re.sub(r"https?://\S+", "", text_to_use)
    text_to_use = re.sub(r"\bstoryline\s*\d+\b", "", text_to_use, flags=re.IGNORECASE)
    text_to_use = re.sub(r"\s*\|\s*Explained[^.?!]*", "", text_to_use, flags=re.IGNORECASE)
    text_to_use = re.sub(r"^(?:NEW DELHI|DELHI|MUMBAI|CHENNAI|BENGALURU|KOLKATA|GUWAHATI|CHANDIGARH|LONDON|LAHORE|BARCELONA|MELBOURNE|WASHINGTON)\s*[:\-]?\s+", "", text_to_use, flags=re.IGNORECASE)
    text_to_use = re.sub(r"\s+", " ", text_to_use).strip()

    sentences = re.split(r"(?<=[.!?])\s+", text_to_use)
    selected = []
    total_len = 0
    for s in sentences:
        s = s.strip()
        if len(s) < 25:
            continue
        if any(bp in s.lower() for bp in boilerplate_phrases):
            continue
        selected.append(s)
        total_len += len(s)
        if len(selected) >= 4 or total_len >= 540:
            break

    if not selected:
        return fallback_summary or text_to_use[:450]

    return " ".join(selected)


def derive_exam_pointer(title, detail, category):
    combined = f"{title} {detail}"
    for keywords, en_gk, hi_gk in STATIC_GK_MAP:
        for kw in keywords:
            # Skip city/state GK pointers for non-domestic categories unless clearly in headline
            if kw in ("Delhi", "New Delhi", "Mumbai", "Chennai", "Bengaluru", "Kolkata", "London") and category in ("economy", "international", "sports"):
                continue
            flags = 0 if kw.isupper() else re.IGNORECASE
            if re.search(rf"\b{re.escape(kw)}\b", combined, flags):
                return en_gk, hi_gk

    defaults = {
        "national": (
            "Relevant for Polity, Government Schemes & National Governance questions in SSC & UPSC Prelims.",
            "एसएससी और यूपीएससी प्रारंभिक परीक्षा में राजव्यवस्था, सरकारी योजनाओं और राष्ट्रीय शासन से जुड़े प्रश्नों के लिए उपयोगी।"
        ),
        "states": (
            "Important for State PSCs & Regional General Awareness (Chief Ministers, Governors & State Schemes).",
            "राज्य पीसीएस और क्षेत्रीय सामान्य ज्ञान (मुख्यमंत्री, राज्यपाल एवं राज्य योजनाएं) के लिए अत्यंत महत्वपूर्ण।"
        ),
        "cities": (
            "Key for Smart Cities Mission, Urban Infrastructure & Municipal Governance current affairs.",
            "स्मार्ट सिटी मिशन, शहरी बुनियादी ढांचे और नगर प्रशासन से जुड़े करेंट अफेयर्स के लिए महत्वपूर्ण।"
        ),
        "international": (
            "Important for International Relations, Bilateral Treaties, Summits & Global Indexes.",
            "अंतर्राष्ट्रीय संबंध, द्विपक्षीय समझौतों, शिखर सम्मेलनों और वैश्विक सूचकांकों के लिए महत्वपूर्ण।"
        ),
        "economy": (
            "High-yield for Banking Awareness (IBPS/SBI), Fiscal Policy, GDP & Monetary updates.",
            "बैंकिंग जागरूकता (IBPS/SBI), राजकोषीय नीति, जीडीपी और मौद्रिक अपडेट के लिए अत्यधिक उपयोगी।"
        ),
        "science_defence": (
            "Crucial for Science & Technology, Space Missions, Defence Exercises & Innovations.",
            "विज्ञान एवं प्रौद्योगिकी, अंतरिक्ष मिशन, रक्षा अभ्यास और नवाचार से जुड़े प्रश्नों के लिए महत्वपूर्ण।"
        ),
        "sports": (
            "Essential for Sports Awards, Championship Winners, Venues & Governing Bodies.",
            "खेल पुरस्कार, चैंपियनशिप विजेता, आयोजन स्थल और खेल महासंघों से जुड़े प्रश्नों के लिए आवश्यक।"
        ),
    }
    return defaults.get(category, defaults["national"])


def enrich_single_item(raw_item):
    title = raw_item["title_en"]
    link = raw_item["link"]
    raw_summary = raw_item["raw_summary"]
    cat = raw_item["category"]

    detail_en = extract_article_body(link, fallback_summary=raw_summary)
    if not detail_en or len(detail_en) < 40:
        detail_en = raw_summary or title

    gk_en, gk_hi = derive_exam_pointer(title, detail_en, cat)
    title_hi = translate_en_to_hi(title)
    detail_hi = translate_en_to_hi(detail_en)

    return {
        "title_en": title,
        "title_hi": title_hi,
        "detail_en": detail_en,
        "detail_hi": detail_hi,
        "gk_en": gk_en,
        "gk_hi": gk_hi,
        "source": raw_item["source"],
    }


def collect_raw_entries(feed_urls, category, seen_titles, limit=3):
    raw_list = []
    for f_url in feed_urls:
        if len(raw_list) >= limit:
            break
        try:
            r = requests.get(f_url, headers=HEADERS, timeout=8)
            if r.status_code != 200:
                continue
            feed = feedparser.parse(r.content)
            for entry in feed.entries:
                if len(raw_list) >= limit:
                    break
                title = clean_text(entry.get("title", ""))
                if not title or len(title) < 15:
                    continue
                norm_title = re.sub(r"[^a-z0-9]", "", title.lower())[:45]
                if norm_title in seen_titles:
                    continue
                seen_titles.add(norm_title)
                raw_summary = clean_text(entry.get("summary", ""))
                src = "PIB" if "pib.gov.in" in f_url else ("The Hindu" if "thehindu" in f_url else "Indian Express")
                raw_list.append({
                    "title_en": title,
                    "raw_summary": raw_summary,
                    "link": entry.get("link", ""),
                    "category": category,
                    "source": src,
                })
        except Exception as e:
            print(f"[WARN] Feed error ({f_url}): {e}", flush=True)
    return raw_list


def build_dynamic_bilingual_quiz(all_categories):
    quiz = []
    nat = all_categories.get("national", [])
    eco = all_categories.get("economy", [])
    sci = all_categories.get("science_defence", [])
    spt = all_categories.get("sports", [])
    wld = all_categories.get("international", [])
    sts = all_categories.get("states", [])

    if nat:
        t = nat[0]["title_en"]
        quiz.append({
            "q_en": f"Regarding today's national highlight '{t[:85]}...', which constitutional body governs India's Union Executive policy?",
            "opts_en": ["A) Union Council of Ministers", "B) Inter-State Judicial Council", "C) Zonal Finance Tribunal", "D) Municipal Election Commission"],
            "ans_en": "A) Union Council of Ministers (Articles 74 & 75 of Indian Constitution)"
        })
    if sts:
        t = sts[0]["title_en"]
        quiz.append({
            "q_en": f"In context of state news ('{t[:85]}...'), which Part of the Indian Constitution defines State Executives & Legislatures?",
            "opts_en": ["A) Part IV (Articles 36–51)", "B) Part VI (Articles 152–237)", "C) Part IX (Articles 243–243O)", "D) Part XI (Articles 245–263)"],
            "ans_en": "B) Part VI (Articles 152–237) covers State Executive, Legislature & High Courts."
        })
    if eco:
        t = eco[0]["title_en"]
        quiz.append({
            "q_en": f"Connected to today's economy update ('{t[:85]}...'), when was the Reserve Bank of India (RBI) established?",
            "opts_en": ["A) 1935 (RBI Act 1934)", "B) 1949 (Banking Act)", "C) 1955 (SBI Act)", "D) 1992 (SEBI Act)"],
            "ans_en": "A) 1 April 1935 under the RBI Act, 1934 (Hilton Young Commission)."
        })
    if sci:
        t = sci[0]["title_en"]
        quiz.append({
            "q_en": f"In view of science developments ('{t[:85]}...'), where is ISRO's Satish Dhawan Space Centre located?",
            "opts_en": ["A) Thiruvananthapuram, Kerala", "B) Sriharikota, Andhra Pradesh", "C) Bengaluru, Karnataka", "D) Balasore, Odisha"],
            "ans_en": "B) Sriharikota, Tirupati district, Andhra Pradesh."
        })
    if spt or wld:
        item = spt[0] if spt else wld[0]
        t = item["title_en"]
        quiz.append({
            "q_en": f"With reference to '{t[:85]}...', where are the headquarters of IOC (Olympic Committee) and FIDE located?",
            "opts_en": ["A) Geneva, Switzerland", "B) Lausanne, Switzerland", "C) London, UK", "D) Paris, France"],
            "ans_en": "B) Lausanne, Switzerland (Olympic Capital)."
        })

    def translate_q(q):
        q["q_hi"] = translate_en_to_hi(q["q_en"])
        q["opts_hi"] = [translate_en_to_hi(o) for o in q["opts_en"]]
        q["ans_hi"] = translate_en_to_hi(q["ans_en"])
        return q

    with ThreadPoolExecutor(max_workers=4) as ex:
        quiz = list(ex.map(translate_q, quiz))
    return quiz


def fetch_native_hindi_pib_highlight(limit=3):
    hindi_items = []
    seen_hi = set()
    sources = [
        ("PIB हिंदी", "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=2&Regid=3"),
        ("अमर उजाला (राष्ट्रीय)", "https://www.amarujala.com/rss/india-news.xml"),
    ]
    for src_name, url in sources:
        if len(hindi_items) >= limit:
            break
        try:
            r = requests.get(url, headers=HEADERS, timeout=8)
            if r.status_code != 200:
                continue
            feed = feedparser.parse(r.content)
            added_from_src = 0
            for e in feed.entries:
                if len(hindi_items) >= limit or added_from_src >= 2:
                    break
                title_hi = clean_text(e.get("title", ""))
                if not title_hi or title_hi[:45] in seen_hi:
                    continue
                seen_hi.add(title_hi[:45])
                link = e.get("link", "")
                raw_sum = clean_text(e.get("summary", ""))
                detail_hi = extract_article_body(link, fallback_summary=raw_sum)
                if not detail_hi or len(detail_hi) < 35:
                    detail_hi = title_hi
                hindi_items.append({
                    "title_hi": title_hi,
                    "detail_hi": detail_hi,
                    "source": src_name,
                })
                added_from_src += 1
        except Exception:
            pass
    return hindi_items


def fetch_all_current_affairs():
    ist_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)
    today_en = ist_now.strftime("%A, %d %B %Y")

    months_hi = {
        "January": "जनवरी", "February": "फरवरी", "March": "मार्च", "April": "अप्रैल",
        "May": "मई", "June": "जून", "July": "जुलाई", "August": "अगस्त",
        "September": "सितंबर", "October": "अक्टूबर", "November": "नवंबर", "December": "दिसंबर"
    }
    days_hi = {
        "Monday": "सोमवार", "Tuesday": "मंगलवार", "Wednesday": "बुधवार", "Thursday": "गुरुवार",
        "Friday": "शुक्रवार", "Saturday": "शनिवार", "Sunday": "रविवार"
    }
    today_hi = f"{days_hi.get(ist_now.strftime('%A'), '')}, {ist_now.strftime('%d')} {months_hi.get(ist_now.strftime('%B'), '')} {ist_now.strftime('%Y')}"

    print(f"Fetching comprehensive current affairs for {today_en} (IST)...", flush=True)
    seen_titles = set()
    limits = {
        "national": 3,
        "states": 3,
        "cities": 2,
        "international": 3,
        "economy": 3,
        "science_defence": 2,
        "sports": 3,
    }

    raw_by_cat = {}
    for cat, feed_urls in CATEGORY_FEEDS.items():
        raw_by_cat[cat] = collect_raw_entries(feed_urls, cat, seen_titles, limit=limits.get(cat, 3))
        print(f" -> Collected {len(raw_by_cat[cat])} feeds for {cat}", flush=True)

    # Enrich & translate all collected items concurrently
    all_raw = [item for lst in raw_by_cat.values() for item in lst]
    print(f" -> Scraping full articles & translating {len(all_raw)} items in parallel...", flush=True)
    with ThreadPoolExecutor(max_workers=6) as ex:
        enriched_flat = list(ex.map(enrich_single_item, all_raw))

    categories_out = {cat: [] for cat in CATEGORY_FEEDS}
    idx = 0
    for cat, lst in raw_by_cat.items():
        n = len(lst)
        categories_out[cat] = enriched_flat[idx:idx + n]
        idx += n

    print(" -> Fetching native Hindi PIB / National highlights...", flush=True)
    hindi_special = fetch_native_hindi_pib_highlight(limit=3)

    print(" -> Building bilingual Practice MCQs...", flush=True)
    daily_quiz = build_dynamic_bilingual_quiz(categories_out)

    return {
        "date_en": today_en,
        "date_hi": today_hi,
        "date_str": today_en,
        "categories": categories_out,
        "hindi_special": hindi_special,
        "daily_quiz": daily_quiz,
    }


if __name__ == "__main__":
    res = fetch_all_current_affairs()
    total = sum(len(v) for v in res["categories"].values())
    print(f"DONE! Total bilingual items: {total}, Native Hindi: {len(res['hindi_special'])}, MCQs: {len(res['daily_quiz'])}", flush=True)
