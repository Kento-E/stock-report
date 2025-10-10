"""
Claude Sonnet株式レポートシステム

Github Actions上で定期実行可能。APIキーや設定値はSecrets/環境変数で管理。
レポートはHTML形式で生成し、メール配信処理の雛形も含む。

- データ収集（株価・ニュース）
- Claude Sonnet APIによる分析
- レポート生成（HTML形式）
- メール配信（SMTP設定は環境変数で管理）
"""

from dotenv import load_dotenv
import os
import sys
import datetime
import requests
import anthropic # pip install anthropic
import yaml # pip install pyyaml
from mail_utils import send_report_via_mail, get_smtp_config, generate_mail_body, markdown_to_html

try:
    from defeatbeta_api.data.ticker import Ticker
    DEFEATBETA_AVAILABLE = True
except ImportError:
    DEFEATBETA_AVAILABLE = False
    print("警告: defeatbeta-apiがインストールされていません。ニュース取得機能が制限されます。")

# 必要なAPIキーや設定値は環境変数（Github Secrets）で管理
load_dotenv()  # .envファイルから環境変数をロード
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MAIL_TO = os.getenv('MAIL_TO')
YAHOO_API_KEY = os.getenv('YAHOO_API_KEY')

# 実行オプション判定（デフォルトGemini、--claude指定時のみClaude）
USE_CLAUDE = "--claude" in sys.argv

def load_stock_symbols(filepath='data/stocks.yaml'):
    """
    銘柄リストファイル（YAML形式）から銘柄情報を読み込む。
    
    YAML形式の例:
    stocks:
      - symbol: 7203.T
        name: トヨタ自動車
        added: 2024-01-01
        quantity: 100
        acquisition_price: 2500
      - symbol: 6758.T
        name: ソニーグループ
    
    返り値: 銘柄情報の辞書リスト (例: [{'symbol': '7203.T', 'name': 'トヨタ自動車', 'quantity': 100, 'acquisition_price': 2500}, ...])
    """
    stocks = []
    # ファイルパスの解決（main.pyからの相対パス）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    full_path = os.path.join(project_root, filepath)
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        # YAMLから銘柄リストを取得
        if data and 'stocks' in data:
            for stock in data['stocks']:
                if isinstance(stock, dict) and 'symbol' in stock:
                    # 銘柄情報を辞書として保存
                    stock_info = {
                        'symbol': stock['symbol'],
                        'name': stock.get('name'),
                        'quantity': stock.get('quantity'),
                        'acquisition_price': stock.get('acquisition_price'),
                        'note': stock.get('note'),
                        'added': stock.get('added')
                    }
                    stocks.append(stock_info)
                elif isinstance(stock, str):
                    # 文字列の場合も対応（後方互換性）
                    stocks.append({'symbol': stock})
        
        if not stocks:
            print("警告: 銘柄リストが空です。デフォルトの銘柄リスト [7203.T, 6758.T] を使用します。")
            return [{'symbol': '7203.T'}, {'symbol': '6758.T'}]
            
    except FileNotFoundError:
        print(f"警告: 銘柄リストファイルが見つかりません: {full_path}")
        print("デフォルトの銘柄リスト [7203.T, 6758.T] を使用します。")
        return [{'symbol': '7203.T'}, {'symbol': '6758.T'}]
    except yaml.YAMLError as e:
        print(f"YAML解析エラー: {e}")
        print("デフォルトの銘柄リスト [7203.T, 6758.T] を使用します。")
        return [{'symbol': '7203.T'}, {'symbol': '6758.T'}]
    except Exception as e:
        print(f"銘柄リストファイルの読み込みエラー: {e}")
        print("デフォルトの銘柄リスト [7203.T, 6758.T] を使用します。")
        return [{'symbol': '7203.T'}, {'symbol': '6758.T'}]
    
    return stocks

# 銘柄の市場を判定するヘルパー関数
def get_currency_for_symbol(symbol):
    """
    銘柄シンボルから通貨を判定する。
    日本株（.T、.JPなどのサフィックス）の場合は「円」、それ以外は「ドル」を返す。
    """
    if symbol.endswith('.T') or symbol.endswith('.JP'):
        return '円'
    return 'ドル'

# 1. データ収集（本番API連携例）
def fetch_stock_data(symbol, stock_info=None):
    """
    株価とニュースデータを取得する。
    
    Args:
        symbol: 銘柄コード
        stock_info: 銘柄情報（保有数、取得単価など）
    
    Returns:
        株価、ニュース、保有情報を含む辞書
    """
    # Yahoo Finance API例（RapidAPI経由）
    url = "https://yfapi.net/v6/finance/quote"
    headers = {"x-api-key": YAHOO_API_KEY}
    params = {"symbols": symbol}
    price = None
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            result = response.json()
            price = result["quoteResponse"]["result"][0]["regularMarketPrice"]
    except Exception as e:
        print(f"株価取得失敗: {e}")
    news = fetch_news(symbol)
    
    data = {
        "symbol": symbol,
        "price": price,
        "news": news
    }
    
    # 保有情報を追加
    if stock_info:
        data['quantity'] = stock_info.get('quantity')
        data['acquisition_price'] = stock_info.get('acquisition_price')
        data['name'] = stock_info.get('name')
    
    return data

