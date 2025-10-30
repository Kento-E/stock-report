"""
レポート生成モジュール

分析結果をHTML形式のレポートとして生成する機能を提供します。
"""

from .simplifier import detect_hold_judgment, simplify_hold_report

__all__ = [
    'detect_hold_judgment',
    'simplify_hold_report',
]
