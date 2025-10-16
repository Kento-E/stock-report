#!/usr/bin/env python3
"""
テストケース数を自動算出してTEST.mdファイルを更新するスクリプト
"""

import subprocess
import re
import sys
from pathlib import Path


def count_tests_in_file(test_file):
    """
    指定されたテストファイルのテストケース数をカウントする
    
    Args:
        test_file: テストファイルのパス
    
    Returns:
        int: テストケース数
    """
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', test_file, '--collect-only', '-q'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 最後の行から "X tests collected" を抽出
        output = result.stdout.strip()
        if not output:
            return 0
        
        last_line = output.split('\n')[-1]
        match = re.search(r'(\d+) tests? collected', last_line)
        
        if match:
            return int(match.group(1))
        
        # "no tests collected" の場合
        if 'no tests collected' in last_line:
            return 0
        
        return 0
    except Exception as e:
        print(f"警告: {test_file} のテストカウントに失敗: {e}", file=sys.stderr)
        return 0


def get_test_counts():
    """
    全テストファイルのテストケース数を取得する
    
    Returns:
        dict: テストファイル名とテストケース数の辞書
    """
    tests_dir = Path('tests')
    test_files = sorted(tests_dir.glob('test_*.py'))
    
    counts = {}
    for test_file in test_files:
        count = count_tests_in_file(str(test_file))
        counts[test_file.name] = count
    
    return counts


def update_test_md(test_counts):
    """
    TEST.mdファイルのテストケース数を更新する
    
    Args:
        test_counts: テストファイル名とテストケース数の辞書
    
    Returns:
        bool: ファイルが更新されたかどうか
    """
    test_md_path = Path('docs/TEST.md')
    
    if not test_md_path.exists():
        print(f"エラー: {test_md_path} が見つかりません", file=sys.stderr)
        return False
    
    # ファイル読み込み
    content = test_md_path.read_text(encoding='utf-8')
    original_content = content
    
    # テーブルの部分を更新
    # テーブルの各行を更新
    for test_file, count in test_counts.items():
        # test_stock_loader.py -> stock_loader.py
        module_name = test_file.replace('test_', '').replace('.py', '.py')
        
        # 既存の行を検索して置換
        pattern = rf'\| `{re.escape(test_file)}` \| {re.escape(module_name)} \| \d+ \|'
        replacement = f'| `{test_file}` | {module_name} | {count} |'
        
        content = re.sub(pattern, replacement, content)
    
    # 変更があったかチェック
    if content == original_content:
        print("TEST.md に変更はありません")
        return False
    
    # ファイル書き込み
    test_md_path.write_text(content, encoding='utf-8')
    print("TEST.md を更新しました")
    
    # 更新内容を表示
    for test_file, count in test_counts.items():
        print(f"  {test_file}: {count} テスト")
    
    return True


def main():
    """メイン処理"""
    print("テストケース数を算出中...")
    
    # テストケース数を取得
    test_counts = get_test_counts()
    
    if not test_counts:
        print("エラー: テストファイルが見つかりません", file=sys.stderr)
        return 1
    
    # TEST.md を更新
    updated = update_test_md(test_counts)
    
    # 終了コード: 変更があった場合は0、なかった場合も0（成功）
    return 0


if __name__ == '__main__':
    sys.exit(main())
