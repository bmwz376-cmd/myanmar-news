1	from flask import Flask, render_template_string
     2	import json
     3	import os
     4	from datetime import datetime, timezone, timedelta
     5	
     6	app = Flask(__name__)
     7	
     8	def load_news_data():
     9	    """JSONファイルからニュースデータを読み込む"""
    10	    try:
    11	        if os.path.exists('myanmar_news_top10.json'):
    12	            with open('myanmar_news_top10.json', 'r', encoding='utf-8') as f:
    13	                data = json.load(f)
    14	                if isinstance(data, list):
    15	                    return data
    16	                else:
    17	                    return []
    18	        else:
    19	            return []
    20	    except Exception as e:
    21	        print(f"Error loading news data: {e}")
    22	        return []
    23	
    24	def get_country_stats(news_list):
    25	    """国別統計を計算"""
    26	    country_counts = {}
    27	    for news in news_list:
    28	        tag = news.get('country_tag', '不明')
    29	        country_counts[tag] = country_counts.get(tag, 0) + 1
    30	    
    31	    # カウント順にソート
    32	    sorted_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
    33	    return sorted_countries
    34	
    35	HTML_TEMPLATE = """
    36	<!DOCTYPE html>
    37	<html lang="ja">
    38	<head>
    39	    <meta charset="UTF-8">
    40	    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    41	    <title>ミャンマーニュース - Myanmar News</title>
    42	    <style>
    43	        * {
    44	            margin: 0;
    45	            padding: 0;
    46	            box-sizing: border-box;
    47	        }
    48	        
    49	        body {
    50	            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    51	            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    52	            min-height: 100vh;
    53	            padding: 20px;
    54	        }
    55	        
    56	        .container {
    57	            max-width: 1200px;
    58	            margin: 0 auto;
    59	        }
    60	        
    61	        header {
    62	            text-align: center;
    63	            color: white;
    64	            margin-bottom: 40px;
    65	            padding: 40px 20px;
    66	        }
    67	        
    68	        header h1 {
    69	            font-size: 3em;
    70	            font-weight: 700;
    71	            margin-bottom: 10px;
    72	            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    73	        }
    74	        
    75	        header p {
    76	            font-size: 1.2em;
    77	            opacity: 0.9;
    78	        }
    79	        
    80	        .stats {
    81	            display: grid;
    82	            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    83	            gap: 20px;
    84	            margin-bottom: 40px;
    85	        }
    86	        
    87	        .stat-card {
    88	            background: rgba(255, 255, 255, 0.15);
    89	            backdrop-filter: blur(10px);
    90	            border-radius: 20px;
    91	            padding: 30px;
    92	            text-align: center;
    93	            color: white;
    94	            border: 1px solid rgba(255, 255, 255, 0.2);
    95	        }
    96	        
    97	        .stat-card h3 {
    98	            font-size: 2.5em;
    99	            margin-bottom: 10px;
   100	        }
   101	        
   102	        .stat-card p {
   103	            font-size: 1em;
   104	            opacity: 0.9;
   105	        }
   106	        
   107	        .country-stats {
   108	            background: rgba(255, 255, 255, 0.15);
   109	            backdrop-filter: blur(10px);
   110	            border-radius: 20px;
   111	            padding: 30px;
   112	            color: white;
   113	            border: 1px solid rgba(255, 255, 255, 0.2);
   114	            margin-bottom: 40px;
   115	        }
   116	        
   117	        .country-stats h2 {
   118	            font-size: 1.8em;
   119	            margin-bottom: 20px;
   120	            text-align: center;
   121	        }
   122	        
   123	        .country-list {
   124	            display: grid;
   125	            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
   126	            gap: 15px;
   127	        }
   128	        
   129	        .country-item {
   130	            background: rgba(255, 255, 255, 0.1);
   131	            padding: 15px;
   132	            border-radius: 10px;
   133	            text-align: center;
   134	            font-size: 1.1em;
   135	        }
   136	        
   137	        .country-item strong {
   138	            font-size: 1.5em;
   139	            display: block;
   140	            margin-top: 5px;
   141	        }
   142	        
   143	        .news-grid {
   144	            display: grid;
   145	            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
   146	            gap: 25px;
   147	            margin-bottom: 40px;
   148	        }
   149	        
   150	        .news-card {
   151	            background: white;
   152	            border-radius: 20px;
   153	            padding: 30px;
   154	            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
   155	            transition: transform 0.3s ease, box-shadow 0.3s ease;
   156	            cursor: pointer;
   157	        }
   158	        
   159	        .news-card:hover {
   160	            transform: translateY(-5px);
   161	            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
   162	        }
   163	        
   164	        .news-source {
   165	            display: inline-block;
   166	            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
   167	            color: white;
   168	            padding: 8px 15px;
   169	            border-radius: 20px;
   170	            font-size: 0.9em;
   171	            margin-bottom: 15px;
   172	            font-weight: 600;
   173	        }
   174	        
   175	        .news-title {
   176	            font-size: 1.3em;
   177	            font-weight: 700;
   178	            color: #2d3748;
   179	            margin-bottom: 15px;
   180	            line-height: 1.4;
   181	        }
   182	        
   183	        .news-summary {
   184	            font-size: 0.95em;
   185	            color: #4a5568;
   186	            margin-bottom: 15px;
   187	            line-height: 1.6;
   188	        }
   189	        
   190	        .news-date {
   191	            color: #a0aec0;
   192	            font-size: 0.9em;
   193	        }
   194	        
   195	        footer {
   196	            text-align: center;
   197	            color: white;
   198	            padding: 30px 20px;
   199	            opacity: 0.9;
   200	        }
   201	        
   202	        @media (max-width: 768px) {
   203	            header h1 {
   204	                font-size: 2em;
   205	            }
   206	            
   207	            .news-grid {
   208	                grid-template-columns: 1fr;
   209	            }
   210	            
   211	            .stats {
   212	                grid-template-columns: 1fr;
   213	            }
   214	            
   215	            .country-list {
   216	                grid-template-columns: 1fr;
   217	            }
   218	        }
   219	    </style>
   220	</head>
   221	<body>
   222	    <div class="container">
   223	        <header>
   224	            <h1>🇲🇲 ミャンマーニュース</h1>
   225	            <p>Myanmar News - 世界中から最新情報を日本語でお届け</p>
   226	        </header>
   227	        
   228	        <div class="stats">
   229	            <div class="stat-card">
   230	                <h3>{{ news_count }}</h3>
   231	                <p>📰 最新ニュース</p>
   232	            </div>
   233	            <div class="stat-card">
   234	                <h3>{{ sources_count }}</h3>
   235	                <p>🌐 情報源</p>
   236	            </div>
   237	            <div class="stat-card">
   238	                <h3>{{ update_date }}</h3>
   239	                <p>🕐 最終��新</p>
   240	            </div>
   241	        </div>
   242	        
   243	        {% if country_stats %}
   244	        <div class="country-stats">
   245	            <h2>📊 国・地域別ニュース統計</h2>
   246	            <div class="country-list">
   247	                {% for country, count in country_stats %}
   248	                <div class="country-item">
   249	                    {{ country }}
   250	                    <strong>{{ count }}件</strong>
   251	                </div>
   252	                {% endfor %}
   253	            </div>
   254	        </div>
   255	        {% endif %}
   256	        
   257	        <div class="news-grid">
   258	            {% for news in news_list %}
   259	            <div class="news-card" onclick="window.open('{{ news.url }}', '_blank')">
   260	                <span class="news-source">{{ news.source }}</span>
   261	                <h2 class="news-title">{{ news.title }}</h2>
   262	                <p class="news-summary">{{ news.summary }}</p>
   263	                <p class="news-date">📅 {{ news.published_date }}</p>
   264	            </div>
   265	            {% endfor %}
   266	        </div>
   267	        
   268	        <footer>
   269	            <p>🌍 世界中のミャンマーニュースを統合収集</p>
   270	            <p>毎朝8時（日本時間）に自動更新</p>
   271	            <p style="margin-top: 10px; opacity: 0.7;">Powered by バイブコーディング × NewsAPI × AI</p>
   272	        </footer>
   273	    </div>
   274	</body>
   275	</html>
   276	"""
   277	
   278	@app.route('/')
   279	def index():
   280	    news_list = load_news_data()
   281	    
   282	    # 日本時間で統計情報を計算
   283	    jst = timezone(timedelta(hours=9))
   284	    news_count = len(news_list)
   285	    sources = list(set([news.get('source', 'Unknown') for news in news_list]))
   286	    sources_count = len(sources)
   287	    update_date = datetime.now(jst).strftime('%Y-%m-%d %H:%M JST')
   288	    
   289	    # 国別統計を取得
   290	    country_stats = get_country_stats(news_list)
   291	    
   292	    return render_template_string(
   293	        HTML_TEMPLATE,
   294	        news_list=news_list,
   295	        news_count=news_count,
   296	        sources_count=sources_count,
   297	        update_date=update_date,
   298	        country_stats=country_stats
   299	    )
   300	
   301	if __name__ == '__main__':
   302	    port = int(os.environ.get('PORT', 5001))
   303	    app.run(host='0.0.0.0', port=port, debug=True)
