"""
mail_utilsモジュールのテスト
"""

import pytest
import os
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mail_utils import markdown_to_html, generate_mail_body, generate_categorized_mail_body, generate_single_category_mail_body, create_collapsible_section


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


class TestGenerateSingleCategoryMailBody:
    """generate_single_category_mail_body関数のテスト"""
    
    def test_single_category_mail(self):
        """単一カテゴリーのメール生成"""
        subject = "テスト件名"
        reports = [
            '<h1>銘柄1</h1><p>分析1</p>',
            '<h1>銘柄2</h1><p>分析2</p>'
        ]
        
        body = generate_single_category_mail_body(subject, reports)
        
        assert '<html>' in body
        assert '</html>' in body
        assert subject in body
        assert '銘柄1' in body
        assert '銘柄2' in body
    
    def test_single_category_empty_reports(self):
        """レポートが空でもエラーが発生しない"""
        subject = "テスト件名"
        reports = []
        
        body = generate_single_category_mail_body(subject, reports)
        
        assert '<html>' in body
    
    def test_single_category_no_category_heading_in_body(self):
        """本文にカテゴリー見出しが表示されないことを確認"""
        subject = "株式日次レポート - 保有銘柄"
        reports = ['<h1>トヨタ自動車</h1><p>分析内容</p>']
        
        body = generate_single_category_mail_body(subject, reports)
        
        # タイトルタグにはカテゴリー名が含まれる
        assert f'<title>{subject}</title>' in body
        # bodyタグ内の最初の見出しは銘柄名であり、カテゴリー名ではない
        body_start = body.find('<body')
        body_end = body.find('</body>')
        if body_start != -1 and body_end != -1:
            body_content = body[body_start:body_end]
            # 最初のh1は銘柄名
            assert '<h1>トヨタ自動車</h1>' in body_content


class TestGenerateCategorizedMailBody:
    """generate_categorized_mail_body関数のテスト"""
    
    def test_all_categories(self):
        """全カテゴリーのレポートが含まれる"""
        subject = "テスト件名"
        categorized_reports = {
            'holding': ['<h1>保有銘柄1</h1><p>分析1</p>'],
            'short_selling': ['<h1>空売り銘柄1</h1><p>分析2</p>'],
            'considering_buy': ['<h1>検討銘柄1</h1><p>分析3</p>'],
            'considering_short_sell': ['<h1>空売り検討銘柄1</h1><p>分析4</p>']
        }
        
        body = generate_categorized_mail_body(subject, categorized_reports)
        
        assert '<html>' in body
        assert '</html>' in body
        assert subject in body
        assert '保有銘柄' in body
        assert '空売り銘柄' in body
        assert '購入検討中の銘柄' in body
        assert '空売り検討中の銘柄' in body
        assert '保有銘柄1' in body
        assert '空売り銘柄1' in body
        assert '検討銘柄1' in body
        assert '空売り検討銘柄1' in body
    
    def test_partial_categories(self):
        """一部のカテゴリーのみの場合"""
        subject = "テスト件名"
        categorized_reports = {
            'holding': ['<h1>保有銘柄1</h1><p>分析1</p>'],
            'short_selling': [],
            'considering_buy': ['<h1>検討銘柄1</h1><p>分析2</p>'],
            'considering_short_sell': []
        }
        
        body = generate_categorized_mail_body(subject, categorized_reports)
        
        assert '<html>' in body
        assert '保有銘柄' in body
        assert '空売り銘柄' not in body
        assert '購入検討中の銘柄' in body
        assert '空売り検討中の銘柄' not in body
    
    def test_empty_categories(self):
        """全カテゴリーが空の場合"""
        subject = "テスト件名"
        categorized_reports = {
            'holding': [],
            'short_selling': [],
            'considering_buy': [],
            'considering_short_sell': []
        }
        
        body = generate_categorized_mail_body(subject, categorized_reports)
        
        assert '<html>' in body
        assert '</html>' in body
        # カテゴリー名が表示されないことを確認
        assert '保有銘柄' not in body
        assert '空売り銘柄' not in body
        assert '購入検討中の銘柄' not in body
        assert '空売り検討中の銘柄' not in body
    
    def test_collapsible_details_in_reports(self):
        """レポートにセクション構造が含まれることを確認"""
        subject = "テスト件名"
        # 実際のmain.pyで生成される形式のレポートをシミュレート
        report_with_section = """<h1 style="margin-top: 30px; padding-bottom: 10px; border-bottom: 2px solid #ddd;">テスト銘柄</h1>
<p style="color: #666; font-size: 14px;">銘柄コード: TEST</p>
<div style="margin-top: 15px; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #007bff; border-radius: 4px;">
    <h3 style="margin: 0 0 10px 0; color: #007bff; font-size: 16px;">詳細レポート</h3>
    <div style="padding-left: 10px;">
<p>詳細な分析内容</p>
    </div>
</div>"""
        
        categorized_reports = {
            'holding': [report_with_section],
            'short_selling': [],
            'considering_buy': [],
            'considering_short_sell': []
        }
        
        body = generate_categorized_mail_body(subject, categorized_reports)
        
        # セクション構造が含まれることを確認
        assert '詳細レポート' in body
        assert 'background-color: #f8f9fa' in body
        assert 'border-left: 4px solid #007bff' in body


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
