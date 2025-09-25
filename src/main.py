
"""
Claude Sonnet株式レポートシステム

Github Actions上で定期実行可能。APIキーや設定値はSecrets/環境変数で管理。
レポートはHTML形式で生成し、メール配信処理の雛形も含む。

- データ収集（株価・ニュース）
- Claude Sonnet APIによる分析
- レポート生成（HTML形式）
- メール配信（SMTP設定は環境変数で管理）
"""

import os
import datetime
import smtplib
import requests
from email.mime.text import MIMEText
from email.utils import formatdate

# 必要なAPIキーや設定値は環境変数（Github Secrets）で管理
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
MAIL_TO = os.getenv('MAIL_TO')
MAIL_FROM = os.getenv('MAIL_FROM')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
YAHOO_API_KEY = os.getenv('YAHOO_API_KEY')

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
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "Content-Type": "application/json"
    }
    prompt = f"{data['symbol']}の株価は{data['price']}円です。ニュース: {', '.join(data['news'])}。これらを分析してください。"
    payload = {
        "model": "claude-sonnet-3",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            result = response.json()
            # Claude APIのレスポンス仕様に合わせて取得
            return result["choices"][0]["message"]["content"]
        else:
            print(f"Claude APIエラー: {response.text}")
            return "分析失敗"
    except Exception as e:
        print(f"Claude API呼び出し失敗: {e}")
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

# 4. メール配信（雛形）
def send_report_via_mail(subject, html_body, to_addr):
    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = MAIL_FROM
    msg["To"] = to_addr
    msg["Date"] = formatdate(localtime=True)
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(MAIL_FROM, [to_addr], msg.as_string())
        print(f"メール送信成功: {to_addr}")
    except Exception as e:
        print(f"メール送信失敗: {e}")

if __name__ == "__main__":
    # 対象銘柄リスト（例）
    symbols = ['7203.T', '6758.T']
    all_reports = []
    for symbol in symbols:
        data = fetch_stock_data(symbol)
        analysis = analyze_with_claude(data)
        html, filename = generate_report_html(symbol, analysis)
        print(f"レポート生成: {filename}")
        all_reports.append(f"<h2>{symbol}</h2>\n{analysis}")

    # 全銘柄分まとめてメール送信
    if MAIL_TO and MAIL_FROM and SMTP_SERVER and SMTP_USER and SMTP_PASS:
        today = datetime.date.today().isoformat()
        subject = f"株式日次レポート ({today})"
        body = f"""
        <html>
        <head><meta charset='utf-8'><title>{subject}</title></head>
        <body>
        <h1>{subject}</h1>
        {''.join(all_reports)}
        </body>
        </html>
        """
        send_report_via_mail(subject, body, MAIL_TO)
