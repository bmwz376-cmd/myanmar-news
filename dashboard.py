# -*- coding: utf-8 -*-
from flask import Flask, render_template_string, jsonify, request
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

app = Flask(__name__)

translation_cache = {}

def translate_to_japanese(text):
    """テキストを日本語に翻訳"""
    if not text or len(text.strip()) == 0:
        return text
    
    if text in translation_cache:
        return translation_cache[text]
    
    try:
        translator = GoogleTranslator(source='auto', target='ja')
        
        if len(text) > 4500:
            chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
            translated_chunks = []
            
            for chunk in chunks:
                translated = translator.translate(chunk)
                translated_chunks.append(translated)
            
            result = ' '.join(translated_chunks)
        else:
            result = translator.translate(text)
        
        translation_cache[text] = result
        return result
        
    except Exception as e:
        print(f"翻訳エラー: {e}")
        return text

# Apple風ハイエンドHTMLテンプレート
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Myanmar 多国籍ニュース - 世界を知る、未来を読む</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --primary-blue: #0071e3;
            --dark-navy: #1d1d1f;
            --light-gray: #f5f5f7;
            --white: #ffffff;
            --shadow: rgba(0, 0, 0, 0.08);
            --shadow-hover: rgba(0, 0, 0, 0.15);
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--light-gray);
            color: var(--dark-navy);
            line-height: 1.6;
            overflow-x: hidden;
        }
        
        /* ヒーローヘッダー - Apple風 */
        .hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8rem 2rem 6rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600"><circle cx="200" cy="100" r="150" fill="rgba(255,255,255,0.03)"/><circle cx="800" cy="400" r="200" fill="rgba(255,255,255,0.02)"/></svg>');
            opacity: 0.5;
        }
        
        .hero-content {
            position: relative;
            z-index: 1;
            max-width: 900px;
            margin: 0 auto;
            animation: fadeInUp 1s ease-out;
        }
        
        .hero-icon {
            font-size: 4rem;
            margin-bottom: 1.5rem;
            display: inline-block;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .hero h1 {
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            letter-spacing: -0.02em;
        }
        
        .hero-subtitle {
            font-size: 1.5rem;
            font-weight: 300;
            opacity: 0.95;
            margin-bottom: 0.5rem;
        }
        
        .hero-update {
            font-size: 1rem;
            opacity: 0.8;
            font-weight: 300;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* コンテナ */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 4rem 2rem;
        }
        
        /* 統計カード - Apple風 */
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin: -4rem auto 4rem;
            max-width: 1200px;
            padding: 0 2rem;
            position: relative;
            z-index: 10;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 2.5rem 2rem;
            border-radius: 24px;
            box-shadow: 0 4px 20px var(--shadow);
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(255, 255, 255, 0.5);
        }
        
        .stat-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 40px var(--shadow-hover);
        }
        
        .stat-number {
            font-size: 4rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            font-size: 1rem;
            color: #86868b;
            font-weight: 500;
        }
        
        /* カテゴリフィルター - Apple風pill */
        .filter-section {
            margin-bottom: 4rem;
        }
        
        .filter-pills {
            display: flex;
            gap: 1rem;
            overflow-x: auto;
            padding: 1rem 0;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
        }
        
        .filter-pills::-webkit-scrollbar {
            display: none;
        }
        
        .pill {
            padding: 0.75rem 1.75rem;
            border-radius: 50px;
            background: white;
            border: 2px solid #d2d2d7;
            color: var(--dark-navy);
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            white-space: nowrap;
            font-size: 0.95rem;
        }
        
        .pill:hover {
            border-color: var(--primary-blue);
            transform: scale(1.05);
        }
        
        .pill.active {
            background: var(--primary-blue);
            border-color: var(--primary-blue);
            color: white;
            box-shadow: 0 4px 12px rgba(0, 113, 227, 0.3);
        }
        
        /* ニュースグリッド */
        .news-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
            gap: 3rem;
        }
        
        /* ニュースカード - Apple News風 */
        .news-card {
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 2px 16px var(--shadow);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            opacity: 0;
            transform: translateY(30px);
            animation: fadeInCard 0.6s ease-out forwards;
        }
        
        .news-card:nth-child(1) { animation-delay: 0.1s; }
        .news-card:nth-child(2) { animation-delay: 0.2s; }
        .news-card:nth-child(3) { animation-delay: 0.3s; }
        .news-card:nth-child(4) { animation-delay: 0.4s; }
        
        @keyframes fadeInCard {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .news-card:hover {
            transform: translateY(-12px) scale(1.02);
            box-shadow: 0 20px 40px var(--shadow-hover);
        }
        
        .news-header {
            padding: 2rem 2rem 1rem;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        
        .source-info {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .country-icon {
            font-size: 2rem;
        }
        
        .source-details h3 {
            font-size: 1rem;
            font-weight: 600;
            color: var(--dark-navy);
            margin-bottom: 0.25rem;
        }
        
        .source-country {
            font-size: 0.85rem;
            color: #86868b;
        }
        
        .category-pill {
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .category-政治, .category-国内政治 { background: #ffe5e5; color: #d32f2f; }
        .category-経済 { background: #fff3cd; color: #f57c00; }
        .category-社会 { background: #e3f2fd; color: #1976d2; }
        .category-人権 { background: #f3e5f5; color: #7b1fa2; }
        .category-国際 { background: #e8f5e9; color: #388e3c; }
        .category-中国視点 { background: #ffe0b2; color: #e65100; }
        .category-日本視点 { background: #ffcdd2; color: #c62828; }
        .category-ASEAN { background: #e0f2f1; color: #00695c; }
        .category-民主化 { background: #ede7f6; color: #5e35b1; }
        .category-ロシア視点 { background: #f5f5f5; color: #424242; }
        
        .news-title {
            padding: 0 2rem;
            font-size: 1.5rem;
            font-weight: 700;
            line-height: 1.4;
            color: var(--dark-navy);
            margin-bottom: 0.75rem;
        }
        
        .news-original {
            padding: 0 2rem;
            font-size: 0.9rem;
            color: #86868b;
            font-style: italic;
            margin-bottom: 1.5rem;
        }
        
        .news-meta {
            padding: 0 2rem;
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            color: #86868b;
            margin-bottom: 1.5rem;
        }
        
        .importance {
            color: #f59e0b;
            font-weight: 600;
        }
        
        .news-content {
            display: none;
            padding: 2rem;
            background: #fafafa;
            border-top: 1px solid #f0f0f0;
            line-height: 1.8;
            animation: fadeIn 0.3s ease-out;
        }
        
        .news-content.show {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .news-actions {
            padding: 2rem;
            display: flex;
            gap: 1rem;
        }
        
        .btn {
            flex: 1;
            padding: 1rem 2rem;
            border-radius: 12px;
            border: none;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-size: 1rem;
        }
        
        .btn-primary {
            background: var(--primary-blue);
            color: white;
        }
        
        .btn-primary:hover {
            background: #0077ed;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 113, 227, 0.3);
        }
        
        .btn-secondary {
            background: #f5f5f7;
            color: var(--dark-navy);
        }
        
        .btn-secondary:hover {
            background: #e8e8ed;
        }
        
        /* フッター */
        .footer {
            text-align: center;
            padding: 4rem 2rem;
            color: #86868b;
        }
        
        .footer h3 {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--dark-navy);
        }
        
        /* レスポンシブ */
        @media (max-width: 768px) {
            .hero {
                padding: 4rem 1.5rem 3rem;
            }
            
            .hero h1 {
                font-size: 2.5rem;
            }
            
            .hero-subtitle {
                font-size: 1.25rem;
            }
            
            .stats {
                grid-template-columns: repeat(2, 1fr);
                gap: 1rem;
                margin-top: -3rem;
            }
            
            .stat-number {
                font-size: 3rem;
            }
            
            .news-grid {
                grid-template-columns: 1fr;
                gap: 2rem;
            }
            
            .news-title {
                font-size: 1.25rem;
            }
        }
    </style>
</head>
<body>
    <!-- ヒーローヘッダー -->
    <section class="hero">
        <div class="hero-content">
            <div class="hero-icon">🌏</div>
            <h1>Myanmar 多国籍ニュース</h1>
            <p class="hero-subtitle">世界を知る、未来を読む</p>
            <p class="hero-update">最終更新: {{ update_time }}</p>
        </div>
    </section>
    
    <!-- 統計カード -->
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{{ total_news }}</div>
            <div class="stat-label">ニュース記事</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ country_count }}</div>
            <div class="stat-label">情報源の国</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ category_count }}</div>
            <div class="stat-label">カテゴリー</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ avg_importance }}</div>
            <div class="stat-label">平均重要度</div>
        </div>
    </div>
    
    <!-- メインコンテンツ -->
    <div class="container">
        <!-- カテゴリフィルター -->
        <section class="filter-section">
            <div class="filter-pills">
                <button class="pill active" onclick="filterNews('all')">すべて</button>
                <button class="pill" onclick="filterNews('ミャンマー')">🇲🇲 ミャンマー</button>
                <button class="pill" onclick="filterNews('中国')">🇨🇳 中国</button>
                <button class="pill" onclick="filterNews('日本')">🇯🇵 日本</button>
                <button class="pill" onclick="filterNews('タイ')">🇹🇭 タイ</button>
                <button class="pill" onclick="filterNews('イギリス')">🇬🇧 イギリス</button>
                <button class="pill" onclick="filterNews('アメリカ')">🇺🇸 アメリカ</button>
                <button class="pill" onclick="filterNews('国際')">🌐 国際</button>
            </div>
        </section>
        
        <!-- ニュースグリッド -->
        <div class="news-grid">
            {% for news in news_list %}
            <article class="news-card" data-country="{{ news.country }}" data-index="{{ loop.index0 }}">
                <div class="news-header">
                    <div class="source-info">
                        <span class="country-icon">{{ get_flag(news.country) }}</span>
                        <div class="source-details">
                            <h3>{{ news.source }}</h3>
                            <p class="source-country">{{ news.country }}</p>
                        </div>
                    </div>
                    <span class="category-pill category-{{ news.category }}">{{ news.category }}</span>
                </div>
                
                <h2 class="news-title">{{ news.title_ja }}</h2>
                <p class="news-original">{{ news.title }}</p>
                
                <div class="news-meta">
                    <span>📅 {{ news.date }}</span>
                    <span class="importance">{{ '⭐' * news.importance }}</span>
                </div>
                
                <div class="news-content" id="content-{{ loop.index0 }}">
                    <p style="color: #86868b; font-style: italic;">📥 記事内容を読み込み中...</p>
                </div>
                
                <div class="news-actions">
                    <button class="btn btn-primary" onclick="toggleContent({{ loop.index0 }})">
                        <span id="btn-text-{{ loop.index0 }}">📖 内容を見る</span>
                    </button>
                    <a href="{{ news.url }}" target="_blank" class="btn btn-secondary">🔗 元記事</a>
                </div>
            </article>
            {% endfor %}
        </div>
    </div>
    
    <!-- フッター -->
    <footer class="footer">
        <h3>Myanmar 多国籍ニュース v3.0</h3>
        <p>多国籍視点で世界を理解する</p>
    </footer>
    
    <script>
        const newsData = {{ news_list | tojson }};
        const loadedContent = {};
        
        function filterNews(country) {
            const cards = document.querySelectorAll('.news-card');
            const pills = document.querySelectorAll('.pill');
            
            pills.forEach(p => p.classList.remove('active'));
            event.target.classList.add('active');
            
            cards.forEach(card => {
                card.style.display = (country === 'all' || card.dataset.country === country) ? 'block' : 'none';
            });
        }
        
        async function toggleContent(index) {
            const contentDiv = document.getElementById(`content-${index}`);
            const btnText = document.getElementById(`btn-text-${index}`);
            
            if (contentDiv.classList.contains('show')) {
                contentDiv.classList.remove('show');
                btnText.textContent = '📖 内容を見る';
            } else {
                contentDiv.classList.add('show');
                btnText.textContent = '📕 内容を隠す';
                
                if (!loadedContent[index]) {
                    const url = newsData[index].url;
                    
                    try {
                        const response = await fetch(`/fetch_content?url=${encodeURIComponent(url)}`);
                        const data = await response.json();
                        
                        if (data.success) {
                            contentDiv.innerHTML = `
                                <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 1.5rem; color: var(--dark-navy);">📰 記事内容</h3>
                                <div style="line-height: 1.9; color: #424245;">${data.content}</div>
                            `;
                            loadedContent[index] = true;
                        } else {
                            contentDiv.innerHTML = '<p style="color: #d32f2f;">⚠️ 記事内容を取得できませんでした</p>';
                        }
                    } catch (error) {
                        contentDiv.innerHTML = '<p style="color: #d32f2f;">❌ エラーが発生しました</p>';
                    }
                }
            }
        }
    </script>
</body>
</html>
"""

def get_flag(country):
    """国旗絵文字を返す"""
    flags = {
        'ミャンマー': '🇲🇲',
        '中国': '🇨🇳',
        '日本': '🇯🇵',
        'タイ': '🇹🇭',
        'イギリス': '🇬🇧',
        'アメリカ': '🇺🇸',
        'ロシア': '🇷🇺',
        '国際': '🌐'
    }
    return flags.get(country, '🌍')

def fetch_article_content(url):
    """記事の内容を取得"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        content = ""
        
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
        
        if not content:
            content_div = soup.find('div', class_=lambda x: x and ('content' in x.lower() or 'article' in x.lower()))
            if content_div:
                paragraphs = content_div.find_all('p')
                content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
        
        if not content:
            paragraphs = soup.find_all('p')
            content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs[:10] if len(p.get_text(strip=True)) > 50])
        
        if content and len(content) > 100:
            return content[:2000] + "..." if len(content) > 2000 else content
        else:
            return "記事内容を抽出できませんでした。元記事リンクからご覧ください。"
            
    except Exception as e:
        return f"記事の取得中にエラーが発生しました: {str(e)}"

@app.route('/')
def dashboard():
    """ダッシュボード表示"""
    try:
        with open('myanmar_news_top10.json', 'r', encoding='utf-8') as f:
            news_list = json.load(f)
        
        print("📰 ニュースタイトルを日本語に翻訳中...")
        for news in news_list:
            if 'title_ja' not in news:
                news['title_ja'] = translate_to_japanese(news['title'])
                print(f"  ✓ 翻訳完了: {news['title'][:50]}...")
        
        total_news = len(news_list)
        countries = set(news['country'] for news in news_list)
        country_count = len(countries)
        categories = set(news['category'] for news in news_list)
        category_count = len(categories)
        avg_importance = round(sum(news['importance'] for news in news_list) / total_news, 1) if total_news > 0 else 0
        
        update_time = datetime.now().strftime('%Y年%m月%d日 %H:%M')
        
        return render_template_string(
            HTML_TEMPLATE,
            news_list=news_list,
            total_news=total_news,
            country_count=country_count,
            category_count=category_count,
            avg_importance=avg_importance,
            update_time=update_time,
            get_flag=get_flag
        )
    
    except FileNotFoundError:
        return """
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; text-align: center; padding: 50px;">
            <h1>⚠️ ニュースデータが見つかりません</h1>
            <p>先に news_collector_pro.py を実行してください</p>
        </body>
        </html>
        """
    except Exception as e:
        return f"""
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; text-align: center; padding: 50px;">
            <h1>❌ エラーが発生しました</h1>
            <p>{str(e)}</p>
        </body>
        </html>
        """

@app.route('/fetch_content')
def fetch_content():
    """記事内容を取得して翻訳するAPI"""
    url = request.args.get('url', '')
    
    if not url:
        return jsonify({'success': False, 'error': 'URLが指定されていません'})
    
    content = fetch_article_content(url)
    
    print(f"📝 記事内容を日本語に翻訳中... ({url})")
    content_ja = translate_to_japanese(content)
    
    return jsonify({
        'success': True,
        'content': content_ja
    })

if __name__ == '__main__':
    print("="*70)
    print("🍎 Myanmar News - Apple風ハイエンドデザイン起動中...")
    print("="*70)
    print("\n✅ ブラウザで以下のURLを開いてください:")
    print("   http://localhost:5000")
    print("\n💡 新機能:")
    print("   - 🍎 Apple公式サイト風デザイン")
    print("   - ✨ 滑らかなアニメーション")
    print("   - 🎨 ガラスモーフィズム")
    print("   - 📱 完全レスポンシブ")
    print("\n⚠️  停止するには: Ctrl + C を押してください\n")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False)