"""
stock_loaderモジュールのテスト
"""

import pytest
import yaml
import os
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from loaders.stock_loader import load_stock_symbols, get_currency_for_symbol, categorize_stock, categorize_stocks, calculate_tax, normalize_symbol


class TestNormalizeSymbol:
    """normalize_symbol関数のテスト"""
    
    def test_numeric_4digit_to_string_with_suffix(self):
        """4桁数値を文字列に変換し.Tサフィックスを追加"""
        assert normalize_symbol(7203) == '7203.T'
        assert normalize_symbol(6758) == '6758.T'
        assert normalize_symbol(1234) == '1234.T'
    
    def test_string_4digit_adds_suffix(self):
        """4桁文字列に.Tサフィックスを追加"""
        assert normalize_symbol('7203') == '7203.T'
        assert normalize_symbol('6758') == '6758.T'
    
    def test_string_with_suffix_unchanged(self):
        """すでにサフィックスがある場合は変更なし"""
        assert normalize_symbol('7203.T') == '7203.T'
        assert normalize_symbol('6758.JP') == '6758.JP'
    
    def test_us_stock_unchanged(self):
        """米国株コードは変更なし"""
        assert normalize_symbol('AAPL') == 'AAPL'
        assert normalize_symbol('MSFT') == 'MSFT'
    
    def test_non_4digit_number_unchanged(self):
        """4桁以外の数字は変更なし（ただし文字列に変換）"""
        assert normalize_symbol(123) == '123'
        assert normalize_symbol(12345) == '12345'
    
    def test_alphanumeric_unchanged(self):
        """英数字混在は変更なし"""
        assert normalize_symbol('BMW.DE') == 'BMW.DE'
        assert normalize_symbol('HSBA.L') == 'HSBA.L'


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
    
    def test_explicit_currency_yen(self):
        """明示的に円を指定"""
        assert get_currency_for_symbol('7203.T', '円') == '円'
    
    def test_explicit_currency_dollar(self):
        """明示的にドルを指定"""
        assert get_currency_for_symbol('AAPL', 'ドル') == 'ドル'
    
    def test_explicit_currency_euro(self):
        """明示的にユーロを指定"""
        assert get_currency_for_symbol('BMW.DE', 'ユーロ') == 'ユーロ'
    
    def test_explicit_currency_pound(self):
        """明示的にポンドを指定"""
        assert get_currency_for_symbol('HSBA.L', 'ポンド') == 'ポンド'
    
    def test_explicit_currency_overrides_auto_detection(self):
        """明示的な通貨指定が自動判定より優先される"""
        # 日本株でもユーロを指定できる
        assert get_currency_for_symbol('7203.T', 'ユーロ') == 'ユーロ'
        # 米国株でも円を指定できる
        assert get_currency_for_symbol('AAPL', '円') == '円'
    
    def test_none_explicit_currency_uses_auto_detection(self):
        """明示的な通貨がNoneの場合は自動判定"""
        assert get_currency_for_symbol('7203.T', None) == '円'
        assert get_currency_for_symbol('AAPL', None) == 'ドル'
    
    def test_4digit_number_detects_yen(self):
        """4桁数字は円と判定"""
        assert get_currency_for_symbol(7203) == '円'
        assert get_currency_for_symbol(6758) == '円'
        assert get_currency_for_symbol('7203') == '円'
        assert get_currency_for_symbol('6758') == '円'
    
    def test_non_4digit_number_detects_dollar(self):
        """4桁以外の数字はドルと判定"""
        assert get_currency_for_symbol(123) == 'ドル'
        assert get_currency_for_symbol(12345) == 'ドル'
        assert get_currency_for_symbol('123') == 'ドル'
        assert get_currency_for_symbol('12345') == 'ドル'


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
    
    def test_currency_field_euro(self, tmp_path):
        """通貨フィールド（ユーロ）のテスト"""
        test_yaml = tmp_path / "euro_stocks.yaml"
        test_data = {
            'stocks': [
                {
                    'symbol': 'BMW.DE',
                    'name': 'BMW',
                    'currency': 'ユーロ'
                }
            ]
        }
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f, allow_unicode=True)
        
        result = load_stock_symbols(str(test_yaml))
        
        assert result[0]['symbol'] == 'BMW.DE'
        assert result[0]['name'] == 'BMW'
        assert result[0]['currency'] == 'ユーロ'
    
    def test_currency_field_pound(self, tmp_path):
        """通貨フィールド（ポンド）のテスト"""
        test_yaml = tmp_path / "pound_stocks.yaml"
        test_data = {
            'stocks': [
                {
                    'symbol': 'HSBA.L',
                    'name': 'HSBC Holdings',
                    'currency': 'ポンド',
                    'quantity': 50,
                    'acquisition_price': 650
                }
            ]
        }
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f, allow_unicode=True)
        
        result = load_stock_symbols(str(test_yaml))
        
        assert result[0]['symbol'] == 'HSBA.L'
        assert result[0]['currency'] == 'ポンド'
        assert result[0]['quantity'] == 50
        assert result[0]['acquisition_price'] == 650
    
    def test_mixed_currencies(self, tmp_path):
        """複数通貨の混在テスト"""
        test_yaml = tmp_path / "mixed_currencies.yaml"
        test_data = {
            'stocks': [
                {'symbol': '7203.T', 'name': 'トヨタ自動車'},  # 円（自動判定）
                {'symbol': 'AAPL', 'name': 'Apple', 'currency': 'ドル'},  # 明示的にドル
                {'symbol': 'BMW.DE', 'name': 'BMW', 'currency': 'ユーロ'},  # 明示的にユーロ
                {'symbol': 'HSBA.L', 'name': 'HSBC', 'currency': 'ポンド'}  # 明示的にポンド
            ]
        }
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f, allow_unicode=True)
        
        result = load_stock_symbols(str(test_yaml))
        
        assert len(result) == 4
        assert result[0]['currency'] is None  # 自動判定用にNone
        assert result[1]['currency'] == 'ドル'
        assert result[2]['currency'] == 'ユーロ'
        assert result[3]['currency'] == 'ポンド'
    
    def test_numeric_symbol_conversion(self, tmp_path):
        """数値型のsymbolが文字列に変換され、4桁なら.Tが追加される"""
        test_yaml = tmp_path / "numeric_symbols.yaml"
        test_data = {
            'stocks': [
                {'symbol': 7203, 'name': 'トヨタ自動車'},
                {'symbol': 6758, 'name': 'ソニーグループ'},
                {'symbol': 1234, 'name': 'テスト銘柄'}
            ]
        }
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f)
        
        result = load_stock_symbols(str(test_yaml))
        
        assert len(result) == 3
        assert result[0]['symbol'] == '7203.T'
        assert result[1]['symbol'] == '6758.T'
        assert result[2]['symbol'] == '1234.T'


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
    
    def test_considering_short_sell(self):
        """空売り検討中の銘柄"""
        stock_info = {'symbol': 'TSLA', 'quantity': 0, 'considering_action': 'short_sell'}
        assert categorize_stock(stock_info) == 'considering_short_sell'
    
    def test_considering_short_sell_no_quantity(self):
        """保有数未設定で空売り検討中の銘柄"""
        stock_info = {'symbol': 'NVDA', 'considering_action': 'short_sell'}
        assert categorize_stock(stock_info) == 'considering_short_sell'


