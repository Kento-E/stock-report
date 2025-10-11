"""
mail_utilsモジュールのテスト
"""

import pytest
import os
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mail_utils import markdown_to_html, generate_mail_body


class TestMarkdownToHtml:
    """markdown_to_html関数のテスト"""
    
    def test_simple_markdown_conversion(self):
        """シンプルなマークダウンのHTML変換"""
        markdown_text = "# 見出し\n\nテキスト"
        html = markdown_to_html(markdown_text)
        
        assert '<h1>' in html or 'h1' in html.lower()
        assert '見出し' in html
        assert 'テキスト' in html
    
    def test_bold_conversion(self):
        """太字マークダウンの変換"""
        markdown_text = "**太字**のテキスト"
        html = markdown_to_html(markdown_text)
        
        assert '太字' in html
    
    def test_list_conversion(self):
        """リストマークダウンの変換"""
        markdown_text = "- 項目1\n- 項目2"
        html = markdown_to_html(markdown_text)
        
        assert '項目1' in html
        assert '項目2' in html


class TestGenerateMailBody:
    """generate_mail_body関数のテスト"""
    
    def test_generate_mail_body_with_reports(self):
        """レポートを含むメール本文の生成"""
        subject = "テスト件名"
        reports = [
            "<h1>銘柄1</h1><p>分析内容1</p>",
            "<h1>銘柄2</h1><p>分析内容2</p>"
        ]
        
        body = generate_mail_body(subject, reports)
        
        assert '<html>' in body
        assert '</html>' in body
        assert subject in body
        assert '銘柄1' in body
        assert '銘柄2' in body
        assert '分析内容1' in body
        assert '分析内容2' in body
    
    def test_generate_mail_body_empty_reports(self):
        """空のレポートリストでもエラーが発生しない"""
        subject = "テスト件名"
        reports = []
        
        body = generate_mail_body(subject, reports)
        
        assert '<html>' in body
        assert '</html>' in body
        assert subject in body
