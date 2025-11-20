"""
データ読み込みモジュール

銘柄リストや投資志向性設定など、各種データの読み込み機能を提供します。
"""

from .preference_loader import generate_preference_prompt, load_investment_preferences
from .stock_loader import (
    calculate_tax,
    categorize_stocks,
    get_currency_for_symbol,
    load_stock_symbols,
)

__all__ = [
    "load_stock_symbols",
    "categorize_stocks",
    "get_currency_for_symbol",
    "calculate_tax",
    "load_investment_preferences",
    "generate_preference_prompt",
]
