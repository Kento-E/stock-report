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
from mail_utils import send_report_via_mail, get_smtp_config, generate_mail_body

# 必要なAPIキーや設定値は環境変数（Github Secrets）で管理
load_dotenv()  # .envファイルから環境変数をロード
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MAIL_TO = os.getenv('MAIL_TO')
YAHOO_API_KEY = os.getenv('YAHOO_API_KEY')

# 実行オプション判定（デフォルトGemini、--claude指定時のみClaude）
USE_CLAUDE = "--claude" in sys.argv


# 1. データ収集・トレンド銘柄抽出
JP_CANDIDATES = [
    '7203.T', '6758.T', '9984.T', '9432.T', '8306.T', '6861.T', '4063.T', '7974.T', '9983.T', '6902.T'
]
US_CANDIDATES = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'V', 'JPM'
]

def fetch_stock_data(symbol):
    url = "https://yfapi.net/v6/finance/quote"
    headers = {"x-api-key": YAHOO_API_KEY}
    params = {"symbols": symbol}
    price = None
    change_percent = None
    volume = None
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            result = response.json()
            info = result["quoteResponse"]["result"][0]
            price = info.get("regularMarketPrice")
            change_percent = info.get("regularMarketChangePercent")
            volume = info.get("regularMarketVolume")
    except Exception as e:
        print(f"株価取得失敗: {e}")
    news = fetch_news(symbol)
    return {
        "symbol": symbol,
        "price": price,
        "change_percent": change_percent,
        "volume": volume,
        "news": news
    }

def pick_trending_symbols(jp_candidates, us_candidates, top_n=3):
    all_syms = jp_candidates + us_candidates
    stock_data = []
    for sym in all_syms:
        data = fetch_stock_data(sym)
        stock_data.append(data)
    # 値上がり率降順で上位N件を抽出（値が取得できたもののみ）
    sorted_syms = sorted(
        [d for d in stock_data if d["change_percent"] is not None],
        key=lambda x: x["change_percent"], reverse=True
    )
    return [d["symbol"] for d in sorted_syms[:top_n]]

def fetch_news(symbol):
    # Google News API等で実装（ここはダミー）
    return [f"{symbol}関連ニュース1", f"{symbol}関連ニュース2"]




# 2. Claude Sonnet API分析（本番APIリクエスト例）

def analyze_with_claude(data):
    """
    Claude Sonnet APIを用いて株価・ニュースデータを分析し、要約・トレンド抽出・リスク/チャンスの指摘を返す。
    """
    if not CLAUDE_API_KEY or CLAUDE_API_KEY.strip() == "":
        print("Claude APIエラー: APIキーが未設定です。環境変数CLAUDE_API_KEYを確認してください。")
        return "分析失敗（APIキー未設定）"
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    prompt = f"{data['symbol']}の株価は{data['price']}円です。ニュース: {', '.join(data['news'])}。これらを分析し、要約・トレンド・リスク/チャンスを日本語で簡潔に示してください。"
    try:
        message = client.messages.create(
            model="claude-3-sonnet-latest",
            max_tokens=1000,
            temperature=0.5,
            system="あなたは株式分析の専門家です。",
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
        print(f"Claude API呼び出し失敗: {e}")
        return "分析失敗"

def analyze_with_gemini(data):
    """
    Gemini APIを用いて株価・ニュースデータを分析し、要約・トレンド抽出・リスク/チャンスの指摘を返す。
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
        print("Gemini APIエラー: APIキーが未設定です。環境変数GEMINI_API_KEYを確認してください。")
        return "分析失敗（Gemini APIキー未設定）"
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"{data['symbol']}の株価は{data['price']}円です。ニュース: {', '.join(data['news'])}。これらを分析し、要約・トレンド・リスク/チャンスを日本語で簡潔に示してください。"
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
            print(f"Gemini APIエラー: {resp.status_code} {resp.text}")
            return "分析失敗"
    except Exception as e:
        print(f"Gemini API呼び出し失敗: {e}")
        return "分析失敗"

# 3. レポート生成（HTML形式）
def generate_report_html(symbol, analysis):
    today = datetime.date.today().isoformat()
    html = f"""
    <html>
    <head><meta charset='utf-8'><title>{symbol} 日次レポート ({today})</title></head>
    <body>
    <h1>{symbol} 日次レポート ({today})</h1>
    <p>{analysis}</p>
    </body>
    </html>
    """
    filename = f"report_{symbol}_{today}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return html, filename

if __name__ == "__main__":
    # トレンド銘柄自動抽出（日本株・米国株から値上がり率上位）
    symbols = pick_trending_symbols(JP_CANDIDATES, US_CANDIDATES, top_n=3)
    print(f"分析対象銘柄: {symbols}")
    all_reports = []
    for symbol in symbols:
        data = fetch_stock_data(symbol)
        if USE_CLAUDE:
            analysis = analyze_with_claude(data)
        else:
            analysis = analyze_with_gemini(data)
        html, filename = generate_report_html(symbol, analysis)
        print(f"レポート生成: {filename}")
        all_reports.append(f"<h2>{symbol}</h2>\n{analysis}")

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
