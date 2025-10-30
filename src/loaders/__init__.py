"""
データ読み込みモジュール

銘柄リストや投資志向性設定など、各種データの読み込み機能を提供します。
"""

from .stock_loader import (
    load_stock_symbols,
    categorize_stocks,
    get_currency_for_symbol,
    calculate_tax
)
from .preference_loader import (
    load_investment_preferences,
    generate_preference_prompt
)

__all__ = [
    'load_stock_symbols',
    'categorize_stocks',
    'get_currency_for_symbol',
    'calculate_tax',
    'load_investment_preferences',
    'generate_preference_prompt',
]
