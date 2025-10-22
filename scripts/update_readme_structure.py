#!/usr/bin/env python3
"""
README.mdのファイル構造セクションを自動更新するスクリプト
"""
import os
import re
from pathlib import Path


def generate_file_structure():
    """
    src/ディレクトリのファイル構造を生成する
    """
    src_dir = Path("src")
    if not src_dir.exists():
        raise FileNotFoundError("src/ ディレクトリが見つかりません")
    
    # Pythonファイルを取得してソート
    py_files = sorted([f for f in src_dir.glob("*.py") if f.is_file()])
    
    # ファイル名とコメントのマッピング
    # main.pyは常に最後に配置
    file_comments = {
        "config.py": "環境変数と設定管理",
        "stock_loader.py": "YAML銘柄リスト読み込み・分類",
        "preference_loader.py": "投資志向性設定読み込み・プロンプト生成",
        "validate_stocks.py": "stocks.yamlバリデーション",
        "validate_preferences.py": "investment_preferences.yamlバリデーション",
        "data_fetcher.py": "株価・ニュースデータ取得",
        "ai_analyzer.py": "AI分析（Claude/Gemini）",
        "report_generator.py": "HTMLレポート生成",
        "report_simplifier.py": "レポート簡略化",
        "mail_utils.py": "メール配信・分類別本文生成",
        "main.py": "メインエントリーポイント",
    }
    
    # main.pyを除外してソート、最後にmain.pyを追加
    sorted_files = []
    main_py = None
    
    for f in py_files:
        if f.name == "main.py":
            main_py = f
        else:
            sorted_files.append(f)
    
    # main.pyを最後に追加
    if main_py:
        sorted_files.append(main_py)
    
    # 構造テキストを生成
    lines = ["```", "src/"]
    
    for i, file_path in enumerate(sorted_files):
        filename = file_path.name
        comment = file_comments.get(filename, "")
        
        # 最後のファイルかどうかで├──または└──を選択
        prefix = "└──" if i == len(sorted_files) - 1 else "├──"
        
        if comment:
            line = f"{prefix} {filename:<28} # {comment}"
        else:
            line = f"{prefix} {filename}"
        
        lines.append(line)
    
    lines.append("```")
    
    return "\n".join(lines)


def update_readme(new_structure):
    """
    README.mdのファイル構造セクションを更新する
    """
    readme_path = Path("README.md")
    
    if not readme_path.exists():
        raise FileNotFoundError("README.md が見つかりません")
    
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # ファイル構造のセクションを探す（```で始まりsrc/を含み```で終わるブロック）
    # システム構成セクション内の構造ブロックを特定
    pattern = r"(```\nsrc/\n(?:.*\n)*?```)"
    
    match = re.search(pattern, content)
    
    if not match:
        print("ファイル構造セクションが見つかりませんでした")
        return False
    
    old_structure = match.group(1)
    
    # 新しい構造と同じなら更新不要
    if old_structure == new_structure:
        print("ファイル構造に変更はありません")
        return False
    
    # 構造を置き換え
    new_content = content.replace(old_structure, new_structure)
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("README.md のファイル構造を更新しました")
    return True


def main():
    """
    メイン処理
    """
    try:
        # カレントディレクトリをリポジトリのルートに変更
        script_dir = Path(__file__).parent
        repo_root = script_dir.parent
        os.chdir(repo_root)
        
        print("ファイル構造を生成中...")
        new_structure = generate_file_structure()
        print(new_structure)
        print()
        
        print("README.md を更新中...")
        updated = update_readme(new_structure)
        
        if updated:
            print("✓ 更新が完了しました")
            return 0
        else:
            print("✓ 更新は不要でした")
            return 0
            
    except Exception as e:
        print(f"エラー: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
