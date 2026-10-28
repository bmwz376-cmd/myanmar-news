#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公開前チェック（myn_rules.md 準拠）
- 画面テキストに許可略称・ブランド名以外の英単語（4文字以上）が1つでもあればNG
- 記事ごとにタイトル・本文・解説3ポイントが日本語、解説は各100文字以上
- タイトル・本文・解説の日本語率90%以上
使い方: python scripts/check_japanese.py [ファイル ...]   （省略時は全HTML）
終了コード 0=全合格 / 1=不合格あり
"""
import re, sys, glob, html as H

ALLOW = set("""ASEAN DVB NUG NLD UN ICC IDP IDPS NGO KIA KIO KNU KNPP CNF AA ULA TNLA MNDAA SAC PDF BGF ICRC OCHA IOM USAID LPG NL-DG MYANMAR NEWS BNI IIMM ACLED UNHCR HRW CRPH SCEF USDP UFC NED FATF AAPP CDM ABSDF NCA BHRN FCCT CHRO GSCB ISP JFM DPNS KSCC IEC AHA PRF MNHRC SEANF IBA BRICS HIV MRTV CNN GMMTV IDPN UMS WAG TPS USCIS NIA ROC ECW CEO SNS DMG ICPO PBS KNLA MMK USD EU NHK JICA RAY""".split())

def is_abbr(w):
    return w.upper() in ALLOW or re.fullmatch(r'[A-Z0-9]+(?:-[A-Z0-9]+)*-?', w) is not None

def visible_text(h):
    h = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>|<!--[\s\S]*?-->', ' ', h, flags=re.I)
    t = re.sub(r'<[^>]+>', '\n', h)
    t = re.sub(r'&[a-zA-Z#0-9]+;', ' ', t)
    t = re.sub(r'https?://\S+|[\w.-]+\.(?:app|com|org|net|no)\b\S*', ' ', t)
    return t

def english_words(t):
    t = t.replace('NL-DG MYANMAR NEWS', ' ')
    return [w for w in re.findall(r'[A-Za-z][A-Za-z0-9\-]*', t)
            if len(w.replace('-', '')) >= 4 and not is_abbr(w)]

def ja_ratio(s):
    s = re.sub(r'[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*', lambda m: '' if is_abbr(m.group()) else m.group(), s)
    s = re.sub(r'[\s\d\W_]', '', s)
    if not s:
        return 1.0
    ja = len(re.findall(r'[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9f]', s))
    return ja / len(s)

def check_html(h, name=''):
    ng = []
    w = english_words(visible_text(h))
    if w:
        ng.append('英単語: ' + ','.join(list(dict.fromkeys(w))[:8]))
    for m in re.finditer(r'<div class="article">([\s\S]*?)<a class="art-link"', h):
        a = m.group(1)
        t = re.search(r'<div class="art-title">([\s\S]*?)</div>', a)
        b = re.search(r'<div class="art-news">([\s\S]*?)</div>', a)
        if t and ja_ratio(visible_text(t.group(1))) < 0.9:
            ng.append('タイトル日本語率不足')
        if b and ja_ratio(visible_text(b.group(1))) < 0.9:
            ng.append('本文日本語率不足')
        if 'class="kaisetsu"' in a:
            ks = [visible_text(x).strip() for x in re.findall(r'<div class="k-point">[\s\S]*?<p>([\s\S]*?)</p>', a)]
            if len(ks) < 3:
                ng.append(f'解説{len(ks)}点のみ')
            for i, k in enumerate(ks, 1):
                if len(k) < 100:
                    ng.append(f'解説{i}が{len(k)}字')
                if ja_ratio(k) < 0.9:
                    ng.append(f'解説{i}日本語率不足')
    return list(dict.fromkeys(ng))

def main(files):
    files = files or sorted(f for f in glob.glob('*.html') if f != 'sample-article.html')
    bad = 0
    for f in files:
        ng = check_html(open(f, encoding='utf-8').read(), f)
        if ng:
            bad += 1
            print(f'NG {f}: ' + ' / '.join(ng))
    print(f'公開前チェック: {len(files)}ファイル中 合格{len(files)-bad} 不合格{bad}')
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
