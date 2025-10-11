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
        name = 'トヨタ自動車'
        analysis = '## テスト分析\n\nこれはテストです。'
        
        html, filename = generate_report_html(symbol, name, analysis)
        
        # HTMLに企業名が含まれることを確認
        assert name in html
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
        name = 'Apple Inc.'
        analysis = 'Test analysis'
        
        html, filename = generate_report_html(symbol, name, analysis)
        
        # タイトルに企業名と銘柄コードが含まれることを確認
        assert f'<title>{name} ({symbol}) 日次レポート' in html
    
    def test_generate_html_with_markdown(self, tmp_path, monkeypatch):
        """マークダウンがHTMLに変換されることを確認"""
        monkeypatch.chdir(tmp_path)
        
        symbol = '7203.T'
        name = 'トヨタ自動車'
        analysis = '## 見出し\n\n**太字**のテキスト'
        
        html, filename = generate_report_html(symbol, name, analysis)
        
        # マークダウンがHTMLに変換されていることを確認
        assert '<h2>' in html or '見出し' in html
        assert '太字' in html
