"""
format_yaml.pyのテスト
"""

import os
import sys
from pathlib import Path

import pytest

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from formatters.format_yaml import format_yaml_file


class TestFormatYaml:
    """format_yaml.pyの機能テスト"""

    def test_format_yaml_well_formatted(self, tmp_path):
        """既にフォーマットされているYAMLファイルは変更されない"""
        yaml_file = tmp_path / "test.yaml"
        content = """stocks:
  - name: テスト株
    symbol: 1234
    quantity: 100
"""
        yaml_file.write_text(content, encoding="utf-8")

        changed, message = format_yaml_file(str(yaml_file))

        assert changed is False
        assert "変更なし" in message
        assert yaml_file.read_text(encoding="utf-8") == content

    def test_format_yaml_bad_indentation(self, tmp_path):
        """インデントがずれているYAMLファイルが修正される"""
        yaml_file = tmp_path / "test.yaml"
        bad_content = """stocks:
  - name:   テスト株
    symbol:    1234
    quantity:     100
"""
        yaml_file.write_text(bad_content, encoding="utf-8")

        changed, message = format_yaml_file(str(yaml_file))

        assert changed is True
        assert "フォーマット完了" in message

        formatted = yaml_file.read_text(encoding="utf-8")
        assert "name:   " not in formatted
        assert "symbol:    " not in formatted
        assert "name: テスト株" in formatted
        assert "symbol: 1234" in formatted

    def test_format_yaml_preserves_comments(self, tmp_path):
        """コメントが保持される"""
        yaml_file = tmp_path / "test.yaml"
        content = """# メインコメント
stocks:
  # 銘柄リスト
  - name: テスト株
    symbol: 1234
"""
        yaml_file.write_text(content, encoding="utf-8")

        changed, message = format_yaml_file(str(yaml_file))

        formatted = yaml_file.read_text(encoding="utf-8")
        assert "# メインコメント" in formatted
        assert "# 銘柄リスト" in formatted

    def test_format_yaml_preserves_quotes(self, tmp_path):
        """引用符が保持される"""
        yaml_file = tmp_path / "test.yaml"
        content = """stocks:
  - name: "テスト株"
    note: "メモ"
"""
        yaml_file.write_text(content, encoding="utf-8")

        changed, message = format_yaml_file(str(yaml_file))

        formatted = yaml_file.read_text(encoding="utf-8")
        assert '"テスト株"' in formatted
        assert '"メモ"' in formatted

    def test_format_yaml_check_only_mode(self, tmp_path):
        """check_onlyモードでファイルが変更されない"""
        yaml_file = tmp_path / "test.yaml"
        bad_content = """stocks:
  - name:   テスト株
    symbol:    1234
"""
        yaml_file.write_text(bad_content, encoding="utf-8")

        changed, message = format_yaml_file(str(yaml_file), check_only=True)

        assert changed is True
        assert "フォーマットが必要" in message
        # ファイルは変更されていないことを確認
        assert yaml_file.read_text(encoding="utf-8") == bad_content

    def test_format_yaml_file_not_found(self):
        """存在しないファイルを指定するとエラーになる"""
        changed, message = format_yaml_file("/nonexistent/file.yaml")

        assert changed is False
        assert "見つかりません" in message

    def test_format_yaml_invalid_yaml(self, tmp_path):
        """不正なYAML構文のファイルを扱う"""
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text(
            "stocks:\n  - name: テスト\n  invalid yaml syntax {{", encoding="utf-8"
        )

        changed, message = format_yaml_file(str(yaml_file))

        assert changed is False
        assert "エラー" in message

    def test_format_yaml_complex_structure(self, tmp_path):
        """複雑なYAML構造が正しくフォーマットされる"""
        yaml_file = tmp_path / "complex.yaml"
        content = """stocks:
  - name:  テスト株1
    symbol:  1234
    quantity:    100
    acquisition_price:   1000
    note:  "メモ"
  - name: テスト株2
    symbol:  5678
    account_type:  NISA
"""
        yaml_file.write_text(content, encoding="utf-8")

        changed, message = format_yaml_file(str(yaml_file))

        assert changed is True
        formatted = yaml_file.read_text(encoding="utf-8")
        # インデントが統一されていることを確認
        lines = formatted.splitlines()
        for line in lines:
            if line.strip() and not line.startswith("#"):
                # 行頭の空白が2の倍数であることを確認
                leading_spaces = len(line) - len(line.lstrip())
                assert leading_spaces % 2 == 0, f"Invalid indentation in line: {line}"

    def test_format_yaml_investment_preferences(self, tmp_path):
        """投資志向性設定ファイルのフォーマット"""
        yaml_file = tmp_path / "preferences.yaml"
        content = """investment_style:   value
risk_tolerance:    high
focus_areas:
  -  fundamental
  -   news
"""
        yaml_file.write_text(content, encoding="utf-8")

        changed, message = format_yaml_file(str(yaml_file))

        assert changed is True
        formatted = yaml_file.read_text(encoding="utf-8")
        assert "investment_style: value" in formatted
        assert "risk_tolerance: high" in formatted
        assert "- fundamental" in formatted
        assert "- news" in formatted