class TestCategorizeStocks:
    """categorize_stocks関数のテスト"""
    
    def test_categorize_all_types(self):
        """全種類の銘柄を分類"""
        stocks = [
            {'symbol': '7203.T', 'name': 'トヨタ', 'quantity': 100},
            {'symbol': '6758.T', 'name': 'ソニー', 'quantity': -50},
            {'symbol': 'AAPL', 'name': 'Apple'},
            {'symbol': 'MSFT', 'name': 'Microsoft', 'quantity': 200},
            {'symbol': 'TSLA', 'name': 'Tesla', 'considering_action': 'short_sell'},
        ]
        
        result = categorize_stocks(stocks)
        
        assert len(result['holding']) == 2
        assert len(result['short_selling']) == 1
        assert len(result['considering_buy']) == 1
        assert len(result['considering_short_sell']) == 1
        assert result['holding'][0]['symbol'] == '7203.T'
        assert result['holding'][1]['symbol'] == 'MSFT'
        assert result['short_selling'][0]['symbol'] == '6758.T'
        assert result['considering_buy'][0]['symbol'] == 'AAPL'
        assert result['considering_short_sell'][0]['symbol'] == 'TSLA'
    
    def test_categorize_empty_list(self):
        """空のリスト"""
        result = categorize_stocks([])
        
        assert len(result['holding']) == 0
        assert len(result['short_selling']) == 0
        assert len(result['considering_buy']) == 0
        assert len(result['considering_short_sell']) == 0
    
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
        assert len(result['considering_short_sell']) == 0


