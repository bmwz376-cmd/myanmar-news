from flask import Flask, render_template_string
import json
import os
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

def load_news_data():
    """JSONファイルからニュースデータを読み込む"""
    try:
        if os.path.exists('myanmar_news_top10.json'):
            with open('myanmar_news_top10.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                else:
                    return []
        else:
            return []
    except Exception as e:
        print(f"Error loading news data: {e}")
        return []

def get_country_stats(news_list):
    """国別統計を計算"""
    country_counts = {}
    for news in news_list:
        tag = news.get('country_tag', '不明')
        country_counts[tag] = country_counts.get(tag, 0) + 1
    
    # カウント順にソート
    sorted_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_countries

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ミャンマーニュース - Myanmar News</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
            padding: 40px 20px;
        }
        
        header h1 {
            font-size: 3em;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .stat-card h3 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .stat-card p {
            font-size: 1em;
            opacity: 0.9;
        }
        
        .country-stats {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 40px;
        }
        
        .country-stats h2 {
            font-size: 1.8em;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .country-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .country-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.1em;
        }
        
        .country-item strong {
            font-size: 1.5em;
            display: block;
            margin-top: 5px;
        }
        
        .news-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        
        .news-card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }
        
        .news-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        
        .news-source {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .news-title {
            font-size: 1.3em;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 15px;
            line-height: 1.4;
        }
        
        .news-summary {
            font-size: 0.95em;
            color: #4a5568;
            margin-bottom: 15px;
            line-height: 1.6;
        }
        
        .news-date {
            color: #a0aec0;
            font-size: 0.9em;
        }
        
        footer {
            text-align: center;
            color: white;
            padding: 30px 20px;
            opacity: 0.9;
        }
        
        @media (max-width: 768px) {
            header h1 {
                font-size: 2em;
            }
            
            .news-grid {
                grid-template-columns: 1fr;
            }
            
            .stats {
                grid-template-columns: 1fr;
            }
            
            .country-list {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🇲🇲 ミャンマーニュース</h1>
            <p>Myanmar News - 世界中から最新情報を日本語でお届け</p>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <h3>{{ news_count }}</h3>
                <p>📰 最新ニュース</p>
            </div>
            <div class="stat-card">
                <h3>{{ sources_count }}</h3>
                <p>🌐 情報源</p>
            </div>
            <div class="stat-card">
                <h3>{{ update_date }}</h3>
                <p>🕐 最終更新</p>
            </div>
        </div>
        
        {% if country_stats %}
        <div class="country-stats">
            <h2>📊 国・地域別ニュース統計</h2>
            <div class="country-list">
                {% for country, count in country_stats %}
                <div class="country-item">
                    {{ country }}
                    <strong>{{ count }}件</strong>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        <div class="news-grid">
            {% for news in news_list %}
            <div class="news-card" onclick="window.open('{{ news.url }}', '_blank')">
                <span class="news-source">{{ news.source }}</span>
                <h2 class="news-title">{{ news.title }}</h2>
                <p class="news-summary">{{ news.summary }}</p>
                <p class="news-date">📅 {{ news.published_date }}</p>
            </div>
            {% endfor %}
        </div>
        
        <footer>
            <p>🌍 世界中のミャンマーニュースを統合収集</p>
            <p>毎朝8時（日本時間）に自動更新</p>
            <p style="margin-top: 10px; opacity: 0.7;">Powered by バイブコーディング × NewsAPI × AI</p>
        </footer>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    news_list = load_news_data()
    
    # 日本時間で統計情報を計算
    jst = timezone(timedelta(hours=9))
    news_count = len(news_list)
    sources = list(set([news.get('source', 'Unknown') for news in news_list]))
    sources_count = len(sources)
    update_date = datetime.now(jst).strftime('%Y-%m-%d %H:%M JST')
    
    # 国別統計を取得
    country_stats = get_country_stats(news_list)
    
    return render_template_string(
        HTML_TEMPLATE,
        news_list=news_list,
        news_count=news_count,
        sources_count=sources_count,
        update_date=update_date,
        country_stats=country_stats
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