def fetch_news(symbol):
    """
    defeatbeta-apiを使用して銘柄に関連するニュースを取得する。
    
    Args:
        symbol: 銘柄コード（例: 'TSLA', '7203.T'）
    
    Returns:
        ニュースの文字列リスト（最大5件）
    """
    if not DEFEATBETA_AVAILABLE:
        # defeatbeta-apiが利用できない場合はダミーデータを返す
        return [f"{symbol}関連ニュースが取得できません（defeatbeta-apiが必要です）"]
    
    try:
        # defeatbeta-apiを使用してニュースを取得
        ticker = Ticker(symbol)
        news_data = ticker.news()
        news_list = news_data.get_news_list()
        
        if news_list.empty:
            print(f"情報: {symbol}のニュースが見つかりませんでした。")
            return [f"{symbol}関連のニュースは現在ありません。"]
        
        # ニュース情報を整形（最大5件）
        formatted_news = []
        for idx, row in news_list.head(5).iterrows():
            title = row.get('title', 'タイトルなし')
            publisher = row.get('publisher', '不明')
            report_date = row.get('report_date', '不明')
            # 簡潔なニュース文字列を作成
            news_str = f"[{report_date}] {publisher}: {title}"
            formatted_news.append(news_str)
        
        return formatted_news
        
    except Exception as e:
        # エラー時はダミーデータを返す
        print(f"ニュース取得エラー ({symbol}): {e}")
        return [f"{symbol}関連ニュースの取得に失敗しました"]




# 2. Claude Sonnet API分析（本番APIリクエスト例）

