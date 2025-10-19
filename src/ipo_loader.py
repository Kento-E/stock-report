"""
上場予定銘柄リスト読み込みモジュール

YAML形式の上場予定銘柄リストファイルから銘柄情報を読み込みます。
"""

import os
import yaml
from datetime import datetime, timedelta


def load_ipo_stocks(filepath='data/ipo_stocks.yaml'):
    """
    上場予定銘柄リストファイル（YAML形式）から銘柄情報を読み込む。
    
    YAML形式の例:
    ipo_stocks:
      - symbol: XXXX.T
        name: サンプル株式会社
        ipo_date: 2025-11-01
        market: 東証プライム
        expected_price: 1000
        currency: 円
        note: 上場予定
    
    返り値: 銘柄情報の辞書リスト
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
        if data and 'ipo_stocks' in data and data['ipo_stocks']:
            for stock in data['ipo_stocks']:
                if isinstance(stock, dict) and 'symbol' in stock and 'name' in stock:
                    # YAMLは日付を自動的にdatetimeオブジェクトに変換する場合があるため、文字列に統一
                    ipo_date = stock.get('ipo_date')
                    if ipo_date and not isinstance(ipo_date, str):
                        ipo_date = str(ipo_date)
                    
                    stock_info = {
                        'symbol': stock['symbol'],
                        'name': stock['name'],
                        'ipo_date': ipo_date,
                        'market': stock.get('market'),
                        'expected_price': stock.get('expected_price'),
                        'note': stock.get('note'),
                        'currency': stock.get('currency')
                    }
                    stocks.append(stock_info)
        
        # 空のリストは正常（上場予定銘柄がない場合）
        return stocks
            
    except FileNotFoundError:
        # ファイルが存在しない場合は空のリストを返す（エラーにしない）
        print(f"情報: 上場予定銘柄リストファイルが見つかりません: {full_path}")
        print("上場予定銘柄のレポートはスキップされます。")
        return []
    except yaml.YAMLError as e:
        error_msg = f"エラー: 上場予定銘柄リストのYAML解析エラー: {e}"
        print(error_msg)
        raise yaml.YAMLError(error_msg)
    except Exception as e:
        error_msg = f"エラー: 上場予定銘柄リストファイルの読み込みエラー: {e}"
        print(error_msg)
        raise


def filter_upcoming_ipos(ipo_stocks, days_ahead=7):
    """
    上場予定日が近い銘柄をフィルタリングする。
    
    Args:
        ipo_stocks: IPO銘柄リスト
        days_ahead: 何日先までの上場予定を含めるか（デフォルト: 7日）
    
    Returns:
        フィルタリングされた銘柄リスト
    """
    if not ipo_stocks:
        return []
    
    today = datetime.now().date()
    cutoff_date = today + timedelta(days=days_ahead)
    
    filtered = []
    for stock in ipo_stocks:
        # 上場日が設定されていない場合は含める
        if not stock.get('ipo_date'):
            filtered.append(stock)
            continue
        
        try:
            # 上場日をパース
            ipo_date = datetime.strptime(stock['ipo_date'], '%Y-%m-%d').date()
            # 今日から指定日数以内の銘柄を含める
            if today <= ipo_date <= cutoff_date:
                filtered.append(stock)
        except (ValueError, TypeError):
            # 日付のパースに失敗した場合も含める
            filtered.append(stock)
    
    return filtered
