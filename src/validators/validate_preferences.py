"""
投資志向性設定ファイル（investment_preferences.yaml）のバリデーションスクリプト

このスクリプトは投資志向性設定ファイルの形式を検証し、
不正なデータの混入を防ぎます。
"""

import sys
import os

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from loaders.preference_loader import load_investment_preferences


def validate_investment_preferences_file(filepath='data/investment_preferences.yaml'):
    """
    投資志向性設定ファイルをバリデーションします。
    
    Args:
        filepath: バリデーション対象のファイルパス
    
    Returns:
        True: バリデーション成功
        False: バリデーション失敗
    """
    print(f"投資志向性設定ファイルをバリデーション中: {filepath}")
    
    try:
        prefs = load_investment_preferences(filepath)
        
        print("✓ バリデーション成功")
        print("\n読み込まれた設定:")
        print(f"  - 投資スタイル: {prefs.get('investment_style')}")
        print(f"  - リスク許容度: {prefs.get('risk_tolerance')}")
        print(f"  - 投資期間: {prefs.get('investment_horizon')}")
        print(f"  - 売買頻度: {prefs.get('trading_frequency')}")
        print(f"  - 重視する指標: {', '.join(prefs.get('focus_areas', []))}")
        if prefs.get('custom_message'):
            print(f"  - カスタムメッセージ: {prefs.get('custom_message')}")
        
        return True
        
    except FileNotFoundError:
        print(f"✗ エラー: ファイルが見つかりません: {filepath}")
        print("  デフォルト設定が使用されます。")
        return True  # ファイルがない場合はエラーとしない（デフォルト設定を使用）
        
    except Exception as e:
        print(f"✗ バリデーションエラー: {e}")
        return False


if __name__ == "__main__":
    # コマンドライン引数からファイルパスを取得（指定がなければデフォルト）
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'data/investment_preferences.yaml'
    
    success = validate_investment_preferences_file(filepath)
    
    if not success:
        print("\nバリデーションに失敗しました。")
        sys.exit(1)
    
    print("\nバリデーションが正常に完了しました。")
    sys.exit(0)
