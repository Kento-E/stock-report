"""
SMTP設定管理モジュール

環境変数からSMTP設定を取得し、メール送信に必要な設定を提供します。
"""

import os


def get_smtp_config():
    """
    環境変数からSMTP設定を取得
    
    Returns:
        dict: SMTP設定情報
            - MAIL_FROM: 送信元メールアドレス
            - SMTP_SERVER: SMTPサーバーアドレス
            - SMTP_PORT: SMTPポート番号
            - SMTP_USER: SMTP認証ユーザー名
            - SMTP_PASS: SMTP認証パスワード
    """
    return {
        'MAIL_FROM': os.getenv('MAIL_FROM'),
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_PORT': int(os.getenv('SMTP_PORT', '587')),
        'SMTP_USER': os.getenv('SMTP_USER'),
        'SMTP_PASS': os.getenv('SMTP_PASS'),
    }
