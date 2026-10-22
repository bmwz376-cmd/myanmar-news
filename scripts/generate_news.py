#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ミャンマーニュース自動生成スクリプト v4.0
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
# v4.0 変更点（fix/translation）
#  - 無料Google翻訳(deep-translator)はActionsのIPで429レート制限になり、
#    失敗時に英語原文/固有名詞置換だけの疑似翻訳を出力していた → 廃止
#  - LLM(Gemini API)で タイトル・本文・記事固有の解説3ポイントを一括生成
#  - 生成後に品質検証（英語混入・文字数）→ リトライ → 失敗なら出力せず異常終了
#    （index.html / archive.html は前号のまま維持され、Actionsは赤表示になる）
#  - DVBのミャンマー無関係記事除外、重複記事除外
# =====================================================================
import sys, json

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash').strip()

class GenerationError(Exception):
    pass

# タイトルに残ってよい英字（固有名詞・略語）
ALLOWED_LATIN = {
    'ACLED', 'LPG', 'LNG', 'ASEAN', 'NUG', 'NUCC', 'PDF', 'AA', 'KIA', 'KIO', 'KNU', 'KNLA',
    'KNPP', 'CNF', 'TNLA', 'MNDAA', 'SAC', 'SCEF', 'NLD', 'USDP', 'UN', 'UNHCR', 'UNICEF',
    'ICRC', 'ICJ', 'ICC', 'WFP', 'WHO', 'IMF', 'EU', 'US', 'USA', 'UK', 'G7', 'DVB', 'BBC',
    'NHK', 'JICA', 'SNS', 'AI', 'IT', 'GDP', 'CDM', 'BGF', 'NGO', 'NPO', 'HRW', 'OCHA',
    'NL-DG', 'Facebook', 'TikTok', 'X', 'BIM', 'CEO', 'COVID', 'IS', 'FAO', 'ILO', 'IOM',
    'BRI', 'CMEC', 'MOGE', 'MEC', 'MEHL', 'NDSC', 'ULA', 'MNHRC', 'ODA', 'ADB',
}

MYANMAR_KEYWORDS = [
    'myanmar', 'burma', 'burmese', 'naypyidaw', 'naypyitaw', 'yangon', 'rangoon', 'mandalay',
    'rakhine', 'arakan', 'sagaing', 'magway', 'bago', 'ayeyarwady', 'irrawaddy', 'tanintharyi',
    'kachin', 'shan', 'karen', 'kayin', 'karenni', 'kayah', 'chin state', 'mon state',
    'rohingya', 'junta', 'tatmadaw', 'min aung hlaing', 'suu kyi', 'nug', 'pdf', 'arakan army',
    'sittwe', 'lashio', 'myawaddy', 'muse', 'tachileik', 'myitkyina', 'nld',
]

def is_japanese(text):
    if not text:
        return False
    ja = sum(1 for c in text if '\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9fff')
    return ja > len(text) * 0.4

def english_leftovers(text):
    """許可リスト外の英単語（3文字以上の英字列）を返す"""
    words = re.findall(r'[A-Za-z][A-Za-z\-]{2,}', text or '')
    return [w for w in words if w not in ALLOWED_LATIN and w.upper() not in ALLOWED_LATIN]

def is_myanmar_related(a):
    t = (a.get('title', '') + ' ' + a.get('content', '')[:1500]).lower()
    return sum(t.count(k) for k in MYANMAR_KEYWORDS) >= 2 or any(k in a.get('title', '').lower() for k in MYANMAR_KEYWORDS)

def normalize_title(t):
    return set(w for w in re.findall(r'[a-z0-9]+', t.lower()) if len(w) > 3)

def similar(t1, t2):
    a, b = normalize_title(t1), normalize_title(t2)
    if not a or not b:
        return False
    return len(a & b) / min(len(a), len(b)) >= 0.6

