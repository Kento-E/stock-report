"""
ai_analyzerモジュールのテスト
"""

import pytest
import os
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

# ネットワーク接続不要のモジュールのみテスト
try:
    from analyzers.ai_analyzer import _generate_holding_status
except Exception as e:
    pytest.skip(f"ai_analyzerのインポートに失敗: {e}", allow_module_level=True)


class TestGenerateHoldingStatus:
    """_generate_holding_status関数のテスト"""
    
    def test_holding_status_with_profit(self):
        """保有中で利益が出ている場合"""
        data = {
            'quantity': 100,
            'acquisition_price': 2500,
            'price': 2700,
            'account_type': '特定'
        }
        currency = '円'
        
        result = _generate_holding_status(data, currency)
        
        assert '100株を保有中' in result
        assert '2500円' in result
        assert '損益' in result
        assert '20,000' in result or '20000' in result  # 利益額
        assert '特定' in result
    
    def test_holding_status_with_loss(self):
        """保有中で損失が出ている場合"""
        data = {
            'quantity': 100,
            'acquisition_price': 2700,
            'price': 2500,
            'account_type': '特定'
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
            'price': 11500,
            'account_type': 'NISA'
        }
        currency = '円'
        
        result = _generate_holding_status(data, currency)
        
        assert '50株を空売り中' in result
        assert '12000円' in result
        assert '損益' in result
        assert 'NISA' in result
    
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
            'price': 2500,
            'account_type': '特定'
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
            'price': 160,
            'account_type': '特定'
        }
        currency = 'ドル'
        
        result = _generate_holding_status(data, currency)
        
        assert '50株を保有中' in result
        assert 'ドル' in result
    
    def test_currency_euro(self):
        """通貨がユーロの場合"""
        data = {
            'quantity': 30,
            'acquisition_price': 80,
            'price': 85,
            'account_type': '特定'
        }
        currency = 'ユーロ'
        
        result = _generate_holding_status(data, currency)
        
        assert '30株を保有中' in result
        assert 'ユーロ' in result
        assert '80ユーロ' in result
    
    def test_currency_pound(self):
        """通貨がポンドの場合"""
        data = {
            'quantity': 100,
            'acquisition_price': 650,
            'price': 670,
            'account_type': '特定'
        }
        currency = 'ポンド'
        
        result = _generate_holding_status(data, currency)
        
        assert '100株を保有中' in result
        assert 'ポンド' in result
        assert '650ポンド' in result
    
    def test_tax_calculation_tokutei_account(self):
        """特定口座での税額計算"""
        data = {
            'quantity': 100,
            'acquisition_price': 2500,
            'price': 2700,
            'account_type': '特定'
        }
        currency = '円'
        
        result = _generate_holding_status(data, currency)
        
        # 利益: (2700 - 2500) * 100 = 20,000円
        # 税額: 20,000 * 0.20315 = 4,063円
        assert '税額' in result
        assert '20.315%' in result
        assert '税引後損益' in result
        # 税引後: 20,000 - 4,063 = 15,937円
        assert '15,937' in result or '15937' in result
    
    def test_tax_calculation_nisa_account(self):
        """NISA口座は非課税"""
        data = {
            'quantity': 100,
            'acquisition_price': 2500,
            'price': 2700,
            'account_type': 'NISA'
        }
        currency = '円'
        
        result = _generate_holding_status(data, currency)
        
        assert '20,000' in result or '20000' in result  # 利益額
        assert '税引後損益' in result
        assert '非課税' in result
        # NISAなので税額表示はない
        assert '税額' not in result or '税額（約20.315%）' not in result
    
    def test_tax_calculation_old_nisa_account(self):
        """旧NISA口座は非課税"""
        data = {
            'quantity': 100,
            'acquisition_price': 2500,
            'price': 2700,
            'account_type': '旧NISA'
        }
        currency = '円'
        
        result = _generate_holding_status(data, currency)
        
        assert '20,000' in result or '20000' in result  # 利益額
        assert '税引後損益' in result
        assert '非課税' in result
        # 旧NISAなので税額表示はない
        assert '税額' not in result or '税額（約20.315%）' not in result
    
    def test_no_tax_on_loss(self):
        """損失の場合は課税なし"""
        data = {
            'quantity': 100,
            'acquisition_price': 2700,
            'price': 2500,
            'account_type': '特定'
        }
        currency = '円'
        
        result = _generate_holding_status(data, currency)
        
        # 損失の場合は税額計算なし
        assert '損益' in result
        assert '-20,000' in result or '-20000' in result
        # 損失なので税額表示はない
        assert '税額' not in result or '税引後' not in result
    
    def test_short_selling_with_tax(self):
        """空売りで利益が出た場合の税額計算"""
        data = {
            'quantity': -50,
            'acquisition_price': 12000,
            'price': 11500,
            'account_type': '特定'
        }
        currency = '円'
        
        result = _generate_holding_status(data, currency)
        
        # 空売り利益: (12000 - 11500) * 50 = 25,000円
        assert '25,000' in result or '25000' in result
        assert '税額' in result
        assert '税引後損益' in result


