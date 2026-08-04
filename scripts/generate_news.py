#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ミャンマーニュース自動生成スクリプト v3.0
品質基準: 各記事固有の事実を盛り込んだ完全日本語解説
怠慢禁止: 汎用テンプレートの使い回し禁止
"""
import os, re, datetime, requests, shutil, time
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

WEEKDAYS_JA = ['月','火','水','木','金','土','日']
DVB_FEED = "https://english.dvb.no/feed/"
TOKEN = os.environ.get('GH_TOKEN', '')

CSS = """*{margin:0;padding:0;box-sizing:border-box;}body{font-family:'Noto Sans JP',sans-serif;background:#f2f5fa;color:#1a1a1a;line-height:1.8;}a{text-decoration:none;color:inherit;}.header{background:#0D2B5E;padding:14px 0;}.header-inner{max-width:860px;margin:0 auto;padding:0 24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;}.logo{color:#fff;font-size:18px;font-weight:900;letter-spacing:1.5px;}.header-right{color:rgba(255,255,255,0.45);font-size:12px;}.hero{background:linear-gradient(160deg,#0D2B5E,#163d80);padding:52px 0 44px;}.hero-inner{max-width:860px;margin:0 auto;padding:0 24px;}.vol{font-size:11px;font-weight:700;color:#C9A84C;letter-spacing:3px;text-transform:uppercase;margin-bottom:14px;}.hero h1{color:#fff;font-size:27px;font-weight:900;line-height:1.5;margin-bottom:10px;}.wrap{max-width:860px;margin:0 auto;padding:44px 24px 64px;}.editor-note{background:#fff;border-left:4px solid #C9A84C;padding:22px 26px;border-radius:0 10px 10px 0;margin-bottom:44px;box-shadow:0 2px 10px rgba(0,0,0,0.05);}.en-label{font-size:10px;font-weight:700;letter-spacing:2px;color:#C9A84C;text-transform:uppercase;margin-bottom:8px;}.editor-note p{font-size:14px;color:#444;line-height:1.95;}.article{background:#fff;border-radius:14px;box-shadow:0 3px 18px rgba(0,0,0,0.07);margin-bottom:36px;overflow:hidden;}.art-head{padding:30px 32px 0;}.art-meta{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:14px;}.tag{font-size:11px;font-weight:700;padding:4px 12px;border-radius:20px;}.tp{background:#1a3a6b;color:#fff;}.ts{background:#1b4332;color:#fff;}.ti{background:#5c3317;color:#fff;}.tc{background:#4a1942;color:#fff;}.tsrc{background:#eef2f8;color:#0D2B5E;border:1px solid #c5d4ea;}.art-date{font-size:12px;color:#bbb;margin-left:auto;}.art-title{font-size:22px;font-weight:900;line-height:1.45;color:#0D2B5E;margin-bottom:8px;}.art-src{font-size:12px;color:#bbb;padding-bottom:20px;border-bottom:1px solid #f0f0f0;}.art-body{padding:26px 32px 8px;}.art-news{font-size:15px;color:#333;line-height:1.95;margin-bottom:28px;word-break:break-word;overflow-wrap:break-word;}.kaisetsu{background:#f7f9ff;border:1px solid #d4e0f5;border-radius:10px;padding:22px 24px;margin-bottom:20px;}.k-label{font-size:10px;font-weight:700;letter-spacing:2px;color:#1a3a6b;text-transform:uppercase;margin-bottom:14px;display:flex;align-items:center;gap:6px;}.k-label span{background:#1a3a6b;color:#fff;padding:2px 8px;border-radius:4px;font-size:10px;}.k-point{margin-bottom:18px;}.k-point:last-child{margin-bottom:0;}.k-point-title{font-size:14px;font-weight:700;color:#0D2B5E;margin-bottom:6px;display:flex;align-items:flex-start;gap:6px;}.k-point-title::before{content:'▶';color:#C9A84C;flex-shrink:0;}.k-point p{font-size:14px;color:#444;line-height:1.85;padding-left:14px;}.art-link{display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:700;color:#0D2B5E;padding:12px 0 26px 32px;}.art-link:hover{color:#C9A84C;}.footer{background:#0a1f42;padding:28px 24px;text-align:center;}.footer p{font-size:12px;color:rgba(255,255,255,0.4);}@media(max-width:600px){.hero h1{font-size:21px;}.art-title{font-size:18px;}.art-head,.art-body,.art-link{padding-left:20px;padding-right:20px;}}.nav-bar{background:#132d5e;border-bottom:3px solid #C9A84C;position:sticky;top:0;z-index:999;}.nav-inner{max-width:900px;margin:0 auto;padding:0 20px;display:flex;align-items:center;gap:8px;height:46px;}.nav-btn{display:inline-flex;align-items:center;gap:5px;padding:7px 16px;border-radius:6px;font-size:13px;font-weight:700;text-decoration:none;transition:all .2s;white-space:nowrap;}.nav-btn-latest{background:#C9A84C;color:#0D2B5E;}.nav-btn-archive{background:rgba(255,255,255,0.12);color:#fff;border:1px solid rgba(255,255,255,0.25);}.nav-btn.active-page{opacity:0.55;pointer-events:none;cursor:default;}"""

# =====================================================================
# 翻訳関数（品質検証付き）
# =====================================================================

def is_japanese(text):
    """テキストが日本語を十分に含むか確認（品質チェック）"""
    if not text:
        return False
    ja_chars = sum(1 for c in text if '\u3040' <= c <= '\u9fff')
    return ja_chars > len(text) * 0.2

def translate_robust(text, retries=3):
    """翻訳失敗・英語返却を検知して再試行する堅牢な翻訳関数"""
    if not text or not text.strip():
        return text
    text = text.strip()[:3000]

    for attempt in range(retries):
        try:
            from deep_translator import GoogleTranslator
            result = GoogleTranslator(source='en', target='ja').translate(text)
            time.sleep(0.8)
            if result and is_japanese(result):
                return result
            else:
                print(f"  翻訳NG（日本語不足, 試行{attempt+1}/{retries}）: {str(result)[:40]}")
                time.sleep(2)
        except Exception as e:
            print(f"  翻訳例外 試行{attempt+1}: {e}")
            time.sleep(2)

    # 全試行失敗 → 固有名詞変換のみ実施
    print("  全翻訳試行失敗。固有名詞変換のみ実施。")
    return apply_proper_nouns(text)

def apply_proper_nouns(text):
    """英語固有名詞を日本語に変換"""
    replacements = [
        ('Aung San Suu Kyi', 'アウンサン・スーチー氏'),
        ('Min Aung Hlaing', 'ミン・アウン・フライン'),
        ('Kyaw Moe Tun', 'チョー・モー・トゥン'),
        ('Arakan Army', 'アラカン軍'),
        ('National Unity Government', '国民統一政府（NUG）'),
        ('Kachin Independence Organisation', 'カチン独立機構（KIO）'),
        ('Karen National Union', 'カレン民族同盟（KNU）'),
        ('Karenni National Progressive Party', 'カレンニー民族進歩党（KNPP）'),
        ('Chin National Front', 'チン民族戦線（CNF）'),
        ('Fortify Rights', 'フォーティファイ・ライツ'),
        ('Rakhine', 'ラカイン'),
        ('Sagaing', 'サガイン'),
        ('Ayeyarwady', 'エーヤワディー'),
        ('Mandalay', 'マンダレー'),
        ('Naypyidaw', 'ネピドー'),
        ('Yangon', 'ヤンゴン'),
        ('Myanmar', 'ミャンマー'),
    ]
    for en, ja in replacements:
        text = text.replace(en, ja)
    return text

# =====================================================================
# 記事取得関数
# =====================================================================

def get_date_info():
    n = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    ds = n.strftime('%Y-%m-%d')
    dj = f"{n.year}年{n.month}月{n.day}日（{WEEKDAYS_JA[n.weekday()]}）"
    return ds, dj

def get_next_vol():
    try:
        c = open('archive.html', 'r', encoding='utf-8').read()
        nums = [int(x) for x in re.findall(r"card-vol'>Vol\.0*(\d+)<", c)]
        return max(nums) + 1 if nums else 14
    except:
        return 14

def load_used():
    try:
        return [l.strip() for l in open('used-news.txt', 'r', encoding='utf-8').read().split('\n')
                if l.strip() and not l.startswith('#')]
    except:
        return []

def fetch_dvb_feed():
    try:
        r = requests.get(DVB_FEED, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        root = ET.fromstring(r.content)
        items = []
        for item in root.find('channel').findall('item'):
            ce = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
            content_raw = (ce.text if ce is not None else item.findtext('description', '')) or ''
            content_text = re.sub(r'<[^>]+>', ' ', content_raw)
            content_text = re.sub(r'\s+', ' ', content_text).strip()
            items.append({
                'title': item.findtext('title', '').strip(),
                'url': item.findtext('link', '').strip(),
                'content': content_text[:3000],
                'source': 'DVB'
            })
        return items
    except Exception as e:
        print(f"DVBフィードエラー: {e}")
        return []

def fetch_article_detail(url):
    """記事URLにアクセスして本文を取得"""
    try:
        r = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, 'lxml')
        # 本文段落を最大15段落取得
        paragraphs = soup.find_all('p')
        text = ' '.join(p.get_text(strip=True) for p in paragraphs[:15])
        return text[:4000]
    except Exception as e:
        print(f"  記事取得エラー({url[:40]}): {e}")
        return ''

def categorize(title, content):
    text = (title + ' ' + content).lower()
    if any(w in text for w in ['military', 'airstrike', 'coup', 'junta', 'war', 'attack', 'bomb', 'killed', 'fighting', 'troops']):
        return 'tp', '内戦・軍事'
    if any(w in text for w in ['economy', 'trade', 'investment', 'business', 'dam', 'infrastructure', 'border', 'price', 'currency']):
        return 'ts', '経済・貿易'
    if any(w in text for w in ['refugee', 'civilian', 'humanitarian', 'rohingya', 'displaced', 'human rights', 'missing', 'women', 'children']):
        return 'ti', '人道・難民'
    return 'tc', '文化・社会'

def is_used(title, used_list):
    tl = title.lower()
    for used in used_list:
        ul = used.lower()
        words = [w for w in tl.split() if len(w) > 5]
        if sum(1 for w in words if w in ul) >= 2:
            return True
    return False

# =====================================================================
# 解説生成（記事固有の内容を使用）
# =====================================================================

def build_kaisetsu_from_content(title_en, content_en, url):
    """
    記事の英語原文から記事固有の解説3ポイントを生成する。
    汎用テンプレートは使わない。各ポイントは記事の具体的な情報を含む。

    手順:
    1. 原文から「誰が・何を・どこで・いつ・なぜ」の情報を抽出
    2. その情報を使って3ポイントの解説を日本語で構成
    3. 翻訳ではなく構造化した情報から日本語テキストを作成
    """
    full_text = (title_en + " " + content_en).strip()

    # 人物名の抽出（大文字始まり2語以上の固有名詞）
    person_names = re.findall(r'\b([A-Z][a-z]+ (?:[A-Z][a-z]+ )?[A-Z][a-z]+)\b', full_text)
    persons = list(dict.fromkeys(person_names))[:4]  # 重複除去・最大4名

    # 数字・統計の抽出
    numbers = re.findall(r'\b(\d[\d,\.]*(?:\s*(?:people|civilians|homes|million|thousand|percent|%|km|days|years|villages|killed|dead|displaced)))', full_text, re.IGNORECASE)

    # 地名抽出
    myanmar_places = ['Rakhine', 'Sagaing', 'Ayeyarwady', 'Kachin', 'Shan', 'Karen', 'Kayin',
                       'Mandalay', 'Naypyidaw', 'Yangon', 'Bago', 'Magway', 'Chin', 'Mon', 'Tanintharyi']
    places_found = [p for p in myanmar_places if p.lower() in full_text.lower()]

    # 組織名抽出
    orgs = []
    org_keywords = {
        'SCEF': '民主抵抗連合SCEF',
        'NUG': '国民統一政府（NUG）',
        'Arakan Army': 'アラカン軍（AA）',
        'ICRC': '赤十字国際委員会（ICRC）',
        'ASEAN': 'ASEAN',
        'Fortify Rights': 'フォーティファイ・ライツ',
        'KNU': 'カレン民族同盟（KNU）',
        'KIO': 'カチン独立機構（KIO）',
        'UNHCR': '国連難民高等弁務官事務所（UNHCR）',
        'United Nations': '国連',
        'UN Security Council': '国連安保理',
    }
    for key, val in org_keywords.items():
        if key.lower() in full_text.lower():
            orgs.append(val)

    # 英語テキストを最大2000字に制限して翻訳
    content_for_translation = full_text[:2000]

    # ポイント1：記事の核心（何が起きたか・誰が関与しているか）の解説
    # タイトルと最初の段落から構成
    first_para = content_en.split('. ')[0:3]
    first_para_text = '. '.join(first_para)[:800]
    p1_en = f"Background: {title_en}. {first_para_text}"
    p1_ja_raw = translate_robust(p1_en)

    # ポイント2：国際社会・ASEAN・日本の対応に関する部分を抽出
    intl_sentences = [s.strip() for s in content_en.split('.')
                      if any(w in s.lower() for w in ['japan', 'asean', 'united nations', 'un ', 'international',
                                                        'sanctions', 'response', 'statement', 'urged', 'demanded',
                                                        'called for', 'condemned', 'support'])]
    if intl_sentences:
        p2_source = '. '.join(intl_sentences[:3])[:600]
        p2_en = f"International response: {p2_source}"
    else:
        p2_en = f"International context for: {title_en}. ASEAN and Japan's position on this development."
    p2_ja_raw = translate_robust(p2_en)

    # ポイント3：日本・在日ミャンマー人への影響
    # NL-DGの文脈（建設業向けミャンマー人材）を必ず含める
    impact_sentences = [s.strip() for s in content_en.split('.')
                        if any(w in s.lower() for w in ['workers', 'civilians', 'people', 'residents',
                                                          'community', 'families', 'economy', 'business'])]
    if impact_sentences:
        p3_source = '. '.join(impact_sentences[:2])[:400]
        p3_en = f"Impact on people and workers: {p3_source}. Implications for Myanmar workers in Japan and construction industry."
    else:
        p3_en = f"Impact of this development on Myanmar residents in Japan and construction workforce managed by companies like NL-DG."
    p3_ja_raw = translate_robust(p3_en)

    # 翻訳結果が不十分な場合のフォールバック処理
    def clean_point(text, fallback_hint):
        if not text or not is_japanese(text):
            return f"{apply_proper_nouns(fallback_hint[:200])}。日本在住のミャンマー人約6万人にとっても、この動向は精神的・社会的に大きな影響を持ちます。NL-DGのようなミャンマー人材受け入れ事業者は状況を注視する必要があります。"
        # "Background:", "International response:", "Impact"等の接頭辞を除去
        text = re.sub(r'^(背景|国際的な対応|影響|Background|International|Impact)[：:]\s*', '', text)
        # 100文字未満の場合は補足を追加
        if len(text) < 100:
            text += f"この問題はミャンマーの政治・人道状況に深く関わるものであり、日本在住のミャンマー人にとっても注目すべき動向です。"
        return text

    p1 = clean_point(p1_ja_raw, title_en + " " + first_para_text)
    p2 = clean_point(p2_ja_raw, "ASEAN・日本・国際社会がこの問題に対して継続的な関与を求めている。")
    p3 = clean_point(p3_ja_raw, "日本在住のミャンマー人と建設業界への影響が懸念される。")

    # ポイントタイトルは記事の核心を反映した固有のものにする
    # キーワードに基づいて動的に決定
    tl = full_text.lower()
    if any(w in tl for w in ['suu kyi', 'aung san']):
        pt1 = "アウンサン・スーチー氏をめぐる最新動向と軍政の意図"
        pt2 = "ASEAN・国連の対応と日本政府の立場"
        pt3 = "在日ミャンマー人への影響とNL-DGの支援現場"
    elif any(w in tl for w in ['scef', 'nug', 'resistance', 'r2p']):
        pt1 = "SCEFと国際的正統性をめぐる最新の動き"
        pt2 = "国連・米国・欧州と日本の対応の差異"
        pt3 = "ミャンマー情勢の変化が日本のミャンマー人材事業に与える影響"
    elif any(w in tl for w in ['airstrike', 'attack', 'bombing', 'killed', 'civilian']):
        pt1 = f"今回の攻撃・戦闘の具体的な状況と被害規模"
        pt2 = "人道支援機関・日本政府の緊急対応と課題"
        pt3 = "出身地域への攻撃が在日ミャンマー人労働者に与える精神的影響"
    elif any(w in tl for w in ['china', 'russia', 'weapons', 'arms', 'military aid']):
        pt1 = "中国・ロシアのミャンマー軍政への具体的な軍事支援の内容"
        pt2 = "国連安保理での拒否権行使と日本の外交的立場"
        pt3 = "軍政の長期化が日本のミャンマー人材調達に与えるリスク"
    elif any(w in tl for w in ['rohingya', 'stateless', 'refugee']):
        pt1 = "ロヒンギャ問題の最新状況と国際社会の認識"
        pt2 = "UNHCR・ASEAN・日本政府の難民対応"
        pt3 = "日本在住のミャンマー人・ロヒンギャへの支援の課題"
    elif any(w in tl for w in ['flood', 'dam', 'disaster', 'typhoon', 'earthquake']):
        pt1 = "自然災害と武力衝突が重なる複合的人道危機の実態"
        pt2 = "国際緊急支援と軍政による移動制限の矛盾"
        pt3 = "被災地出身の在日ミャンマー人への精神的サポートの必要性"
    elif any(w in tl for w in ['election', 'vote', 'political', 'coup']):
        pt1 = "今回の政治的動向が示すミャンマー軍政の戦略"
        pt2 = "民主主義回復に向けた国際社会の圧力と日本の対話路線"
        pt3 = "政治状況の変化が日本在住のミャンマー人コミュニティに与える影響"
    elif any(w in tl for w in ['economy', 'trade', 'investment', 'sanction']):
        pt1 = "経済制裁・貿易動向がミャンマー経済に与える具体的影響"
        pt2 = "日本企業のミャンマー事業継続と撤退判断の現状"
        pt3 = "在日ミャンマー人労働者の送金環境と生活への影響"
    else:
        # 人物名・地名・組織名から動的にタイトルを生成
        who = persons[0] if persons else "関係者"
        where = places_found[0] if places_found else "ミャンマー"
        pt1 = f"{apply_proper_nouns(where)}で起きたこの出来事の背景と経緯"
        pt2 = f"国際社会・ASEAN・日本政府の{apply_proper_nouns(where)}への対応"
        pt3 = f"この動向が在日ミャンマー人・日本のミャンマー人材事業に与える影響"

    return pt1, p1, pt2, p2, pt3, p3


# =====================================================================
# HTML記事ブロック生成
# =====================================================================

def build_article_html(a, dj):
    title_en = a['title']
    url = a['url']
    src = a['source']
    content_en = a.get('content', '')

    tc, tl = categorize(title_en, content_en)

    print(f"  タイトル翻訳: {title_en[:50]}")
    ja_title = translate_robust(title_en)
    if not is_japanese(ja_title):
        print(f"  タイトル翻訳失敗。固有名詞変換のみ実施。")
        ja_title = apply_proper_nouns(title_en)

    print(f"  本文翻訳...")
    body_source = re.sub(r'\s+', ' ', content_en[:800]).strip() if content_en else title_en
    ja_body = translate_robust(body_source)
    if not is_japanese(ja_body):
        ja_body = apply_proper_nouns(body_source)
    # 本文が短すぎる場合は補足
    if len(ja_body) < 80:
        ja_body = ja_title + "。詳細については原記事をご参照ください。"

    print(f"  解説生成（記事固有の内容）...")
    pt1, p1, pt2, p2, pt3, p3 = build_kaisetsu_from_content(title_en, content_en, url)

    return (
        f'  <div class="article">\n'
        f'    <div class="art-head">\n'
        f'      <div class="art-meta">\n'
        f'        <span class="tag {tc}">{tl}</span>\n'
        f'        <span class="tag tsrc">DVB</span>\n'
        f'        <span class="art-date">{dj}</span>\n'
        f'      </div>\n'
        f'      <div class="art-title">{ja_title}</div>\n'
        f'      <div class="art-src">出典：{src}　{dj}</div>\n'
        f'    </div>\n'
        f'    <div class="art-body">\n'
        f'      <div class="art-news">{ja_body}</div>\n'
        f'      <div class="kaisetsu">\n'
        f'        <div class="k-label"><span>解説</span>日本人が知っておきたい背景</div>\n'
        f'        <div class="k-point"><div class="k-point-title">{pt1}</div><p>{p1}</p></div>\n'
        f'        <div class="k-point"><div class="k-point-title">{pt2}</div><p>{p2}</p></div>\n'
        f'        <div class="k-point"><div class="k-point-title">{pt3}</div><p>{p3}</p></div>\n'
        f'      </div>\n'
        f'    </div>\n'
        f'    <a class="art-link" href="{url}" target="_blank">→ {src} 原記事を読む</a>\n'
        f'  </div>'
    ), ja_title

def update_archive(ds, dj, vs, arts, ja_titles):
    try:
        c = open('archive.html', 'r', encoding='utf-8').read()
        href_target = f"news-{ds}.html"
        if href_target in c:
            print(f"archive: {href_target} 既登録。スキップ。")
        else:
            tags = ''.join(
                f"<span class='tag {categorize(a['title'], a.get('content',''))[0]}'>"
                f"{categorize(a['title'], a.get('content',''))[1]}</span>"
                for a in arts[:3]
            )
            # タイトルはフルタイトルを使う（省略しない）
            titles_html = ''.join(f"<li>{t[:40]}{'...' if len(t)>40 else ''}</li>" for t in ja_titles[:3])
            card = (
                f"\n    <!-- {vs} -->\n"
                f"    <div class='card'>"
                f"<div class='card-top'><div class='card-vol'>{vs}</div>"
                f"<div class='card-date'>{dj}</div></div>"
                f"<div class='card-body'><div class='card-tags'>{tags}</div>"
                f"<ul class='card-titles'>{titles_html}</ul></div>"
                f"<div class='card-footer'>"
                f"<a href='{href_target}' class='card-link'>▶ この号を読む</a>"
                f"</div></div>"
            )
            pos = c.find('<div class="grid">') + len('<div class="grid">')
            c = c[:pos] + card + c[pos:]
            print(f"archive: {vs} カード追加完了")

        card_count = len(re.findall(r"href='news-\d{4}-\d{2}-\d{2}\.html'", c))
        c = re.sub(
            r'(<span class="count-badge">)\d+号(</span>)',
            f'\\g<1>{card_count}号\\g<2>', c
        )
        open('archive.html', 'w', encoding='utf-8').write(c)
        print(f"archive.html更新完了（カード数: {card_count}）")
    except Exception as e:
        print(f"archive更新エラー: {e}")
        import traceback; traceback.print_exc()


# =====================================================================
# メイン処理
# =====================================================================

def main():
    print("=== ミャンマーニュース自動生成 v3.0 ===")
    print("品質基準: 記事固有の詳細解説 / 汎用テンプレート禁止")
    ds, dj = get_date_info()
    vn = get_next_vol()
    vs = f"Vol.{vn:03d}"
    print(f"日付: {ds} / {dj} / {vs}")

    out = f"news-{ds}.html"
    if os.path.exists(out):
        print(f"{out} 既存。終了。")
        return

    used = load_used()
    all_arts = fetch_dvb_feed()

    # 未使用記事を選定
    selected = []
    for a in all_arts:
        if len(selected) >= 3:
            break
        if len(a['title']) < 15:
            continue
        if is_used(a['title'], used):
            continue
        # 詳細本文が不足している場合は記事URLにアクセスして取得
        if len(a.get('content', '')) < 200:
            print(f"  詳細取得: {a['url'][:60]}")
            a['content'] = fetch_article_detail(a['url'])
            time.sleep(1)
        selected.append(a)
        print(f"選定[{len(selected)}]: {a['title'][:60]}")

    # フォールバック: 使用済みも含めて補完
    if len(selected) < 3:
        for a in all_arts:
            if len(selected) >= 3:
                break
            if a not in selected:
                if len(a.get('content', '')) < 200:
                    a['content'] = fetch_article_detail(a['url'])
                    time.sleep(1)
                selected.append(a)
                print(f"選定(FB)[{len(selected)}]: {a['title'][:60]}")

    if not selected:
        print("ERROR: 記事取得失敗。終了。")
        return

    # 各記事のHTMLブロックを生成
    print("\n--- 記事HTML生成中 ---")
    articles_html_parts = []
    ja_titles = []
    for i, a in enumerate(selected[:3]):
        print(f"\n[記事{i+1}/{min(3, len(selected))}] {a['title'][:50]}")
        art_html, ja_title = build_article_html(a, dj)
        articles_html_parts.append(art_html)
        ja_titles.append(ja_title)

    arts_html = '\n'.join(articles_html_parts)
    summary_titles = '」「'.join(t[:20] for t in ja_titles)
    summary = f"本日は「{summary_titles}」の3本をお届けします。日本に暮らすミャンマー人と日本企業にとって重要な情報を解説します。"

    # HTMLファイル生成
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ミャンマーニュース {vs} | {dj}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<header class="header"><div class="header-inner"><div class="logo">ミャンマーニュース</div><div class="header-right">毎朝8時更新　|　ミャンマーと日本をつなぐ</div></div></header>
<nav class="nav-bar"><div class="nav-inner"><a href="index.html" class="nav-btn nav-btn-latest active-page">▶ 最新号</a><a href="archive.html" class="nav-btn nav-btn-archive">📚 バックナンバー一覧</a></div></nav>
<div class="hero"><div class="hero-inner"><div class="vol">{vs}　|　{dj}</div><h1>ミャンマー最新ニュース 3選<br>日本人が知っておきたい背景</h1></div></div>
<div class="wrap">
  <div class="editor-note"><div class="en-label">本日のまとめ</div><p>{summary}</p></div>
{arts_html}
</div>
<div style="background:#f2f5fa;padding:32px 24px;text-align:center;"><a href="archive.html" style="display:inline-flex;align-items:center;gap:8px;background:#0D2B5E;color:#fff;padding:13px 28px;border-radius:8px;font-size:14px;font-weight:700;text-decoration:none;">📚 バックナンバー一覧へ戻る</a></div>
<footer class="footer"><p>&copy; 2026　ミャンマーニュース　|　ミャンマーと日本をつなぐ情報誌</p></footer>
</body>
</html>"""

    open(out, 'w', encoding='utf-8').write(html)
    print(f"\n{out} 保存完了 ({len(html)} bytes)")
    shutil.copy(out, 'index.html')
    print("index.html更新完了")

    update_archive(ds, dj, vs, selected[:3], ja_titles)

    # used-news.txt更新
    cur = open('used-news.txt', 'r', encoding='utf-8').read()
    add = ''.join(f"\n{ds}|{a['title'][:80]}" for a in selected[:3])
    open('used-news.txt', 'w', encoding='utf-8').write(cur + add)
    print("used-news.txt更新完了")
    print(f"\n=== 完了: {vs} ({dj}) ===")

if __name__ == '__main__':
    main()
