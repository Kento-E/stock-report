"""
YAML自動フォーマットスクリプト

このスクリプトはYAMLファイルを自動的にフォーマットし、
インデントのズレなどを修正します。
コメントは保持されます。
"""

import sys
import os
from ruamel.yaml import YAML
from io import StringIO


def format_yaml_file(filepath: str, check_only: bool = False) -> tuple[bool, str]:
    """
    YAMLファイルをフォーマットする
    
    Args:
        filepath: フォーマット対象のYAMLファイルパス
        check_only: True の場合、フォーマットが必要かチェックするのみ（ファイルは変更しない）
        
    Returns:
        (変更があったか, メッセージ)
    """
    # ファイルの存在確認
    if not os.path.exists(filepath):
        return False, f"ファイルが見つかりません: {filepath}"
    
    try:
        # 元のファイル内容を読み込み
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # ruamel.yamlでフォーマット
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.default_flow_style = False
        yaml.map_indent = 2
        yaml.sequence_indent = 4
        yaml.sequence_dash_offset = 2
        yaml.width = 4096  # 行の折り返しを防ぐ
        
        # 読み込み
        data = yaml.load(StringIO(original_content))
        
        # フォーマット後の内容を生成
        output = StringIO()
        yaml.dump(data, output)
        formatted_content = output.getvalue()
        
        # 変更があったか確認
        if original_content == formatted_content:
            return False, "フォーマット済み（変更なし）"
        
        # check_onlyモードの場合はここで終了
        if check_only:
            return True, "フォーマットが必要です"
        
        # ファイルに書き込み
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        return True, "フォーマット完了"
        
    except Exception as e:
        return False, f"エラー: {e}"


def main():
    """
    メイン処理
    コマンドライン引数でファイルパスを受け取り、フォーマットを実行する
    """
    # コマンドライン引数の解析
    check_only = '--check' in sys.argv
    if check_only:
        sys.argv.remove('--check')
    
    # ファイルパスの取得
    if len(sys.argv) < 2:
        print("使用方法: python format_yaml.py <filepath> [--check]")
        print("  --check: フォーマットが必要かチェックするのみ（ファイルは変更しない）")
        return 1
    
    filepath = sys.argv[1]
    
    print(f"🔧 {'チェック中' if check_only else 'フォーマット中'}: {filepath}")
    print("-" * 60)
    
    # フォーマット実行
    changed, message = format_yaml_file(filepath, check_only)
    
    if changed:
        if check_only:
            print(f"⚠️  {message}")
            return 1
        else:
            print(f"✅ {message}")
            return 0
    else:
        print(f"✓ {message}")
        return 0


if __name__ == '__main__':
    sys.exit(main())
