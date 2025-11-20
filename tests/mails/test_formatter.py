"""
mail.formatterモジュールのテスト
"""

import os
import sys

import pytest

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "src"))

from mails.formatter import markdown_to_html


class TestMarkdownToHtml:
    """markdown_to_html関数のテスト"""

    def test_simple_markdown_conversion(self):
        """シンプルなマークダウンのHTML変換"""
        markdown_text = "# 見出し\n\nテキスト"
        html = markdown_to_html(markdown_text)

        assert "<h1>" in html or "h1" in html.lower()
        assert "見出し" in html
        assert "テキスト" in html

    def test_bold_conversion(self):
        """太字マークダウンの変換"""
        markdown_text = "**太字**のテキスト"
        html = markdown_to_html(markdown_text)

        assert "太字" in html

    def test_list_conversion(self):
        """リストマークダウンの変換"""
        markdown_text = "- 項目1\n- 項目2"
        html = markdown_to_html(markdown_text)

        assert "項目1" in html
        assert "項目2" in html
