#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, datetime, requests, shutil, time
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

WEEKDAYS_JA = ['月','火','水','木','金','土','日']
DVB_FEED = "https://english.dvb.no/feed/"
BNI_URL  = "https://www.bnionline.net/en/news/myanmar"

CSS = """*{margin:0;padding:0;box-sizing:border-box;}body{font-family:'Noto Sans JP',sans-serif;background:#f2f5fa;color:#1a1a1a;line-height:1.8;}a{text-decoration:none;color:inherit;}.header{background:#0D2B5E;padding:14px 0;}.header-inner{max-width:860px;margin:0 auto;padding:0 24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;}.logo{color:#fff;font-size:18px;font-weight:900;letter-spacing:1.5px;}.header-right{color:rgba(255,255,255,0.45);font-size:12px;}.hero{background:linear-gradient(160deg,#0D2B5E,#163d80);padding:52px 0 44px;}.hero-inner{max-width:860px;margin:0 auto;padding:0 24px;}.vol{font-size:11px;font-weight:700;color:#C9A84C;letter-spacing:3px;text-transform:uppercase;margin-bottom:14px;}.hero h1{color:#fff;font-size:27px;font-weight:900;line-height:1.5;margin-bottom:10px;}.wrap{max-width:860px;margin:0 auto;padding:44px 24px 64px;}.editor-note{background:#fff;border-left:4px solid #C9A84C;padding:22px 26px;border-radius:0 10px 10px 0;margin-bottom:44px;box-shadow:0 2px 10px rgba(0,0,0,0.05);}.en-label{font-size:10px;font-weight:700;letter-spacing:2px;color:#C9A84C;text-transform:uppercase;margin-bottom:8px;}.editor-note p{font-size:14px;color:#444;line-height:1.95;}.article{background:#fff;border-radius:14px;box-shadow:0 3px 18px rgba(0,0,0,0.07);margin-bottom:36px;overflow:hidden;}.art-head{padding:30px 32px 0;}.art-meta{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:14px;}.tag{font-size:11px;font-weight:700;padding:4px 12px;border-radius:20px;}.tp{background:#1a3a6b;color:#fff;}.ts{background:#1b4332;color:#fff;}.ti{background:#5c3317;color:#fff;}.tc{background:#4a1942;color:#fff;}.tsrc{background:#eef2f8;color:#0D2B5E;border:1px solid #c5d4ea;}.art-date{font-size:12px;color:#bbb;margin-left:auto;}.art-title{font-size:22px;font-weight:900;line-height:1.45;color:#0D2B5E;margin-bottom:8px;}.art-src{font-size:12px;color:#bbb;padding-bottom:20px;border-bottom:1px solid #f0f0f0;}.art-body{padding:26px 32px 8px;}.art-news{font-size:15px;color:#333;line-height:1.95;margin-bottom:28px;}.kaisetsu{background:#f7f9ff;border:1px solid #d4e0f5;border-radius:10px;padding:22px 24px;margin-bottom:20px;}.k-label{font-size:10px;font-weight:700;letter-spacing:2px;color:#1a3a6b;text-transform:uppercase;margin-bottom:14px;display:flex;align-items:center;gap:6px;}.k-label span{background:#1a3a6b;color:#fff;padding:2px 8px;border-radius:4px;font-size:10px;}.k-point{margin-bottom:18px;}.k-point:last-child{margin-bottom:0;}.k-point-title{font-size:14px;font-weight:700;color:#0D2B5E;margin-bottom:6px;display:flex;align-items:flex-start;gap:6px;}.k-point-title::before{content:'▶';color:#C9A84C;flex-shrink:0;}.k-point p{font-size:14px;color:#444;line-height:1.85;padding-left:14px;}.art-link{display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:700;color:#0D2B5E;padding:12px 0 26px 32px;}.art-link:hover{color:#C9A84C;}.footer{background:#0a1f42;padding:28px 24px;text-align:center;}.footer p{font-size:12px;color:rgba(255,255,255,0.4);}@media(max-width:600px){.hero h1{font-size:21px;}.art-title{font-size:18px;}.art-head,.art-body,.art-link{padding-left:20px;padding-right:20px;}}.nav-bar{background:#132d5e;border-bottom:3px solid #C9A84C;position:sticky;top:0;z-index:999;}.nav-inner{max-width:900px;margin:0 auto;padding:0 20px;display:flex;align-items:center;gap:8px;height:46px;}.nav-btn{display:inline-flex;align-items:center;gap:5px;padding:7px 16px;border-radius:6px;font-size:13px;font-weight:700;text-decoration:none;transition:all .2s;white-space:nowrap;}.nav-btn-latest{background:#C9A84C;color:#0D2B5E;}.nav-btn-archive{background:rgba(255,255,255,0.12);color:#fff;border:1px solid rgba(255,255,255,0.25);}.nav-btn.active-page{opacity:0.55;pointer-events:none;cursor:default;}"""

