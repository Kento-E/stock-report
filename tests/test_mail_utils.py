"""
mail_utilsモジュールのテスト
"""

import pytest
import os
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mail_utils import markdown_to_html, generate_mail_body, generate_categorized_mail_body, generate_single_category_mail_body, extract_judgment_from_analysis, generate_toc


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
        """レポートに折りたたみ可能な<details>タグが含まれることを確認"""
        subject = "テスト件名"
        # 実際のmain.pyで生成される形式のレポートをシミュレート
        report_with_details = """<h1 style="margin-top: 30px; padding-bottom: 10px; border-bottom: 2px solid #ddd;">テスト銘柄</h1>
<p style="color: #666; font-size: 14px;">銘柄コード: TEST</p>
<details>
<summary style="cursor: pointer; font-weight: bold; color: #007bff; padding: 10px 0;">詳細レポートを表示</summary>
<div style="margin-top: 15px; padding-left: 20px; border-left: 3px solid #007bff;">
<p>詳細な分析内容</p>
</div>
</details>"""
        
        categorized_reports = {
            'holding': [report_with_details],
            'short_selling': [],
            'considering_buy': [],
            'considering_short_sell': []
        }
        
        body = generate_categorized_mail_body(subject, categorized_reports)
        
        # detailsタグとsummaryタグが含まれることを確認
        assert '<details>' in body
        assert '<summary' in body
        assert '詳細レポートを表示' in body
        assert '</details>' in body


class TestExtractJudgmentFromAnalysis:
    """extract_judgment_from_analysis関数のテスト"""
    
    def test_extract_buy_judgment(self):
        """買い判断の抽出"""
        analysis = """
## 売買判断: 買い
現在の株価は割安であり、買いを推奨します。
"""
        judgment = extract_judgment_from_analysis(analysis)
        assert '買い' in judgment
    
    def test_extract_hold_judgment(self):
        """ホールド判断の抽出"""
        analysis = """
## 売買判断: ホールド
様子見を推奨します。
"""
        judgment = extract_judgment_from_analysis(analysis)
        assert 'ホールド' in judgment
    
    def test_extract_sell_judgment(self):
        """売り判断の抽出"""
        analysis = """
## 売買判断: 売り
利益確定のタイミングです。
"""
        judgment = extract_judgment_from_analysis(analysis)
        assert '売り' in judgment
    
    def test_extract_judgment_with_colon(self):
        """コロン付き判断の抽出"""
        analysis = """
売買判断：買い増し
追加購入を推奨します。
"""
        judgment = extract_judgment_from_analysis(analysis)
        assert '買い' in judgment
    
    def test_extract_judgment_english(self):
        """英語の判断の抽出"""
        analysis = """
Judgment: Buy
The stock is undervalued.
"""
        judgment = extract_judgment_from_analysis(analysis)
        assert 'Buy' in judgment
    
    def test_extract_judgment_not_found(self):
        """判断が見つからない場合"""
        analysis = """
これは株価の分析です。
"""
        judgment = extract_judgment_from_analysis(analysis)
        assert judgment == "-"
    
    def test_extract_judgment_empty(self):
        """空の分析テキスト"""
        judgment = extract_judgment_from_analysis("")
        assert judgment == "-"
    
    def test_extract_judgment_truncate_long(self):
        """長い判断文の切り詰め"""
        analysis = """
売買判断: これは非常に長い判断文で、30文字を超える内容が含まれており、切り詰められるべきです。
"""
        judgment = extract_judgment_from_analysis(analysis)
        assert len(judgment) <= 30


class TestGenerateToc:
    """generate_toc関数のテスト"""
    
    def test_generate_toc_with_multiple_stocks(self):
        """複数銘柄の目次生成"""
        stock_info = [
            {'symbol': '7203.T', 'name': 'トヨタ自動車', 'judgment': '買い', 'id': 'stock-7203-T'},
            {'symbol': 'AAPL', 'name': 'Apple', 'judgment': 'ホールド', 'id': 'stock-AAPL'}
        ]
        
        toc = generate_toc(stock_info)
        
        assert 'トヨタ自動車' in toc
        assert 'Apple' in toc
        assert '7203.T' in toc
        assert 'AAPL' in toc
        assert '買い' in toc
        assert 'ホールド' in toc
        assert 'href="#stock-7203-T"' in toc
        assert 'href="#stock-AAPL"' in toc
        assert '<table' in toc
        assert '銘柄一覧' in toc
    
    def test_generate_toc_single_stock(self):
        """単一銘柄の目次生成"""
        stock_info = [
            {'symbol': '6758.T', 'name': 'ソニー', 'judgment': '売り', 'id': 'stock-6758-T'}
        ]
        
        toc = generate_toc(stock_info)
        
        assert 'ソニー' in toc
        assert '6758.T' in toc
        assert '売り' in toc
        assert 'href="#stock-6758-T"' in toc
    
    def test_generate_toc_empty(self):
        """空のリストの目次生成"""
        toc = generate_toc([])
        assert toc == ""
    
    def test_generate_toc_table_structure(self):
        """テーブル構造の確認"""
        stock_info = [
            {'symbol': 'TEST', 'name': 'テスト銘柄', 'judgment': '様子見', 'id': 'stock-TEST'}
        ]
        
        toc = generate_toc(stock_info)
        
        assert '<thead>' in toc
        assert '<tbody>' in toc
        assert '<th' in toc
        assert '<td' in toc
        assert '銘柄名' in toc
        assert '銘柄コード' in toc
        assert '売買判断' in toc
    
    def test_generate_toc_alternating_colors(self):
        """行の交互背景色の確認"""
        stock_info = [
            {'symbol': 'A', 'name': '銘柄A', 'judgment': '買い', 'id': 'stock-A'},
            {'symbol': 'B', 'name': '銘柄B', 'judgment': '売り', 'id': 'stock-B'},
            {'symbol': 'C', 'name': '銘柄C', 'judgment': 'ホールド', 'id': 'stock-C'}
        ]
        
        toc = generate_toc(stock_info)
        
        # 背景色の指定が含まれることを確認
        assert 'background-color' in toc
    
    def test_generate_toc_html_escaping(self):
        """HTMLエスケープの確認（XSS対策）"""
        stock_info = [
            {
                'symbol': '<script>alert("xss")</script>',
                'name': '<img src=x onerror=alert(1)>',
                'judgment': '<b>危険</b>',
                'id': 'stock-test'
            }
        ]
        
        toc = generate_toc(stock_info)
        
        # 危険なHTMLタグがエスケープされていることを確認
        assert '<script>' not in toc
        assert '<img src=' not in toc  # タグとして解釈されないこと
        # エスケープされた形式で含まれていることを確認
        assert '&lt;script&gt;' in toc
        assert '&lt;img' in toc
        assert '&lt;b&gt;' in toc


class TestGenerateSingleCategoryMailBodyWithToc:
    """generate_single_category_mail_body関数の目次対応テスト"""
    
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


class TestGenerateCategorizedMailBodyWithToc:
    """generate_categorized_mail_body関数の目次対応テスト"""
    
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
