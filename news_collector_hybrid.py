  1	#!/usr/bin/env python3
     2	# -*- coding: utf-8 -*-
     3	"""
     4	ミャンマーニュース収集ハイブリッド版
     5	NewsAPI + Web Scraping を統合し、重複を排除して10件に厳選
     6	"""
     7	
     8	import requests
     9	from bs4 import BeautifulSoup
    10	from deep_translator import GoogleTranslator
    11	import json
    12	from datetime import datetime, timezone, timedelta
    13	import time
    14	import os
    15	from difflib import SequenceMatcher
    16	
    17	# 日本時間（JST）
    18	JST = timezone(timedelta(hours=9))
    19	
    20	# NewsAPI設定
    21	NEWSAPI_KEY = os.environ.get('NEWSAPI_KEY', '54eacbe065dd4677964af80b966be5a2')
    22	NEWSAPI_BASE_URL = 'https://newsapi.org/v2/everything'
    23	
    24	# 翻訳設定
    25	translator_ja = GoogleTranslator(source='auto', target='ja')
    26	
    27	# ヘッダー設定
    28	HEADERS = {
    29	    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    30	}
    31	
    32	def similarity(a, b):
    33	    """2つの文字列の類似度を計算（0.0〜1.0）"""
    34	    return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    35	
    36	def is_duplicate(news_item, news_list, threshold=0.85):
    37	    """重複チェック（タイトルの類似度で判定）"""
    38	    for existing in news_list:
    39	        if similarity(news_item['title_en'], existing['title_en']) > threshold:
    40	            return True
    41	    return False
    42	
    43	def translate_text(text, max_length=5000):
    44	    """テキストを日本語に翻訳（長文対応）"""
    45	    if not text:
    46	        return ""
    47	    try:
    48	        # 長すぎる場合は分割
    49	        if len(text) > max_length:
    50	            text = text[:max_length]
    51	        return translator_ja.translate(text)
    52	    except Exception as e:
    53	        print(f"  ⚠️ 翻訳エラー: {e}")
    54	        return text
    55	
    56	# ==================== NewsAPI収集 ====================
    57	
    58	def fetch_from_newsapi():
    59	    """NewsAPIから各国のミャンマーニュースを収集"""
    60	    print("\n🌍 NewsAPIから収集中...")
    61	    all_news = []
    62	    
    63	    # 検索クエリ（国・地域別）
    64	    queries = [
    65	        {'q': 'Myanmar OR Burma', 'language': 'en', 'country_tag': '🌍国際'},
    66	        {'q': 'Myanmar AND (military OR coup OR crisis)', 'language': 'en', 'country_tag': '🇲🇲ミャンマー'},
    67	        {'q': 'Myanmar AND Thailand', 'language': 'en', 'country_tag': '🇹🇭タイ'},
    68	        {'q': 'Myanmar', 'language': 'en', 'sources': 'the-washington-post,reuters,bbc-news,cnn', 'country_tag': '🇺🇸アメリカ'},
    69	        {'q': 'ミャンマー', 'language': 'ja', 'country_tag': '🇯🇵日本'},
    70	        {'q': '미얀마', 'language': 'ko', 'country_tag': '🇰🇷韓国'},
    71	        {'q': '缅甸', 'language': 'zh', 'country_tag': '🇨🇳中国'},
    72	    ]
    73	    
    74	    for query_config in queries:
    75	        try:
    76	            # APIパラメータ
    77	            params = {
    78	                'apiKey': NEWSAPI_KEY,
    79	                'q': query_config['q'],
    80	                'language': query_config.get('language', 'en'),
    81	                'sortBy': 'publishedAt',
    82	                'pageSize': 5,
    83	                'from': (datetime.now(JST) - timedelta(days=3)).strftime('%Y-%m-%d')
    84	            }
    85	            
    86	            # ソース指定がある場合
    87	            if 'sources' in query_config:
    88	                params['sources'] = query_config['sources']
    89	            
    90	            response = requests.get(NEWSAPI_BASE_URL, params=params, timeout=10)
    91	            
    92	            if response.status_code == 200:
    93	                data = response.json()
    94	                articles = data.get('articles', [])
    95	                
    96	                for article in articles:
    97	                    title_en = article.get('title', '')
    98	                    description_en = article.get('description', '') or article.get('content', '')
    99	                    
   100	                    if not title_en or title_en == '[Removed]':
   101	                        continue
   102	                    
   103	                    # 日本語に翻訳
   104	                    title_ja = translate_text(title_en)
   105	                    summary_ja = translate_text(description_en[:500] if description_en else '')
   106	                    
   107	                    news_item = {
   108	                        'title': title_ja,
   109	                        'title_en': title_en,
   110	                        'summary': summary_ja,
   111	                        'url': article.get('url', ''),
   112	                        'source': f"{query_config['country_tag']} {article.get('source', {}).get('name', 'NewsAPI')}",
   113	                        'published_date': article.get('publishedAt', '')[:10],
   114	                        'country_tag': query_config['country_tag']
   115	                    }
   116	                    
   117	                    # 重複チェック
   118	                    if not is_duplicate(news_item, all_news):
   119	                        all_news.append(news_item)
   120	                        print(f"  ✓ {query_config['country_tag']}: {title_ja[:50]}...")
   121	                
   122	                time.sleep(0.5)  # API制限対策
   123	                
   124	            else:
   125	                print(f"  ⚠️ NewsAPI エラー ({query_config['country_tag']}): {response.status_code}")
   126	                
   127	        except Exception as e:
   128	            print(f"  ❌ NewsAPI 収集エラー ({query_config['country_tag']}): {e}")
   129	    
   130	    print(f"  → NewsAPI: {len(all_news)}件収集")
   131	    return all_news
   132	
   133	# ==================== Web Scraping収集 ====================
   134	
   135	def fetch_bbc_news():
   136	    """BBC Myanmar ニュース収集（改良版）"""
   137	    print("\n📰 BBC Myanmar から収集中...")
   138	    news_list = []
   139	    
   140	    try:
   141	        url = 'https://www.bbc.com/news/topics/c8nq32jw5r7t'
   142	        response = requests.get(url, headers=HEADERS, timeout=15)
   143	        
   144	        if response.status_code == 200:
   145	            soup = BeautifulSoup(response.content, 'html.parser')
   146	            
   147	            # BBC の記事を検索（複数のセレクタを試行）
   148	            articles = soup.select('div[data-testid="edinburgh-card"]')
   149	            
   150	            if not articles:
   151	                articles = soup.select('article')
   152	            
   153	            for article in articles[:5]:
   154	                try:
   155	                    # タイトル取得
   156	                    title_tag = article.find('h2') or article.find('h3')
   157	                    if not title_tag:
   158	                        continue
   159	                    
   160	                    title_en = title_tag.get_text(strip=True)
   161	                    
   162	                    # URL取得
   163	                    link_tag = article.find('a', href=True)
   164	                    if not link_tag:
   165	                        continue
   166	                    
   167	                    article_url = link_tag['href']
   168	                    if not article_url.startswith('http'):
   169	                        article_url = 'https://www.bbc.com' + article_url
   170	                    
   171	                    # 概要取得
   172	                    summary_tag = article.find('p')
   173	                    summary_en = summary_tag.get_text(strip=True) if summary_tag else ''
   174	                    
   175	                    # 翻訳
   176	                    title_ja = translate_text(title_en)
   177	                    summary_ja = translate_text(summary_en) if summary_en else title_ja
   178	                    
   179	                    news_item = {
   180	                        'title': title_ja,
   181	                        'title_en': title_en,
   182	                        'summary': summary_ja,
   183	                        'url': article_url,
   184	                        'source': '🌍国際 BBC News',
   185	                        'published_date': datetime.now(JST).strftime('%Y-%m-%d'),
   186	                        'country_tag': '🌍国際'
   187	                    }
   188	                    
   189	                    news_list.append(news_item)
   190	                    print(f"  ✓ BBC: {title_ja[:50]}...")
   191	                    
   192	                except Exception as e:
   193	                    continue
   194	                    
   195	    except Exception as e:
   196	        print(f"  ❌ BBC 収集エラー: {e}")
   197	    
   198	    print(f"  → BBC: {len(news_list)}件収集")
   199	    return news_list
   200	
   201	def fetch_reuters_news():
   202	    """Reuters Myanmar ニュース収集（改良版）"""
   203	    print("\n📰 Reuters Myanmar から収集中...")
   204	    news_list = []
   205	    
   206	    try:
   207	        url = 'https://www.reuters.com/world/asia-pacific/myanmar/'
   208	        response = requests.get(url, headers=HEADERS, timeout=15)
   209	        
   210	        if response.status_code == 200:
   211	            soup = BeautifulSoup(response.content, 'html.parser')
   212	            
   213	            # Reuters の記事を検索
   214	            articles = soup.select('li[data-testid="MediaStoryCard"]')
   215	            
   216	            if not articles:
   217	                articles = soup.select('article')
   218	            
   219	            for article in articles[:5]:
   220	                try:
   221	                    # タイトル取得
   222	                    title_tag = article.find('h3') or article.find('h2')
   223	                    if not title_tag:
   224	                        continue
   225	                    
   226	                    title_en = title_tag.get_text(strip=True)
   227	                    
   228	                    # URL取得
   229	                    link_tag = article.find('a', href=True)
   230	                    if not link_tag:
   231	                        continue
   232	                    
   233	                    article_url = link_tag['href']
   234	                    if not article_url.startswith('http'):
   235	                        article_url = 'https://www.reuters.com' + article_url
   236	                    
   237	                    # 概要取得
   238	                    summary_tag = article.find('p')
   239	                    summary_en = summary_tag.get_text(strip=True) if summary_tag else ''
   240	                    
   241	                    # 翻訳
   242	                    title_ja = translate_text(title_en)
   243	                    summary_ja = translate_text(summary_en) if summary_en else title_ja
   244	                    
   245	                    news_item = {
   246	                        'title': title_ja,
   247	                        'title_en': title_en,
   248	                        'summary': summary_ja,
   249	                        'url': article_url,
   250	                        'source': '🌍国際 Reuters',
   251	                        'published_date': datetime.now(JST).strftime('%Y-%m-%d'),
   252	                        'country_tag': '🌍国際'
   253	                    }
   254	                    
   255	                    news_list.append(news_item)
   256	                    print(f"  ✓ Reuters: {title_ja[:50]}...")
   257	                    
   258	                except Exception as e:
   259	                    continue
   260	                    
   261	    except Exception as e:
   262	        print(f"  ❌ Reuters 収集エラー: {e}")
   263	    
   264	    print(f"  → Reuters: {len(news_list)}件収集")
   265	    return news_list
   266	
   267	def fetch_rfa_news():
   268	    """Radio Free Asia Myanmar ニュース収集（改良版）"""
   269	    print("\n📰 Radio Free Asia Myanmar から収集中...")
   270	    news_list = []
   271	    
   272	    try:
   273	        url = 'https://www.rfa.org/english/news/myanmar'
   274	        response = requests.get(url, headers=HEADERS, timeout=15)
   275	        
   276	        if response.status_code == 200:
   277	            soup = BeautifulSoup(response.content, 'html.parser')
   278	            
   279	            # RFA の記事を検索
   280	            articles = soup.select('div.sectionteaser')
   281	            
   282	            if not articles:
   283	                articles = soup.select('article')
   284	            
   285	            for article in articles[:5]:
   286	                try:
   287	                    # タイトル取得
   288	                    title_tag = article.find('h2') or article.find('h3') or article.find('a')
   289	                    if not title_tag:
   290	                        continue
   291	                    
   292	                    title_en = title_tag.get_text(strip=True)
   293	                    
   294	                    # URL取得
   295	                    link_tag = article.find('a', href=True)
   296	                    if not link_tag:
   297	                        continue
   298	                    
   299	                    article_url = link_tag['href']
   300	                    if not article_url.startswith('http'):
   301	                        article_url = 'https://www.rfa.org' + article_url
   302	                    
   303	                    # 概要取得
   304	                    summary_tag = article.find('p')
   305	                    summary_en = summary_tag.get_text(strip=True) if summary_tag else ''
   306	                    
   307	                    # 翻訳
   308	                    title_ja = translate_text(title_en)
   309	                    summary_ja = translate_text(summary_en) if summary_en else title_ja
   310	                    
   311	                    news_item = {
   312	                        'title': title_ja,
   313	                        'title_en': title_en,
   314	                        'summary': summary_ja,
   315	                        'url': article_url,
   316	                        'source': '🇺🇸アメリカ Radio Free Asia',
   317	                        'published_date': datetime.now(JST).strftime('%Y-%m-%d'),
   318	                        'country_tag': '🇺🇸アメリカ'
   319	                    }
   320	                    
   321	                    news_list.append(news_item)
   322	                    print(f"  ✓ RFA: {title_ja[:50]}...")
   323	                    
   324	                except Exception as e:
   325	                    continue
   326	                    
   327	    except Exception as e:
   328	        print(f"  ❌ RFA 収集エラー: {e}")
   329	    
   330	    print(f"  → RFA: {len(news_list)}件収集")
   331	    return news_list
   332	
   333	def fetch_irrawaddy_news():
   334	    """The Irrawaddy ニュース収集（ミャンマー国内メディア）"""
   335	    print("\n📰 The Irrawaddy から収集中...")
   336	    news_list = []
   337	    
   338	    try:
   339	        url = 'https://www.irrawaddy.com/'
   340	        response = requests.get(url, headers=HEADERS, timeout=15)
   341	        
   342	        if response.status_code == 200:
   343	            soup = BeautifulSoup(response.content, 'html.parser')
   344	            
   345	            # 記事を検索
   346	            articles = soup.select('article')
   347	            
   348	            for article in articles[:5]:
   349	                try:
   350	                    # タイトル取得
   351	                    title_tag = article.find('h2') or article.find('h3')
   352	                    if not title_tag:
   353	                        continue
   354	                    
   355	                    title_en = title_tag.get_text(strip=True)
   356	                    
   357	                    # URL取得
   358	                    link_tag = title_tag.find('a', href=True) or article.find('a', href=True)
   359	                    if not link_tag:
   360	                        continue
   361	                    
   362	                    article_url = link_tag['href']
   363	                    if not article_url.startswith('http'):
   364	                        article_url = 'https://www.irrawaddy.com' + article_url
   365	                    
   366	                    # 概要取得
   367	                    summary_tag = article.find('p')
   368	                    summary_en = summary_tag.get_text(strip=True) if summary_tag else ''
   369	                    
   370	                    # 翻訳
   371	                    title_ja = translate_text(title_en)
   372	                    summary_ja = translate_text(summary_en) if summary_en else title_ja
   373	                    
   374	                    news_item = {
   375	                        'title': title_ja,
   376	                        'title_en': title_en,
   377	                        'summary': summary_ja,
   378	                        'url': article_url,
   379	                        'source': '🇲🇲ミャンマー The Irrawaddy',
   380	                        'published_date': datetime.now(JST).strftime('%Y-%m-%d'),
   381	                        'country_tag': '🇲🇲ミャンマー'
   382	                    }
   383	                    
   384	                    news_list.append(news_item)
   385	                    print(f"  ✓ Irrawaddy: {title_ja[:50]}...")
   386	                    
   387	                except Exception as e:
   388	                    continue
   389	                    
   390	    except Exception as e:
   391	        print(f"  ❌ Irrawaddy 収集エラー: {e}")
   392	    
   393	    print(f"  → Irrawaddy: {len(news_list)}件収集")
   394	    return news_list
   395	
   396	# ==================== メイン処理 ====================
   397	
   398	def main():
   399	    """メイン処理：全ソースから収集して統合"""
   400	    print("=" * 60)
   401	    print("📰 ミャンマーニュース収集ハイブリッド版を開始...")
   402	    print("=" * 60)
   403	    
   404	    all_news = []
   405	    
   406	    # NewsAPI から収集
   407	    newsapi_articles = fetch_from_newsapi()
   408	    all_news.extend(newsapi_articles)
   409	    
   410	    # Web Scraping から収集
   411	    bbc_articles = fetch_bbc_news()
   412	    reuters_articles = fetch_reuters_news()
   413	    rfa_articles = fetch_rfa_news()
   414	    irrawaddy_articles = fetch_irrawaddy_news()
   415	    
   416	    # 統合（重複排除しながら）
   417	    for article in (bbc_articles + reuters_articles + rfa_articles + irrawaddy_articles):
   418	        if not is_duplicate(article, all_news, threshold=0.85):
   419	            all_news.append(article)
   420	    
   421	    print("\n" + "=" * 60)
   422	    print(f"📊 合計: {len(all_news)}件のニュースを収集")
   423	    print("=" * 60)
   424	    
   425	    # 最新順にソート
   426	    all_news.sort(key=lambda x: x.get('published_date', ''), reverse=True)
   427	    
   428	    # 上位10件を厳選
   429	    top_10_news = all_news[:10]
   430	    
   431	    # JSONファイルに保存
   432	    output_file = 'myanmar_news_top10.json'
   433	    with open(output_file, 'w', encoding='utf-8') as f:
   434	        json.dump(top_10_news, f, ensure_ascii=False, indent=2)
   435	    
   436	    print(f"\n✅ 完了！{len(top_10_news)}件のニュースを保存しました")
   437	    print("=" * 60)
   438	    
   439	    # 統計情報を表示
   440	    country_counts = {}
   441	    for news in top_10_news:
   442	        tag = news.get('country_tag', '不明')
   443	        country_counts[tag] = country_counts.get(tag, 0) + 1
   444	    
   445	    print("\n📊 国別統計:")
   446	    for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
   447	        print(f"  {country}: {count}件")
   448	    print("=" * 60)
   449	
   450	if __name__ == '__main__':
   451	    main()