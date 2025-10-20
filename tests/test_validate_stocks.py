"""
validate_stocksモジュールのテスト
"""

import pytest
import yaml
import os
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from validate_stocks import validate_stock_entry, validate_stocks_yaml


class TestValidateStockEntry:
    """validate_stock_entry関数のテスト"""
    
    def test_valid_minimal_entry(self):
        """最小限の有効なエントリー（symbolのみ）"""
        stock = {'symbol': '7203.T'}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) == 0
    
    def test_valid_full_entry(self):
        """全フィールドを持つ有効なエントリー"""
        stock = {
            'symbol': '7203.T',
            'name': 'トヨタ自動車',
            'quantity': 100,
            'acquisition_price': 2500,
            'currency': '円',
            'account_type': '特定',
            'considering_action': 'buy',
            'note': 'テストメモ',
            'added': '2025-10-07'
        }
        errors = validate_stock_entry(stock, 0)
        assert len(errors) == 0
    
    def test_valid_string_entry(self):
        """文字列形式のエントリー（後方互換性）"""
        stock = '7203.T'
        errors = validate_stock_entry(stock, 0)
        assert len(errors) == 0
    
    def test_missing_symbol(self):
        """symbolフィールドが欠落"""
        stock = {'name': 'トヨタ自動車'}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) > 0
        assert any('symbol' in err for err in errors)
    
    def test_empty_symbol(self):
        """symbolが空文字列"""
        stock = {'symbol': ''}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) > 0
    
    def test_invalid_type_not_dict(self):
        """辞書でも文字列でもない型"""
        stock = 12345
        errors = validate_stock_entry(stock, 0)
        assert len(errors) > 0
    
    def test_invalid_quantity_type(self):
        """quantityが数値でない"""
        stock = {'symbol': '7203.T', 'quantity': 'invalid'}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) > 0
        assert any('quantity' in err for err in errors)
    
    def test_valid_negative_quantity(self):
        """負のquantity（空売り）は有効"""
        stock = {'symbol': '6758.T', 'quantity': -50}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) == 0
    
    def test_invalid_acquisition_price_type(self):
        """acquisition_priceが数値でない"""
        stock = {'symbol': '7203.T', 'acquisition_price': 'invalid'}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) > 0
        assert any('acquisition_price' in err for err in errors)
    
    def test_invalid_acquisition_price_negative(self):
        """acquisition_priceが負の値"""
        stock = {'symbol': '7203.T', 'acquisition_price': -100}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) > 0
        assert any('acquisition_price' in err for err in errors)
    
    def test_invalid_acquisition_price_zero(self):
        """acquisition_priceがゼロ"""
        stock = {'symbol': '7203.T', 'acquisition_price': 0}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) > 0
    
    def test_valid_account_type_tokutei(self):
        """有効なaccount_type（特定）"""
        stock = {'symbol': '7203.T', 'account_type': '特定'}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) == 0
    
    def test_valid_account_type_nisa(self):
        """有効なaccount_type（NISA）"""
        stock = {'symbol': 'AAPL', 'account_type': 'NISA'}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) == 0
    
    def test_valid_account_type_old_nisa(self):
        """有効なaccount_type（旧NISA）"""
        stock = {'symbol': 'MSFT', 'account_type': '旧NISA'}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) == 0
    
    def test_invalid_account_type(self):
        """無効なaccount_type"""
        stock = {'symbol': '7203.T', 'account_type': '無効な口座'}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) > 0
        assert any('account_type' in err for err in errors)
    
    def test_valid_considering_action_buy(self):
        """有効なconsidering_action（buy）"""
        stock = {'symbol': 'AAPL', 'considering_action': 'buy'}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) == 0
    
    def test_valid_considering_action_short_sell(self):
        """有効なconsidering_action（short_sell）"""
        stock = {'symbol': 'TSLA', 'considering_action': 'short_sell'}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) == 0
    
    def test_invalid_considering_action(self):
        """無効なconsidering_action"""
        stock = {'symbol': 'AAPL', 'considering_action': 'hold'}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) > 0
        assert any('considering_action' in err for err in errors)
    
    def test_valid_currency_yen(self):
        """有効なcurrency（円）"""
        stock = {'symbol': '7203.T', 'currency': '円'}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) == 0
    
    def test_valid_currency_dollar(self):
        """有効なcurrency（ドル）"""
        stock = {'symbol': 'AAPL', 'currency': 'ドル'}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) == 0
    
    def test_valid_currency_euro(self):
        """有効なcurrency（ユーロ）"""
        stock = {'symbol': 'BMW.DE', 'currency': 'ユーロ'}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) == 0
    
    def test_valid_currency_pound(self):
        """有効なcurrency（ポンド）"""
        stock = {'symbol': 'HSBA.L', 'currency': 'ポンド'}
        errors = validate_stock_entry(stock, 0)
        assert len(errors) == 0
    
    def test_none_values_allowed(self):
        """Noneの値は許可される"""
        stock = {
            'symbol': '7203.T',
            'name': None,
            'quantity': None,
            'acquisition_price': None,
            'currency': None,
            'account_type': None
        }
        errors = validate_stock_entry(stock, 0)
        assert len(errors) == 0


