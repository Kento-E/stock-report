"""
投資志向性設定の読み込みモジュール

投資志向性設定ファイル（data/investment_preferences.yaml）を読み込み、
AI分析用のプロンプト文字列を生成します。
"""

import os
import yaml

# 有効な設定値の定義
VALID_INVESTMENT_STYLES = ['growth', 'value', 'income', 'balanced', 'speculative']
VALID_RISK_TOLERANCES = ['low', 'medium', 'high']
VALID_INVESTMENT_HORIZONS = ['short', 'medium', 'long']
VALID_TRADING_FREQUENCIES = ['high', 'medium', 'low']
VALID_FOCUS_AREAS = ['technical', 'fundamental', 'news', 'dividend', 'momentum']

# 日本語表示用の辞書
INVESTMENT_STYLE_LABELS = {
    'growth': '成長投資（成長性重視、高リスク・高リターン）',
    'value': 'バリュー投資（割安株投資、中リスク・中リターン）',
    'income': 'インカムゲイン投資（配当・優待重視、低リスク・安定志向）',
    'balanced': 'バランス投資（成長と配当のバランス、中リスク）',
    'speculative': '投機的投資（短期売買、高リスク・高リターン）'
}

RISK_TOLERANCE_LABELS = {
    'low': '低リスク（元本重視、安全性優先）',
    'medium': '中リスク（適度なリスクとリターンのバランス）',
    'high': '高リスク（積極的なリターン追求、損失許容度が高い）'
}

INVESTMENT_HORIZON_LABELS = {
    'short': '短期（数日～数週間）',
    'medium': '中期（数ヶ月～1年）',
    'long': '長期（数年以上）'
}

TRADING_FREQUENCY_LABELS = {
    'high': '頻繁（デイトレード、スイングトレード）',
    'medium': '適度（週次～月次で売買）',
    'low': '少ない（バイ&ホールド、長期保有）'
}

FOCUS_AREA_LABELS = {
    'technical': 'テクニカル分析（チャート、移動平均、RSIなど）',
    'fundamental': 'ファンダメンタル分析（PER、PBR、財務状況）',
    'news': 'ニュース・イベント（市場センチメント、企業ニュース）',
    'dividend': '配当利回り（株主優待、インカムゲイン）',
    'momentum': 'モメンタム（トレンド、勢い）'
}

# デフォルト設定
DEFAULT_PREFERENCES = {
    'investment_style': 'balanced',
    'risk_tolerance': 'medium',
    'investment_horizon': 'medium',
    'trading_frequency': 'medium',
    'focus_areas': ['fundamental', 'news'],
    'custom_message': ''
}


def load_investment_preferences(filepath='data/investment_preferences.yaml'):
    """
    投資志向性設定ファイルを読み込みます。
    
    Args:
        filepath: 設定ファイルのパス（デフォルト: 'data/investment_preferences.yaml'）
    
    Returns:
        投資志向性の設定内容を含む辞書
        
    Raises:
        FileNotFoundError: 設定ファイルが見つからない場合
        ValueError: 設定ファイルの形式が不正な場合
        yaml.YAMLError: YAML構文エラーの場合
    """
    if not os.path.exists(filepath):
        print(f"警告: 投資志向性設定ファイル '{filepath}' が見つかりません。デフォルト設定を使用します。")
        return DEFAULT_PREFERENCES.copy()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            prefs = yaml.safe_load(f)
        
        if prefs is None:
            print(f"警告: 投資志向性設定ファイルが空です。デフォルト設定を使用します。")
            return DEFAULT_PREFERENCES.copy()
        
        # デフォルト値とマージ
        result = DEFAULT_PREFERENCES.copy()
        result.update(prefs)
        
        # バリデーション
        _validate_preferences(result)
        
        return result
        
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"投資志向性設定ファイル '{filepath}' のYAML構文エラー: {e}")
    except Exception as e:
        raise ValueError(f"投資志向性設定ファイル '{filepath}' の読み込みエラー: {e}")


