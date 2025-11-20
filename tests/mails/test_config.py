"""
mail.configモジュールのテスト
"""

import os
import sys

import pytest

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "src"))

from mails.config import get_smtp_config


class TestGetSmtpConfig:
    """get_smtp_config関数のテスト"""

    def test_get_smtp_config_returns_dict(self):
        """SMTP設定が辞書として返されることを確認"""
        config = get_smtp_config()

        assert isinstance(config, dict)
        assert "SMTP_SERVER" in config
        assert "SMTP_PORT" in config
        assert "SMTP_USER" in config
        assert "SMTP_PASS" in config
        assert "MAIL_FROM" in config
