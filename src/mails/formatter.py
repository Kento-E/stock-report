"""
テキストフォーマットモジュール

マークダウンからHTMLへの変換を担当します。
"""

import markdown


def markdown_to_html(markdown_text):
    """
    マークダウンテキストをHTMLに変換
    
    Args:
        markdown_text: マークダウン形式のテキスト
    
    Returns:
        str: HTML形式のテキスト
    """
    return markdown.markdown(markdown_text, extensions=['extra', 'nl2br'])
