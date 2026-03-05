"""
format_toml.pyのテスト
"""

import os
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from formatters.format_toml import format_toml_file


class TestFormatToml:
    """format_toml.pyの機能テスト"""

    def test_validate_valid_toml(self, tmp_path):
        """正常なTOMLファイルはエラーなし"""
        toml_file = tmp_path / "test.toml"
        content = """[[stocks]]
name = "テスト株"
symbol = "1234"
quantity = 100
"""
        toml_file.write_text(content, encoding="utf-8")

        has_error, message = format_toml_file(str(toml_file))

        assert has_error is False
        assert "エラーなし" in message

    def test_validate_invalid_toml(self, tmp_path):
        """不正なTOML構文のファイルはエラーあり"""
        toml_file = tmp_path / "invalid.toml"
        toml_file.write_text("invalid toml [[[", encoding="utf-8")

        has_error, message = format_toml_file(str(toml_file))

        assert has_error is True
        assert "TOML構文エラー" in message

    def test_validate_file_not_found(self):
        """存在しないファイルを指定するとエラーになる"""
        has_error, message = format_toml_file("/nonexistent/file.toml")

        assert has_error is False
        assert "見つかりません" in message

    def test_validate_investment_preferences(self, tmp_path):
        """投資志向性設定ファイルの検証"""
        toml_file = tmp_path / "preferences.toml"
        content = """investment_style = "value"
risk_tolerance = "high"
focus_areas = ["fundamental", "news"]
"""
        toml_file.write_text(content, encoding="utf-8")

        has_error, message = format_toml_file(str(toml_file))

        assert has_error is False

    def test_check_only_mode_same_behavior(self, tmp_path):
        """check_onlyモードでも同じ動作をする（TOMLは再フォーマット不要）"""
        toml_file = tmp_path / "test.toml"
        content = 'name = "テスト"\n'
        toml_file.write_text(content, encoding="utf-8")

        has_error_normal, _ = format_toml_file(str(toml_file))
        has_error_check, _ = format_toml_file(str(toml_file), check_only=True)

        assert has_error_normal == has_error_check
        # ファイルは変更されていないことを確認
        assert toml_file.read_text(encoding="utf-8") == content

    def test_validate_stocks_toml(self, tmp_path):
        """stocks.toml形式のファイルの検証"""
        toml_file = tmp_path / "stocks.toml"
        content = """[[stocks]]
name = "テスト株1"
symbol = "1234"
quantity = 100
acquisition_price = 1000
account_type = "NISA"

[[stocks]]
name = "テスト株2"
symbol = "5678"
account_type = "旧NISA"
"""
        toml_file.write_text(content, encoding="utf-8")

        has_error, message = format_toml_file(str(toml_file))

        assert has_error is False
