"""
レポート生成モジュール

分析結果をHTML形式のレポートとして生成します。
"""

import datetime
import os
from mails.formatter import markdown_to_html
from reports.simplifier import detect_hold_judgment, simplify_hold_report


def generate_report_html(symbol, company_name, analysis, stock_data=None):
    """
    HTMLレポートを生成する。
    
    Args:
        symbol: 銘柄コード (例: '7203.T')
        company_name: 企業名 (例: 'トヨタ自動車')
        analysis: 分析結果のテキスト
        stock_data: 株価データ（簡略化レポート用、オプション）
    
    Returns:
        (html, filename) のタプル
    """
    today = datetime.date.today().isoformat()
    
    # 簡略化オプションを環境変数から取得（config.pyを経由せずに直接取得）
    simplify_hold = os.getenv('SIMPLIFY_HOLD_REPORTS', 'true').lower() in ('true', '1', 'yes')
    
    # ホールド判断の検出と簡略化
    if simplify_hold and detect_hold_judgment(analysis):
        if stock_data:
            current_price = stock_data.get('price', 'N/A')
            currency = stock_data.get('currency', '円')
        else:
            # stock_dataがない場合はデフォルト値を使用
            current_price = 'N/A'
            currency = '円'
        
        # 簡略化されたレポートを生成
        analysis = simplify_hold_report(symbol, company_name, analysis, current_price, currency)
    
    analysis_html = markdown_to_html(analysis)
    # 見出しに企業名と銘柄コードを統合して表示
    html = f"""
    <html>
    <head><meta charset='utf-8'><title>{company_name} ({symbol}) 日次レポート ({today})</title></head>
    <body>
    <h1>{company_name}（{symbol}）</h1>
    <p style="color: #666; font-size: 14px;">日付: {today}</p>
    {analysis_html}
    </body>
    </html>
    """
    filename = f"report_{symbol}_{today}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return html, filename
