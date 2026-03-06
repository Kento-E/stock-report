"""
stocks.tomlファイルのバリデーションスクリプト

このスクリプトはstocks.tomlファイルの形式をチェックし、
必須フィールドや有効な値の範囲を検証します。
"""

import os
import sys
from datetime import date
from typing import Any, List

import tomllib


def validate_stock_entry(stock: Any, index: int) -> List[str]:
    """
    個別の銘柄エントリーを検証する

    Args:
        stock: 銘柄エントリー（辞書または文字列）
        index: エントリーのインデックス番号

    Returns:
        エラーメッセージのリスト（空なら検証成功）
    """
    errors = []

    # 文字列形式は後方互換性のため許可
    if isinstance(stock, str):
        if not stock:
            errors.append(f"銘柄[{index}]: 銘柄コードが空です")
        return errors

    # 辞書形式でない場合はエラー
    if not isinstance(stock, dict):
        errors.append(f"銘柄[{index}]: 銘柄エントリーは辞書または文字列である必要があります")
        return errors

    # 必須フィールド: symbol
    if "symbol" not in stock:
        errors.append(f"銘柄[{index}]: 必須フィールド 'symbol' が見つかりません")
        return errors

    # symbolが空でないことを確認（文字列または数値を許可）
    symbol = stock["symbol"]
    if symbol is None or symbol == "":
        errors.append(f"銘柄[{index}]: 'symbol' が空です")
    elif not isinstance(symbol, (str, int)):
        errors.append(f"銘柄[{index}]: 'symbol' は文字列または数値である必要があります")

    # 任意フィールドの型チェック
    if "name" in stock and stock["name"] is not None:
        if not isinstance(stock["name"], str):
            errors.append(f"銘柄[{index}] ({stock['symbol']}): 'name' は文字列である必要があります")

    if "quantity" in stock and stock["quantity"] is not None:
        if not isinstance(stock["quantity"], (int, float)):
            errors.append(
                f"銘柄[{index}] ({stock['symbol']}): 'quantity' は数値である必要があります"
            )

    if "acquisition_price" in stock and stock["acquisition_price"] is not None:
        if not isinstance(stock["acquisition_price"], (int, float)):
            errors.append(
                f"銘柄[{index}] ({stock['symbol']}): 'acquisition_price' は数値である必要があります"
            )
        elif stock["acquisition_price"] <= 0:
            errors.append(
                f"銘柄[{index}] ({stock['symbol']}): 'acquisition_price' は正の数である必要があります"
            )

    if "currency" in stock and stock["currency"] is not None:
        if not isinstance(stock["currency"], str):
            errors.append(
                f"銘柄[{index}] ({stock['symbol']}): 'currency' は文字列である必要があります"
            )
        # 通貨の値は柔軟に許可（円、ドル、ユーロ、ポンドなど）

    if "account_type" in stock and stock["account_type"] is not None:
        if not isinstance(stock["account_type"], str):
            errors.append(
                f"銘柄[{index}] ({stock['symbol']}): 'account_type' は文字列である必要があります"
            )
        elif stock["account_type"] not in ["特定", "NISA", "旧NISA"]:
            errors.append(
                f"銘柄[{index}] ({stock['symbol']}): 'account_type' は '特定', 'NISA', '旧NISA' のいずれかである必要があります"
            )

    if "considering_action" in stock and stock["considering_action"] is not None:
        if not isinstance(stock["considering_action"], str):
            errors.append(
                f"銘柄[{index}] ({stock['symbol']}): 'considering_action' は文字列である必要があります"
            )
        elif stock["considering_action"] not in ["buy", "short_sell"]:
            errors.append(
                f"銘柄[{index}] ({stock['symbol']}): 'considering_action' は 'buy' または 'short_sell' である必要があります"
            )

    if "note" in stock and stock["note"] is not None:
        if not isinstance(stock["note"], str):
            errors.append(f"銘柄[{index}] ({stock['symbol']}): 'note' は文字列である必要があります")

    if "added" in stock and stock["added"] is not None:
        # added は文字列、整数、または日付型を許可
        if not isinstance(stock["added"], (str, int, date)):
            errors.append(
                f"銘柄[{index}] ({stock['symbol']}): 'added' は文字列または日付型である必要があります"
            )

    return errors


def validate_stocks_toml(filepath: str) -> tuple[bool, List[str]]:
    """
    stocks.tomlファイル全体を検証する

    Args:
        filepath: TOMLファイルのパス

    Returns:
        (検証成功か, エラーメッセージのリスト)
    """
    errors = []

    # ファイルの存在確認
    if not os.path.exists(filepath):
        errors.append(f"ファイルが見つかりません: {filepath}")
        return False, errors

    # TOMLとして読み込めるか確認
    try:
        with open(filepath, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        errors.append(f"TOML解析エラー: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"ファイル読み込みエラー: {e}")
        return False, errors

    # データが空でないことを確認
    if data is None:
        errors.append("TOMLファイルが空です")
        return False, errors

    # 最上位が辞書であることを確認
    if not isinstance(data, dict):
        errors.append("TOMLファイルの最上位要素は辞書である必要があります")
        return False, errors

    # stocksキーの存在確認
    if "stocks" not in data:
        errors.append("'stocks' キーが見つかりません")
        return False, errors

    stocks = data["stocks"]

    # stocksがリストであることを確認
    if not isinstance(stocks, list):
        errors.append("'stocks' の値はリストである必要があります")
        return False, errors

    # stocksが空でないことを確認
    if not stocks:
        errors.append("'stocks' リストが空です。少なくとも1つの銘柄を追加してください")
        return False, errors

    # 各銘柄エントリーを検証
    for i, stock in enumerate(stocks):
        entry_errors = validate_stock_entry(stock, i)
        errors.extend(entry_errors)

    # エラーがなければ成功
    return len(errors) == 0, errors


def main():
    """
    メイン処理
    コマンドライン引数でファイルパスを受け取り、検証を実行する
    """
    # デフォルトのファイルパス
    default_path = "data/stocks.toml"

    # コマンドライン引数からファイルパスを取得
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # スクリプトのディレクトリからの相対パスを解決
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        filepath = os.path.join(project_root, default_path)

    print(f"🔍 Validating: {filepath}")
    print("-" * 60)

    # 検証実行
    success, errors = validate_stocks_toml(filepath)

    if success:
        print("✅ 検証成功: stocks.tomlファイルは正しい形式です")
        return 0
    else:
        print("❌ 検証失敗: 以下のエラーが見つかりました:")
        print()
        for error in errors:
            print(f"  • {error}")
        print()
        print(f"合計 {len(errors)} 件のエラー")
        return 1


if __name__ == "__main__":
    sys.exit(main())
