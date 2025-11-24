import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import json
from datetime import datetime

def translate_to_japanese(text):
    """テキストを日本語に翻訳"""
    try:
        translator = GoogleTranslator(source='auto', target='ja')
        return translator.translate(text)
    except:
        return text

def collect_bbc_news():
    """BBCニュースを収集"""
    news_list = []
    try:
        url = "https://www.bbc.com/news/topics/c8nq32jw5r7t"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = soup.find_all('div', {'data-testid': 'card-text-wrapper'}, limit=5)
        
        for article in articles:
            try:
                title_tag = article.find('h2')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    link_tag = article.find('a')
                    link = "https://www.bbc.com" + link_tag['href'] if link_tag and link_tag.get('href') else ""
                    
                    news_list.append({
                        'title': title,
                        'title_ja': translate_to_japanese(title),
                        'url': link,
                        'source': 'BBC News',
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
            except:
                continue
    except:
        pass
    
    return news_list

def collect_reuters_news():
    """Reutersニュースを収集"""
    news_list = []
    try:
        url = "https://www.reuters.com/world/asia-pacific/myanmar/"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = soup.find_all('a', {'data-testid': 'Heading'}, limit=5)
        
        for article in articles:
            try:
                title = article.get_text(strip=True)
                link = "https://www.reuters.com" + article['href'] if article.get('href') else ""
                
                news_list.append({
                    'title': title,
                    'title_ja': translate_to_japanese(title),
                    'url': link,
                    'source': 'Reuters',
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
            except:
                continue
    except:
        pass
    
    return news_list

def main():
    """メイン処理"""
    print("📰 ニュース収集を開始...")
    
    all_news = []
    
    # BBCから収集
    print("  → BBC News から収集中...")
    bbc_news = collect_bbc_news()
    all_news.extend(bbc_news)
    print(f"  ✓ BBC: {len(bbc_news)}件")
    
    # Reutersから収集
    print("  → Reuters から収集中...")
    reuters_news = collect_reuters_news()
    all_news.extend(reuters_news)
    print(f"  ✓ Reuters: {len(reuters_news)}件")
    
    # トップ10を選択
    top_10 = all_news[:10]
    
    # JSONに保存
    with open('myanmar_news_top10.json', 'w', encoding='utf-8') as f:
        json.dump(top_10, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完了！合計 {len(top_10)} 件のニュースを保存しました")

if __name__ == "__main__":
    main()