PROPER_NOUNS = {
    'Myanmar': 'ミャンマー',
    'Aung San Suu Kyi': 'アウンサン・スーチー氏',
    'ASEAN Special Envoy': 'ASEAN特使',
    'Rakhine': 'ラカイン州',
    'Sagaing': 'サガイン地域',
    'Kachin': 'カチン州',
    'Shan': 'シャン州',
    'Karen': 'カレン州',
    'Mandalay': 'マンダレー',
    'Naypyidaw': 'ネピドー',
    'Yangon': 'ヤンゴン',
    'Myitsone Dam': 'ミッソネダム',
}

def get_jst():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=9)

def get_date_info():
    n = get_jst()
    ds = n.strftime('%Y-%m-%d')
    dj = f"{n.year}年{n.month}月{n.day}日（{WEEKDAYS_JA[n.weekday()]}）"
    return ds, dj

def get_next_vol():
    try:
        c = open('archive.html','r',encoding='utf-8').read()
        nums = [int(x) for x in re.findall(r'card-vol\">Vol\.0*(\d+)<', c)]
        return max(nums)+1 if nums else 13
    except:
        return 13

def load_used():
    try:
        return [l.strip() for l in open('used-news.txt','r',encoding='utf-8').read().split('\n')
                if l.strip() and not l.startswith('#')]
    except:
        return []

def fetch_dvb():
    try:
        r = requests.get(DVB_FEED, timeout=15, headers={'User-Agent':'Mozilla/5.0'})
        root = ET.fromstring(r.content)
        items = []
        for item in root.find('channel').findall('item'):
            ce = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
            items.append({'title':item.findtext('title',''),'url':item.findtext('link',''),
                          'content':(ce.text if ce is not None else item.findtext('description','')) or '',
                          'source':'DVB'})
        return items
    except Exception as e:
        print(f"DVBエラー:{e}"); return []

def fetch_bni():
    try:
        r = requests.get(BNI_URL, timeout=15, headers={'User-Agent':'Mozilla/5.0'})
        soup = BeautifulSoup(r.text,'lxml')
        seen,items = set(),[]
        for a in soup.find_all('a', href=re.compile(r'/en/news/')):
            h = a.get('href','')
            if h in seen: continue
            seen.add(h)
            t = a.get_text(strip=True)
            if len(t) > 20:
                url = f"https://www.bnionline.net{h}" if h.startswith('/') else h
                items.append({'title':t,'url':url,'content':'','source':'BNI Online'})
        return items
    except Exception as e:
        print(f"BNIエラー:{e}"); return []

def fetch_detail(url):
    try:
        r = requests.get(url, timeout=15, headers={'User-Agent':'Mozilla/5.0'})
        soup = BeautifulSoup(r.text,'lxml')
        return ' '.join(p.get_text(strip=True) for p in soup.find_all('p')[:12])[:2000]
    except:
        return ''

def translate_to_ja(text):
    if not text or not text.strip():
        return text
    try:
        from deep_translator import GoogleTranslator
        max_len = 4500
        if len(text) <= max_len:
            result = GoogleTranslator(source='en', target='ja').translate(text)
            time.sleep(0.5)
            return result if result else text
        else:
            parts = []
            sentences = text.split('. ')
            chunk = ''
            for s in sentences:
                if len(chunk) + len(s) < max_len:
                    chunk += s + '. '
                else:
                    if chunk:
                        translated = GoogleTranslator(source='en', target='ja').translate(chunk)
                        parts.append(translated if translated else chunk)
                        time.sleep(0.5)
                    chunk = s + '. '
            if chunk:
                translated = GoogleTranslator(source='en', target='ja').translate(chunk)
                parts.append(translated if translated else chunk)
            return ''.join(parts)
    except Exception as e:
        print(f"翻訳エラー:{e}")
        for en, ja in PROPER_NOUNS.items():
            text = text.replace(en, ja)
        return text

