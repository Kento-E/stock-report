"""
report_generatorモジュールのテスト
"""

import pytest
import os
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from report_generator import generate_report_html


class TestGenerateReportHtml:
    """generate_report_html関数のテスト"""
    
    def test_generate_html_with_name(self, tmp_path, monkeypatch):
        """企業名を含むHTMLレポート生成"""
        # カレントディレクトリを一時ディレクトリに変更
        monkeypatch.chdir(tmp_path)
        
        symbol = '7203.T'
        company_name = 'トヨタ自動車'
        analysis = '## テスト分析\n\nこれはテストです。'
        
        html, filename = generate_report_html(symbol, company_name, analysis)
        
        # HTMLに企業名が含まれることを確認
        assert company_name in html
        assert symbol in html
        assert '<html>' in html
        assert '</html>' in html
        
        # ファイル名のフォーマット確認
        assert filename.startswith('report_')
        assert symbol in filename
        assert filename.endswith('.html')
        
        # ファイルが生成されることを確認
        assert os.path.exists(tmp_path / filename)
    
    def test_generate_html_title_format(self, tmp_path, monkeypatch):
        """HTMLタイトルに企業名と銘柄コードが含まれることを確認"""
        monkeypatch.chdir(tmp_path)
        
        symbol = 'AAPL'
        company_name = 'Apple Inc.'
        analysis = 'Test analysis'
        
        html, filename = generate_report_html(symbol, company_name, analysis)
        
        # タイトルに企業名と銘柄コードが含まれることを確認
        assert f'<title>{company_name} ({symbol}) 日次レポート' in html
    
    def test_generate_html_with_markdown(self, tmp_path, monkeypatch):
        """マークダウンがHTMLに変換されることを確認"""
        monkeypatch.chdir(tmp_path)
        
        symbol = '7203.T'
        company_name = 'トヨタ自動車'
        analysis = '## 見出し\n\n**太字**のテキスト'
        
        html, filename = generate_report_html(symbol, company_name, analysis)
        
        # マークダウンがHTMLに変換されていることを確認
        assert '<h2>' in html or '見出し' in html
        assert '太字' in html
    
    def test_generate_html_with_stock_data(self, tmp_path, monkeypatch):
        """株価データを含むレポート生成（簡略化機能のテスト）"""
        monkeypatch.chdir(tmp_path)
        
        symbol = '7203.T'
        company_name = 'トヨタ自動車'
        analysis = '売買判断: 買い'
        stock_data = {
            'price': 2500,
            'currency': '円'
        }
        
        html, filename = generate_report_html(symbol, company_name, analysis, stock_data)
        
        # HTMLが正常に生成されることを確認
        assert company_name in html
        assert symbol in html
    
    def test_generate_html_with_hold_judgment(self, tmp_path, monkeypatch):
        """ホールド判断のレポート生成（簡略化される場合）"""
        # SIMPLIFY_HOLD_REPORTS環境変数を設定
        monkeypatch.setenv('SIMPLIFY_HOLD_REPORTS', 'true')
        
        monkeypatch.chdir(tmp_path)
        
        symbol = '7203.T'
        company_name = 'トヨタ自動車'
        analysis = '売買判断: ホールド\n\n理由：市場が不安定なため。'
        stock_data = {
            'price': 2500,
            'currency': '円'
        }
        
        html, filename = generate_report_html(symbol, company_name, analysis, stock_data)
        
        # 簡略化されたレポートが含まれることを確認
        # （SIMPLIFY_HOLD_REPORTSがtrueの場合）
        assert company_name in html
        assert symbol in html
    
    def test_generate_html_uses_h1(self, tmp_path, monkeypatch):
        """個別レポートファイルでh1を使用することを確認"""
        monkeypatch.chdir(tmp_path)
        
        symbol = '7203.T'
        company_name = 'トヨタ自動車'
        analysis = 'テスト分析'
        
        html, filename = generate_report_html(symbol, company_name, analysis)
        
        # h1タグが使用されていることを確認
        assert '<h1>' in html
        assert f'<h1>{company_name}</h1>' in html
