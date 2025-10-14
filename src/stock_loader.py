"""
銘柄リスト読み込みモジュール

YAML形式の銘柄リストファイルから銘柄情報を読み込みます。
"""

import os
import yaml


def load_stock_symbols(filepath='data/stocks.yaml'):
    """
    銘柄リストファイル（YAML形式）から銘柄情報を読み込む。
    
    YAML形式の例:
    stocks:
      - symbol: 7203.T
        name: トヨタ自動車
        added: 2024-01-01
        quantity: 100
        acquisition_price: 2500
      - symbol: 6758.T
        name: ソニーグループ
    
    返り値: 銘柄情報の辞書リスト (例: [{'symbol': '7203.T', 'name': 'トヨタ自動車', 'quantity': 100, 'acquisition_price': 2500}, ...])
    """
    stocks = []
    # ファイルパスの解決（main.pyからの相対パス）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    full_path = os.path.join(project_root, filepath)
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        # YAMLから銘柄リストを取得
        if data and 'stocks' in data and data['stocks']:
            for stock in data['stocks']:
                if isinstance(stock, dict) and 'symbol' in stock:
                    # 銘柄情報を辞書として保存
                    stock_info = {
                        'symbol': stock['symbol'],
                        'name': stock.get('name'),
                        'quantity': stock.get('quantity'),
                        'acquisition_price': stock.get('acquisition_price'),
                        'note': stock.get('note'),
                        'added': stock.get('added')
                    }
                    stocks.append(stock_info)
                elif isinstance(stock, str):
                    # 文字列の場合も対応（後方互換性）
                    stocks.append({'symbol': stock})
        
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


def get_currency_for_symbol(symbol):
    """
    銘柄シンボルから通貨を判定する。
    日本株（.T、.JPなどのサフィックス）の場合は「円」、それ以外は「ドル」を返す。
    """
    if symbol.endswith('.T') or symbol.endswith('.JP'):
        return '円'
    return 'ドル'


def categorize_stock(stock_info):
    """
    銘柄を保有状況に基づいて分類する。
    
    Args:
        stock_info: 銘柄情報の辞書
        
    Returns:
        分類名（'holding', 'short_selling', 'considering_buy'）
    """
    quantity = stock_info.get('quantity')
    
    if quantity is None:
        # 保有数未設定は購入検討中
        return 'considering_buy'
    elif quantity > 0:
        # 正の値は保有中
        return 'holding'
    elif quantity < 0:
        # 負の値は空売り中
        return 'short_selling'
    else:
        # ゼロの場合も購入検討中とみなす
        return 'considering_buy'


def categorize_stocks(stocks):
    """
    銘柄リストを分類別に振り分ける。
    
    Args:
        stocks: 銘柄情報の辞書リスト
        
    Returns:
        分類別の銘柄辞書 {'holding': [...], 'short_selling': [...], 'considering_buy': [...]}
    """
    categorized = {
        'holding': [],
        'short_selling': [],
        'considering_buy': []
    }
    
    for stock_info in stocks:
        category = categorize_stock(stock_info)
        categorized[category].append(stock_info)
    
    return categorized