def apply_proper_nouns(text):
    for en, ja in PROPER_NOUNS.items():
        text = text.replace(en, ja)
    return text

def categorize(title, content):
    text = (title+' '+content).lower()
    if any(w in text for w in ['military','airstrike','coup','fighting','junta','war','attack','bomb','killed']):
        return 'tp','内戦・軍事'
    if any(w in text for w in ['economy','trade','investment','business','dam','infrastructure','border','price']):
        return 'ts','経済・貿易'
    if any(w in text for w in ['refugee','civilian','humanitarian','rohingya','displaced','human rights','missing']):
        return 'ti','人道・難民'
    return 'tc','文化・社会'

def is_used(title, used_list):
    tl = title.lower()
    for used in used_list:
        ul = used.lower()
        words = [w for w in tl.split() if len(w) > 6]
        if sum(1 for w in words if w in ul) >= 2:
            return True
    return False

def build_kaisetsu(category_label):
    if category_label == '内戦・軍事':
        p1 = "2021年2月の軍事クーデター以降、ミャンマーでは軍政と市民不服従運動（CDM）が続いています。軍の空爆や地上戦により多くの市民が犠牲となり、国内避難民は推計250万人を超えています。"
        p2 = "日本政府は対話を通じた解決を支持しつつ、ASEAN主導の「五項目合意」の実施を求めています。軍政への経済的影響力を持つ中国とインドの動向が、情勢の鍵を握っています。"
        p3 = "日本在住のミャンマー人約6万人の多くが、故郷の家族や友人の安否を心配しています。建設・介護・製造業で活躍するミャンマー人労働者にとって、母国の情勢は精神的に大きな負担となっています。"
    elif category_label == '経済・貿易':
        p1 = "クーデター後の経済制裁と政情不安により、ミャンマーの外国直接投資は大幅に減少しました。一方、中国・タイ・インドとの国境貿易は続いており、一部セクターでは復活の兆しも見られます。"
        p2 = "日本企業はミャンマーからの撤退・縮小が相次ぎましたが、長期的な投資機会として注目し続ける企業もあります。インフラ・エネルギー分野では、民政移管後の再参入を見据えた情報収集が続いています。"
        p3 = "ミャンマーからの技能実習生・特定技能労働者は建設・介護・農業など幅広い分野で活躍しています。NL-DGのような人材紹介企業にとって、ミャンマーの経済状況は採用環境に直接影響します。"
    elif category_label == '人道・難民':
        p1 = "国連の報告によれば、ミャンマー国内の人道的危機は深刻化しており、推計1,800万人以上が人道支援を必要としています。ロヒンギャ問題を含む少数民族への迫害も国際社会から強い批判を受けています。"
        p2 = "国際赤十字や国連難民高等弁務官事務所（UNHCR）が支援活動を続けていますが、軍政による制限で物資の届かない地域が多く存在します。日本のNGOも現地支援に取り組んでいます。"
        p3 = "日本国内のミャンマー人コミュニティは、母国の家族への送金や情報支援を続けています。難民認定や在留資格の問題も、在日ミャンマー人社会の重要な課題となっています。"
    else:
        p1 = "ミャンマーは仏教文化を中心とした豊かな多民族社会ですが、クーデター後は文化的・社会的活動も制限を受けています。若い世代を中心に、海外への移住や難民申請が増加しています。"
        p2 = "日本はミャンマーとの文化・教育交流を重視しており、日本語学習者数はASEAN主要国の中でも高い水準を保っています。政情安定後の人的交流再活性化に向けた準備が民間レベルで続いています。"
        p3 = "在日ミャンマー人は日本社会に溶け込みながら、母国の文化を大切にしています。NL-DGが支援するミャンマー人人材は、建設現場やBIM設計の現場で高い評価を得ています。"
    return p1, p2, p3

