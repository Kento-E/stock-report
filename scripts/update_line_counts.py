#!/usr/bin/env python3
"""
Pythonソースファイルの行数を自動算出してrequirements.instructions.mdファイルを更新するスクリプト
"""

import re
import sys
from pathlib import Path


def count_lines_in_file(file_path):
    """
    指定されたファイルの行数をカウントする
    
    Args:
        file_path: ファイルのパス（Path型）
    
    Returns:
        int: 行数
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except Exception as e:
        print(f"警告: {file_path} の行数カウントに失敗: {e}", file=sys.stderr)
        return 0


def get_source_file_line_counts():
    """
    srcディレクトリ内の全Pythonファイルの行数を取得する
    
    Returns:
        dict: ファイル名と行数の辞書
    """
    src_dir = Path('src')
    
    # 特定のファイルのみを対象とする（要件定義書に記載されているファイル）
    target_files = [
        'main.py',
        'config.py',
        'stock_loader.py',
        'data_fetcher.py',
        'ai_analyzer.py',
        'report_generator.py',
        'mail_utils.py'
    ]
    
    counts = {}
    for filename in target_files:
        file_path = src_dir / filename
        if file_path.exists():
            count = count_lines_in_file(file_path)
            counts[filename] = count
        else:
            print(f"警告: {file_path} が見つかりません", file=sys.stderr)
    
    return counts


def update_requirements_md(line_counts):
    """
    requirements.instructions.mdファイルの行数を更新する
    
    Args:
        line_counts: ファイル名と行数の辞書
    
    Returns:
        bool: ファイルが更新されたかどうか
    """
    req_md_path = Path('.github/instructions/requirements.instructions.md')
    
    if not req_md_path.exists():
        print(f"エラー: {req_md_path} が見つかりません", file=sys.stderr)
        return False
    
    # ファイル読み込み
    content = req_md_path.read_text(encoding='utf-8')
    original_content = content
    
    # 各ファイルの行数表記を更新
    # パターン: "- **filename**：説明（XX行）"
    for filename, count in line_counts.items():
        # ファイル名から拡張子を除いた部分を取得
        base_name = filename
        
        # 既存の行を検索して置換
        # 例: "- **main.py**：メインエントリーポイント。各モジュールを組み合わせたオーケストレーション処理（76行）"
        pattern = rf'(- \*\*{re.escape(base_name)}\*\*：[^（]+)（\d+行）'
        replacement = rf'\1（{count}行）'
        
        content = re.sub(pattern, replacement, content)
    
    # 変更があったかチェック
    if content == original_content:
        print("requirements.instructions.md に変更はありません")
        return False
    
    # ファイル書き込み
    req_md_path.write_text(content, encoding='utf-8')
    print("requirements.instructions.md を更新しました")
    
    # 更新内容を表示
    for filename, count in line_counts.items():
        print(f"  {filename}: {count} 行")
    
    return True


def main():
    """メイン処理"""
    print("ソースファイルの行数を算出中...")
    
    # 行数を取得
    line_counts = get_source_file_line_counts()
    
    if not line_counts:
        print("エラー: ソースファイルが見つかりません", file=sys.stderr)
        return 1
    
    # requirements.instructions.md を更新
    updated = update_requirements_md(line_counts)
    
    # 終了コード: 変更があった場合は0、なかった場合も0（成功）
    return 0


if __name__ == '__main__':
    sys.exit(main())
