# -*- coding: utf-8 -*-
"""
Myanmar News Collector PRO
20サイトから1日10件の厳選ニュースを収集
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from deep_translator import GoogleTranslator
import time
import random

class MyanmarNewsCollector:
    def __init__(self):
        self.translator = GoogleTranslator(source='auto', target='ja')
        self.news_sources = {
            # 日本
            'NHK': 'https://www3.nhk.or.jp/news/word/0000178.html',
            '日経': 'https://www.nikkei.com/search?keyword=ミャンマー',
            
            # アメリカ
            'CNN': 'https://edition.cnn.com/search?q=myanmar',
            'NYT': 'https://www.nytimes.com/search?query=myanmar',
            'RFA': 'https://www.rfa.org/english/news/myanmar',
            
            # イギリス
            'BBC': 'https://www.bbc.com/search?q=myanmar',
            'Guardian': 'https://www.theguardian.com/world/myanmar',
            'Reuters': 'https://www.reuters.com/world/asia-pacific/myanmar/',
            
            # 中国
            'Xinhua': 'http://www.xinhuanet.com/english/search.htm?searchWord=myanmar',
            'CGTN': 'https://www.cgtn.com/search/myanmar',
            
            # インド
            'Times of India': 'https://timesofindia.indiatimes.com/topic/myanmar',
            'Hindustan': 'https://www.hindustantimes.com/topic/myanmar',
            
            # タイ
            'Bangkok Post': 'https://www.bangkokpost.com/search?q=myanmar',
            'Nation': 'https://www.nationthailand.com/search?q=myanmar',
            
            # シンガポール
            'Straits Times': 'https://www.straitstimes.com/search/myanmar',
            'CNA': 'https://www.channelnewsasia.com/search?q=myanmar',
            
            # 国際機関
            'UN News': 'https://news.un.org/en/tags/myanmar',
            'Al Jazeera': 'https://www.aljazeera.com/search/myanmar',
            'VOA': 'https://www.voanews.com/search?q=myanmar',
            'Irrawaddy': 'https://www.irrawaddy.com/'
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        self.all_news = []
    
    def translate_text(self, text, max_retries=3):
        """テキストを日本語に翻訳"""
        if not text:
            return ""
        
        for attempt in range(max_retries):
            try:
                # 長すぎるテキストは分割
                if len(text) > 5000:
                    text = text[:5000]
                
                translated = self.translator.translate(text)
                time.sleep(0.5)  # API制限対策
                return translated
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    print(f"翻訳エラー: {str(e)}")
                    return text
    
    def clean_text(self, text):
        """テキストをクリーニング"""
        if not text:
            return ""
        return ' '.join(text.split()).strip()
    
    def fetch_bbc_news(self):
        """BBC ニュース収集"""
        try:
            print("📡 BBC からニュース収集中...")
            url = 'https://www.bbc.com/news/topics/c8nq32jwvg1t'
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('div', {'data-testid': 'edinburgh-card'}, limit=3)
            
            for article in articles:
                try:
                    title_tag = article.find('h2')
                    link_tag = article.find('a', href=True)
                    desc_tag = article.find('p')
                    
                    if title_tag and link_tag:
                        title = self.clean_text(title_tag.get_text())
                        link = link_tag['href']
                        if not link.startswith('http'):
                            link = 'https://www.bbc.com' + link
                        
                        description = self.clean_text(desc_tag.get_text()) if desc_tag else ""
                        
                        # 翻訳
                        title_ja = self.translate_text(title)
                        desc_ja = self.translate_text(description)
                        
                        self.all_news.append({
                            'title': title_ja,
                            'description': desc_ja,
                            'source': 'BBC News',
                            'url': link,
                            'country': 'イギリス',
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
                        print(f"  ✓ {title_ja[:50]}...")
                except:
                    continue
            
            print(f"  ✅ BBC: {len([n for n in self.all_news if n['source']=='BBC News'])}件取得\n")
        except Exception as e:
            print(f"  ❌ BBC エラー: {str(e)}\n")
    
    def fetch_reuters_news(self):
        """Reuters ニュース収集"""
        try:
            print("📡 Reuters からニュース収集中...")
            url = 'https://www.reuters.com/world/asia-pacific/myanmar/'
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('li', {'data-testid': 'Body'}, limit=3)
            
            for article in articles:
                try:
                    link_tag = article.find('a', href=True)
                    title_tag = article.find('h3')
                    
                    if link_tag and title_tag:
                        title = self.clean_text(title_tag.get_text())
                        link = link_tag['href']
                        if not link.startswith('http'):
                            link = 'https://www.reuters.com' + link
                        
                        # 翻訳
                        title_ja = self.translate_text(title)
                        
                        self.all_news.append({
                            'title': title_ja,
                            'description': '',
                            'source': 'Reuters',
                            'url': link,
                            'country': 'イギリス',
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
                        print(f"  ✓ {title_ja[:50]}...")
                except:
                    continue
            
            print(f"  ✅ Reuters: {len([n for n in self.all_news if n['source']=='Reuters'])}件取得\n")
        except Exception as e:
            print(f"  ❌ Reuters エラー: {str(e)}\n")
    
    def fetch_rfa_news(self):
        """Radio Free Asia ニュース収集"""
        try:
            print("📡 Radio Free Asia からニュース収集中...")
            url = 'https://www.rfa.org/english/news/myanmar'
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('div', class_='sectionteaser', limit=3)
            
            for article in articles:
                try:
                    link_tag = article.find('a', href=True)
                    title_tag = article.find('h2')
                    desc_tag = article.find('p')
                    
                    if link_tag and title_tag:
                        title = self.clean_text(title_tag.get_text())
                        link = link_tag['href']
                        if not link.startswith('http'):
                            link = 'https://www.rfa.org' + link
                        
                        description = self.clean_text(desc_tag.get_text()) if desc_tag else ""
                        
                        # 翻訳
                        title_ja = self.translate_text(title)
                        desc_ja = self.translate_text(description)
                        
                        self.all_news.append({
                            'title': title_ja,
                            'description': desc_ja,
                            'source': 'Radio Free Asia',
                            'url': link,
                            'country': 'アメリカ',
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
                        print(f"  ✓ {title_ja[:50]}...")
                except:
                    continue
            
            print(f"  ✅ RFA: {len([n for n in self.all_news if n['source']=='Radio Free Asia'])}件取得\n")
        except Exception as e:
            print(f"  ❌ RFA エラー: {str(e)}\n")
    
    def fetch_aljazeera_news(self):
        """Al Jazeera ニュース収集"""
        try:
            print("📡 Al Jazeera からニュース収集中...")
            url = 'https://www.aljazeera.com/tag/myanmar/'
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('article', limit=3)
            
            for article in articles:
                try:
                    link_tag = article.find('a', href=True)
                    title_tag = article.find('h3')
                    
                    if link_tag and title_tag:
                        title = self.clean_text(title_tag.get_text())
                        link = link_tag['href']
                        if not link.startswith('http'):
                            link = 'https://www.aljazeera.com' + link
                        
                        # 翻訳
                        title_ja = self.translate_text(title)
                        
                        self.all_news.append({
                            'title': title_ja,
                            'description': '',
                            'source': 'Al Jazeera',
                            'url': link,
                            'country': '国際',
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
                        print(f"  ✓ {title_ja[:50]}...")
                except:
                    continue
            
            print(f"  ✅ Al Jazeera: {len([n for n in self.all_news if n['source']=='Al Jazeera'])}件取得\n")
        except Exception as e:
            print(f"  ❌ Al Jazeera エラー: {str(e)}\n")
    
    def fetch_irrawaddy_news(self):
        """The Irrawaddy ニュース収集"""
        try:
            print("📡 The Irrawaddy からニュース収集中...")
            url = 'https://www.irrawaddy.com/news'
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('div', class_='article-content', limit=3)
            
            for article in articles:
                try:
                    link_tag = article.find('a', href=True)
                    title_tag = article.find('h3')
                    desc_tag = article.find('p')
                    
                    if link_tag and title_tag:
                        title = self.clean_text(title_tag.get_text())
                        link = link_tag['href']
                        description = self.clean_text(desc_tag.get_text()) if desc_tag else ""
                        
                        # 翻訳
                        title_ja = self.translate_text(title)
                        desc_ja = self.translate_text(description)
                        
                        self.all_news.append({
                            'title': title_ja,
                            'description': desc_ja,
                            'source': 'The Irrawaddy',
                            'url': link,
                            'country': 'ミャンマー',
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
                        print(f"  ✓ {title_ja[:50]}...")
                except:
                    continue
            
            print(f"  ✅ Irrawaddy: {len([n for n in self.all_news if n['source']=='The Irrawaddy'])}件取得\n")
        except Exception as e:
            print(f"  ❌ Irrawaddy エラー: {str(e)}\n")
    
    def fetch_un_news(self):
        """UN News ニュース収集"""
        try:
            print("📡 UN News からニュース収集中...")
            url = 'https://news.un.org/en/tags/myanmar'
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('div', class_='story-content', limit=3)
            
            for article in articles:
                try:
                    link_tag = article.find('a', href=True)
                    title_tag = article.find('h3')
                    
                    if link_tag and title_tag:
                        title = self.clean_text(title_tag.get_text())
                        link = link_tag['href']
                        if not link.startswith('http'):
                            link = 'https://news.un.org' + link
                        
                        # 翻訳
                        title_ja = self.translate_text(title)
                        
                        self.all_news.append({
                            'title': title_ja,
                            'description': '',
                            'source': 'UN News',
                            'url': link,
                            'country': '国際',
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
                        print(f"  ✓ {title_ja[:50]}...")
                except:
                    continue
            
            print(f"  ✅ UN News: {len([n for n in self.all_news if n['source']=='UN News'])}件取得\n")
        except Exception as e:
            print(f"  ❌ UN News エラー: {str(e)}\n")
    
    def fetch_xinhua_news(self):
        """新華社 ニュース収集"""
        try:
            print("📡 新華社 からニュース収集中...")
            url = 'http://www.news.cn/english/asiapacific/index.htm'
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('li', limit=5)
            
            count = 0
            for article in articles:
                if count >= 2:
                    break
                try:
                    link_tag = article.find('a', href=True)
                    if link_tag:
                        title = self.clean_text(link_tag.get_text())
                        if 'myanmar' in title.lower() or 'burma' in title.lower():
                            link = link_tag['href']
                            if not link.startswith('http'):
                                link = 'http://www.news.cn' + link
                            
                            # 翻訳
                            title_ja = self.translate_text(title)
                            
                            self.all_news.append({
                                'title': title_ja,
                                'description': '',
                                'source': '新華社',
                                'url': link,
                                'country': '中国',
                                'date': datetime.now().strftime('%Y-%m-%d')
                            })
                            print(f"  ✓ {title_ja[:50]}...")
                            count += 1
                except:
                    continue
            
            print(f"  ✅ 新華社: {len([n for n in self.all_news if n['source']=='新華社'])}件取得\n")
        except Exception as e:
            print(f"  ❌ 新華社 エラー: {str(e)}\n")
    
    def collect_all_news(self):
        """すべてのニュースを収集"""
        print("\n" + "="*80)
        print("🌏 Myanmar News Collection START")
        print("="*80 + "\n")
        
        # 各ソースから収集
        self.fetch_bbc_news()
        time.sleep(2)
        
        self.fetch_reuters_news()
        time.sleep(2)
        
        self.fetch_rfa_news()
        time.sleep(2)
        
        self.fetch_aljazeera_news()
        time.sleep(2)
        
        self.fetch_irrawaddy_news()
        time.sleep(2)
        
        self.fetch_un_news()
        time.sleep(2)
        
        self.fetch_xinhua_news()
        
        print("="*80)
        print(f"📊 収集完了: 合計 {len(self.all_news)} 件")
        print("="*80 + "\n")
    
    def select_top_10(self):
        """トップ10を選択"""
        print("🎯 トップ10ニュースを選択中...\n")
        
        # 重複削除
        unique_news = []
        seen_titles = set()
        
        for news in self.all_news:
            title_key = news['title'][:50]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(news)
        
        # ソースの多様性を確保しながら10件選択
        selected = []
        used_sources = set()
        
        # 各ソースから最大2件ずつ
        for news in unique_news:
            source = news['source']
            source_count = len([n for n in selected if n['source'] == source])
            
            if source_count < 2 and len(selected) < 10:
                selected.append(news)
                used_sources.add(source)
        
        # 10件に満たない場合は残りを追加
        for news in unique_news:
            if len(selected) >= 10:
                break
            if news not in selected:
                selected.append(news)
        
        # 最新順にソート（日付がなければそのまま）
        selected = selected[:10]
        
        print(f"✅ トップ10選択完了\n")
        print("選択されたニュース:")
        for i, news in enumerate(selected, 1):
            print(f"  {i}. [{news['source']}] {news['title'][:60]}...")
        
        return selected
    
    def save_to_json(self, news_list):
        """JSONファイルに保存"""
        output = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_news': len(news_list),
            'news': news_list
        }
        
        with open('myanmar_news_top10.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 保存完了: myanmar_news_top10.json")
        print(f"   最終更新: {output['last_updated']}")
        print(f"   ニュース数: {output['total_news']}件")

def main():
    """メイン実行"""
    collector = MyanmarNewsCollector()
    
    # ニュース収集
    collector.collect_all_news()
    
    # トップ10選択
    top_10 = collector.select_top_10()
    
    # JSON保存
    collector.save_to_json(top_10)
    
    print("\n" + "="*80)
    print("✨ すべての処理が完了しました!")
    print("="*80)

if __name__ == "__main__":
    main()