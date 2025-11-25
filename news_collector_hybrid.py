#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ミャンマーニュース収集ハイブリッド版
NewsAPI + Web Scraping を統合し、重複を排除して10件に厳選
"""

import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import json
from datetime import datetime, timezone, timedelta
import time
import os
from difflib import SequenceMatcher

# 日本時間（JST）
JST = timezone(timedelta(hours=9))

# NewsAPI設定
NEWSAPI_KEY = os.environ.get('NEWSAPI_KEY', '54eacbe065dd4677964af80b966be5a2')
NEWSAPI_BASE_URL = 'https://newsapi.org/v2/everything'

# 翻訳設定
translator_ja = GoogleTranslator(source='auto', target='ja')

# ヘッダー設定
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def similarity(a, b):
    """2つの文字列の類似度を計算（0.0〜1.0）"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def is_duplicate(news_item, news_list, threshold=0.85):
    """重複チェック（タイトルの類似度で判定）"""
    for existing in news_list:
        if similarity(news_item['title_en'], existing['title_en']) > threshold:
            return True
    return False

def translate_text(text, max_length=5000):
    """テキストを日本語に翻訳（長文対応）"""
    if not text:
        return ""
    try:
        # 長すぎる場合は分割
        if len(text) > max_length:
            text = text[:max_length]
        return translator_ja.translate(text)
    except Exception as e:
        print(f"  ⚠️ 翻訳エラー: {e}")
        return text

# ==================== NewsAPI収集 ====================

