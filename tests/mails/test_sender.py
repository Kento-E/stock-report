"""
mail.senderモジュールのテスト
"""

import os
import sys

import pytest

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "src"))

from mails.sender import send_report_via_mail


class TestSendReportViaMail:
    """send_report_via_mail関数のテスト"""

    def test_send_report_via_mail_signature(self):
        """send_report_via_mail関数が存在し、呼び出し可能であることを確認"""
        # 実際のメール送信はテスト環境では実行しないため、
        # 関数の存在とシグネチャのみを確認
        assert callable(send_report_via_mail)

        # 関数のパラメータを確認
        import inspect

        sig = inspect.signature(send_report_via_mail)
        params = list(sig.parameters.keys())
        assert "subject" in params
        assert "html_body" in params
        assert "to_addrs" in params
        assert "mail_from" in params
        assert "smtp_server" in params
        assert "smtp_port" in params
        assert "smtp_user" in params
        assert "smtp_pass" in params
