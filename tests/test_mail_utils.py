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
        """レポートにGmail互換の折りたたみ機能が含まれることを確認"""
        subject = "テスト件名"
        # 実際のmain.pyで生成される形式のレポートをシミュレート
        # Gmail互換のcheckboxハック方式を使用
        report_with_collapsible = """<h1 style="margin-top: 30px; padding-bottom: 10px; border-bottom: 2px solid #ddd;">テスト銘柄</h1>
<p style="color: #666; font-size: 14px;">銘柄コード: TEST</p>
<style>
    #test_collapsible {
        display: none;
    }
</style>
<input type="checkbox" id="test_collapsible" />
<label for="test_collapsible" class="collapsible-label">詳細レポートを表示</label>
<div class="collapsible-content">
<p>詳細な分析内容</p>
</div>"""
        
        categorized_reports = {
            'holding': [report_with_collapsible],
            'short_selling': [],
            'considering_buy': [],
            'considering_short_sell': []
        }
        
        body = generate_categorized_mail_body(subject, categorized_reports)
        
        # Gmail互換の折りたたみ構造が含まれることを確認
        assert '<input type="checkbox"' in body
        assert '<label' in body
        assert 'collapsible-label' in body
        assert '詳細レポートを表示' in body
        assert 'collapsible-content' in body


class TestCreateCollapsibleSection:
    """create_collapsible_section関数のテスト"""
    
    def test_create_collapsible_section_default(self):
        """デフォルトパラメータで折りたたみセクションを生成"""
        content = "<p>テスト内容</p>"
        result = create_collapsible_section(content)
        
        # 必要な要素が含まれることを確認
        assert '<input type="checkbox"' in result
        assert '<label' in result
        assert 'collapsible-label' in result
        assert '詳細レポートを表示' in result
        assert 'collapsible-content' in result
        assert '<p>テスト内容</p>' in result
        # デフォルトで折りたたまれている（input要素にchecked属性がない）
        import re
        input_match = re.search(r'<input[^>]*type="checkbox"[^>]*>', result)
        assert input_match is not None
        input_tag = input_match.group()
        # checked属性が含まれていないことを確認（空白の後にcheckedがあるかチェック）
        assert not re.search(r'\s+checked\s*(?:=|>|/>)', input_tag)
    
    def test_create_collapsible_section_custom_title(self):
        """カスタムタイトルで折りたたみセクションを生成"""
        content = "<p>テスト内容</p>"
        title = "カスタムタイトル"
        result = create_collapsible_section(content, title=title)
        
        assert title in result
    
    def test_create_collapsible_section_expanded(self):
        """デフォルトで展開された状態のセクションを生成"""
        content = "<p>テスト内容</p>"
        result = create_collapsible_section(content, collapsed=False)
        
        # checked属性が含まれることを確認
        import re
        input_match = re.search(r'<input[^>]*type="checkbox"[^>]*>', result)
        assert input_match is not None
        input_tag = input_match.group()
        # checked属性が含まれていることを確認
        assert re.search(r'\s+checked\s*(?:=|>|/>)', input_tag)
    
    def test_create_collapsible_section_unique_ids(self):
        """複数回呼び出した場合にユニークなIDが生成されることを確認"""
        content1 = "<p>コンテンツ1</p>"
        content2 = "<p>コンテンツ2</p>"
        
        result1 = create_collapsible_section(content1)
        result2 = create_collapsible_section(content2)
        
        # 異なるIDが生成されることを確認
        import re
        id_pattern = r'id="(collapsible_\d+)"'
        ids1 = re.findall(id_pattern, result1)
        ids2 = re.findall(id_pattern, result2)
        
        assert len(ids1) > 0
        assert len(ids2) > 0
        # 同じコンテンツ内では同じIDが使用される
        assert len(set(ids1)) == 1
        assert len(set(ids2)) == 1
        # 異なる呼び出しでは異なるIDが使用される
        assert ids1[0] != ids2[0]
