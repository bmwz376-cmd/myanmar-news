import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import json
from datetime import datetime
import time

def translate_to_japanese(text):
    """テキストを日本語に翻訳"""
    try:
        if not text or len(text) > 5000:
            return text
        translator = GoogleTranslator(source='auto', target='ja')
        time.sleep(0.5)  # 翻訳API制限対策
        return translator.translate(text)
    except Exception as e:
        print(f"  ✗ 翻訳エラー: {e}")
        return text

def collect_bbc_myanmar():
    """BBC Myanmar ニュースを収集"""
    news_list = []
    try:
        print("  → BBC Myanmar から収集中...")
        url = "https://www.bbc.com/news/topics/c8nq32jw5r7t"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = soup.find_all(['div', 'article'], limit=10)
        
        for article in articles:
            try:
                title_tag = article.find(['h2', 'h3', 'a'])
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    if len(title) < 10 or 'Myanmar' not in title and 'Burma' not in title:
                        continue
                    
                    link_tag = article.find('a', href=True)
                    link = link_tag['href'] if link_tag else ""
                    if link and not link.startswith('http'):
                        link = "https://www.bbc.com" + link
                    
                    if title and link:
                        news_list.append({
                            'title': title,
                            'title_ja': translate_to_japanese(title),
                            'url': link,
                            'source': 'BBC News',
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
                        print(f"  ✓ BBC: {title[:50]}...")
            except Exception as e:
                continue
        
        print(f"  ✓ BBC: {len(news_list)}件収集")
    except Exception as e:
        print(f"  ✗ BBCエラー: {e}")
    
    return news_list

def collect_reuters_myanmar():
    """Reuters Myanmar ニュースを収集"""
    news_list = []
    try:
        print("  → Reuters Myanmar から収集中...")
        url = "https://www.reuters.com/world/asia-pacific/myanmar/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = soup.find_all('a', {'data-testid': 'Heading'}, limit=10)
        
        for article in articles:
            try:
                title = article.get_text(strip=True)
                if len(title) < 10:
                    continue
                    
                link = article.get('href', '')
                if link and not link.startswith('http'):
                    link = "https://www.reuters.com" + link
                
                if title and link:
                    news_list.append({
                        'title': title,
                        'title_ja': translate_to_japanese(title),
                        'url': link,
                        'source': 'Reuters',
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
                    print(f"  ✓ Reuters: {title[:50]}...")
            except Exception as e:
                continue
        
        print(f"  ✓ Reuters: {len(news_list)}件収集")
    except Exception as e:
        print(f"  ✗ Reutersエラー: {e}")
    
    return news_list

def collect_rfa_myanmar():
    """Radio Free Asia Myanmar ニュースを収集"""
    news_list = []
    try:
        print("  → Radio Free Asia Myanmar から収集中...")
        url = "https://www.rfa.org/english/news/myanmar"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = soup.find_all(['h2', 'h3', 'div'], class_=['story', 'title'], limit=10)
        
        for article in articles:
            try:
                title_tag = article.find('a') or article
                title = title_tag.get_text(strip=True)
                
                if len(title) < 10:
                    continue
                
                link_tag = article.find('a', href=True)
                link = link_tag['href'] if link_tag else ""
                if link and not link.startswith('http'):
                    link = "https://www.rfa.org" + link
                
                if title and link:
                    news_list.append({
                        'title': title,
                        'title_ja': translate_to_japanese(title),
                        'url': link,
                        'source': 'Radio Free Asia',
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
                    print(f"  ✓ RFA: {title[:50]}...")
            except Exception as e:
                continue
        
        print(f"  ✓ RFA: {len(news_list)}件収集")
    except Exception as e:
        print(f"  ✗ RFAエラー: {e}")
    
    return news_list

def main():
    """メイン処理"""
    print("📰 ミャンマーニュース収集を開始...")
    print("=" * 50)
    
    all_news = []
    
    # 各サイトから収集
    all_news.extend(collect_bbc_myanmar())
    all_news.extend(collect_reuters_myanmar())
    all_news.extend(collect_rfa_myanmar())
    
    print("=" * 50)
    print(f"📊 合計: {len(all_news)}件のニュースを収集")
    
    # 重複を削除（タイトルが同じものを除外）
    seen_titles = set()
    unique_news = []
    for news in all_news:
        if news['title'] not in seen_titles:
            seen_titles.add(news['title'])
            unique_news.append(news)
    
    # トップ10を選択
    top_10 = unique_news[:10]
    
    # JSONに保存
    with open('myanmar_news_top10.json', 'w', encoding='utf-8') as f:
        json.dump(top_10, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完了！{len(top_10)}件のニュースを保存しました")
    print("=" * 50)
    
    # 保存したニュースのタイトルを表示
    for i, news in enumerate(top_10, 1):
        print(f"{i}. [{news['source']}] {news['title_ja'][:60]}...")

if __name__ == "__main__":
    main()