def build_article(a, dj):
    title_en = a['title']
    url = a['url']
    src = a['source']
    content_en = a.get('content','')
    tc, tl = categorize(title_en, content_en)
    print(f"  タイトル翻訳中: {title_en[:50]}...")
    ja_title = translate_to_ja(title_en)
    ja_title = apply_proper_nouns(ja_title)
    body_en = content_en[:600] if content_en else title_en
    body_en_clean = re.sub(r'<[^>]+>', '', body_en)
    print(f"  本文翻訳中...")
    ja_body = translate_to_ja(body_en_clean)
    ja_body = apply_proper_nouns(ja_body)
    p1, p2, p3 = build_kaisetsu(tl)
    return f"""
  <div class="article">
    <div class="art-head">
      <div class="art-meta"><span class="tag {tc}">{tl}</span><span class="tag tsrc">{src}</span><span class="art-date">{dj}</span></div>
      <div class="art-title">{ja_title}</div>
      <div class="art-src">出典：{src}　{dj}</div>
    </div>
    <div class="art-body">
      <div class="art-news">{ja_body}</div>
      <div class="kaisetsu">
        <div class="k-label"><span>解説</span>日本人が知っておきたい背景</div>
        <div class="k-point"><div class="k-point-title">背景と経緯</div><p>{p1}</p></div>
        <div class="k-point"><div class="k-point-title">国際社会と日本の対応</div><p>{p2}</p></div>
        <div class="k-point"><div class="k-point-title">日本への影響</div><p>{p3}</p></div>
      </div>
    </div>
    <a class="art-link" href="{url}" target="_blank">→ {src} 原記事を読む</a>
  </div>"""

def update_archive(ds, dj, vs, vn, arts):
    try:
        c = open('archive.html','r',encoding='utf-8').read()
        tags = ''.join(f"<span class='card-tag'>{categorize(a['title'],a.get('content',''))[1]}</span>" for a in arts[:3])
        titles = ''.join(f"<li>{translate_to_ja(a['title'])[:28]}...</li>" for a in arts[:3])
        card = f"\n    <!-- {vs} -->\n    <div class='card'><div class='card-top'><div class='card-vol'>{vs}</div><div class='card-date'>{dj}</div></div><div class='card-body'><div class='card-tags'>{tags}</div><ul class='card-titles'>{titles}</ul></div><div class='card-footer'><a href='news-{ds}.html' class='card-link'>▶ この号を読む</a></div></div>"
        pos = c.find('<div class="grid">') + len('<div class="grid">')
        c = c[:pos] + card + c[pos:]
        c = re.sub(r'(<div class="lb-title">)[^<]*(</div>)', f'\\g<1>{vs} | {dj}\\g<2>', c)
        c = re.sub(r'(<span class="count-badge">)\d+(</span>)', f'\\g<1>{vn}\\g<2>', c)
        open('archive.html','w',encoding='utf-8').write(c)
        print("archive.html更新完了")
    except Exception as e:
        print(f"archive更新エラー:{e}")

def main():
    print("=== ミャンマーニュース自動生成 ===")
    ds, dj = get_date_info()
    vn = get_next_vol()
    vs = f"Vol.{vn:03d}"
    print(f"{ds} / {dj} / {vs}")
    out = f"news-{ds}.html"
    if os.path.exists(out):
        print(f"{out} 既存。スキップ。"); return
    used = load_used()
    dvb = fetch_dvb()
    bni = fetch_bni()
    all_arts = dvb + bni
    selected = []
    for a in all_arts:
        if len(selected) >= 3: break
        if len(a['title']) < 15: continue
        if is_used(a['title'], used): continue
        if not a.get('content'): a['content'] = fetch_detail(a['url'])
        selected.append(a)
        print(f"選定: {a['title'][:60]}")
    if len(selected) < 3:
        for a in all_arts:
            if len(selected) >= 3: break
            if a not in selected:
                if not a.get('content'): a['content'] = fetch_detail(a['url'])
                selected.append(a)
    if not selected:
        print("ERROR: 記事なし"); return
    print("記事を日本語に翻訳中（しばらくお待ちください）...")
    arts_html = ''.join(build_article(a, dj) for a in selected[:3])
    ja_titles = [translate_to_ja(a['title'])[:20] for a in selected[:3]]
    summary_titles = '、'.join(ja_titles)
    summary = f"本日は「{summary_titles}」の3本をお届けします。日本に暮らすミャンマー人と日本企業にとって重要な情報を解説します。"
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
    open(out,'w',encoding='utf-8').write(html)
    print(f"{out} 保存完了 ({len(html)} bytes)")
    shutil.copy(out, 'index.html')
    print("index.html更新完了")
    update_archive(ds, dj, vs, vn, selected[:3])
    cur = open('used-news.txt','r',encoding='utf-8').read()
    add = ''.join(f"\n{ds}|{a['title'][:60]}" for a in selected[:3])
    open('used-news.txt','w',encoding='utf-8').write(cur+add)
    print("used-news.txt更新完了")
    print(f"=== 完了: {vs} ({dj}) ===")

if __name__ == '__main__':
    main()