class TestAccountType:
    """account_typeフィールドのテスト"""
    
    def test_load_with_account_type_tokutei(self, tmp_path):
        """特定口座の読み込み"""
        test_yaml = tmp_path / "tokutei_account.yaml"
        test_data = {
            'stocks': [
                {
                    'symbol': '7203.T',
                    'name': 'トヨタ自動車',
                    'quantity': 100,
                    'acquisition_price': 2500,
                    'account_type': '特定'
                }
            ]
        }
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f, allow_unicode=True)
        
        result = load_stock_symbols(str(test_yaml))
        
        assert result[0]['account_type'] == '特定'
    
    def test_load_with_account_type_nisa(self, tmp_path):
        """NISA口座の読み込み"""
        test_yaml = tmp_path / "nisa_account.yaml"
        test_data = {
            'stocks': [
                {
                    'symbol': 'AAPL',
                    'name': 'Apple',
                    'account_type': 'NISA'
                }
            ]
        }
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f, allow_unicode=True)
        
        result = load_stock_symbols(str(test_yaml))
        
        assert result[0]['account_type'] == 'NISA'
    
    def test_load_with_account_type_old_nisa(self, tmp_path):
        """旧NISA口座の読み込み"""
        test_yaml = tmp_path / "old_nisa_account.yaml"
        test_data = {
            'stocks': [
                {
                    'symbol': 'MSFT',
                    'name': 'Microsoft',
                    'account_type': '旧NISA'
                }
            ]
        }
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f, allow_unicode=True)
        
        result = load_stock_symbols(str(test_yaml))
        
        assert result[0]['account_type'] == '旧NISA'
    
    def test_default_account_type(self, tmp_path):
        """account_type未設定時はデフォルト（特定）"""
        test_yaml = tmp_path / "default_account.yaml"
        test_data = {
            'stocks': [
                {
                    'symbol': '6758.T',
                    'name': 'ソニー'
                }
            ]
        }
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f, allow_unicode=True)
        
        result = load_stock_symbols(str(test_yaml))
        
        assert result[0]['account_type'] == '特定'
    
    def test_invalid_account_type_defaults_to_tokutei(self, tmp_path):
        """無効なaccount_typeは特定にフォールバック"""
        test_yaml = tmp_path / "invalid_account.yaml"
        test_data = {
            'stocks': [
                {
                    'symbol': 'TSLA',
                    'name': 'Tesla',
                    'account_type': '無効な口座種別'
                }
            ]
        }
        with open(test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f, allow_unicode=True)
        
        result = load_stock_symbols(str(test_yaml))
        
        assert result[0]['account_type'] == '特定'


class TestCalculateTax:
    """calculate_tax関数のテスト"""
    
    def test_tax_tokutei_with_profit(self):
        """特定口座での利益に対する課税"""
        # 100,000円の利益
        tax = calculate_tax(100000, '特定')
        # 20.315%の税金
        expected = 100000 * 0.20315
        assert abs(tax - expected) < 0.01
    
    def test_tax_nisa_with_profit(self):
        """NISA口座での利益は非課税"""
        tax = calculate_tax(100000, 'NISA')
        assert tax == 0
    
    def test_tax_old_nisa_with_profit(self):
        """旧NISA口座での利益は非課税"""
        tax = calculate_tax(100000, '旧NISA')
        assert tax == 0
    
    def test_tax_with_loss(self):
        """損失の場合は課税なし"""
        tax = calculate_tax(-50000, '特定')
        assert tax == 0
    
    def test_tax_with_zero_profit(self):
        """損益ゼロの場合は課税なし"""
        tax = calculate_tax(0, '特定')
        assert tax == 0
    
    def test_tax_tokutei_large_profit(self):
        """特定口座での大きな利益に対する課税"""
        # 1,000,000円の利益
        tax = calculate_tax(1000000, '特定')
        expected = 1000000 * 0.20315
        assert abs(tax - expected) < 0.01
    
    def test_tax_small_profit(self):
        """小さな利益に対する課税（端数処理確認）"""
        # 1円の利益
        tax = calculate_tax(1, '特定')
        expected = 1 * 0.20315
        assert abs(tax - expected) < 0.01
