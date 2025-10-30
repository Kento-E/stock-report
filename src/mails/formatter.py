"""
テキストフォーマットモジュール

マークダウンからHTMLへの変換や、レポートセクションの生成を担当します。
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


def create_collapsible_section(content, title="詳細レポート", collapsed=True):
    """
    レポートセクションを生成する。
    
    注意: メールクライアントの制限により、コンテンツは常に表示されます。
    
    Args:
        content: 表示対象のHTMLコンテンツ
        title: セクションのタイトル
        collapsed: 未使用（後方互換性のため保持）
    
    Returns:
        str: HTMLセクション
    """
    html = f"""
<div style="margin-top: 15px; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #007bff; border-radius: 4px;">
    <h3 style="margin: 0 0 10px 0; color: #007bff; font-size: 16px;">{title}</h3>
    <div style="padding-left: 10px;">
{content}
    </div>
</div>
"""
    return html
