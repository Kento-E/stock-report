"""
preference_loaderモジュールのテスト
"""

import pytest
import os
import sys
import tempfile
import yaml

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from preference_loader import (
    load_investment_preferences,
    generate_preference_prompt,
    _validate_preferences,
    DEFAULT_PREFERENCES,
    VALID_INVESTMENT_STYLES,
    VALID_RISK_TOLERANCES,
    VALID_INVESTMENT_HORIZONS,
    VALID_TRADING_FREQUENCIES,
    VALID_FOCUS_AREAS
)


class TestLoadInvestmentPreferences:
    """load_investment_preferences関数のテスト"""
    
    def test_load_valid_preferences_file(self):
        """有効な設定ファイルを読み込める"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump({
                'investment_style': 'growth',
                'risk_tolerance': 'high',
                'investment_horizon': 'long',
                'trading_frequency': 'low',
                'focus_areas': ['technical', 'momentum'],
                'custom_message': 'テクノロジー企業重視'
            }, f, allow_unicode=True)
            filepath = f.name
        
        try:
            prefs = load_investment_preferences(filepath)
            
            assert prefs['investment_style'] == 'growth'
            assert prefs['risk_tolerance'] == 'high'
            assert prefs['investment_horizon'] == 'long'
            assert prefs['trading_frequency'] == 'low'
            assert prefs['focus_areas'] == ['technical', 'momentum']
            assert prefs['custom_message'] == 'テクノロジー企業重視'
        finally:
            os.unlink(filepath)
    
    def test_load_file_not_found_returns_default(self):
        """ファイルが見つからない場合はデフォルト設定を返す"""
        prefs = load_investment_preferences('nonexistent_file.yaml')
        
        assert prefs == DEFAULT_PREFERENCES
    
    def test_load_empty_file_returns_default(self):
        """空のファイルの場合はデフォルト設定を返す"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write('')
            filepath = f.name
        
        try:
            prefs = load_investment_preferences(filepath)
            assert prefs == DEFAULT_PREFERENCES
        finally:
            os.unlink(filepath)
    
    def test_load_partial_preferences_merges_with_default(self):
        """一部の設定のみ指定した場合、残りはデフォルト値とマージされる"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump({
                'investment_style': 'value',
                'risk_tolerance': 'low'
            }, f, allow_unicode=True)
            filepath = f.name
        
        try:
            prefs = load_investment_preferences(filepath)
            
            assert prefs['investment_style'] == 'value'
            assert prefs['risk_tolerance'] == 'low'
            # デフォルト値がマージされている
            assert prefs['investment_horizon'] == DEFAULT_PREFERENCES['investment_horizon']
            assert prefs['trading_frequency'] == DEFAULT_PREFERENCES['trading_frequency']
            assert prefs['focus_areas'] == DEFAULT_PREFERENCES['focus_areas']
        finally:
            os.unlink(filepath)
    
    def test_load_invalid_yaml_syntax_raises_error(self):
        """YAML構文エラーの場合は例外が発生する"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write('invalid: yaml: syntax:')
            filepath = f.name
        
        try:
            with pytest.raises(yaml.YAMLError):
                load_investment_preferences(filepath)
        finally:
            os.unlink(filepath)


class TestValidatePreferences:
    """_validate_preferences関数のテスト"""
    
    def test_valid_preferences(self):
        """有効な設定値は検証を通過する"""
        prefs = {
            'investment_style': 'balanced',
            'risk_tolerance': 'medium',
            'investment_horizon': 'medium',
            'trading_frequency': 'medium',
            'focus_areas': ['fundamental', 'news']
        }
        
        # 例外が発生しないことを確認
        _validate_preferences(prefs)
    
    def test_invalid_investment_style_raises_error(self):
        """無効な investment_style は例外を発生させる"""
        prefs = {'investment_style': 'invalid_style'}
        
        with pytest.raises(ValueError, match='無効な investment_style'):
            _validate_preferences(prefs)
    
    def test_invalid_risk_tolerance_raises_error(self):
        """無効な risk_tolerance は例外を発生させる"""
        prefs = {'risk_tolerance': 'super_high'}
        
        with pytest.raises(ValueError, match='無効な risk_tolerance'):
            _validate_preferences(prefs)
    
    def test_invalid_investment_horizon_raises_error(self):
        """無効な investment_horizon は例外を発生させる"""
        prefs = {'investment_horizon': 'ultra_long'}
        
        with pytest.raises(ValueError, match='無効な investment_horizon'):
            _validate_preferences(prefs)
    
    def test_invalid_trading_frequency_raises_error(self):
        """無効な trading_frequency は例外を発生させる"""
        prefs = {'trading_frequency': 'ultra_high'}
        
        with pytest.raises(ValueError, match='無効な trading_frequency'):
            _validate_preferences(prefs)
    
    def test_invalid_focus_areas_not_list_raises_error(self):
        """focus_areas がリストでない場合は例外を発生させる"""
        prefs = {'focus_areas': 'not_a_list'}
        
        with pytest.raises(ValueError, match='focus_areas はリスト形式'):
            _validate_preferences(prefs)
    
    def test_invalid_focus_areas_value_raises_error(self):
        """無効な focus_areas の値は例外を発生させる"""
        prefs = {'focus_areas': ['fundamental', 'invalid_area']}
        
        with pytest.raises(ValueError, match='無効な focus_areas'):
            _validate_preferences(prefs)
    
    def test_all_valid_investment_styles(self):
        """すべての有効な investment_style を検証できる"""
        for style in VALID_INVESTMENT_STYLES:
            prefs = {'investment_style': style}
            _validate_preferences(prefs)  # 例外が発生しないことを確認
    
    def test_all_valid_risk_tolerances(self):
        """すべての有効な risk_tolerance を検証できる"""
        for tolerance in VALID_RISK_TOLERANCES:
            prefs = {'risk_tolerance': tolerance}
            _validate_preferences(prefs)  # 例外が発生しないことを確認
    
    def test_all_valid_investment_horizons(self):
        """すべての有効な investment_horizon を検証できる"""
        for horizon in VALID_INVESTMENT_HORIZONS:
            prefs = {'investment_horizon': horizon}
            _validate_preferences(prefs)  # 例外が発生しないことを確認
    
    def test_all_valid_trading_frequencies(self):
        """すべての有効な trading_frequency を検証できる"""
        for frequency in VALID_TRADING_FREQUENCIES:
            prefs = {'trading_frequency': frequency}
            _validate_preferences(prefs)  # 例外が発生しないことを確認
    
    def test_all_valid_focus_areas(self):
        """すべての有効な focus_areas を検証できる"""
        prefs = {'focus_areas': VALID_FOCUS_AREAS}
        _validate_preferences(prefs)  # 例外が発生しないことを確認


