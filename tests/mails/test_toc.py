"""
mail.tocモジュールのテスト
"""

import pytest
import os
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from mails.toc import extract_judgment_from_analysis, generate_toc


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
    
    def test_extract_judgment_removes_trailing_verbs(self):
        """動詞や説明文が含まれる判断からクリーンな判断のみを抽出"""
        # ユーザーが報告した問題のテストケース
        test_cases = [
            ("売買判断: 買いを推奨します", "買い"),
            ("売買判断：ホールドを提供します", "ホールド"),
            ("判断: 買い増しが良いでしょう", "買い増し"),
            ("売買判断：様子見を維持します", "様子見"),
        ]
        
        for analysis, expected in test_cases:
            judgment = extract_judgment_from_analysis(analysis)
            # 動詞や助詞が含まれていないことを確認
            assert 'を推奨' not in judgment
            assert 'を提供' not in judgment
            assert 'が良い' not in judgment
            assert 'を維持' not in judgment
            # 期待される判断が含まれることを確認
            assert expected in judgment


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
        # リンクは削除されたため、href属性は存在しない
        assert 'href=' not in toc
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
        # リンクは削除されたため、href属性は存在しない
        assert 'href=' not in toc
    
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