def fetch_from_newsapi():
    """NewsAPIから各国のミャンマーニュースを収集"""
    print("\n🌍 NewsAPIから収集中...")
    all_news = []
    
    # 検索クエリ（国・地域別）
    queries = [
        {'q': 'Myanmar OR Burma', 'language': 'en', 'country_tag': '🌍国際'},
        {'q': 'Myanmar AND (military OR coup OR crisis)', 'language': 'en', 'country_tag': '🇲🇲ミャンマー'},
        {'q': 'Myanmar AND Thailand', 'language': 'en', 'country_tag': '🇹🇭タイ'},
        {'q': 'Myanmar', 'language': 'en', 'sources': 'the-washington-post,reuters,bbc-news,cnn', 'country_tag': '🇺🇸アメリカ'},
        {'q': 'ミャンマー', 'language': 'ja', 'country_tag': '🇯🇵日本'},
        {'q': '미얀마', 'language': 'ko', 'country_tag': '🇰🇷韓国'},
        {'q': '缅甸', 'language': 'zh', 'country_tag': '🇨🇳中国'},
    ]
    
    for query_config in queries:
        try:
            # APIパラメータ
            params = {
                'apiKey': NEWSAPI_KEY,
                'q': query_config['q'],
                'language': query_config.get('language', 'en'),
                'sortBy': 'publishedAt',
                'pageSize': 5,
                'from': (datetime.now(JST) - timedelta(days=3)).strftime('%Y-%m-%d')
            }
            
            # ソース指定がある場合
            if 'sources' in query_config:
                params['sources'] = query_config['sources']
            
            response = requests.get(NEWSAPI_BASE_URL, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                for article in articles:
                    title_en = article.get('title', '')
                    description_en = article.get('description', '') or article.get('content', '')
                    
                    if not title_en or title_en == '[Removed]':
                        continue
                    
                    # 日本語に翻訳
                    title_ja = translate_text(title_en)
                    summary_ja = translate_text(description_en[:500] if description_en else '')
                    
                    news_item = {
                        'title': title_ja,
                        'title_en': title_en,
                        'summary': summary_ja,
                        'url': article.get('url', ''),
                        'source': f"{query_config['country_tag']} {article.get('source', {}).get('name', 'NewsAPI')}",
                        'published_date': article.get('publishedAt', '')[:10],
                        'country_tag': query_config['country_tag']
                    }
                    
                    # 重複チェック
                    if not is_duplicate(news_item, all_news):
                        all_news.append(news_item)
                        print(f"  ✓ {query_config['country_tag']}: {title_ja[:50]}...")
                
                time.sleep(0.5)  # API制限対策
                
            else:
                print(f"  ⚠️ NewsAPI エラー ({query_config['country_tag']}): {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ NewsAPI 収集エラー ({query_config['country_tag']}): {e}")
    
    print(f"  → NewsAPI: {len(all_news)}件収集")
    return all_news

# ==================== Web Scraping収集 ====================

def fetch_bbc_news():
    """BBC Myanmar ニュース収集（改良版）"""
    print("\n📰 BBC Myanmar から収集中...")
    news_list = []
    
    try:
        url = 'https://www.bbc.com/news/topics/c8nq32jw5r7t'
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # BBC の記事を検索（複数のセレクタを試行）
            articles = soup.select('div[data-testid="edinburgh-card"]')
            
            if not articles:
                articles = soup.select('article')
            
            for article in articles[:5]:
                try:
                    # タイトル取得
                    title_tag = article.find('h2') or article.find('h3')
                    if not title_tag:
                        continue
                    
                    title_en = title_tag.get_text(strip=True)
                    
                    # URL取得
                    link_tag = article.find('a', href=True)
                    if not link_tag:
                        continue
                    
                    article_url = link_tag['href']
                    if not article_url.startswith('http'):
                        article_url = 'https://www.bbc.com' + article_url
                    
                    # 概要取得
                    summary_tag = article.find('p')
                    summary_en = summary_tag.get_text(strip=True) if summary_tag else ''
                    
                    # 翻訳
                    title_ja = translate_text(title_en)
                    summary_ja = translate_text(summary_en) if summary_en else title_ja
                    
                    news_item = {
                        'title': title_ja,
                        'title_en': title_en,
                        'summary': summary_ja,
                        'url': article_url,
                        'source': '🌍国際 BBC News',
                        'published_date': datetime.now(JST).strftime('%Y-%m-%d'),
                        'country_tag': '🌍国際'
                    }
                    
                    news_list.append(news_item)
                    print(f"  ✓ BBC: {title_ja[:50]}...")
                    
                except Exception as e:
                    continue
                    
    except Exception as e:
        print(f"  ❌ BBC 収集エラー: {e}")
    
    print(f"  → BBC: {len(news_list)}件収集")
    return news_list

def fetch_reuters_news():
    """Reuters Myanmar ニュース収集（改良版）"""
    print("\n📰 Reuters Myanmar から収集中...")
    news_list = []
    
    try:
        url = 'https://www.reuters.com/world/asia-pacific/myanmar/'
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Reuters の記事を検索
            articles = soup.select('li[data-testid="MediaStoryCard"]')
            
            if not articles:
                articles = soup.select('article')
            
            for article in articles[:5]:
                try:
                    # タイトル取得
                    title_tag = article.find('h3') or article.find('h2')
                    if not title_tag:
                        continue
                    
                    title_en = title_tag.get_text(strip=True)
                    
                    # URL取得
                    link_tag = article.find('a', href=True)
                    if not link_tag:
                        continue
                    
                    article_url = link_tag['href']
                    if not article_url.startswith('http'):
                        article_url = 'https://www.reuters.com' + article_url
                    
                    # 概要取得
                    summary_tag = article.find('p')
                    summary_en = summary_tag.get_text(strip=True) if summary_tag else ''
                    
                    # 翻訳
                    title_ja = translate_text(title_en)
                    summary_ja = translate_text(summary_en) if summary_en else title_ja
                    
                    news_item = {
                        'title': title_ja,
                        'title_en': title_en,
                        'summary': summary_ja,
                        'url': article_url,
                        'source': '🌍国際 Reuters',
                        'published_date': datetime.now(JST).strftime('%Y-%m-%d'),
                        'country_tag': '🌍国際'
                    }
                    
                    news_list.append(news_item)
                    print(f"  ✓ Reuters: {title_ja[:50]}...")
                    
                except Exception as e:
                    continue
                    
    except Exception as e:
        print(f"  ❌ Reuters 収集エラー: {e}")
    
    print(f"  → Reuters: {len(news_list)}件収集")
    return news_list

def fetch_rfa_news():
    """Radio Free Asia Myanmar ニュース収集（改良版）"""
    print("\n📰 Radio Free Asia Myanmar から収集中...")
    news_list = []
    
    try:
        url = 'https://www.rfa.org/english/news/myanmar'
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # RFA の記事を検索
            articles = soup.select('div.sectionteaser')
            
            if not articles:
                articles = soup.select('article')
            
            for article in articles[:5]:
                try:
                    # タイトル取得
                    title_tag = article.find('h2') or article.find('h3') or article.find('a')
                    if not title_tag:
                        continue
                    
                    title_en = title_tag.get_text(strip=True)
                    
                    # URL取得
                    link_tag = article.find('a', href=True)
                    if not link_tag:
                        continue
                    
                    article_url = link_tag['href']
                    if not article_url.startswith('http'):
                        article_url = 'https://www.rfa.org' + article_url
                    
                    # 概要取得
                    summary_tag = article.find('p')
                    summary_en = summary_tag.get_text(strip=True) if summary_tag else ''
                    
                    # 翻訳
                    title_ja = translate_text(title_en)
                    summary_ja = translate_text(summary_en) if summary_en else title_ja
                    
                    news_item = {
                        'title': title_ja,
                        'title_en': title_en,
                        'summary': summary_ja,
                        'url': article_url,
                        'source': '🇺🇸アメリカ Radio Free Asia',
                        'published_date': datetime.now(JST).strftime('%Y-%m-%d'),
                        'country_tag': '🇺🇸アメリカ'
                    }
                    
                    news_list.append(news_item)
                    print(f"  ✓ RFA: {title_ja[:50]}...")
                    
                except Exception as e:
                    continue
                    
    except Exception as e:
        print(f"  ❌ RFA 収集エラー: {e}")
    
    print(f"  → RFA: {len(news_list)}件収集")
    return news_list

def fetch_irrawaddy_news():
    """The Irrawaddy ニュース収集（ミャンマー国内メディア）"""
    print("\n📰 The Irrawaddy から収集中...")
    news_list = []
    
    try:
        url = 'https://www.irrawaddy.com/'
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 記事を検索
            articles = soup.select('article')
            
            for article in articles[:5]:
                try:
                    # タイトル取得
                    title_tag = article.find('h2') or article.find('h3')
                    if not title_tag:
                        continue
                    
                    title_en = title_tag.get_text(strip=True)
                    
                    # URL取得
                    link_tag = title_tag.find('a', href=True) or article.find('a', href=True)
                    if not link_tag:
                        continue
                    
                    article_url = link_tag['href']
                    if not article_url.startswith('http'):
                        article_url = 'https://www.irrawaddy.com' + article_url
                    
                    # 概要取得
                    summary_tag = article.find('p')
                    summary_en = summary_tag.get_text(strip=True) if summary_tag else ''
                    
                    # 翻訳
                    title_ja = translate_text(title_en)
                    summary_ja = translate_text(summary_en) if summary_en else title_ja
                    
                    news_item = {
                        'title': title_ja,
                        'title_en': title_en,
                        'summary': summary_ja,
                        'url': article_url,
                        'source': '🇲🇲ミャンマー The Irrawaddy',
                        'published_date': datetime.now(JST).strftime('%Y-%m-%d'),
                        'country_tag': '🇲🇲ミャンマー'
                    }
                    
                    news_list.append(news_item)
                    print(f"  ✓ Irrawaddy: {title_ja[:50]}...")
                    
                except Exception as e:
                    continue
                    
    except Exception as e:
        print(f"  ❌ Irrawaddy 収集エラー: {e}")
    
    print(f"  → Irrawaddy: {len(news_list)}件収集")
    return news_list

# ==================== メイン処理 ====================

def main():
    """メイン処理：全ソースから収集して統合"""
    print("=" * 60)
    print("📰 ミャンマーニュース収集ハイブリッド版を開始...")
    print("=" * 60)
    
    all_news = []
    
    # NewsAPI から収集
    newsapi_articles = fetch_from_newsapi()
    all_news.extend(newsapi_articles)
    
    # Web Scraping から収集
    bbc_articles = fetch_bbc_news()
    reuters_articles = fetch_reuters_news()
    rfa_articles = fetch_rfa_news()
    irrawaddy_articles = fetch_irrawaddy_news()
    
    # 統合（重複排除しながら）
    for article in (bbc_articles + reuters_articles + rfa_articles + irrawaddy_articles):
        if not is_duplicate(article, all_news, threshold=0.85):
            all_news.append(article)
    
    print("\n" + "=" * 60)
    print(f"📊 合計: {len(all_news)}件のニュースを収集")
    print("=" * 60)
    
    # 最新順にソート
    all_news.sort(key=lambda x: x.get('published_date', ''), reverse=True)
    
    # 上位10件を厳選
    top_10_news = all_news[:10]
    
    # JSONファイルに保存
    output_file = 'myanmar_news_top10.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(top_10_news, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完了！{len(top_10_news)}件のニュースを保存しました")
    print("=" * 60)
    
    # 統計情報を表示
    country_counts = {}
    for news in top_10_news:
        tag = news.get('country_tag', '不明')
        country_counts[tag] = country_counts.get(tag, 0) + 1
    
    print("\n📊 国別統計:")
    for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {country}: {count}件")
    print("=" * 60)

if __name__ == '__main__':
    main()
