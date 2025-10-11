"""
レポート生成モジュール

分析結果をHTML形式のレポートとして生成します。
"""

import datetime
from mail_utils import markdown_to_html


def generate_report_html(symbol, name, analysis):
    """
    HTMLレポートを生成する。
    
    Args:
        symbol: 銘柄コード (例: '7203.T')
        name: 企業名 (例: 'トヨタ自動車')
        analysis: 分析結果のテキスト
    
    Returns:
        (html, filename) のタプル
    """
    today = datetime.date.today().isoformat()
    analysis_html = markdown_to_html(analysis)
    # 見出しに企業名を使用し、銘柄コードを副題として表示
    html = f"""
    <html>
    <head><meta charset='utf-8'><title>{name} ({symbol}) 日次レポート ({today})</title></head>
    <body>
    <h1>{name}</h1>
    <p style="color: #666; font-size: 14px;">銘柄コード: {symbol} | 日付: {today}</p>
    {analysis_html}
    </body>
    </html>
    """
    filename = f"report_{symbol}_{today}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return html, filename
