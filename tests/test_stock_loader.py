"""
stock_loaderモジュールのテスト
"""

import pytest
import yaml
import os
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from stock_loader import load_stock_symbols, get_currency_for_symbol, categorize_stock, categorize_stocks


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


class TestCategorizeStock:
    """categorize_stock関数のテスト"""
    
    def test_holding_stock(self):
        """保有中の銘柄"""
        stock_info = {'symbol': '7203.T', 'quantity': 100}
        assert categorize_stock(stock_info) == 'holding'
    
    def test_short_selling_stock(self):
        """空売り中の銘柄"""
        stock_info = {'symbol': '6758.T', 'quantity': -50}
        assert categorize_stock(stock_info) == 'short_selling'
    
    def test_considering_buy_no_quantity(self):
        """保有数未設定（購入検討中）"""
        stock_info = {'symbol': 'AAPL'}
        assert categorize_stock(stock_info) == 'considering_buy'
    
    def test_considering_buy_zero_quantity(self):
        """保有数ゼロ（購入検討中）"""
        stock_info = {'symbol': 'MSFT', 'quantity': 0}
        assert categorize_stock(stock_info) == 'considering_buy'


class TestCategorizeStocks:
    """categorize_stocks関数のテスト"""
    
    def test_categorize_all_types(self):
        """全種類の銘柄を分類"""
        stocks = [
            {'symbol': '7203.T', 'name': 'トヨタ', 'quantity': 100},
            {'symbol': '6758.T', 'name': 'ソニー', 'quantity': -50},
            {'symbol': 'AAPL', 'name': 'Apple'},
            {'symbol': 'MSFT', 'name': 'Microsoft', 'quantity': 200},
        ]
        
        result = categorize_stocks(stocks)
        
        assert len(result['holding']) == 2
        assert len(result['short_selling']) == 1
        assert len(result['considering_buy']) == 1
        assert result['holding'][0]['symbol'] == '7203.T'
        assert result['holding'][1]['symbol'] == 'MSFT'
        assert result['short_selling'][0]['symbol'] == '6758.T'
        assert result['considering_buy'][0]['symbol'] == 'AAPL'
    
    def test_categorize_empty_list(self):
        """空のリスト"""
        result = categorize_stocks([])
        
        assert len(result['holding']) == 0
        assert len(result['short_selling']) == 0
        assert len(result['considering_buy']) == 0
    
    def test_categorize_single_category(self):
        """単一カテゴリーのみ"""
        stocks = [
            {'symbol': '7203.T', 'quantity': 100},
            {'symbol': '6758.T', 'quantity': 50},
        ]
        
        result = categorize_stocks(stocks)
        
        assert len(result['holding']) == 2
        assert len(result['short_selling']) == 0
        assert len(result['considering_buy']) == 0
