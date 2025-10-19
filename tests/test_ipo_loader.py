"""
上場予定銘柄リスト読み込みモジュールのテスト
"""

import os
import yaml
import tempfile
from datetime import datetime, timedelta
import pytest
from src.ipo_loader import load_ipo_stocks, filter_upcoming_ipos


class TestLoadIpoStocks:
    """IPO銘柄リスト読み込み機能のテスト"""
    
    def test_load_valid_yaml_file(self):
        """有効なYAMLファイルから銘柄を読み込めることをテスト"""
        yaml_content = """
ipo_stocks:
  - symbol: XXXX.T
    name: サンプル株式会社
    ipo_date: 2025-11-01
    market: 東証プライム
    expected_price: 1000
    currency: 円
    note: 上場予定
  - symbol: YYYY
    name: Sample Inc.
    market: NASDAQ
    currency: ドル
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            stocks = load_ipo_stocks(temp_file)
            assert len(stocks) == 2
            assert stocks[0]['symbol'] == 'XXXX.T'
            assert stocks[0]['name'] == 'サンプル株式会社'
            # YAMLは日付を自動的にdatetimeオブジェクトに変換する場合がある
            assert str(stocks[0]['ipo_date']) == '2025-11-01'
            assert stocks[0]['market'] == '東証プライム'
            assert stocks[0]['expected_price'] == 1000
            assert stocks[0]['currency'] == '円'
            assert stocks[1]['symbol'] == 'YYYY'
            assert stocks[1]['name'] == 'Sample Inc.'
        finally:
            os.unlink(temp_file)
    
    def test_load_file_not_found(self):
        """ファイルが存在しない場合は空のリストを返すことをテスト"""
        stocks = load_ipo_stocks('nonexistent_file.yaml')
        assert stocks == []
    
    def test_load_empty_stocks_list(self):
        """空の銘柄リストを読み込めることをテスト"""
        yaml_content = """
ipo_stocks: []
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            stocks = load_ipo_stocks(temp_file)
            assert stocks == []
        finally:
            os.unlink(temp_file)
    
    def test_load_no_ipo_stocks_key(self):
        """ipo_stocksキーがない場合は空のリストを返すことをテスト"""
        yaml_content = """
other_data: value
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            stocks = load_ipo_stocks(temp_file)
            assert stocks == []
        finally:
            os.unlink(temp_file)
    
    def test_load_invalid_yaml(self):
        """不正なYAMLの場合はエラーを発生させることをテスト"""
        yaml_content = """
ipo_stocks:
  - symbol: XXXX.T
    name: サンプル株式会社
  invalid yaml content [
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            with pytest.raises(yaml.YAMLError):
                load_ipo_stocks(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_missing_required_fields(self):
        """必須フィールド（symbolまたはname）がない場合はスキップされることをテスト"""
        yaml_content = """
ipo_stocks:
  - symbol: XXXX.T
    name: サンプル株式会社
  - symbol: YYYY
    # name が欠けている
  - name: ZZZ Inc.
    # symbol が欠けている
  - symbol: ZZZZ
    name: 正常な株式会社
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            stocks = load_ipo_stocks(temp_file)
            # 必須フィールドがある銘柄のみ読み込まれる
            assert len(stocks) == 2
            assert stocks[0]['symbol'] == 'XXXX.T'
            assert stocks[1]['symbol'] == 'ZZZZ'
        finally:
            os.unlink(temp_file)


class TestFilterUpcomingIpos:
    """上場予定銘柄フィルタリング機能のテスト"""
    
    def test_filter_upcoming_within_7_days(self):
        """7日以内の上場予定銘柄をフィルタリングできることをテスト"""
        today = datetime.now().date()
        tomorrow = (today + timedelta(days=1)).strftime('%Y-%m-%d')
        next_week = (today + timedelta(days=7)).strftime('%Y-%m-%d')
        next_month = (today + timedelta(days=30)).strftime('%Y-%m-%d')
        
        stocks = [
            {'symbol': 'A', 'name': 'Company A', 'ipo_date': tomorrow},
            {'symbol': 'B', 'name': 'Company B', 'ipo_date': next_week},
            {'symbol': 'C', 'name': 'Company C', 'ipo_date': next_month},
        ]
        
        filtered = filter_upcoming_ipos(stocks, days_ahead=7)
        assert len(filtered) == 2
        assert filtered[0]['symbol'] == 'A'
        assert filtered[1]['symbol'] == 'B'
    
    def test_filter_with_no_date(self):
        """上場日が設定されていない銘柄は含めることをテスト"""
        stocks = [
            {'symbol': 'A', 'name': 'Company A'},
            {'symbol': 'B', 'name': 'Company B', 'ipo_date': None},
        ]
        
        filtered = filter_upcoming_ipos(stocks)
        assert len(filtered) == 2
    
    def test_filter_empty_list(self):
        """空のリストを渡した場合は空のリストを返すことをテスト"""
        filtered = filter_upcoming_ipos([])
        assert filtered == []
    
    def test_filter_invalid_date_format(self):
        """不正な日付フォーマットの場合は含めることをテスト"""
        stocks = [
            {'symbol': 'A', 'name': 'Company A', 'ipo_date': 'invalid-date'},
        ]
        
        filtered = filter_upcoming_ipos(stocks)
        assert len(filtered) == 1
    
    def test_filter_past_date(self):
        """過去の日付は除外されることをテスト"""
        yesterday = (datetime.now().date() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        stocks = [
            {'symbol': 'A', 'name': 'Company A', 'ipo_date': yesterday},
        ]
        
        filtered = filter_upcoming_ipos(stocks)
        assert len(filtered) == 0
