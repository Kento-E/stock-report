"""
メール本文生成モジュール

銘柄レポートからHTMLメール本文を生成します。
"""

import datetime


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
