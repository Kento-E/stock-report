"""
データ収集モジュール

株価データ（Yahoo Finance API）とニュースデータ（defeatbeta-api）を取得します。
"""

import requests

from config import DEFEATBETA_AVAILABLE, YAHOO_API_KEY

if DEFEATBETA_AVAILABLE:
    from defeatbeta_api.data.ticker import Ticker


def fetch_stock_data(symbol, stock_info=None):
    """
    株価とニュースデータを取得する。

    Args:
        symbol: 銘柄コード
        stock_info: 銘柄情報（保有数、取得単価など）

    Returns:
        株価、ニュース、保有情報を含む辞書
    """
    # Yahoo Finance API例（RapidAPI経由）
    url = "https://yfapi.net/v6/finance/quote"
    headers = {"x-api-key": YAHOO_API_KEY}
    params = {"symbols": symbol}
    price = None
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            result = response.json()
            price = result["quoteResponse"]["result"][0]["regularMarketPrice"]
    except Exception as e:
        print(f"株価取得失敗: {e}")
    news = fetch_news(symbol)

    data = {"symbol": symbol, "price": price, "news": news}

    # 保有情報を追加
    if stock_info:
        data["quantity"] = stock_info.get("quantity")
        data["acquisition_price"] = stock_info.get("acquisition_price")
        data["name"] = stock_info.get("name")
        data["currency"] = stock_info.get("currency")

    return data


def fetch_news(symbol):
    """
    defeatbeta-apiを使用して銘柄に関連するニュースを取得する。

    Args:
        symbol: 銘柄コード（例: 'TSLA', '7203.T'）

    Returns:
        ニュースの文字列リスト（最大5件）
    """
    if not DEFEATBETA_AVAILABLE:
        # defeatbeta-apiが利用できない場合はダミーデータを返す
        return [f"{symbol}関連ニュースが取得できません（defeatbeta-apiが必要です）"]

    try:
        # defeatbeta-apiを使用してニュースを取得
        ticker = Ticker(symbol)
        news_data = ticker.news()
        news_list = news_data.get_news_list()

        if news_list.empty:
            print(f"情報: {symbol}のニュースが見つかりませんでした。")
            return [f"{symbol}関連のニュースは現在ありません。"]

        # ニュース情報を整形（最大5件）
        formatted_news = []
        for idx, row in news_list.head(5).iterrows():
            title = row.get("title", "タイトルなし")
            publisher = row.get("publisher", "不明")
            report_date = row.get("report_date", "不明")
            # 簡潔なニュース文字列を作成
            news_str = f"[{report_date}] {publisher}: {title}"
            formatted_news.append(news_str)

        return formatted_news

    except Exception as e:
        # エラー時はダミーデータを返す
        print(f"ニュース取得エラー ({symbol}): {e}")
        return [f"{symbol}関連ニュースの取得に失敗しました"]