def analyze_with_claude(data):
    """
    Claude Sonnet APIを用いて株価・ニュースデータを分析し、要約・トレンド抽出・リスク/チャンスの指摘と売買判断を返す。
    """
    if not CLAUDE_API_KEY or CLAUDE_API_KEY.strip() == "":
        error_msg = "Claude APIエラー: APIキーが未設定です。環境変数CLAUDE_API_KEYを確認してください。"
        print(error_msg)
        return f"## 分析失敗\n\n**エラー内容:** {error_msg}"
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    currency = get_currency_for_symbol(data['symbol'])
    
    # 保有状況に基づいたプロンプトの生成
    holding_status = ""
    if data.get('quantity') is not None:
        quantity = data['quantity']
        acquisition_price = data.get('acquisition_price')
        
        if quantity > 0:
            holding_status = f"現在の保有状況: {quantity}株を保有中"
            if acquisition_price:
                holding_status += f"（取得単価: {acquisition_price}{currency}）"
                if data['price']:
                    profit_loss = (data['price'] - acquisition_price) * quantity
                    profit_rate = ((data['price'] - acquisition_price) / acquisition_price) * 100
                    holding_status += f"\n現在の損益: {profit_loss:,.0f}{currency}（{profit_rate:+.2f}%）"
        elif quantity < 0:
            holding_status = f"現在の保有状況: {abs(quantity)}株を空売り中（信用売り）"
            if acquisition_price:
                holding_status += f"（空売り価格: {acquisition_price}{currency}）"
                if data['price']:
                    profit_loss = (acquisition_price - data['price']) * abs(quantity)
                    profit_rate = ((acquisition_price - data['price']) / acquisition_price) * 100
                    holding_status += f"\n現在の損益: {profit_loss:,.0f}{currency}（{profit_rate:+.2f}%）"
        else:
            holding_status = "現在の保有状況: 保有なし（購入または空売りを検討中）"
    else:
        holding_status = "現在の保有状況: 保有なし（購入または空売りを検討中）"
    
    prompt = f"""
{data['symbol']}の分析をお願いします。

現在の株価: {data['price']}{currency}
{holding_status}

最近のニュース:
{chr(10).join(f"- {news}" for news in data['news'])}

以下の観点から分析してください：
1. 株価とニュースの要約
2. 現在のトレンドと今後の見通し
3. リスク要因とチャンス要因
4. 売買判断（買い/売り/ホールド/様子見）とその理由
5. 推奨する指値価格（買い注文または売り注文）

保有状況を考慮して、具体的な売買アクションを提案してください。
"""
    
    try:
        message = client.messages.create(
            model="claude-3-sonnet-latest",
            max_tokens=1500,
            temperature=0.5,
            system="あなたは株式分析の専門家です。データに基づいて客観的な分析と売買判断を提供してください。",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        return message.content[0].text
    except Exception as e:
        error_msg = f"Claude API呼び出し失敗: {str(e)}"
        print(error_msg)
        return f"## 分析失敗\n\n**エラー内容:** {error_msg}\n\n**エラータイプ:** {type(e).__name__}"

def analyze_with_gemini(data):
    """
    Gemini APIを用いて株価・ニュースデータを分析し、要約・トレンド抽出・リスク/チャンスの指摘と売買判断を返す。
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
        error_msg = "Gemini APIエラー: APIキーが未設定です。環境変数GEMINI_API_KEYを確認してください。"
        print(error_msg)
        return f"## 分析失敗\n\n**エラー内容:** {error_msg}"
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    currency = get_currency_for_symbol(data['symbol'])
    
    # 保有状況に基づいたプロンプトの生成
    holding_status = ""
    if data.get('quantity') is not None:
        quantity = data['quantity']
        acquisition_price = data.get('acquisition_price')
        
        if quantity > 0:
            holding_status = f"現在の保有状況: {quantity}株を保有中"
            if acquisition_price:
                holding_status += f"（取得単価: {acquisition_price}{currency}）"
                if data['price']:
                    profit_loss = (data['price'] - acquisition_price) * quantity
                    profit_rate = ((data['price'] - acquisition_price) / acquisition_price) * 100
                    holding_status += f"\n現在の損益: {profit_loss:,.0f}{currency}（{profit_rate:+.2f}%）"
        elif quantity < 0:
            holding_status = f"現在の保有状況: {abs(quantity)}株を空売り中（信用売り）"
            if acquisition_price:
                holding_status += f"（空売り価格: {acquisition_price}{currency}）"
                if data['price']:
                    profit_loss = (acquisition_price - data['price']) * abs(quantity)
                    profit_rate = ((acquisition_price - data['price']) / acquisition_price) * 100
                    holding_status += f"\n現在の損益: {profit_loss:,.0f}{currency}（{profit_rate:+.2f}%）"
        else:
            holding_status = "現在の保有状況: 保有なし（購入または空売りを検討中）"
    else:
        holding_status = "現在の保有状況: 保有なし（購入または空売りを検討中）"
    
    prompt = (
        "あなたは株式分析の専門家です。データに基づいて客観的な分析と売買判断を提供してください。\n\n"
        f"{data['symbol']}の分析をお願いします。\n\n"
        f"現在の株価: {data['price']}{currency}\n"
        f"{holding_status}\n\n"
        f"最近のニュース:\n"
        f"{chr(10).join(f'- {news}' for news in data['news'])}\n\n"
        "以下の観点から分析してください：\n"
        "1. 株価とニュースの要約\n"
        "2. 現在のトレンドと今後の見通し\n"
        "3. リスク要因とチャンス要因\n"
        "4. 売買判断（買い/売り/ホールド/様子見）とその理由\n"
        "5. 推奨する指値価格（買い注文または売り注文）\n\n"
        "保有状況を考慮して、具体的な売買アクションを提案してください。"
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        if resp.status_code == 200:
            result = resp.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            error_msg = f"Gemini APIエラー: HTTPステータス {resp.status_code}"
            error_detail = resp.text[:500]  # 最初の500文字のみ含める
            print(f"{error_msg}\n応答内容: {error_detail}")
            return f"## 分析失敗\n\n**エラー内容:** {error_msg}\n\n**API応答:** {error_detail}"
    except Exception as e:
        error_msg = f"Gemini API呼び出し失敗: {str(e)}"
        print(error_msg)
        return f"## 分析失敗\n\n**エラー内容:** {error_msg}\n\n**エラータイプ:** {type(e).__name__}"

# 3. レポート生成（HTML形式）
def generate_report_html(symbol, analysis):
    today = datetime.date.today().isoformat()
    analysis_html = markdown_to_html(analysis)
    html = f"""
    <html>
    <head><meta charset='utf-8'><title>{symbol} 日次レポート ({today})</title></head>
    <body>
    <h1>{symbol} 日次レポート ({today})</h1>
    {analysis_html}
    </body>
    </html>
    """
    filename = f"report_{symbol}_{today}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return html, filename

if __name__ == "__main__":
    # 対象銘柄リスト（data/stocks.yamlから読み込み）
    stocks = load_stock_symbols()
    print(f"分析対象銘柄: {[s['symbol'] for s in stocks]}")
    all_reports = []
    for stock_info in stocks:
        symbol = stock_info['symbol']
        data = fetch_stock_data(symbol, stock_info)
        if USE_CLAUDE:
            analysis = analyze_with_claude(data)
        else:
            analysis = analyze_with_gemini(data)
        html, filename = generate_report_html(symbol, analysis)
        print(f"レポート生成: {filename}")
        analysis_html = markdown_to_html(analysis)
        all_reports.append(f"<h1>{symbol}</h1>\n{analysis_html}")

    # 全銘柄分まとめてメール送信
    smtp_conf = get_smtp_config()
    if MAIL_TO and all(smtp_conf.values()):
        today = datetime.date.today().isoformat()
        subject = f"株式日次レポート ({today})"
        body = generate_mail_body(subject, all_reports)
        send_report_via_mail(
            subject, body, MAIL_TO,
            smtp_conf['MAIL_FROM'], smtp_conf['SMTP_SERVER'], smtp_conf['SMTP_PORT'], smtp_conf['SMTP_USER'], smtp_conf['SMTP_PASS']
        )
