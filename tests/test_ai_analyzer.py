"""
ai_analyzerモジュールのテスト
"""

import pytest
import os
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# ネットワーク接続不要のモジュールのみテスト
try:
    from ai_analyzer import _generate_holding_status
except Exception as e:
    pytest.skip(f"ai_analyzerのインポートに失敗: {e}", allow_module_level=True)


class TestGenerateHoldingStatus:
    """_generate_holding_status関数のテスト"""
    
    def test_holding_status_with_profit(self):
        """保有中で利益が出ている場合"""
        data = {
            'quantity': 100,
            'acquisition_price': 2500,
            'price': 2700
        }
        currency = '円'
        
        result = _generate_holding_status(data, currency)
        
        assert '100株を保有中' in result
        assert '2500円' in result
        assert '損益' in result
        assert '20,000' in result or '20000' in result  # 利益額
    
    def test_holding_status_with_loss(self):
        """保有中で損失が出ている場合"""
        data = {
            'quantity': 100,
            'acquisition_price': 2700,
            'price': 2500
        }
        currency = '円'
        
        result = _generate_holding_status(data, currency)
        
        assert '100株を保有中' in result
        assert '2700円' in result
        assert '損益' in result
        assert '-20,000' in result or '-20000' in result  # 損失額
    
    def test_short_selling_status(self):
        """空売り中の場合"""
        data = {
            'quantity': -50,
            'acquisition_price': 12000,
            'price': 11500
        }
        currency = '円'
        
        result = _generate_holding_status(data, currency)
        
        assert '50株を空売り中' in result
        assert '12000円' in result
        assert '損益' in result
    
    def test_no_holding_with_quantity_zero(self):
        """保有数がゼロの場合"""
        data = {
            'quantity': 0,
            'price': 2500
        }
        currency = '円'
        
        result = _generate_holding_status(data, currency)
        
        assert '保有なし' in result
        assert '検討中' in result
    
    def test_no_holding_without_quantity(self):
        """保有数が未設定の場合"""
        data = {
            'price': 2500
        }
        currency = '円'
        
        result = _generate_holding_status(data, currency)
        
        assert '保有なし' in result
        assert '検討中' in result
    
    def test_holding_without_acquisition_price(self):
        """取得単価が未設定の場合"""
        data = {
            'quantity': 100,
            'price': 2500
        }
        currency = '円'
        
        result = _generate_holding_status(data, currency)
        
        assert '100株を保有中' in result
        # 取得単価が未設定なので損益計算は含まれない
        assert '損益' not in result
    
    def test_currency_dollar(self):
        """通貨がドルの場合"""
        data = {
            'quantity': 50,
            'acquisition_price': 150,
            'price': 160
        }
        currency = 'ドル'
        
        result = _generate_holding_status(data, currency)
        
        assert '50株を保有中' in result
        assert 'ドル' in result