PROMPT = """あなたは在日ミャンマー人材を扱う日本企業（建設業向け人材紹介・BIM研修のNL-DG）向けに、
ミャンマーニュースを日本語で解説する編集者です。以下の英語記事を読み、JSONのみで出力してください。

要件:
- title_ja: 自然な日本語の見出し（40字以内）。英単語は使わず、固有名詞はカタカナ表記。略語（ASEAN, NUG, ACLED, LPG 等）のみ英字可。
- body_ja: 記事本文の要約を自然な日本語で 250〜400字。記事にある具体的事実（人名・地名・数字・日付）を必ず含める。
- points: 3要素の配列。各要素は {"title": 見出し(30字以内・記事固有), "text": 本文(150〜250字)}
  1つ目「背景と経緯」: この出来事に至る経緯・背景（クーデター以降の流れ等）をこの記事に即して。
  2つ目「国際社会と日本の対応」: 国連・ASEAN・米中・日本政府などの対応をこの記事に即して。
  3つ目「日本への影響」: 日本企業・在日ミャンマー人・建設業の外国人材受け入れへの具体的影響。
- 汎用的な定型文は禁止。各ポイントにこの記事固有の事実を最低1つ含めること。
- 記事にない事実を捏造しない。推測は「〜とみられる」等と明示。
- 全文日本語。

出力形式: {"title_ja": "...", "body_ja": "...", "points": [{"title": "...", "text": "..."}, ...]}

記事タイトル: {TITLE}
記事URL: {URL}
記事本文:
{CONTENT}
"""

def call_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "responseMimeType": "application/json"},
    }
    r = requests.post(url, params={"key": GEMINI_API_KEY}, json=body, timeout=120)
    if r.status_code != 200:
        raise GenerationError(f"Gemini HTTP {r.status_code}: {r.text[:300]}")
    data = r.json()
    try:
        txt = data['candidates'][0]['content']['parts'][0]['text']
    except Exception:
        raise GenerationError(f"Gemini応答形式エラー: {str(data)[:300]}")
    txt = re.sub(r'^```(?:json)?|```$', '', txt.strip()).strip()
    return json.loads(txt)

def validate(res):
    errs = []
    t = (res.get('title_ja') or '').strip()
    b = (res.get('body_ja') or '').strip()
    pts = res.get('points') or []
    if not is_japanese(t):
        errs.append('タイトルが日本語でない')
    left = english_leftovers(t)
    if left:
        errs.append(f'タイトルに英語混入: {left}')
    if not is_japanese(b) or len(b) < 150:
        errs.append(f'本文が日本語でない/短い({len(b)}字)')
    if len(english_leftovers(b)) > 5:
        errs.append(f'本文に英語混入: {english_leftovers(b)[:5]}')
    if len(pts) != 3:
        errs.append(f'解説ポイント数が{len(pts)}')
    for i, p in enumerate(pts[:3]):
        pt, px = (p.get('title') or '').strip(), (p.get('text') or '').strip()
        if not pt or not is_japanese(pt):
            errs.append(f'解説{i+1}見出し不正')
        if len(px) < 100 or not is_japanese(px):
            errs.append(f'解説{i+1}本文不足({len(px)}字)')
        if len(english_leftovers(px)) > 5:
            errs.append(f'解説{i+1}に英語混入')
    return errs

def generate_article_ja(a, retries=4):
    """記事の日本語タイトル・本文・解説を生成。品質NGならリトライ、最終的に例外。"""
    prompt = (PROMPT.replace('{TITLE}', a['title']).replace('{URL}', a['url'])
              .replace('{CONTENT}', (a.get('content') or a['title'])[:6000]))
    last = ''
    for attempt in range(1, retries + 1):
        try:
            res = call_gemini(prompt)
            errs = validate(res)
            if not errs:
                return res
            last = '; '.join(errs)
            print(f"  品質NG 試行{attempt}/{retries}: {last}")
            prompt += f"\n\n前回の出力は次の理由で不合格でした。修正して再出力してください: {last}"
        except Exception as e:
            last = str(e)
            print(f"  生成エラー 試行{attempt}/{retries}: {last[:200]}")
        time.sleep(5 * attempt)
    raise GenerationError(f"記事生成失敗: {a['title'][:60]} / {last[:200]}")

import html as _html
def esc(s):
    return _html.escape(s or '', quote=False)

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
# =====================================================================
# HTML記事ブロック生成
# =====================================================================

