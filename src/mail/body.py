"""
メール本文生成モジュール

銘柄レポートからHTMLメール本文を生成します。
単一カテゴリー、分類別など、複数の形式に対応しています。
"""

import datetime


def generate_mail_body(subject, all_reports):
    """
    シンプルなメール本文を生成する（後方互換性のため保持）
    
    Args:
        subject: メール件名
        all_reports: レポートのリスト
    
    Returns:
        str: HTML形式のメール本文
    """
    today = datetime.date.today().isoformat()
    body = f"""
    <html>
    <head><meta charset='utf-8'><title>{subject}</title></head>
    <body>
    {''.join(all_reports)}
    </body>
    </html>
    """
    return body


def generate_single_category_mail_body(subject, reports, toc_html=""):
    """
    単一カテゴリーのレポートからHTMLメール本文を生成する。
    
    Args:
        subject: メール件名
        reports: レポートのリスト
        toc_html: 目次のHTML（省略可能）
    
    Returns:
        str: HTML形式のメール本文
    """
    body = f"""
    <html>
    <head><meta charset='utf-8'><title>{subject}</title></head>
    <body style="font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px;">
    {toc_html}
    {''.join(reports)}
    </body>
    </html>
    """
    return body


def generate_categorized_mail_body(subject, categorized_reports, toc_html=""):
    """
    分類別のレポートからHTMLメール本文を生成する。
    
    Args:
        subject: メール件名
        categorized_reports: 分類別のレポート辞書
            {'holding': [...], 'short_selling': [...], 'considering_buy': [...], 'considering_short_sell': [...]}
        toc_html: 目次のHTML（省略可能）
    
    Returns:
        str: HTML形式のメール本文
    """
    category_names = {
        'holding': '保有銘柄',
        'short_selling': '空売り銘柄',
        'considering_buy': '購入検討中の銘柄',
        'considering_short_sell': '空売り検討中の銘柄'
    }
    
    sections = []
    
    # 各分類のセクションを生成
    for category in ['holding', 'short_selling', 'considering_buy', 'considering_short_sell']:
        reports = categorized_reports.get(category, [])
        if reports:
            section_title = category_names[category]
            section_html = f'<h2 style="color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-top: 30px;">{section_title}</h2>\n'
            section_html += ''.join(reports)
            sections.append(section_html)
    
    body = f"""
    <html>
    <head><meta charset='utf-8'><title>{subject}</title></head>
    <body style="font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px;">
    {toc_html}
    {''.join(sections)}
    </body>
    </html>
    """
    return body
