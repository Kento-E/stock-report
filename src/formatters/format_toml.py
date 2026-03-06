"""
TOML構文チェックスクリプト

このスクリプトはTOMLファイルの構文を検証します。
"""

import os
import sys
import tomllib


def format_toml_file(filepath: str, check_only: bool = False) -> tuple[bool, str]:
    """
    TOMLファイルの構文を検証する

    Args:
        filepath: 検証対象のTOMLファイルパス
        check_only: このパラメータは後方互換性のために残していますが、
                    TOMLは再フォーマット不要のため常に構文チェックのみ実行します

    Returns:
        (エラーがあったか, メッセージ)
    """
    # ファイルの存在確認
    if not os.path.exists(filepath):
        return False, f"ファイルが見つかりません: {filepath}"

    try:
        with open(filepath, "rb") as f:
            tomllib.load(f)
        return False, "バリデーション済み（エラーなし）"
    except tomllib.TOMLDecodeError as e:
        return True, f"TOML構文エラー: {e}"
    except Exception as e:
        return False, f"エラー: {e}"


def main():
    """
    メイン処理
    コマンドライン引数でファイルパスを受け取り、構文チェックを実行する
    """
    # ファイルパスの取得
    if len(sys.argv) < 2:
        print("使用方法: python format_toml.py <filepath>")
        return 1

    filepath = sys.argv[1]

    print(f"🔧 チェック中: {filepath}")
    print("-" * 60)

    # 構文チェック実行
    has_error, message = format_toml_file(filepath)

    if has_error:
        print(f"❌ {message}")
        return 1
    else:
        print(f"✓ {message}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
