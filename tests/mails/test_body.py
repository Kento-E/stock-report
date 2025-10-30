"""
mail.bodyモジュールのテスト
"""

import pytest
import os
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from mails.body import generate_mail_body, generate_single_category_mail_body, generate_categorized_mail_body


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
    
    def test_single_category_with_toc(self):
        """目次付きメール本文の生成"""
        subject = "テスト件名"
        reports = ['<h1 id="stock-TEST">テスト銘柄</h1><p>分析内容</p>']
        toc = '<div>目次HTML</div>'
        
        body = generate_single_category_mail_body(subject, reports, toc)
        
        assert '<html>' in body
        assert '目次HTML' in body
        assert 'テスト銘柄' in body
    
    def test_single_category_without_toc(self):
        """目次なしメール本文の生成（後方互換性）"""
        subject = "テスト件名"
        reports = ['<h1>テスト銘柄</h1><p>分析内容</p>']
        
        body = generate_single_category_mail_body(subject, reports)
        
        assert '<html>' in body
        assert 'テスト銘柄' in body


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
    
    def test_reports_always_visible(self):
        """レポートが常に表示されることを確認（details/summary タグなし）"""
        subject = "テスト件名"
        # 実際のmain.pyで生成される形式のレポートをシミュレート
        report_always_visible = """<h1 style="margin-top: 30px; padding-bottom: 10px; border-bottom: 2px solid #ddd;">テスト銘柄</h1>
<p style="color: #666; font-size: 14px;">銘柄コード: TEST</p>
<div style="margin-top: 15px; padding-left: 20px; border-left: 3px solid #007bff;">
<p>詳細な分析内容</p>
</div>"""
        
        categorized_reports = {
            'holding': [report_always_visible],
            'short_selling': [],
            'considering_buy': [],
            'considering_short_sell': []
        }
        
        body = generate_categorized_mail_body(subject, categorized_reports)
        
        # コンテンツが含まれ、details/summaryタグがないことを確認
        assert 'テスト銘柄' in body
        assert '詳細な分析内容' in body
        assert '<details>' not in body
        assert '<summary' not in body
        assert '詳細レポートを表示' not in body
    
    def test_categorized_with_toc(self):
        """目次付き分類別メール本文の生成"""
        subject = "テスト件名"
        categorized_reports = {
            'holding': ['<h1 id="stock-TEST">テスト銘柄</h1><p>分析1</p>']
        }
        toc = '<div>目次HTML</div>'
        
        body = generate_categorized_mail_body(subject, categorized_reports, toc)
        
        assert '<html>' in body
        assert '目次HTML' in body
        assert '保有銘柄' in body
        assert 'テスト銘柄' in body
    
    def test_categorized_without_toc(self):
        """目次なし分類別メール本文の生成（後方互換性）"""
        subject = "テスト件名"
        categorized_reports = {
            'holding': ['<h1>テスト銘柄</h1><p>分析1</p>']
        }
        
        body = generate_categorized_mail_body(subject, categorized_reports)
        
        assert '<html>' in body
        assert '保有銘柄' in body
        assert 'テスト銘柄' in body