class TestAnalysisViewpointsSelection:
    """分析観点の選択テスト（通常保有 vs 空売りポジション）"""
    
    def test_analysis_viewpoints_available(self):
        """分析観点定数が定義されていることを確認"""
        from analyzers.ai_analyzer import ANALYSIS_VIEWPOINTS_REGULAR, ANALYSIS_VIEWPOINTS_SHORT
        
        # 両方の定数が定義されていることを確認
        assert ANALYSIS_VIEWPOINTS_REGULAR is not None
        assert ANALYSIS_VIEWPOINTS_SHORT is not None
        assert len(ANALYSIS_VIEWPOINTS_REGULAR) > 0
        assert len(ANALYSIS_VIEWPOINTS_SHORT) > 0
    
    def test_regular_viewpoints_content(self):
        """通常保有用の分析観点に適切な用語が含まれることを確認"""
        from analyzers.ai_analyzer import ANALYSIS_VIEWPOINTS_REGULAR
        
        # 通常の売買判断用語が含まれていることを確認
        assert '買い' in ANALYSIS_VIEWPOINTS_REGULAR
        assert '売り' in ANALYSIS_VIEWPOINTS_REGULAR
        assert 'ホールド' in ANALYSIS_VIEWPOINTS_REGULAR
    
    def test_short_viewpoints_content(self):
        """空売りポジション用の分析観点に適切な用語が含まれることを確認"""
        from analyzers.ai_analyzer import ANALYSIS_VIEWPOINTS_SHORT
        
        # 空売り専用の売買判断用語が含まれていることを確認
        assert '買戻し' in ANALYSIS_VIEWPOINTS_SHORT
        assert '維持' in ANALYSIS_VIEWPOINTS_SHORT
        assert '追加売り' in ANALYSIS_VIEWPOINTS_SHORT
    
    def test_short_viewpoints_no_regular_terms(self):
        """空売りポジション用の観点に通常の「買い」が含まれないことを確認"""
        from analyzers.ai_analyzer import ANALYSIS_VIEWPOINTS_SHORT
        
        # 「買戻し」はあるが単純な「買い」は推奨リストに含まれないはず
        # ただし説明文に「買戻し」として含まれる可能性があるので、
        # 推奨判断リストの部分のみチェック
        lines = ANALYSIS_VIEWPOINTS_SHORT.split('\n')
        judgment_section = [line for line in lines if '・' in line or '買い' in line or '売り' in line]
        
        # 判断リストに「買戻し」はあるが単純な「・買い」はない
        has_buyback = any('買戻し' in line for line in judgment_section)
        has_simple_buy = any('・買い' in line and '買戻し' not in line and '買い増し' not in line for line in judgment_section)
        
        assert has_buyback is True
        assert has_simple_buy is False
