"""
レポート生成モジュール

分析結果をHTML形式のレポートとして生成します。
"""

import datetime
from mail_utils import markdown_to_html


def generate_report_html(symbol, name, analysis, is_ipo=False):
    """
    HTMLレポートを生成する。
    
    Args:
        symbol: 銘柄コード (例: '7203.T')
        name: 企業名 (例: 'トヨタ自動車')
        analysis: 分析結果のテキスト
        is_ipo: IPO銘柄の場合True（デフォルト: False）
    
    Returns:
        (html, filename) のタプル
    """
    today = datetime.date.today().isoformat()
    analysis_html = markdown_to_html(analysis)
    
    # IPO銘柄の場合はタイトルと見出しを変更
    if is_ipo:
        title_suffix = "上場予定銘柄レポート"
        heading_suffix = "（上場予定）"
    else:
        title_suffix = "日次レポート"
        heading_suffix = ""
    
    # 見出しに企業名を使用し、銘柄コードを副題として表示
    html = f"""
    <html>
    <head><meta charset='utf-8'><title>{name} ({symbol}) {title_suffix} ({today})</title></head>
    <body>
    <h1>{name}{heading_suffix}</h1>
    <p style="color: #666; font-size: 14px;">銘柄コード: {symbol} | 日付: {today}</p>
    {analysis_html}
    </body>
    </html>
    """
    
    # IPO銘柄の場合はファイル名にipo_プレフィックスを追加
    prefix = "ipo_report_" if is_ipo else "report_"
    filename = f"{prefix}{symbol}_{today}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return html, filename