def _validate_preferences(prefs):
    """
    投資志向性設定の妥当性を検証します。
    
    Args:
        prefs: 投資志向性の設定内容を含む辞書
        
    Raises:
        ValueError: 設定値が不正な場合
    """
    # investment_styleの検証
    if 'investment_style' in prefs and prefs['investment_style'] not in VALID_INVESTMENT_STYLES:
        raise ValueError(
            f"無効な investment_style: '{prefs['investment_style']}'. "
            f"有効な値: {', '.join(VALID_INVESTMENT_STYLES)}"
        )
    
    # risk_toleranceの検証
    if 'risk_tolerance' in prefs and prefs['risk_tolerance'] not in VALID_RISK_TOLERANCES:
        raise ValueError(
            f"無効な risk_tolerance: '{prefs['risk_tolerance']}'. "
            f"有効な値: {', '.join(VALID_RISK_TOLERANCES)}"
        )
    
    # investment_horizonの検証
    if 'investment_horizon' in prefs and prefs['investment_horizon'] not in VALID_INVESTMENT_HORIZONS:
        raise ValueError(
            f"無効な investment_horizon: '{prefs['investment_horizon']}'. "
            f"有効な値: {', '.join(VALID_INVESTMENT_HORIZONS)}"
        )
    
    # trading_frequencyの検証
    if 'trading_frequency' in prefs and prefs['trading_frequency'] not in VALID_TRADING_FREQUENCIES:
        raise ValueError(
            f"無効な trading_frequency: '{prefs['trading_frequency']}'. "
            f"有効な値: {', '.join(VALID_TRADING_FREQUENCIES)}"
        )
    
    # focus_areasの検証
    if 'focus_areas' in prefs:
        if not isinstance(prefs['focus_areas'], list):
            raise ValueError("focus_areas はリスト形式で指定してください。")
        
        invalid_areas = [area for area in prefs['focus_areas'] if area not in VALID_FOCUS_AREAS]
        if invalid_areas:
            raise ValueError(
                f"無効な focus_areas: {', '.join(invalid_areas)}. "
                f"有効な値: {', '.join(VALID_FOCUS_AREAS)}"
            )


def generate_preference_prompt(prefs=None):
    """
    投資志向性設定からAI分析用のプロンプト文字列を生成します。
    
    Args:
        prefs: 投資志向性の設定内容を含む辞書（Noneの場合はファイルから読み込み）
    
    Returns:
        AI分析用のプロンプト文字列
    """
    if prefs is None:
        try:
            prefs = load_investment_preferences()
        except Exception as e:
            print(f"警告: 投資志向性設定の読み込みに失敗しました。デフォルト設定を使用します。エラー: {e}")
            prefs = DEFAULT_PREFERENCES.copy()
    
    # プロンプト文字列を構築
    prompt_parts = ["投資家の志向性:"]
    
    # 投資スタイル
    investment_style = prefs.get('investment_style', 'balanced')
    prompt_parts.append(f"- 投資スタイル: {INVESTMENT_STYLE_LABELS.get(investment_style, investment_style)}")
    
    # リスク許容度
    risk_tolerance = prefs.get('risk_tolerance', 'medium')
    prompt_parts.append(f"- リスク許容度: {RISK_TOLERANCE_LABELS.get(risk_tolerance, risk_tolerance)}")
    
    # 投資期間
    investment_horizon = prefs.get('investment_horizon', 'medium')
    prompt_parts.append(f"- 投資期間: {INVESTMENT_HORIZON_LABELS.get(investment_horizon, investment_horizon)}")
    
    # 売買頻度
    trading_frequency = prefs.get('trading_frequency', 'medium')
    prompt_parts.append(f"- 売買頻度: {TRADING_FREQUENCY_LABELS.get(trading_frequency, trading_frequency)}")
    
    # 重視する指標
    focus_areas = prefs.get('focus_areas', ['fundamental', 'news'])
    if focus_areas:
        focus_labels = [FOCUS_AREA_LABELS.get(area, area) for area in focus_areas]
        prompt_parts.append(f"- 重視する指標: {', '.join(focus_labels)}")
    
    # カスタムメッセージ
    custom_message = prefs.get('custom_message', '').strip()
    if custom_message:
        prompt_parts.append(f"- 追加の要望: {custom_message}")
    
    return '\n'.join(prompt_parts)
