"""
銘柄リスト読み込みモジュール

YAML形式の銘柄リストファイルから銘柄情報を読み込みます。
"""

import os

import yaml


def normalize_symbol(symbol):
    """
    銘柄コードを正規化する。

    Args:
        symbol: 銘柄コード（文字列または数値）

    Returns:
        正規化された銘柄コード（文字列）

    数値の場合は文字列に変換し、4桁の数字の場合は日本株として.Tサフィックスを追加する。
    """
    # 数値の場合は文字列に変換
    if isinstance(symbol, int):
        symbol = str(symbol)

    # 文字列でない場合はそのまま返す（バリデーションで弾かれる）
    if not isinstance(symbol, str):
        return symbol

    # 4桁の数字のみで構成されている場合、日本株として.Tを追加
    if symbol.isdigit() and len(symbol) == 4:
        return f"{symbol}.T"

    return symbol


def load_stock_symbols(filepath="data/stocks.yaml"):
    """
    銘柄リストファイル（YAML形式）から銘柄情報を読み込む。

    YAML形式の例:
    stocks:
      - symbol: 7203.T
        name: トヨタ自動車
        added: 2024-01-01
        quantity: 100
        acquisition_price: 2500
        currency: 円
      - symbol: 6758.T
        name: ソニーグループ
      - symbol: AAPL
        name: Apple Inc.
        currency: ドル
      - symbol: BMW.DE
        name: BMW
        currency: ユーロ

    返り値: 銘柄情報の辞書リスト (例: [{'symbol': '7203.T', 'name': 'トヨタ自動車', 'quantity': 100, 'acquisition_price': 2500, 'currency': '円'}, ...])
    """
    stocks = []
    # ファイルパスの解決（main.pyからの相対パス）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # script_dirは src/loaders なので、2階層上る: src/loaders -> src -> プロジェクトルート
    project_root = os.path.dirname(os.path.dirname(script_dir))
    full_path = os.path.join(project_root, filepath)

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # YAMLから銘柄リストを取得
        if data and "stocks" in data and data["stocks"]:
            for stock in data["stocks"]:
                if isinstance(stock, dict) and "symbol" in stock:
                    # symbolを正規化（数値の場合は文字列に変換し、4桁なら.Tを追加）
                    symbol = normalize_symbol(stock["symbol"])

                    # 銘柄情報を辞書として保存
                    account_type = stock.get("account_type", "特定")
                    # 有効な口座種別のバリデーション
                    valid_account_types = ["特定", "NISA", "旧NISA"]
                    if account_type not in valid_account_types:
                        account_type = "特定"  # 無効な値の場合はデフォルトに

                    stock_info = {
                        "symbol": symbol,
                        "name": stock.get("name"),
                        "quantity": stock.get("quantity"),
                        "acquisition_price": stock.get("acquisition_price"),
                        "note": stock.get("note"),
                        "added": stock.get("added"),
                        "considering_action": stock.get("considering_action", "buy"),
                        "currency": stock.get("currency"),
                        "account_type": account_type,
                    }
                    stocks.append(stock_info)
                elif isinstance(stock, str):
                    # 文字列の場合も対応（後方互換性）
                    stocks.append({"symbol": stock})

        if not stocks:
            error_msg = f"エラー: 銘柄リストが空です。{full_path} に銘柄を追加してください。"
            print(error_msg)
            raise ValueError(error_msg)

    except FileNotFoundError:
        error_msg = f"エラー: 銘柄リストファイルが見つかりません: {full_path}"
        print(error_msg)
        raise FileNotFoundError(error_msg)
    except yaml.YAMLError as e:
        error_msg = f"エラー: YAML解析エラー: {e}"
        print(error_msg)
        raise yaml.YAMLError(error_msg)
    except Exception as e:
        error_msg = f"エラー: 銘柄リストファイルの読み込みエラー: {e}"
        print(error_msg)
        raise

    return stocks


def get_currency_for_symbol(symbol, explicit_currency=None):
    """
    銘柄シンボルから通貨を判定する。

    Args:
        symbol: 銘柄コード
        explicit_currency: 明示的に指定された通貨（任意）

    Returns:
        通貨単位（円、ドル、ユーロなど）

    明示的に通貨が指定されている場合はそれを優先し、
    未指定の場合は銘柄シンボルから自動判定する。
    日本株（.T、.JPなどのサフィックス、または4桁数字）の場合は「円」、それ以外は「ドル」を返す。
    """
    if explicit_currency:
        return explicit_currency

    # 文字列に変換（数値の場合に備えて）
    symbol_str = str(symbol)

    # 日本株の判定：.TまたはJPサフィックス、または4桁の数字のみ
    if symbol_str.endswith(".T") or symbol_str.endswith(".JP"):
        return "円"
    if symbol_str.isdigit() and len(symbol_str) == 4:
        return "円"

    return "ドル"


def categorize_stock(stock_info):
    """
    銘柄を保有状況に基づいて分類する。

    Args:
        stock_info: 銘柄情報の辞書

    Returns:
        分類名（'holding', 'short_selling', 'considering_buy', 'considering_short_sell'）
    """
    quantity = stock_info.get("quantity")
    considering_action = stock_info.get("considering_action", "buy")  # デフォルトは購入検討

    if quantity is None or quantity == 0:
        # 保有数未設定またはゼロの場合は検討中
        if considering_action == "short_sell":
            return "considering_short_sell"
        else:
            return "considering_buy"
    elif quantity > 0:
        # 正の値は保有中
        return "holding"
    elif quantity < 0:
        # 負の値は空売り中
        return "short_selling"


def categorize_stocks(stocks):
    """
    銘柄リストを分類別に振り分ける。

    Args:
        stocks: 銘柄情報の辞書リスト

    Returns:
        分類別の銘柄辞書 {'holding': [...], 'short_selling': [...], 'considering_buy': [...], 'considering_short_sell': [...]}
    """
    categorized = {
        "holding": [],
        "short_selling": [],
        "considering_buy": [],
        "considering_short_sell": [],
    }

    for stock_info in stocks:
        category = categorize_stock(stock_info)
        categorized[category].append(stock_info)

    return categorized


def calculate_tax(profit_loss, account_type):
    """
    口座種別に応じて税額を計算する。

    Args:
        profit_loss: 譲渡益（円またはドルなど）
        account_type: 口座種別（'特定', 'NISA', '旧NISA'）

    Returns:
        税額（譲渡益がマイナスまたは非課税口座の場合は0）
    """
    # 損失の場合は課税なし
    if profit_loss <= 0:
        return 0

    # 口座種別による課税判定
    if account_type in ["NISA", "旧NISA"]:
        # NISA口座は非課税
        return 0
    else:
        # 特定口座は譲渡益の20.315%課税
        return profit_loss * 0.20315
