"""
メール関連ユーティリティ（後方互換性レイヤー）

このモジュールは後方互換性のために保持されています。
新しいコードでは mail パッケージから直接インポートしてください。

推奨される使用方法:
    from mail import get_smtp_config, send_report_via_mail
    from mail.toc import extract_judgment_from_analysis, generate_toc
    from mail.body import generate_mail_body, generate_categorized_mail_body
    from mail.formatter import markdown_to_html, create_collapsible_section
"""

# 後方互換性のため、mailパッケージから全ての関数をインポート
from mail import (
    get_smtp_config,
    markdown_to_html,
    create_collapsible_section,
    extract_judgment_from_analysis,
    generate_toc,
    generate_mail_body,
    generate_single_category_mail_body,
    generate_categorized_mail_body,
    send_report_via_mail,
)

__all__ = [
    'get_smtp_config',
    'markdown_to_html',
    'create_collapsible_section',
    'extract_judgment_from_analysis',
    'generate_toc',
    'generate_mail_body',
    'generate_single_category_mail_body',
    'generate_categorized_mail_body',
    'send_report_via_mail',
]
