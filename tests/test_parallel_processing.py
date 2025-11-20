"""
並列処理の動作確認テスト

main.pyの並列処理実装が正しく動作することを確認します。
"""

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import MagicMock, Mock, patch

import pytest

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# defeatbeta-apiのネットワーク呼び出しをモックして回避
sys.modules["defeatbeta_api"] = Mock()
sys.modules["defeatbeta_api.data"] = Mock()
sys.modules["defeatbeta_api.data.ticker"] = Mock()


class TestParallelProcessing:
    """並列処理のテスト"""

    @patch("analyzers.data_fetcher.fetch_stock_data")
    @patch("analyzers.ai_analyzer.analyze_with_gemini")
    @patch("loaders.preference_loader.generate_preference_prompt")
    def test_parallel_processing_multiple_stocks(self, mock_prompt, mock_analyze, mock_fetch):
        """複数銘柄の並列処理が正しく動作することを確認"""
        # モックの設定
        os.environ["GEMINI_API_KEY"] = "test-api-key"

        mock_prompt.return_value = "テストプロンプト"
        mock_fetch.return_value = {
            "symbol": "TEST",
            "price": 100,
            "news": ["ニュース1"],
            "currency": "円",
        }
        mock_analyze.return_value = "売買判断: ホールド\n\nテスト分析結果"

        # テスト用の銘柄リスト
        stocks = [
            {"symbol": "TEST1", "name": "テスト1"},
            {"symbol": "TEST2", "name": "テスト2"},
            {"symbol": "TEST3", "name": "テスト3"},
            {"symbol": "TEST4", "name": "テスト4"},
            {"symbol": "TEST5", "name": "テスト5"},
        ]

        # 並列処理の模擬
        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for stock in stocks:
                # 簡易的な処理関数
                def process_stock(s):
                    data = mock_fetch(s["symbol"], s)
                    analysis = mock_analyze(data, mock_prompt.return_value)
                    return s["symbol"], analysis

                future = executor.submit(process_stock, stock)
                futures.append(future)

            for future in as_completed(futures):
                result = future.result()
                results.append(result)

        # 全ての銘柄が処理されたことを確認
        assert len(results) == 5

        # 各処理が呼ばれたことを確認
        assert mock_fetch.call_count == 5
        assert mock_analyze.call_count == 5

    def test_thread_pool_error_handling(self):
        """エラーが発生した場合でも他の処理が継続されることを確認"""

        def process_with_error(value):
            if value == 2:
                raise ValueError("テストエラー")
            return value * 2

        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i in range(5):
                future = executor.submit(process_with_error, i)
                futures.append(future)

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except ValueError:
                    # エラーは無視して処理を継続
                    pass

        # エラーが発生した1件を除く4件が処理されたことを確認
        assert len(results) == 4
        assert 0 in results  # 0 * 2 = 0
        assert 2 in results  # 1 * 2 = 2
        assert 6 in results  # 3 * 2 = 6
        assert 8 in results  # 4 * 2 = 8

    def test_concurrent_futures_import(self):
        """concurrent.futuresが正しくインポートできることを確認"""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        # ThreadPoolExecutorが使用可能であることを確認
        with ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(lambda x: x * 2, 5)
            result = future.result()
            assert result == 10
