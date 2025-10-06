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
from mail_utils import send_report_via_mail, get_smtp_config, generate_mail_body, markdown_to_html

# 必要なAPIキーや設定値は環境変数（Github Secrets）で管理
load_dotenv()  # .envファイルから環境変数をロード
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MAIL_TO = os.getenv('MAIL_TO')
YAHOO_API_KEY = os.getenv('YAHOO_API_KEY')

# 株銘柄リスト（環境変数で指定、未設定の場合はデフォルト値）
STOCK_SYMBOLS = os.getenv('STOCK_SYMBOLS', '7203.T,6758.T')

# 実行オプション判定（デフォルトGemini、--claude指定時のみClaude）
USE_CLAUDE = "--claude" in sys.argv

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
def fetch_stock_data(symbol):
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
    return {
        "symbol": symbol,
        "price": price,
        "news": news
    }

def fetch_news(symbol):
    # Google News API等で実装（ここはダミー）
    return [f"{symbol}関連ニュース1", f"{symbol}関連ニュース2"]




# 2. Claude Sonnet API分析（本番APIリクエスト例）

def analyze_with_claude(data):
    """
    Claude Sonnet APIを用いて株価・ニュースデータを分析し、要約・トレンド抽出・リスク/チャンスの指摘を返す。
    """
    if not CLAUDE_API_KEY or CLAUDE_API_KEY.strip() == "":
        error_msg = "Claude APIエラー: APIキーが未設定です。環境変数CLAUDE_API_KEYを確認してください。"
        print(error_msg)
        return f"## 分析失敗\n\n**エラー内容:** {error_msg}"
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    currency = get_currency_for_symbol(data['symbol'])
    prompt = f"{data['symbol']}の株価は{data['price']}{currency}です。ニュース: {', '.join(data['news'])}。これらを分析し、要約・トレンド・リスク/チャンスを日本語で簡潔に示してください。"
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
        error_msg = f"Claude API呼び出し失敗: {str(e)}"
        print(error_msg)
        return f"## 分析失敗\n\n**エラー内容:** {error_msg}\n\n**エラータイプ:** {type(e).__name__}"

def analyze_with_gemini(data):
    """
    Gemini APIを用いて株価・ニュースデータを分析し、要約・トレンド抽出・リスク/チャンスの指摘を返す。
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
        error_msg = "Gemini APIエラー: APIキーが未設定です。環境変数GEMINI_API_KEYを確認してください。"
        print(error_msg)
        return f"## 分析失敗\n\n**エラー内容:** {error_msg}"
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    currency = get_currency_for_symbol(data['symbol'])
    prompt = (
        "あなたは株式分析の専門家です。"
        f"{data['symbol']}の株価は{data['price']}{currency}です。"
        f"ニュース: {', '.join(data['news'])}。"
        "これらを分析し、要約・トレンド・リスク/チャンスを日本語で簡潔に示してください。"
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
    # 対象銘柄リスト（環境変数STOCK_SYMBOLSから取得、カンマ区切り）
    symbols = [s.strip() for s in STOCK_SYMBOLS.split(',') if s.strip()]
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