class TestValidateStocksYaml:
    """validate_stocks_yaml関数のテスト"""
    
    def test_valid_yaml_file(self, tmp_path):
        """正常なYAMLファイル"""
        test_yaml = tmp_path / "test_stocks.yaml"
        test_data = {
            'stocks': [
                {
                    'symbol': '7203.T',
                    'name': 'トヨタ自動車',
                    'quantity': 100,
                    'acquisition_price': 2500,
                    'currency': '円',
                    'account_type': '特定'
                },
                {
                    'symbol': 'AAPL',
                    'name': 'Apple Inc.',
                    'currency': 'ドル'
                }
            ]
        }
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f, allow_unicode=True)
        
        success, errors = validate_stocks_yaml(str(test_yaml))
        
        assert success is True
        assert len(errors) == 0
    
    def test_file_not_found(self):
        """存在しないファイル"""
        success, errors = validate_stocks_yaml('/nonexistent/path/stocks.yaml')
        
        assert success is False
        assert len(errors) > 0
        assert any('見つかりません' in err for err in errors)
    
    def test_invalid_yaml_syntax(self, tmp_path):
        """不正なYAML構文"""
        test_yaml = tmp_path / "invalid.yaml"
        with open(test_yaml, 'w') as f:
            f.write("invalid: yaml: syntax:")
        
        success, errors = validate_stocks_yaml(str(test_yaml))
        
        assert success is False
        assert len(errors) > 0
        assert any('YAML解析エラー' in err for err in errors)
    
    def test_empty_yaml_file(self, tmp_path):
        """空のYAMLファイル"""
        test_yaml = tmp_path / "empty.yaml"
        with open(test_yaml, 'w') as f:
            f.write("")
        
        success, errors = validate_stocks_yaml(str(test_yaml))
        
        assert success is False
        assert len(errors) > 0
    
    def test_missing_stocks_key(self, tmp_path):
        """stocksキーが欠落"""
        test_yaml = tmp_path / "no_stocks.yaml"
        test_data = {'other_key': 'value'}
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f)
        
        success, errors = validate_stocks_yaml(str(test_yaml))
        
        assert success is False
        assert len(errors) > 0
        assert any('stocks' in err for err in errors)
    
    def test_empty_stocks_list(self, tmp_path):
        """空の銘柄リスト"""
        test_yaml = tmp_path / "empty_stocks.yaml"
        test_data = {'stocks': []}
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f)
        
        success, errors = validate_stocks_yaml(str(test_yaml))
        
        assert success is False
        assert len(errors) > 0
        assert any('空です' in err for err in errors)
    
    def test_stocks_not_a_list(self, tmp_path):
        """stocksがリストでない"""
        test_yaml = tmp_path / "stocks_not_list.yaml"
        test_data = {'stocks': 'not a list'}
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f)
        
        success, errors = validate_stocks_yaml(str(test_yaml))
        
        assert success is False
        assert len(errors) > 0
        assert any('リスト' in err for err in errors)
    
    def test_multiple_errors(self, tmp_path):
        """複数のエラーを含むファイル"""
        test_yaml = tmp_path / "multiple_errors.yaml"
        test_data = {
            'stocks': [
                {'name': 'トヨタ自動車'},  # symbolが欠落
                {'symbol': 'AAPL', 'quantity': 'invalid'},  # quantityが無効
                {'symbol': 'MSFT', 'account_type': '無効'}  # account_typeが無効
            ]
        }
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f, allow_unicode=True)
        
        success, errors = validate_stocks_yaml(str(test_yaml))
        
        assert success is False
        assert len(errors) >= 3  # 少なくとも3つのエラー
    
    def test_backward_compatibility_string_format(self, tmp_path):
        """後方互換性: 文字列形式の銘柄リスト"""
        test_yaml = tmp_path / "string_stocks.yaml"
        test_data = {
            'stocks': ['7203.T', 'AAPL', 'MSFT']
        }
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f)
        
        success, errors = validate_stocks_yaml(str(test_yaml))
        
        assert success is True
        assert len(errors) == 0
    
    def test_mixed_format_valid(self, tmp_path):
        """混在形式（文字列と辞書）の有効なリスト"""
        test_yaml = tmp_path / "mixed_stocks.yaml"
        test_data = {
            'stocks': [
                '7203.T',
                {'symbol': 'AAPL', 'name': 'Apple'},
                'MSFT'
            ]
        }
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f)
        
        success, errors = validate_stocks_yaml(str(test_yaml))
        
        assert success is True
        assert len(errors) == 0
