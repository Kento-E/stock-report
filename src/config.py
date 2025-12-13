"""
環境変数と設定値の管理モジュール

このモジュールは環境変数の読み込みと、システム全体で使用される設定値を一元管理します。
"""

import os
import sys

from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()

# APIキー
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YAHOO_API_KEY = os.getenv("YAHOO_API_KEY")

# メール設定
MAIL_TO = os.getenv("MAIL_TO")

# 実行オプション判定（デフォルトGemini、--claude指定時のみClaude）
USE_CLAUDE = "--claude" in sys.argv

# Geminiモデル選択（デフォルト: gemini-2.0-flash-exp）
# 注: gemini-1.5-flashは2025年9月に廃止済み
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

# Gemini API 日次処理制限（デフォルト: 18）
# 無料枠は20 RPDだが、余裕を持たせて18に設定
try:
    GEMINI_DAILY_LIMIT = int(os.getenv("GEMINI_DAILY_LIMIT", "18"))
    if GEMINI_DAILY_LIMIT < 1 or GEMINI_DAILY_LIMIT > 20:
        print(f"警告: GEMINI_DAILY_LIMITの値が範囲外です（{GEMINI_DAILY_LIMIT}）。デフォルト値18を使用します。")
        GEMINI_DAILY_LIMIT = 18
except ValueError:
    print(f"警告: GEMINI_DAILY_LIMITの値が不正です。デフォルト値18を使用します。")
    GEMINI_DAILY_LIMIT = 18

# レポート簡略化オプション（デフォルト: true）
SIMPLIFY_HOLD_REPORTS = os.getenv("SIMPLIFY_HOLD_REPORTS", "true").lower() in ("true", "1", "yes")

# defeatbeta-apiの可用性チェック
try:
    from defeatbeta_api.data.ticker import Ticker

    DEFEATBETA_AVAILABLE = True
except ImportError:
    DEFEATBETA_AVAILABLE = False
    print("警告: defeatbeta-apiがインストールされていません。ニュース取得機能が制限されます。")