class TestGeneratePreferencePrompt:
    """generate_preference_prompt関数のテスト"""
    
    def test_generate_prompt_with_default_preferences(self):
        """デフォルト設定でプロンプトを生成できる"""
        prefs = DEFAULT_PREFERENCES
        
        prompt = generate_preference_prompt(prefs)
        
        assert '投資家の志向性' in prompt
        assert '投資スタイル' in prompt
        assert 'リスク許容度' in prompt
        assert '投資期間' in prompt
        assert '売買頻度' in prompt
        assert '重視する指標' in prompt
    
    def test_generate_prompt_with_growth_style(self):
        """成長投資スタイルのプロンプトを生成できる"""
        prefs = {
            'investment_style': 'growth',
            'risk_tolerance': 'high',
            'investment_horizon': 'long',
            'trading_frequency': 'low',
            'focus_areas': ['technical', 'momentum']
        }
        
        prompt = generate_preference_prompt(prefs)
        
        assert '成長投資' in prompt
        assert '高リスク' in prompt
        assert '長期' in prompt
        assert 'テクニカル分析' in prompt
        assert 'モメンタム' in prompt
    
    def test_generate_prompt_with_value_style(self):
        """バリュー投資スタイルのプロンプトを生成できる"""
        prefs = {
            'investment_style': 'value',
            'risk_tolerance': 'low',
            'investment_horizon': 'long',
            'trading_frequency': 'low',
            'focus_areas': ['fundamental']
        }
        
        prompt = generate_preference_prompt(prefs)
        
        assert 'バリュー投資' in prompt
        assert '低リスク' in prompt
        assert 'ファンダメンタル分析' in prompt
    
    def test_generate_prompt_with_income_style(self):
        """インカムゲイン投資スタイルのプロンプトを生成できる"""
        prefs = {
            'investment_style': 'income',
            'risk_tolerance': 'low',
            'investment_horizon': 'long',
            'trading_frequency': 'low',
            'focus_areas': ['dividend', 'fundamental']
        }
        
        prompt = generate_preference_prompt(prefs)
        
        assert 'インカムゲイン投資' in prompt
        assert '配当利回り' in prompt
    
    def test_generate_prompt_with_speculative_style(self):
        """投機的投資スタイルのプロンプトを生成できる"""
        prefs = {
            'investment_style': 'speculative',
            'risk_tolerance': 'high',
            'investment_horizon': 'short',
            'trading_frequency': 'high',
            'focus_areas': ['technical', 'momentum', 'news']
        }
        
        prompt = generate_preference_prompt(prefs)
        
        assert '投機的投資' in prompt
        assert '短期' in prompt
        assert '頻繁' in prompt
    
    def test_generate_prompt_with_custom_message(self):
        """カスタムメッセージを含むプロンプトを生成できる"""
        prefs = {
            'investment_style': 'balanced',
            'risk_tolerance': 'medium',
            'investment_horizon': 'medium',
            'trading_frequency': 'medium',
            'focus_areas': ['fundamental', 'news'],
            'custom_message': '環境に配慮した企業を優先したい'
        }
        
        prompt = generate_preference_prompt(prefs)
        
        assert '環境に配慮した企業を優先したい' in prompt
        assert '追加の要望' in prompt
    
    def test_generate_prompt_without_custom_message(self):
        """カスタムメッセージがない場合は含まれない"""
        prefs = {
            'investment_style': 'balanced',
            'risk_tolerance': 'medium',
            'investment_horizon': 'medium',
            'trading_frequency': 'medium',
            'focus_areas': ['fundamental'],
            'custom_message': ''
        }
        
        prompt = generate_preference_prompt(prefs)
        
        assert '追加の要望' not in prompt
    
    def test_generate_prompt_with_none_loads_from_file(self):
        """prefs=Noneの場合はファイルから読み込む（またはデフォルト）"""
        prompt = generate_preference_prompt(None)
        
        # プロンプトが生成されることを確認
        assert '投資家の志向性' in prompt
        assert '投資スタイル' in prompt
    
    def test_generate_prompt_multiple_focus_areas(self):
        """複数のfocus_areasが正しく表示される"""
        prefs = {
            'investment_style': 'balanced',
            'risk_tolerance': 'medium',
            'investment_horizon': 'medium',
            'trading_frequency': 'medium',
            'focus_areas': ['technical', 'fundamental', 'news', 'dividend', 'momentum']
        }
        
        prompt = generate_preference_prompt(prefs)
        
        assert 'テクニカル分析' in prompt
        assert 'ファンダメンタル分析' in prompt
        assert 'ニュース・イベント' in prompt
        assert '配当利回り' in prompt
        assert 'モメンタム' in prompt
