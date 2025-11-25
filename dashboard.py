Copyfrom flask import Flask, render_template_string
import json
import os
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ミャンマーニュース - Myanmar News Daily</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
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
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        
        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .subtitle {
            font-size: 1.1rem;
            opacity: 0.95;
            font-weight: 400;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9rem;
        }
        
        .news-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }
        
        .news-card {
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            display: flex;
            flex-direction: column;
        }
        
        .news-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        
        .news-header {
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .news-title {
            font-size: 1.25rem;
            font-weight: 600;
            line-height: 1.4;
            margin-bottom: 10px;
        }
        
        .news-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
            opacity: 0.9;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .country-tag {
            display: inline-block;
            padding: 4px 12px;
            background: rgba(255,255,255,0.2);
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .news-body {
            padding: 20px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }
        
        .news-description {
            color: #333;
            line-height: 1.6;
            margin-bottom: 15px;
            flex-grow: 1;
        }
        
        .news-link {
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 500;
            text-align: center;
            transition: opacity 0.3s ease;
        }
        
        .news-link:hover {
            opacity: 0.9;
        }
        
        .update-time {
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        @media (max-width: 768px) {
            h1 {
                font-size: 2rem;
            }
            
            .news-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🇲🇲 ミャンマーニュース</h1>
            <p class="subtitle">世界中から厳選された最新ニュース | Daily Myanmar News Updates</p>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ total_count }}</div>
                <div class="stat-label">総ニュース数</div>
            </div>
            {% for country, count in country_stats.items() %}
            <div class="stat-card">
                <div class="stat-number">{{ count }}</div>
                <div class="stat-label">{{ country }}</div>
            </div>
            {% endfor %}
        </div>
        
        <div class="news-grid">
            {% for article in articles %}
            <article class="news-card">
                <div class="news-header">
                    <h2 class="news-title">{{ article.title_ja }}</h2>
                    <div class="news-meta">
                        <span class="country-tag">{{ article.country }}</span>
                        <span>{{ article.published_date }}</span>
                    </div>
                </div>
                <div class="news-body">
                    <p class="news-description">{{ article.description_ja }}</p>
                    <a href="{{ article.url }}" target="_blank" class="news-link">続きを読む →</a>
                </div>
            </article>
            {% endfor %}
        </div>
        
        <div class="update-time">
            <p>最終更新: {{ update_time }}</p>
            <p style="margin-top: 10px; font-size: 0.9rem;">毎朝8時（日本時間）に自動更新されます</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    try:
        with open('myanmar_news_top10.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # データがリスト形式の場合とdict形式の場合の両方に対応
        if isinstance(data, list):
            articles = data
        else:
            articles = data.get('articles', [])
        
        # 国別統計を計算
        country_stats = {}
        for article in articles:
            country = article.get('country', '不明')
            country_stats[country] = country_stats.get(country, 0) + 1
        
        # 更新時刻を日本時間で表示
        jst = timezone(timedelta(hours=9))
        update_time = datetime.now(jst).strftime('%Y年%m月%d日 %H:%M:%S (JST)')
        
        return render_template_string(
            HTML_TEMPLATE,
            articles=articles,
            total_count=len(articles),
            country_stats=country_stats,
            update_time=update_time
        )
    except FileNotFoundError:
        return render_template_string("""
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                    }
                    .message {
                        text-align: center;
                        padding: 40px;
                        background: rgba(255,255,255,0.1);
                        border-radius: 20px;
                        backdrop-filter: blur(10px);
                    }
                </style>
            </head>
            <body>
                <div class="message">
                    <h1>📰 ニュース準備中...</h1>
                    <p>最新ニュースを収集中です。しばらくお待ちください。</p>
                </div>
            </body>
            </html>
        """)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
