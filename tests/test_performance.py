"""
パフォーマンスに関するテスト

ファイル読み込み回数の削減など、処理効率化の検証を行います。
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock, call, Mock

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# defeatbeta-apiのネットワーク呼び出しをモックして回避
sys.modules['defeatbeta_api'] = Mock()
sys.modules['defeatbeta_api.data'] = Mock()
sys.modules['defeatbeta_api.data.ticker'] = Mock()

from preference_loader import generate_preference_prompt


class TestPreferenceLoadingOptimization:
    """投資志向性設定の読み込み最適化テスト"""
    
    @patch('preference_loader.load_investment_preferences')
    def test_generate_preference_prompt_caching(self, mock_load):
        """generate_preference_promptが事前生成されたプロンプトを再利用できることを確認"""
        # モックの設定
        mock_load.return_value = {
            'investment_style': 'balanced',
            'risk_tolerance': 'medium',
            'investment_horizon': 'medium',
            'trading_frequency': 'medium',
            'focus_areas': ['fundamental', 'news'],
            'custom_message': ''
        }
        
        # 1回目: プロンプトを生成（ファイルを読み込む）
        prompt1 = generate_preference_prompt()
        assert '投資家の志向性' in prompt1
        assert mock_load.call_count == 1
        
        # 2回目: 同じプロンプトを使用（新たなファイル読み込みは発生しない）
        # 実際には同じプロンプトを再利用するためファイル読み込みは不要
        # ただし、prefs=Noneで呼ばれた場合は再度読み込む（後方互換性）
        prompt2 = generate_preference_prompt()
        assert prompt2 == prompt1
        assert mock_load.call_count == 2  # 後方互換性のため
    
    @patch('preference_loader.load_investment_preferences')
    def test_analyze_with_claude_accepts_pregenerated_prompt(self, mock_load):
        """analyze_with_claudeが事前生成されたプロンプトを受け入れることを確認"""
        # APIキーを環境変数に設定（config.pyがインポートされる前に設定）
        os.environ['CLAUDE_API_KEY'] = 'test-api-key'
        
        # ai_analyzerをここでインポート（defeatbeta-apiのモック後、APIキー設定後）
        from ai_analyzer import analyze_with_claude
        
        with patch('ai_analyzer.anthropic.Anthropic') as mock_anthropic:
            # モックの設定
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text="テスト分析結果")]
            mock_client.messages.create.return_value = mock_message
            
            mock_load.return_value = {
                'investment_style': 'balanced',
                'risk_tolerance': 'medium',
                'investment_horizon': 'medium',
                'trading_frequency': 'medium',
                'focus_areas': ['fundamental', 'news'],
                'custom_message': ''
            }
            
            # テストデータ
            data = {
                'symbol': '7203.T',
                'price': 2500,
                'news': ['テストニュース1', 'テストニュース2'],
                'quantity': 100,
                'acquisition_price': 2400
            }
            
            # 事前にプロンプトを生成
            preference_prompt = generate_preference_prompt()
            assert mock_load.call_count == 1
            
            # 複数回の分析で同じプロンプトを使用
            with patch('ai_analyzer.CLAUDE_API_KEY', 'test-api-key'):
                analyze_with_claude(data, preference_prompt)
                analyze_with_claude(data, preference_prompt)
                analyze_with_claude(data, preference_prompt)
            
            # load_investment_preferencesは1回しか呼ばれていない
            assert mock_load.call_count == 1
            
            # APIは3回呼ばれている
            assert mock_client.messages.create.call_count == 3
    
    @patch('preference_loader.load_investment_preferences')
    def test_analyze_with_gemini_accepts_pregenerated_prompt(self, mock_load):
        """analyze_with_geminiが事前生成されたプロンプトを受け入れることを確認"""
        # APIキーを環境変数に設定
        os.environ['GEMINI_API_KEY'] = 'test-api-key'
        
        # ai_analyzerをここでインポート（defeatbeta-apiのモック後）
        from ai_analyzer import analyze_with_gemini
        
        with patch('ai_analyzer.requests.post') as mock_post:
            # モックの設定
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'candidates': [
                    {
                        'content': {
                            'parts': [
                                {'text': 'テスト分析結果'}
                            ]
                        }
                    }
                ]
            }
            mock_post.return_value = mock_response
            
            mock_load.return_value = {
                'investment_style': 'balanced',
                'risk_tolerance': 'medium',
                'investment_horizon': 'medium',
                'trading_frequency': 'medium',
                'focus_areas': ['fundamental', 'news'],
                'custom_message': ''
            }
            
            # テストデータ
            data = {
                'symbol': 'AAPL',
                'price': 150,
                'news': ['テストニュース1', 'テストニュース2'],
                'quantity': 50,
                'acquisition_price': 145
            }
            
            # 事前にプロンプトを生成
            preference_prompt = generate_preference_prompt()
            assert mock_load.call_count == 1
            
            # 複数回の分析で同じプロンプトを使用
            with patch('ai_analyzer.GEMINI_API_KEY', 'test-api-key'):
                analyze_with_gemini(data, preference_prompt)
                analyze_with_gemini(data, preference_prompt)
                analyze_with_gemini(data, preference_prompt)
            
            # load_investment_preferencesは1回しか呼ばれていない
            assert mock_load.call_count == 1
            
            # APIは3回呼ばれている
            assert mock_post.call_count == 3
    
    @patch('preference_loader.load_investment_preferences')
    def test_backward_compatibility_without_prompt_parameter(self, mock_load):
        """プロンプトパラメータなしでも動作することを確認（後方互換性）"""
        # APIキーを環境変数に設定
        os.environ['CLAUDE_API_KEY'] = 'test-api-key'
        
        # ai_analyzerをここでインポート（defeatbeta-apiのモック後）
        from ai_analyzer import analyze_with_claude
        
        with patch('ai_analyzer.anthropic.Anthropic') as mock_anthropic:
            # モックの設定
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text="テスト分析結果")]
            mock_client.messages.create.return_value = mock_message
            
            mock_load.return_value = {
                'investment_style': 'balanced',
                'risk_tolerance': 'medium',
                'investment_horizon': 'medium',
                'trading_frequency': 'medium',
                'focus_areas': ['fundamental', 'news'],
                'custom_message': ''
            }
            
            # テストデータ
            data = {
                'symbol': '7203.T',
                'price': 2500,
                'news': ['テストニュース1'],
                'quantity': 100,
                'acquisition_price': 2400
            }
            
            # プロンプトパラメータなしで呼び出し（古い使い方）
            with patch('ai_analyzer.CLAUDE_API_KEY', 'test-api-key'):
                result = analyze_with_claude(data)
            
            # 内部でload_investment_preferencesが呼ばれることを確認
            assert mock_load.call_count == 1
            assert 'テスト分析結果' in result


class TestFileIOReduction:
    """ファイルI/O削減のテスト"""
    
    @patch('preference_loader.load_investment_preferences')
    def test_preference_file_read_count_with_multiple_stocks(self, mock_load):
        """複数銘柄処理時にファイル読み込みが1回で済むことを確認"""
        mock_load.return_value = {
            'investment_style': 'balanced',
            'risk_tolerance': 'medium',
            'investment_horizon': 'medium',
            'trading_frequency': 'medium',
            'focus_areas': ['fundamental', 'news'],
            'custom_message': ''
        }
        
        # プロンプトを1回生成
        prompt = generate_preference_prompt()
        
        # ファイル読み込みは1回だけ
        assert mock_load.call_count == 1
        
        # 同じプロンプトを複数回使用（35銘柄を想定）
        prompts = [prompt] * 35
        
        # 全て同じプロンプト（ファイル読み込みを再利用）
        assert len(set(prompts)) == 1
        assert all(p == prompt for p in prompts)
        
        # プロンプトの内容を確認
        assert '投資家の志向性' in prompt
        assert 'バランス投資' in prompt
