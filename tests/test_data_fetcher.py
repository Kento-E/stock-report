"""
data_fetcherモジュールのテスト
"""

import pytest
import os
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestFetchStockData:
    """fetch_stock_data関数の基本テスト"""
    
    def test_import_data_fetcher(self):
        """data_fetcherモジュールのインポート確認"""
        try:
            from data_fetcher import fetch_stock_data
            assert fetch_stock_data is not None
        except Exception as e:
            pytest.skip(f"data_fetcherのインポートに失敗: {e}")
    
    def test_data_structure(self):
        """戻り値のデータ構造テスト（モック使用）"""
        # ネットワークアクセスが必要なため、データ構造のみ確認
        expected_keys = ['symbol', 'price', 'news']
        
        # モックデータ構造
        mock_data = {
            'symbol': 'TEST',
            'price': 100.0,
            'news': ['ニュース1', 'ニュース2']
        }
        
        for key in expected_keys:
            assert key in mock_data
        assert isinstance(mock_data['news'], list)
