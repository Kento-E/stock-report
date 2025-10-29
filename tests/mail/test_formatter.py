"""
mail.formatterモジュールのテスト
"""

import pytest
import os
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from mail.formatter import markdown_to_html, create_collapsible_section


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


class TestCreateCollapsibleSection:
    """create_collapsible_section関数のテスト"""
    
    def test_create_collapsible_section_default(self):
        """デフォルトパラメータでセクションを生成"""
        content = "<p>テスト内容</p>"
        result = create_collapsible_section(content)
        
        # 必要な要素が含まれることを確認
        assert '<p>テスト内容</p>' in result
        assert 'background-color: #f8f9fa' in result
        assert 'border-left: 4px solid #007bff' in result
        assert '詳細レポート' in result
    
    def test_create_collapsible_section_custom_title(self):
        """カスタムタイトルでセクションを生成"""
        content = "<p>テスト内容</p>"
        title = "カスタムタイトル"
        result = create_collapsible_section(content, title=title)
        
        assert title in result
        assert '<p>テスト内容</p>' in result
    
    def test_create_collapsible_section_expanded(self):
        """collapsed引数は無視されることを確認（後方互換性）"""
        content = "<p>テスト内容</p>"
        result = create_collapsible_section(content, collapsed=False)
        
        # collapsed引数に関わらず同じ出力
        assert '<p>テスト内容</p>' in result
        assert 'background-color: #f8f9fa' in result
    
    def test_create_collapsible_section_always_visible(self):
        """コンテンツが常に表示されることを確認"""
        content1 = "<p>コンテンツ1</p>"
        content2 = "<p>コンテンツ2</p>"
        
        result1 = create_collapsible_section(content1)
        result2 = create_collapsible_section(content2)
        
        # 両方のコンテンツが含まれる
        assert '<p>コンテンツ1</p>' in result1
        assert '<p>コンテンツ2</p>' in result2
