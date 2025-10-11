"""
stock_loaderモジュールのテスト
"""

import pytest
import yaml
import os
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from stock_loader import load_stock_symbols, get_currency_for_symbol


class TestGetCurrencyForSymbol:
    """get_currency_for_symbol関数のテスト"""
    
    def test_japanese_stock_with_t_suffix(self):
        """日本株（.T）の通貨判定"""
        assert get_currency_for_symbol('7203.T') == '円'
    
    def test_japanese_stock_with_jp_suffix(self):
        """日本株（.JP）の通貨判定"""
        assert get_currency_for_symbol('6758.JP') == '円'
    
    def test_us_stock(self):
        """米国株の通貨判定"""
        assert get_currency_for_symbol('AAPL') == 'ドル'
        assert get_currency_for_symbol('MSFT') == 'ドル'


class TestLoadStockSymbols:
    """load_stock_symbols関数のテスト"""
    
    def test_load_valid_yaml_file(self, tmp_path):
        """正常なYAMLファイルの読み込み"""
        # テスト用YAMLファイルを作成
        test_yaml = tmp_path / "test_stocks.yaml"
        test_data = {
            'stocks': [
                {
                    'symbol': '7203.T',
                    'name': 'トヨタ自動車',
                    'quantity': 100,
                    'acquisition_price': 2500
                },
                {
                    'symbol': 'AAPL',
                    'name': 'Apple Inc.'
                }
            ]
        }
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f, allow_unicode=True)
        
        # 読み込みテスト
        result = load_stock_symbols(str(test_yaml))
        
        assert len(result) == 2
        assert result[0]['symbol'] == '7203.T'
        assert result[0]['name'] == 'トヨタ自動車'
        assert result[0]['quantity'] == 100
        assert result[0]['acquisition_price'] == 2500
        assert result[1]['symbol'] == 'AAPL'
        assert result[1]['name'] == 'Apple Inc.'
    
    def test_load_file_not_found(self):
        """存在しないファイルの読み込みでエラー"""
        with pytest.raises(FileNotFoundError):
            load_stock_symbols('/nonexistent/path/stocks.yaml')
    
    def test_load_empty_stocks_list(self, tmp_path):
        """空の銘柄リストでエラー"""
        test_yaml = tmp_path / "empty_stocks.yaml"
        test_data = {'stocks': []}
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f)
        
        with pytest.raises(ValueError):
            load_stock_symbols(str(test_yaml))
    
    def test_load_no_stocks_key(self, tmp_path):
        """stocksキーがない場合"""
        test_yaml = tmp_path / "no_stocks_key.yaml"
        test_data = {'other_key': 'value'}
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f)
        
        with pytest.raises(ValueError):
            load_stock_symbols(str(test_yaml))
    
    def test_load_invalid_yaml(self, tmp_path):
        """不正なYAMLファイルの読み込み"""
        test_yaml = tmp_path / "invalid.yaml"
        with open(test_yaml, 'w') as f:
            f.write("invalid: yaml: syntax:")
        
        with pytest.raises(yaml.YAMLError):
            load_stock_symbols(str(test_yaml))
    
    def test_backward_compatibility_string_format(self, tmp_path):
        """後方互換性：文字列形式の銘柄リスト"""
        test_yaml = tmp_path / "string_stocks.yaml"
        test_data = {
            'stocks': ['7203.T', 'AAPL']
        }
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f)
        
        result = load_stock_symbols(str(test_yaml))
        
        assert len(result) == 2
        assert result[0]['symbol'] == '7203.T'
        assert result[1]['symbol'] == 'AAPL'
    
    def test_holding_info_fields(self, tmp_path):
        """保有情報フィールドのテスト"""
        test_yaml = tmp_path / "holding_stocks.yaml"
        test_data = {
            'stocks': [
                {
                    'symbol': '7203.T',
                    'name': 'トヨタ自動車',
                    'quantity': 100,
                    'acquisition_price': 2500,
                    'note': 'テストメモ',
                    'added': '2025-10-07'
                }
            ]
        }
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f, allow_unicode=True)
        
        result = load_stock_symbols(str(test_yaml))
        
        assert result[0]['quantity'] == 100
        assert result[0]['acquisition_price'] == 2500
        assert result[0]['note'] == 'テストメモ'
        assert result[0]['added'] == '2025-10-07'
