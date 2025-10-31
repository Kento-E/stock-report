"""
メール関連機能のパッケージ

このパッケージは、メール送信、HTMLレポート生成、目次作成などの
メール関連機能を提供します。
"""

from .config import get_smtp_config
from .formatter import markdown_to_html
from .toc import extract_judgment_from_analysis, generate_toc
from .body import generate_single_category_mail_body
from .sender import send_report_via_mail

__all__ = [
    'get_smtp_config',
    'markdown_to_html',
    'extract_judgment_from_analysis',
    'generate_toc',
    'generate_single_category_mail_body',
    'send_report_via_mail',
]