def build_article_html(a, dj):
    title_en = a['title']
    url = a['url']
    src = a['source']
    tc, tl = categorize(title_en, a.get('content', ''))

    print(f"  日本語記事・解説を生成中: {title_en[:50]}")
    res = generate_article_ja(a)
    ja_title = res['title_ja'].strip()
    ja_body = res['body_ja'].strip()
    pts = res['points'][:3]

    kp = ''.join(
        f'        <div class="k-point"><div class="k-point-title">{esc(p["title"])}</div><p>{esc(p["text"])}</p></div>\n'
        for p in pts
    )
    return (
        f'  <div class="article">\n'
        f'    <div class="art-head">\n'
        f'      <div class="art-meta">\n'
        f'        <span class="tag {tc}">{tl}</span>\n'
        f'        <span class="tag tsrc">{esc(src)}</span>\n'
        f'        <span class="art-date">{dj}</span>\n'
        f'      </div>\n'
        f'      <div class="art-title">{esc(ja_title)}</div>\n'
        f'      <div class="art-src">出典：{esc(src)}　{dj}</div>\n'
        f'    </div>\n'
        f'    <div class="art-body">\n'
        f'      <div class="art-news">{esc(ja_body)}</div>\n'
        f'      <div class="kaisetsu">\n'
        f'        <div class="k-label"><span>解説</span>日本人が知っておきたい背景</div>\n'
        f'{kp}'
        f'      </div>\n'
        f'    </div>\n'
        f'    <a class="art-link" href="{url}" target="_blank">→ {esc(src)} 原記事を読む</a>\n'
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
    print("=== ミャンマーニュース自動生成 v4.0 ===")
    print("品質基準: 記事固有の詳細解説 / 汎用テンプレート禁止")
    ds, dj = get_date_info()
    vn = get_next_vol()
    vs = f"Vol.{vn:03d}"
    print(f"日付: {ds} / {dj} / {vs}")

    out = f"news-{ds}.html"
    if os.path.exists(out):
        print(f"{out} 既存。終了。")
        return

    if not GEMINI_API_KEY:
        print("ERROR: Secret GEMINI_API_KEY が未設定です。英語のまま公開しないため中止します（前号を維持）。")
        sys.exit(1)

    used = load_used()
    used_titles = [u.split('|', 1)[-1] for u in used]
    all_arts = fetch_dvb_feed()
    if not all_arts:
        print("ERROR: DVBフィード取得失敗。前号を維持して終了。")
        sys.exit(1)

    # 未使用・ミャンマー関連・重複なしの記事を選定（使用済み記事での補完はしない）
    selected = []
    for a in all_arts:
        if len(selected) >= 3:
            break
        if len(a['title']) < 15:
            continue
        if is_used(a['title'], used) or any(similar(a['title'], u) for u in used_titles):
            print(f"  除外(使用済み): {a['title'][:60]}")
            continue
        if any(similar(a['title'], s['title']) for s in selected):
            print(f"  除外(重複): {a['title'][:60]}")
            continue
        if len(a.get('content', '')) < 200:
            print(f"  詳細取得: {a['url'][:60]}")
            a['content'] = fetch_article_detail(a['url'])
            time.sleep(1)
        if not is_myanmar_related(a):
            print(f"  除外(ミャンマー無関係): {a['title'][:60]}")
            continue
        selected.append(a)
        print(f"選定[{len(selected)}]: {a['title'][:60]}")

    if len(selected) < 3:
        print(f"ERROR: 新規記事が{len(selected)}本しかありません。前号を維持して終了。")
        sys.exit(1)

    # 各記事のHTMLブロックを生成（1本でも失敗したら何も書き込まずに異常終了）
    print("\n--- 記事HTML生成中 ---")
    articles_html_parts = []
    ja_titles = []
    try:
        for i, a in enumerate(selected[:3]):
            print(f"\n[記事{i+1}/3] {a['title'][:50]}")
            art_html, ja_title = build_article_html(a, dj)
            articles_html_parts.append(art_html)
            ja_titles.append(ja_title)
    except GenerationError as e:
        print(f"ERROR: {e}\n英語・テンプレートのまま公開しないため中止します（前号を維持）。")
        sys.exit(1)
    arts_html = '\n'.join(articles_html_parts)
    summary_titles = '」「'.join(t[:20] for t in ja_titles)
    summary = f"本日は「{summary_titles}」の3本をお届けします。日本に暮らすミャンマー人と日本企業にとって重要な情報を解説します。"

    # HTMLファイル生成
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
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
